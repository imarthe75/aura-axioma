import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Upload, 
  Database, 
  Clock, 
  ShieldCheck, 
  ChevronRight, 
  MapPin, 
  FileText, 
  TrendingUp, 
  Calendar,
  Filter,
  RefreshCw,
  MoreHorizontal
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

// API Configuration
const API_BASE = '/axioma/api';

const App = () => {
  const [activeTab, setActiveTab] = useState('explorer');
  const [activeCatalog, setActiveCatalog] = useState('geo');
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({});

  // Fetch data from API
  const fetchData = async () => {
    setLoading(true);
    try {
      let endpoint = '';
      let params = { q: searchTerm };

      if (activeCatalog === 'geo') {
        if (searchTerm.length === 5 && !isNaN(searchTerm)) {
          endpoint = `/geo/cp/${searchTerm}`;
        } else {
          endpoint = `/geo/settlements`;
        }
      } else if (activeCatalog === 'financial') {
        endpoint = `/financial/instituciones`;
        if (filters.tipo) params.tipo = filters.tipo;
      } else if (activeCatalog === 'fiscal') {
        endpoint = `/catalogs/fiscal/cat_prod_serv`;
        params.search = searchTerm;
      }

      const res = await axios.get(`${API_BASE}${endpoint}`, { params });
      setResults(Array.isArray(res.data) ? res.data : (res.data.data || [res.data]));
    } catch (err) {
      console.error(err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (searchTerm.length > 2 || activeTab === 'explorer') {
      const timer = setTimeout(fetchData, 500);
      return () => clearTimeout(timer);
    }
  }, [searchTerm, activeCatalog, filters]);

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col font-inter">
      {/* Premium Navbar */}
      <header className="premium-gradient text-white p-6 shadow-2xl flex justify-between items-center px-12 border-b border-white/10 sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <motion.div 
            whileHover={{ rotate: 180 }}
            transition={{ duration: 0.6 }}
            className="bg-gradient-to-br from-blue-500 to-emerald-500 p-2.5 rounded-xl shadow-lg shadow-blue-500/20"
          >
            <Database size={28} />
          </motion.div>
          <div className="flex flex-col">
            <h1 className="text-2xl font-extrabold tracking-tight outfit">Aura <span className="text-blue-400">Axioma</span></h1>
            <span className="text-[10px] uppercase tracking-[0.2em] opacity-50 font-semibold">Master Catalog Service</span>
          </div>
        </div>
        <nav className="flex gap-8 bg-white/5 p-1 rounded-full border border-white/10">
          {[
            { id: 'explorer', label: 'Explorador', icon: Search },
            { id: 'admin', label: 'Administración', icon: ShieldCheck },
            { id: 'docs', label: 'API Docs', icon: FileText }
          ].map((item) => (
            <button 
              key={item.id}
              onClick={() => setActiveTab(item.id)} 
              className={`flex items-center gap-2 px-6 py-2 rounded-full transition-all duration-300 ${
                activeTab === item.id 
                ? 'bg-white text-slate-900 shadow-lg font-bold' 
                : 'hover:bg-white/10 text-white/70'
              }`}
            >
              <item.icon size={18} />
              <span className="text-sm">{item.label}</span>
            </button>
          ))}
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-1 p-12 max-w-7xl mx-auto w-full">
        <AnimatePresence mode="wait">
          {activeTab === 'explorer' && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-10"
            >
              {/* Search Section */}
              <div className="glass-card p-10 rounded-[2rem] relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl"></div>
                
                <div className="flex flex-col md:flex-row justify-between items-end gap-6 mb-8 relative z-10">
                  <div className="max-w-xl">
                    <h2 className="text-3xl font-bold text-slate-800 mb-2 outfit">Consultar Catálogo Maestro</h2>
                    <p className="text-slate-500">Accede a la fuente única de verdad para datos geográficos, fiscales y financieros.</p>
                  </div>
                  <div className="flex gap-2 p-1 bg-slate-100 rounded-xl border border-slate-200">
                    {[
                      { id: 'geo', label: 'Geográfico', icon: MapPin },
                      { id: 'fiscal', label: 'Fiscal', icon: TrendingUp },
                      { id: 'financial', label: 'Financiero', icon: TrendingUp }
                    ].map(cat => (
                      <button
                        key={cat.id}
                        onClick={() => setActiveCatalog(cat.id)}
                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                          activeCatalog === cat.id ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                        }`}
                      >
                        {cat.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="relative group">
                  <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors" size={24} />
                  <input 
                    type="text" 
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder={
                      activeCatalog === 'geo' ? "Buscar por CP o Nombre de Asentamiento..." :
                      activeCatalog === 'fiscal' ? "Buscar Clave de Producto o Servicio SAT..." :
                      "Buscar Institución Financiera por nombre o clave..."
                    }
                    className="w-full pl-16 pr-6 py-6 bg-slate-50 border-2 border-slate-100 rounded-2xl focus:outline-none focus:border-blue-500 focus:bg-white transition-all text-xl shadow-inner shadow-slate-200/50"
                  />
                  {loading && (
                    <RefreshCw className="absolute right-6 top-1/2 -translate-y-1/2 text-blue-500 animate-spin" size={24} />
                  )}
                </div>

                {activeCatalog === 'financial' && (
                  <div className="flex gap-4 mt-6">
                    <span className="text-sm font-bold text-slate-400 flex items-center gap-2 uppercase tracking-wider"><Filter size={14}/> Filtrar por Tipo:</span>
                    {['BANCA MULTIPLE', 'SOFIPO', 'IFPE'].map(t => (
                      <button 
                        key={t}
                        onClick={() => setFilters(prev => ({...prev, tipo: prev.tipo === t ? null : t}))}
                        className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all border ${
                          filters.tipo === t ? 'bg-blue-500 border-blue-500 text-white shadow-md shadow-blue-500/20' : 'bg-white border-slate-200 text-slate-500 hover:border-blue-300'
                        }`}
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Results Section */}
              <div className="grid grid-cols-1 gap-8">
                <div className="flex justify-between items-center px-4">
                  <h3 className="text-xl font-bold text-slate-800 outfit">Resultados Encontrados ({results.length})</h3>
                  <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest">
                    <ShieldCheck size={14} className="text-green-500" /> Datos Certificados
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {results.length > 0 ? results.map((item, idx) => (
                    <motion.div 
                      key={item.id || idx}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: idx * 0.05 }}
                      className="bg-white p-6 rounded-3xl border border-slate-200 hover:border-blue-400 hover:shadow-xl hover:shadow-blue-500/5 transition-all group cursor-pointer"
                    >
                      <div className="flex justify-between items-start mb-6">
                        <div className="bg-slate-50 p-3 rounded-2xl group-hover:bg-blue-50 transition-colors">
                          {activeCatalog === 'geo' ? <MapPin className="text-blue-500" size={24}/> :
                           activeCatalog === 'fiscal' ? <TrendingUp className="text-emerald-500" size={24}/> :
                           <Database className="text-indigo-500" size={24}/>}
                        </div>
                        <span className="text-[10px] font-bold bg-slate-100 text-slate-500 px-3 py-1 rounded-full group-hover:bg-blue-100 group-hover:text-blue-600 transition-colors uppercase">
                          {item.cp || item.clave || item.code || 'ID:' + (item.id?.substring(0,4))}
                        </span>
                      </div>
                      <h4 className="font-bold text-slate-800 text-lg mb-2 leading-tight">
                        {item.name || item.nombre || item.description || 'Sin nombre'}
                      </h4>
                      <div className="space-y-2">
                        {item.municipality_name && <p className="text-sm text-slate-500 flex items-center gap-2"><MoreHorizontal size={14}/> {item.municipality_name}</p>}
                        {item.state_name && <p className="text-xs font-bold text-blue-600/70">{item.state_name}</p>}
                        {item.tipo_entidad && <p className="text-xs font-bold text-emerald-600/70">{item.tipo_entidad}</p>}
                      </div>
                    </motion.div>
                  )) : (
                    <div className="col-span-full py-20 text-center glass-card rounded-[2rem]">
                      <div className="bg-slate-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 text-slate-300">
                        <Search size={40} />
                      </div>
                      <p className="text-slate-400 font-medium">No se encontraron resultados para tu búsqueda.</p>
                      <button onClick={fetchData} className="mt-4 text-blue-500 font-bold hover:underline">Reintentar consulta</button>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'admin' && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white p-12 rounded-[2rem] shadow-sm border border-slate-200"
            >
              <div className="flex justify-between items-start mb-10">
                <div>
                  <h2 className="text-3xl font-bold text-slate-800 mb-2 outfit">Control de Ingesta SCD2</h2>
                  <p className="text-slate-500">Gestión de versiones y actualización de catálogos maestros.</p>
                </div>
                <button 
                  onClick={() => axios.post(`${API_BASE}/sync/initial`)}
                  className="bg-slate-900 text-white px-8 py-3 rounded-2xl font-bold hover:bg-blue-600 transition-all shadow-lg flex items-center gap-2"
                >
                  <RefreshCw size={20} /> Forzar Sincronización
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                <div className="lg:col-span-2">
                  <div className="border-3 border-dashed border-slate-200 rounded-[2.5rem] p-20 flex flex-col items-center justify-center bg-slate-50 hover:bg-slate-100 hover:border-blue-300 transition-all cursor-pointer group">
                    <motion.div 
                      whileHover={{ scale: 1.1 }}
                      className="bg-blue-500 p-6 rounded-3xl text-white mb-6 shadow-xl shadow-blue-500/30"
                    >
                      <Upload size={40} />
                    </motion.div>
                    <p className="text-slate-700 font-bold text-xl">Carga Masiva de Datos</p>
                    <p className="text-sm text-slate-400 mt-2">Suelta archivos .csv, .xls o .txt (SEPOMEX)</p>
                  </div>
                </div>
                
                <div className="space-y-6">
                  <div className="bg-emerald-50 border border-emerald-100 p-8 rounded-[2rem]">
                    <h4 className="font-bold text-emerald-800 mb-4 flex items-center gap-2"><ShieldCheck size={20}/> Integridad Referencial</h4>
                    <p className="text-sm text-emerald-700/80 leading-relaxed">El sistema aplica lógica Slow Changing Dimension Tipo 2 automáticamente para mantener el historial de cambios.</p>
                  </div>
                  <div className="bg-blue-50 border border-blue-100 p-8 rounded-[2rem]">
                    <h4 className="font-bold text-blue-800 mb-4 flex items-center gap-2"><Clock size={20}/> Última Sincronización</h4>
                    <p className="text-3xl font-black text-blue-900">Hoy, 09:42</p>
                    <p className="text-xs font-bold text-blue-600 mt-2 uppercase tracking-widest">Estado: Exitoso</p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Premium Footer */}
      <footer className="p-12 border-t border-slate-200 bg-white">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex flex-col items-center md:items-start">
            <h4 className="font-extrabold text-slate-800 outfit text-lg">Casmarts <span className="text-blue-500">Aura</span></h4>
            <p className="text-slate-400 text-sm mt-1">&copy; 2026 Inteligencia Corporativa para México.</p>
          </div>
          <div className="flex gap-12">
            <div>
              <p className="text-[10px] font-bold text-slate-300 uppercase tracking-[0.2em] mb-4">Sistemas</p>
              <div className="flex gap-6">
                <ShieldCheck size={20} className="text-slate-200 hover:text-blue-500 transition-colors cursor-pointer" />
                <Database size={20} className="text-slate-200 hover:text-blue-500 transition-colors cursor-pointer" />
                <Calendar size={20} className="text-slate-200 hover:text-blue-500 transition-colors cursor-pointer" />
              </div>
            </div>
            <div>
              <p className="text-[10px] font-bold text-slate-300 uppercase tracking-[0.2em] mb-4">Certificación</p>
              <div className="bg-slate-50 px-4 py-2 rounded-xl border border-slate-100 flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs font-bold text-slate-600">SCD2 v2.0 Operational</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
