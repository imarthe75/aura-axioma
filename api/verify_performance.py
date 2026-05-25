import time
import os
from sqlalchemy import create_engine, text

def benchmark_query(conn, query_text, params, label):
    latencies = []
    # Run 10 times to get average latency
    for _ in range(10):
        start = time.perf_counter()
        result = conn.execute(text(query_text), params)
        rows = result.fetchall()
        end = time.perf_counter()
        latencies.append((end - start) * 1000) # milliseconds
        
    avg_latency = sum(latencies) / len(latencies)
    print(f"[{label}]")
    print(f"  - Registros encontrados: {len(rows)}")
    print(f"  - Latencia promedio (10 ejecuciones): {avg_latency:.2f} ms")
    assert avg_latency < 50, f"ADVERTENCIA: Latencia promedio de {avg_latency:.2f}ms excede los 50ms!"
    print(f"  - Verificación: COMPLETA (Latencia < 50ms) ✅")

def main():
    db_url = os.getenv("DATABASE_URL", "postgresql://admin:casmarts_secure_db_pwd_2026@casmarts-core-db-primary:5432/db_core_knowledge")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("Iniciando Benchmarks de Búsqueda Predictiva Trigram...")
        
        # 1. Benchmark Asentamientos
        benchmark_query(
            conn,
            """
            SELECT id, name 
            FROM geo.asentamientos 
            WHERE name ILIKE :q 
            LIMIT 50
            """,
            {"q": "%Centro%"},
            "Geo Asentamientos Fuzzy Search"
        )
        
        # 2. Benchmark SAT Productos/Servicios
        benchmark_query(
            conn,
            """
            SELECT id, code, description 
            FROM fiscal.cat_prod_serv 
            WHERE (description ILIKE :q OR code ILIKE :q) 
              AND scd_is_current = TRUE
            LIMIT 50
            """,
            {"q": "%carbón%"},
            "SAT Productos/Servicios Fuzzy Search"
        )

if __name__ == "__main__":
    main()
