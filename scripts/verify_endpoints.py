import requests

def test_endpoints():
    # Use the internal port 8085 and the correct v1 prefix
    base_url = "http://localhost:8085/v1"
    
    print("--- Testing Spanish Endpoints ---")
    
    # 1. Geografía
    print("Testing /geografia/estados...")
    resp = requests.get(f"{base_url}/geografia/estados")
    print(f"Status: {resp.status_code}")
    
    # 2. Catálogos / Calendario
    print("Testing /catalogos/calendario/festivos...")
    resp = requests.get(f"{base_url}/catalogos/calendario/festivos")
    print(f"Status: {resp.status_code}")
    
    # 3. Finanzas
    print("Testing /finanzas/instituciones...")
    resp = requests.get(f"{base_url}/finanzas/instituciones")
    print(f"Status: {resp.status_code}")
    
    # 4. Fiscal
    print("Testing /fiscal/unidades-medida...")
    resp = requests.get(f"{base_url}/fiscal/unidades-medida")
    print(f"Status: {resp.status_code}")

    # 5. INEGI
    print("Testing /inegi/localidades...")
    resp = requests.get(f"{base_url}/inegi/localidades")
    print(f"Status: {resp.status_code}")

if __name__ == "__main__":
    try:
        test_endpoints()
    except Exception as e:
        print(f"Connection error: {e}. Make sure the service is running.")
