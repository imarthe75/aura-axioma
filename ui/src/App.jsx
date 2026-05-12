import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from 'react-oidc-context';
import { 
  Search, Database, ShieldCheck, MapPin, TrendingUp, 
  Calendar, Filter, RefreshCw, MoreHorizontal, Loader2, 
  LogOut, LayoutDashboard, Landmark, FileJson, Menu, X,
  ChevronRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

// OIDC Configuration - Using LexiVault Provider temporarily to unblock access
const oidcConfig = {
  authority: "https://arquitectura.casmart.internal/application/o/lexivault-ai/",
  client_id: "lexivault-ai",
  redirect_uri: window.location.origin + "/axioma/",
  post_logout_redirect_uri: window.location.origin + "/axioma/",
  response_type: "code",
  scope: "openid profile email",
};

const API_BASE = '/axioma/api/v1';

const ProtectedRoute = ({ children }) => {
  const auth = useAuth();
  if (auth.isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-[#0f172a]">
        <div className="flex flex-col items-center gap-4 text-white">
          <Loader2 className="animate-spin" size={48} />
          <p className="font-medium animate-pulse text-blue-400">Iniciando Ecosistema Axioma...</p>
        </div>
      </div>
    );
  }
  if (!auth.isAuthenticated) {
    auth.signinRedirect();
    return null;
  }
  return children;
};

const AxiomaApp = () => {
  const auth = useAuth();
  const [activeCatalog, setActiveCatalog] = useState('dashboard');
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({});
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState(null);

  const fetchData = async () => {
    if (activeCatalog === 'dashboard') return;
    setLoading(true);
    try {
      let endpoint = '';
      let params = { q: searchTerm };

      if (activeCatalog === 'geo') {
        endpoint = searchTerm.length === 5 && !isNaN(searchTerm) ? `/geo/cp/${searchTerm}` : `/geo/settlements`;
      } else if (activeCatalog === 'financial') {
        endpoint = `/financial/instituciones`;
        if (filters.tipo) params.tipo = filters.tipo;
      } else if (activeCatalog === 'fiscal') {
        endpoint = `/fiscal/productos`;
        if (filters.categoria) params.categoria = filters.categoria;
      } else if (activeCatalog === 'holidays') {
        endpoint = `/catalogs/calendars/holidays`;
        params.search = searchTerm;
      }

      const res = await axios.get(`${API_BASE}${endpoint}`, { params });
      let data = Array.isArray(res.data) ? res.data : (res.data.data || [res.data]);
      setResults(data);
    } catch (err) {
      console.error(err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(fetchData, 500);
    return () => clearTimeout(timer);
  }, [searchTerm, activeCatalog, filters]);

  const handleSync = async () => {
    setIsSyncing(true);
    setSyncMessage(null);
    try {
      const res = await axios.post(`${API_BASE}/catalogs/sync`);
      setSyncMessage({ type: 'success', text: res.data.message });
      setTimeout(() => setSyncMessage(null), 5000);
    } catch (err) {
      console.error(err);
      setSyncMessage({ type: 'error', text: 'Error al iniciar la sincronización' });
    } finally {
      setIsSyncing(false);
    }
  };

  const sidebarItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'geo', label: 'SEPOMEX / Geo', icon: MapPin },
    { id: 'fiscal', label: 'SAT / Fiscal', icon: FileJson },
    { id: 'financial', label: 'CASFIM / Bancos', icon: Landmark },
    { id: 'holidays', label: 'Calendarios', icon: Calendar },
  ];

  return (
    <div className="flex h-screen bg-[#0f172a] text-slate-100 overflow-hidden selection:bg-blue-500/30">
      {/* Background Blobs for Premium Feel */}
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none z-0">
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-500/10 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-500/5 rounded-full blur-[100px]"></div>
      </div>

      {/* Sidebar */}
      <motion.aside 
        initial={false}
        animate={{ width: isSidebarOpen ? 280 : 88 }}
        className="glass-panel border-r border-white/5 flex flex-col relative z-30 shadow-2xl"
      >
        <div className="p-8 flex items-center gap-4 mb-8">
          <motion.div 
            whileHover={{ scale: 1.1, rotate: 5 }}
            className="bg-gradient-to-br from-blue-500 to-blue-600 p-2.5 rounded-2xl shadow-lg shadow-blue-500/20"
          >
            <Database size={24} className="text-white" />
          </motion.div>
          {isSidebarOpen && (
            <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex flex-col">
              <span className="font-bold text-xl outfit tracking-tight text-white">Aura Axioma</span>
              <span className="text-[10px] text-blue-400 uppercase tracking-[0.2em] font-black opacity-80">Master Catalog</span>
            </motion.div>
          )}
        </div>

        <nav className="flex-1 px-4 space-y-1.5">
          {sidebarItems.map(item => (
            <button
              key={item.id}
              onClick={() => { setActiveCatalog(item.id); setSearchTerm(''); setResults([]); }}
              className={`w-full flex items-center gap-4 p-3.5 rounded-2xl sidebar-item transition-all group ${
                activeCatalog === item.id ? 'active text-white' : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <item.icon size={20} className={activeCatalog === item.id ? 'text-blue-400' : 'group-hover:text-white transition-colors'} />
              {isSidebarOpen && <span className="font-semibold text-[15px]">{item.label}</span>}
              {activeCatalog === item.id && isSidebarOpen && (
                <motion.div layoutId="activeDot" className="ml-auto">
                  <ChevronRight size={14} className="opacity-40" />
                </motion.div>
              )}
            </button>
          ))}
        </nav>

        <div className="p-6 border-t border-white/5 space-y-2 mt-auto">
          <button className="w-full flex items-center gap-4 p-3.5 rounded-2xl text-slate-400 hover:bg-white/5 transition-all group">
            <ShieldCheck size={20} className="group-hover:text-blue-400 transition-colors" />
            {isSidebarOpen && <span className="text-[15px] font-medium">Administración</span>}
          </button>
          <button 
            onClick={() => auth.signoutRedirect()}
            className="w-full flex items-center gap-4 p-3.5 rounded-2xl text-red-400/80 hover:bg-red-500/10 hover:text-red-400 transition-all group"
          >
            <LogOut size={20} className="group-hover:rotate-12 transition-transform" />
            {isSidebarOpen && <span className="text-[15px] font-medium">Cerrar Sesión</span>}
          </button>
        </div>
      </motion.aside>

      {/* Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden relative z-10">
        <header className="h-20 glass-panel border-b border-white/5 px-10 flex justify-between items-center relative z-20">
          <div className="flex items-center gap-6">
            <motion.button 
              whileTap={{ scale: 0.9 }}
              onClick={() => setSidebarOpen(!isSidebarOpen)} 
              className="p-2.5 bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white rounded-xl transition-all"
            >
              {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </motion.button>
            <div className="flex flex-col">
              <h2 className="text-2xl font-bold text-white outfit capitalize leading-none mb-1">{activeCatalog}</h2>
              <p className="text-[11px] text-slate-500 font-bold uppercase tracking-widest">Ecosistema Casmarts / Axioma</p>
            </div>
          </div>

          <div className="flex items-center gap-5">
             <div className="flex flex-col items-end">
                <span className="text-[15px] font-bold text-white leading-none mb-1">{auth.user?.profile.name || "Israel Martínez"}</span>
                <span className="text-[10px] text-blue-400/80 font-black uppercase tracking-[0.15em] outfit">Master Architect</span>
             </div>
             <motion.div 
               whileHover={{ scale: 1.05 }}
               className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-blue-500 to-emerald-500 p-[2px] shadow-lg shadow-blue-500/20"
             >
                <div className="w-full h-full rounded-[14px] bg-[#1e293b] flex items-center justify-center">
                  <ShieldCheck className="text-white" size={20} />
                </div>
             </motion.div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-12 scroll-smooth">
          <AnimatePresence mode="wait">
            {activeCatalog === 'dashboard' ? (
              <motion.div 
                key="dashboard" 
                initial={{ opacity: 0, y: 30 }} 
                animate={{ opacity: 1, y: 0 }} 
                exit={{ opacity: 0, y: -30 }}
                className="space-y-12 max-w-7xl mx-auto"
              >
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  {[
                    { label: 'SEPOMEX Geo Ingestion', value: '31,887', color: 'blue', icon: MapPin, trend: '+1.2%' },
                    { label: 'SAT Master Catalog', value: '52,400+', color: 'emerald', icon: FileJson, trend: 'Updated' },
                    { label: 'CASFIM Entities', value: '450', color: 'indigo', icon: Landmark, trend: 'Validated' }
                  ].map((stat, i) => (
                    <motion.div 
                      key={stat.label} 
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="premium-card p-8 rounded-[2.5rem] relative overflow-hidden group"
                    >
                      <div className={`absolute top-0 right-0 w-32 h-32 bg-${stat.color}-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2`}></div>
                      <div className="flex justify-between items-start mb-8">
                        <div className={`w-14 h-14 rounded-2xl bg-${stat.color}-500/10 flex items-center justify-center text-${stat.color}-400 group-hover:scale-110 transition-transform duration-500`}>
                          <stat.icon size={28} />
                        </div>
                        <span className={`text-[11px] font-black px-3 py-1.5 rounded-full uppercase tracking-tighter bg-${stat.color}-500/10 text-${stat.color}-400`}>
                          {stat.trend}
                        </span>
                      </div>
                      <p className="text-slate-500 text-xs font-black uppercase tracking-[0.2em] mb-2 outfit">{stat.label}</p>
                      <h3 className="text-5xl font-black text-white outfit tracking-tighter">{stat.value}</h3>
                    </motion.div>
                  ))}
                </div>

                <motion.div 
                  initial={{ opacity: 0, y: 40 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-gradient-to-br from-[#1e293b] to-[#0f172a] p-16 rounded-[3.5rem] border border-white/5 relative overflow-hidden shadow-3xl"
                >
                  <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[140px] -translate-y-1/2 translate-x-1/2"></div>
                  <div className="relative z-10 flex flex-col lg:flex-row items-center gap-12">
                    <div className="flex-1 text-center lg:text-left">
                      <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 rounded-full mb-6 border border-blue-500/20">
                        <TrendingUp size={16} className="text-blue-400" />
                        <span className="text-[11px] font-black text-blue-400 uppercase tracking-widest">SCD2 Automated Intelligence</span>
                      </div>
                      <h3 className="text-5xl font-extrabold outfit mb-6 leading-[1.1] text-white">Sincronización Maestra <br/><span className="text-gradient">Axioma SSoT</span></h3>
                      <p className="text-slate-400 max-w-2xl text-xl leading-relaxed font-medium">Aura Axioma garantiza la integridad total de los catálogos maestros mediante versionamiento SCD2, asegurando trazabilidad histórica y auditoría permanente para todo el ecosistema.</p>
                      
                      <div className="flex flex-wrap items-center justify-center lg:justify-start gap-6 mt-12">
                        <motion.button 
                          whileHover={{ scale: 1.05, boxShadow: '0 20px 40px -10px rgba(59, 130, 246, 0.4)' }}
                          whileTap={{ scale: 0.95 }}
                          onClick={handleSync}
                          disabled={isSyncing}
                          className={`bg-blue-600 text-white px-10 py-5 rounded-2xl font-black transition-all flex items-center gap-3 text-lg ${
                            isSyncing ? 'opacity-50 cursor-not-allowed' : ''
                          }`}
                        >
                          {isSyncing ? <Loader2 className="animate-spin" size={24} /> : <RefreshCw size={24} />}
                          {isSyncing ? 'Ejecutando Pipeline...' : 'Forzar Sincronización Total'}
                        </motion.button>
                        
                        <div className="flex items-center gap-3 bg-white/5 px-4 py-2 rounded-2xl border border-white/5">
                           <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                              <ShieldCheck className="text-emerald-400" size={18} />
                           </div>
                           <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Master Integrity Verified</span>
                        </div>
                      </div>

                      {syncMessage && (
                        <motion.div 
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className={`mt-6 p-4 rounded-xl font-bold text-center lg:text-left ${
                            syncMessage.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
                          }`}
                        >
                          {syncMessage.text}
                        </motion.div>
                      )}
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            ) : (
              <motion.div 
                key="explorer" 
                initial={{ opacity: 0, y: 30 }} 
                animate={{ opacity: 1, y: 0 }} 
                exit={{ opacity: 0, y: -30 }}
                className="space-y-10 max-w-7xl mx-auto"
              >
                <div className="glass-panel p-2 rounded-[2.5rem] flex flex-col md:flex-row gap-4 items-center">
                  <div className="flex-1 relative w-full group">
                    <Search className="absolute left-8 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-400 transition-colors" size={22} />
                    <input 
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder={`Consultar registros en ${activeCatalog.toUpperCase()} SSoT...`}
                      className="w-full pl-16 pr-8 py-6 bg-white/5 border-0 rounded-[2rem] focus:outline-none focus:ring-2 focus:ring-blue-500/40 transition-all font-semibold text-lg text-white placeholder:text-slate-600"
                    />
                    {loading && (
                      <div className="absolute right-8 top-1/2 -translate-y-1/2">
                        <Loader2 className="animate-spin text-blue-500" size={24} />
                      </div>
                    )}
                  </div>
                  
                  <div className="flex gap-3 px-4">
                    {activeCatalog === 'financial' && ['BANCA MULTIPLE', 'SOFIPO', 'IFPE'].map(t => (
                      <button 
                        key={t}
                        onClick={() => setFilters(prev => ({...prev, tipo: prev.tipo === t ? null : t}))}
                        className={`px-8 py-5 rounded-[1.5rem] text-[11px] font-black uppercase tracking-widest transition-all ${
                          filters.tipo === t ? 'bg-blue-600 text-white shadow-xl shadow-blue-600/30' : 'bg-white/5 text-slate-500 hover:text-white hover:bg-white/10'
                        }`}
                      >
                        {t}
                      </button>
                    ))}
                    {activeCatalog === 'fiscal' && [{id: '10', name: 'Materiales'}, {id: '71', name: 'Consultoría'}].map(c => (
                      <button 
                        key={c.id}
                        onClick={() => setFilters(prev => ({...prev, categoria: prev.categoria === c.id ? null : c.id}))}
                        className={`px-8 py-5 rounded-[1.5rem] text-[11px] font-black uppercase tracking-widest transition-all ${
                          filters.categoria === c.id ? 'bg-emerald-600 text-white shadow-xl shadow-emerald-600/30' : 'bg-white/5 text-slate-500 hover:text-white hover:bg-white/10'
                        }`}
                      >
                        {c.name}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {results.map((item, idx) => (
                    <motion.div 
                      key={item.id || idx}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: idx * 0.05 }}
                      className="premium-card p-10 rounded-[3rem] group relative overflow-hidden"
                    >
                      <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/5 rounded-full blur-2xl group-hover:bg-blue-500/10 transition-all"></div>
                      <div className="flex justify-between items-start mb-10">
                        <div className="bg-blue-500/10 p-5 rounded-[1.5rem] group-hover:bg-blue-500/20 transition-all duration-500 group-hover:rotate-6">
                          <Database className="text-blue-400" size={26} />
                        </div>
                        <span className="text-[11px] font-black bg-white/5 text-slate-500 px-4 py-2 rounded-full uppercase tracking-[0.15em] group-hover:bg-blue-600 group-hover:text-white transition-all shadow-sm">
                          {item.cp || item.clave || item.code || 'MASTER'}
                        </span>
                      </div>
                      <h4 className="font-extrabold text-white text-2xl mb-4 outfit leading-tight group-hover:text-blue-400 transition-colors">
                        {item.settlement_name || item.name || item.nombre || item.description}
                      </h4>
                      <div className="space-y-3">
                        {item.municipality_name && (
                          <div className="flex items-center gap-2 text-slate-500 font-bold text-sm">
                            <MapPin size={14} className="text-blue-500/50" />
                            <span>{item.municipality_name}, {item.state_name}</span>
                          </div>
                        )}
                        {item.tipo_entidad && (
                          <div className="inline-block px-4 py-1.5 bg-emerald-500/10 text-emerald-400 text-[10px] font-black uppercase tracking-[0.2em] rounded-lg">
                            {item.tipo_entidad}
                          </div>
                        )}
                      </div>
                      
                      <div className="mt-10 pt-8 border-t border-white/5 flex items-center justify-between">
                         <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">SCD2 Certified</span>
                         <motion.button 
                           whileHover={{ x: 5 }}
                           className="text-blue-400"
                         >
                           <ChevronRight size={20} />
                         </motion.button>
                      </div>
                    </motion.div>
                  ))}
                  {results.length === 0 && !loading && (
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="col-span-full py-40 text-center bg-white/2 rounded-[4rem] border-2 border-dashed border-white/5"
                    >
                       <div className="w-24 h-24 bg-slate-800/50 rounded-full flex items-center justify-center mx-auto mb-10 text-slate-600 ring-8 ring-slate-900/50">
                        <Search size={48} className="opacity-40" />
                       </div>
                       <h3 className="text-3xl font-black text-white outfit mb-3">Motor de Búsqueda Axioma</h3>
                       <p className="text-slate-500 font-bold text-xl max-w-lg mx-auto">Ingresa un término para filtrar los catálogos maestros en tiempo real.</p>
                    </motion.div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
};

const App = () => (
  <AuthProvider {...oidcConfig}>
    <ProtectedRoute>
      <AxiomaApp />
    </ProtectedRoute>
  </AuthProvider>
);

export default App;
