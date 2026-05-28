import React, { useState, useEffect, useCallback } from 'react';
import { AuthProvider, useAuth } from 'react-oidc-context';
import { 
  Search, Database, ShieldCheck, MapPin, TrendingUp, 
  Calendar, Filter, RefreshCw, MoreHorizontal, Loader2, 
  LogOut, LayoutDashboard, Landmark, FileJson, Menu, X,
  ChevronRight, Compass, ExternalLink, ArrowUpRight, History,
  CheckCircle2, AlertCircle, Plus, Edit3, Archive, Clock,
  Activity, GitBranch, Zap, Settings, Server, Cpu, CalendarClock
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import AuraShowcase from './components/AuraShowcase';

// OIDC Configuration - Dedicated Axioma Provider
const oidcConfig = {
  authority: "https://auth.casmart.internal/application/o/axioma/",
  client_id: "axioma",
  redirect_uri: window.location.origin,
  post_logout_redirect_uri: window.location.origin,
  response_type: "code",
  scope: "openid profile email",
};

const API_BASE = '/api/v1';

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

// Utility: format date to Mexico locale
const fmtDate = (iso) => {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('es-MX', { 
    day: '2-digit', month: 'short', year: 'numeric', 
    hour: '2-digit', minute: '2-digit', timeZone: 'America/Mexico_City' 
  });
};

const fmtDateShort = (dateStr) => {
  if (!dateStr) return '—';
  const d = new Date(dateStr + 'T12:00:00');
  return d.toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' });
};

// SCD2 Catalog Card
const SCD2CatalogCard = ({ data, color, icon: Icon, delay = 0 }) => {
  const colors = {
    blue:   { bg: 'bg-blue-500/10',   text: 'text-blue-400',   border: 'border-blue-500/20',   dot: 'bg-blue-400',   badge: 'bg-blue-500/10 text-blue-400' },
    emerald:{ bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/20', dot: 'bg-emerald-400', badge: 'bg-emerald-500/10 text-emerald-400' },
    indigo: { bg: 'bg-indigo-500/10',  text: 'text-indigo-400',  border: 'border-indigo-500/20',  dot: 'bg-indigo-400',  badge: 'bg-indigo-500/10 text-indigo-400' },
    amber:  { bg: 'bg-amber-500/10',   text: 'text-amber-400',   border: 'border-amber-500/20',   dot: 'bg-amber-400',   badge: 'bg-amber-500/10 text-amber-400' },
  };
  const c = colors[color] || colors.blue;
  if (!data) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className={`relative overflow-hidden rounded-2xl border ${c.border} bg-slate-900/60 p-6 flex flex-col gap-4 group hover:bg-slate-900/80 transition-all duration-300`}
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className={`w-10 h-10 rounded-xl ${c.bg} flex items-center justify-center ${c.text} group-hover:scale-110 transition-transform duration-300`}>
          <Icon size={20} />
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${c.dot} animate-pulse`} />
          <span className={`text-[10px] font-black uppercase tracking-widest ${c.text}`}>LIVE</span>
        </div>
      </div>

      {/* Label & Main Count */}
      <div>
        <p className="text-[11px] text-slate-500 font-black uppercase tracking-[0.18em] mb-1">{data.label}</p>
        <h3 className="text-4xl font-black text-white outfit tracking-tighter">{(data.current || 0).toLocaleString()}</h3>
        <p className="text-[11px] text-slate-600 mt-1">registros vigentes</p>
      </div>

      {/* SCD2 Metrics Row */}
      <div className="grid grid-cols-3 gap-2 pt-3 border-t border-white/5">
        <div className="flex flex-col items-center gap-1">
          <div className="flex items-center gap-1">
            <Plus size={10} className="text-emerald-400" />
            <span className="text-[18px] font-black text-emerald-400 outfit">{(data.new || 0).toLocaleString()}</span>
          </div>
          <span className="text-[9px] text-slate-600 font-black uppercase tracking-wider">Nuevos</span>
        </div>
        <div className="flex flex-col items-center gap-1">
          <div className="flex items-center gap-1">
            <Edit3 size={10} className="text-amber-400" />
            <span className="text-[18px] font-black text-amber-400 outfit">{(data.modified || 0).toLocaleString()}</span>
          </div>
          <span className="text-[9px] text-slate-600 font-black uppercase tracking-wider">Modificados</span>
        </div>
        <div className="flex flex-col items-center gap-1">
          <div className="flex items-center gap-1">
            <Archive size={10} className="text-slate-400" />
            <span className="text-[18px] font-black text-slate-400 outfit">{(data.historical || 0).toLocaleString()}</span>
          </div>
          <span className="text-[9px] text-slate-600 font-black uppercase tracking-wider">Histórico</span>
        </div>
      </div>

      {/* Last Sync */}
      <div className="flex items-center gap-2 pt-2 border-t border-white/5">
        <Clock size={11} className="text-slate-600" />
        <span className="text-[10px] text-slate-600 font-bold">Última sync: {fmtDate(data.last_update)}</span>
      </div>
    </motion.div>
  );
};

// Admin Panel Component
const AdminView = ({ adminStatus, adminLoading, fetchAdminStatus, handleSync, isSyncing, syncMessage }) => {
  if (adminLoading && !adminStatus) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-slate-400">
          <Loader2 className="animate-spin text-blue-500" size={40} />
          <p className="font-semibold text-sm animate-pulse">Obteniendo estado del sistema...</p>
        </div>
      </div>
    );
  }

  const sistema = adminStatus?.sistema || {};
  const cron = adminStatus?.proxima_sync_automatica || {};
  const catalogos = adminStatus?.catalogos || {};

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-8 max-w-7xl mx-auto"
    >
      {/* Title */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white outfit tracking-tight mb-1">Administración de Catálogos</h1>
          <p className="text-sm text-slate-500 font-medium">
            Control maestro del pipeline de datos, sincronización y auditoría del estado del motor SCD2.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={fetchAdminStatus}
            className="flex items-center gap-2 px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-slate-300 hover:text-white text-[12px] font-bold uppercase tracking-wider transition-all"
          >
            <RefreshCw size={14} />
            <span>Refrescar</span>
          </motion.button>
          <motion.button 
            whileHover={{ scale: 1.04, boxShadow: '0 12px 32px -8px rgba(59,130,246,0.45)' }}
            whileTap={{ scale: 0.96 }}
            onClick={handleSync}
            disabled={isSyncing}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold text-[13px] transition-all"
          >
            {isSyncing ? <Loader2 className="animate-spin" size={16} /> : <Zap size={16} />}
            <span>Sincronizar Todo</span>
          </motion.button>
        </div>
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* DB Card */}
        <div className="bg-slate-900/60 border border-white/5 rounded-2xl p-6 flex items-center gap-4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${sistema.db_status === 'ok' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
            <Database size={24} />
          </div>
          <div>
            <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-1">Base de Datos Central</p>
            <h3 className="text-lg font-bold text-white outfit">
              {sistema.db_status === 'ok' ? 'Conectado / Saludable' : 'Error de Conexión'}
            </h3>
            <span className="text-[11px] text-slate-600 font-mono">db_core_knowledge</span>
          </div>
        </div>

        {/* Celery Worker Card */}
        <div className="bg-slate-900/60 border border-white/5 rounded-2xl p-6 flex items-center gap-4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${sistema.celery_worker === 'ok' ? 'bg-emerald-500/10 text-emerald-400 animate-pulse' : 'bg-red-500/10 text-red-400'}`}>
            <Cpu size={24} />
          </div>
          <div>
            <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-1">Celery Workers (Async Sync)</p>
            <h3 className="text-lg font-bold text-white outfit">
              {sistema.celery_worker === 'ok' ? 'Activos y En Línea' : 'Desconectado'}
            </h3>
            <span className="text-[11px] text-slate-600 font-mono">
              {sistema.workers_activos && sistema.workers_activos.length > 0 ? sistema.workers_activos.join(', ') : 'Ninguno'}
            </span>
          </div>
        </div>

        {/* Next Sync Card */}
        <div className="bg-slate-900/60 border border-white/5 rounded-2xl p-6 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center">
            <CalendarClock size={24} />
          </div>
          <div>
            <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-1">Próxima Sync Programada</p>
            <h3 className="text-lg font-bold text-white outfit font-bold">
              En {cron.dias_restantes} días (Domingo)
            </h3>
            <span className="text-[10px] text-slate-600 block">
              {cron.schedule}
            </span>
          </div>
        </div>
      </div>

      {/* Sync feedback message */}
      <AnimatePresence>
        {syncMessage && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={`flex items-center gap-3 p-4 rounded-xl border text-sm font-bold ${
              syncMessage.type === 'success' 
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' 
                : 'bg-red-500/10 border-red-500/20 text-red-400'
            }`}
          >
            {syncMessage.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
            {syncMessage.text}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Catalogs SCD2 Audit Table */}
      <div className="bg-slate-900/60 border border-white/5 rounded-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-white/5 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Server size={16} className="text-blue-400" />
            <h2 className="text-sm font-black text-white uppercase tracking-widest">Estructura y Auditoría de Catálogos (SCD2)</h2>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5">
                <th className="px-6 py-3 text-left text-[10px] font-black text-slate-500 uppercase tracking-widest">Catálogo</th>
                <th className="px-6 py-3 text-left text-[10px] font-black text-slate-500 uppercase tracking-widest">Tabla Postgres</th>
                <th className="px-6 py-3 text-right text-[10px] font-black text-slate-500 uppercase tracking-widest">Vigentes (SCD2)</th>
                <th className="px-6 py-3 text-right text-[10px] font-black text-slate-500 uppercase tracking-widest">Historial</th>
                <th className="px-6 py-3 text-center text-[10px] font-black text-slate-500 uppercase tracking-widest">Versión Máx</th>
                <th className="px-6 py-3 text-left text-[10px] font-black text-slate-500 uppercase tracking-widest">Última Actualización</th>
                <th className="px-6 py-3 text-center text-[10px] font-black text-slate-500 uppercase tracking-widest">Estado</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(catalogos).map(([key, cat]) => (
                <tr key={key} className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors">
                  <td className="px-6 py-4">
                    <span className="font-bold text-white text-[14px]">{cat.label}</span>
                  </td>
                  <td className="px-6 py-4 font-mono text-[11px] text-slate-500">{cat.tabla}</td>
                  <td className="px-6 py-4 text-right font-black text-white text-[13px]">{cat.vigentes?.toLocaleString() || 0}</td>
                  <td className="px-6 py-4 text-right font-bold text-slate-400 text-[13px]">{cat.historicos?.toLocaleString() || 0}</td>
                  <td className="px-6 py-4 text-center">
                    <span className="px-2 py-0.5 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-md text-[11px] font-black">
                      v{cat.max_version || 1}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-400 text-[12px] font-medium">{cat.ultima_sync ? fmtDate(cat.ultima_sync) : '—'}</td>
                  <td className="px-6 py-4 text-center">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-wider ${
                      cat.status === 'ok' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
                    }`}>
                      {cat.status === 'ok' ? 'SALUDABLE' : 'ERROR'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
};

const AxiomaApp = () => {
  const auth = useAuth();
  
  useEffect(() => {
    if (auth.user?.access_token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${auth.user.access_token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [auth.user]);

  const [activeCatalog, setActiveCatalog] = useState('dashboard');
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({});
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState(null);
  const [stats, setStats] = useState(null);
  const [scd2History, setScd2History] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [adminStatus, setAdminStatus] = useState(null);
  const [adminLoading, setAdminLoading] = useState(false);

  const fetchStats = useCallback(async () => {
    if (!auth.user?.access_token) return;
    try {
      const res = await axios.get(`${API_BASE}/catalogs/stats`);
      setStats(res.data);
      setLastRefresh(new Date());
    } catch (err) {
      console.error("Failed to fetch stats", err);
    }
  }, [auth.user]);

  const fetchScd2History = useCallback(async () => {
    if (!auth.user?.access_token) return;
    setHistoryLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/catalogs/scd2-history?days=30`);
      setScd2History(res.data || []);
    } catch (err) {
      console.error("Failed to fetch SCD2 history", err);
    } finally {
      setHistoryLoading(false);
    }
  }, [auth.user]);

  const fetchAdminStatus = useCallback(async () => {
    if (!auth.user?.access_token) return;
    setAdminLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/admin/status`);
      setAdminStatus(res.data);
    } catch (err) {
      console.error('Admin status fetch failed', err);
    } finally {
      setAdminLoading(false);
    }
  }, [auth.user]);

  useEffect(() => {
    if (auth.user?.access_token) {
      fetchStats();
      fetchScd2History();
      // Auto-refresh every 60 seconds
      const interval = setInterval(() => {
        fetchStats();
        fetchScd2History();
      }, 60000);
      return () => clearInterval(interval);
    }
  }, [auth.user, fetchStats, fetchScd2History]);

  const fetchData = async () => {
    if (activeCatalog === 'dashboard') return;
    if (!auth.user?.access_token) return;
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
    if (auth.user?.access_token) {
      const timer = setTimeout(fetchData, 500);
      return () => clearTimeout(timer);
    }
  }, [searchTerm, activeCatalog, filters, auth.user]);

  const handleSync = async () => {
    setIsSyncing(true);
    setSyncMessage(null);
    try {
      const res = await axios.post(`${API_BASE}/catalogs/sync`);
      setSyncMessage({ type: 'success', text: res.data.message || 'Sincronización iniciada.' });
      // Refresh stats after 5s to pick up changes
      setTimeout(() => { fetchStats(); fetchScd2History(); }, 5000);
      setTimeout(() => setSyncMessage(null), 8000);
    } catch (err) {
      console.error(err);
      setSyncMessage({ type: 'error', text: 'Error al iniciar la sincronización' });
    } finally {
      setIsSyncing(false);
    }
  };

  const sidebarItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'showcase', label: 'Showcase SSoT', icon: Compass },
    { id: 'geo', label: 'SEPOMEX / Geo', icon: MapPin },
    { id: 'fiscal', label: 'SAT / Fiscal', icon: FileJson },
    { id: 'financial', label: 'CASFIM / Bancos', icon: Landmark },
    { id: 'holidays', label: 'Calendarios', icon: Calendar },
  ];

  // Navigate to admin and load its data
  const goToAdmin = () => {
    setActiveCatalog('admin');
    setSearchTerm('');
    setResults([]);
    fetchAdminStatus();
  };

  // Badge colors for SCD2 history catalog column
  const catalogBadgeColor = (cat) => {
    if (cat.includes('Geo') || cat.includes('SEPOMEX')) return 'bg-blue-500/15 text-blue-400 border-blue-500/20';
    if (cat.includes('SAT') || cat.includes('Fiscal')) return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20';
    if (cat.includes('CASFIM') || cat.includes('Banco')) return 'bg-indigo-500/15 text-indigo-400 border-indigo-500/20';
    return 'bg-slate-500/15 text-slate-400 border-slate-500/20';
  };

  return (
    <div className="flex h-screen bg-[#0f172a] text-slate-100 overflow-hidden selection:bg-blue-500/30">
      {/* Background Blobs */}
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none z-0">
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-500/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-500/5 rounded-full blur-[100px]" />
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
          <button
            onClick={goToAdmin}
            className={`w-full flex items-center gap-4 p-3.5 rounded-2xl transition-all group ${
              activeCatalog === 'admin' ? 'bg-blue-500/10 text-blue-400' : 'text-slate-400 hover:bg-white/5 hover:text-white'
            }`}
          >
            <Settings size={20} className={activeCatalog === 'admin' ? 'text-blue-400' : 'group-hover:text-blue-400 transition-colors'} />
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
        {/* Header */}
        <header className="h-16 glass-panel border-b border-white/5 px-6 flex justify-between items-center relative z-20">
          <div className="flex items-center gap-4">
            <motion.button 
              whileTap={{ scale: 0.9 }}
              onClick={() => setSidebarOpen(!isSidebarOpen)} 
              className="p-2 bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white rounded-xl transition-all"
            >
              {isSidebarOpen ? <X size={18} /> : <Menu size={18} />}
            </motion.button>
            <div className="flex flex-col">
              <h2 className="text-xl font-bold text-white outfit capitalize leading-none mb-0.5">{activeCatalog}</h2>
              <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Ecosistema Casmarts / Axioma</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Swagger button */}
            <motion.a
              href="/api/docs"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-xl text-slate-300 hover:text-white transition-all text-[12px] font-bold uppercase tracking-wider"
            >
              <Zap size={14} className="text-amber-400" />
              <span>API Docs</span>
              <ExternalLink size={12} className="opacity-50" />
            </motion.a>

            {/* Auto-refresh indicator */}
            {lastRefresh && (
              <div className="flex items-center gap-1.5 px-3 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-[10px] text-emerald-400 font-black uppercase tracking-wider">Live</span>
              </div>
            )}

            <div className="flex flex-col items-end">
              <span className="text-[14px] font-bold text-white leading-none mb-0.5">{auth.user?.profile.name || "Israel Martínez"}</span>
              <span className="text-[10px] text-blue-400/80 font-black uppercase tracking-[0.15em] outfit">Master Architect</span>
            </div>
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-500 to-emerald-500 p-[2px] shadow-lg shadow-blue-500/20"
            >
              <div className="w-full h-full rounded-[10px] bg-[#1e293b] flex items-center justify-center">
                <ShieldCheck className="text-white" size={16} />
              </div>
            </motion.div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8 scroll-smooth">
          <AnimatePresence mode="wait">
            {activeCatalog === 'dashboard' ? (
              <motion.div 
                key="dashboard" 
                initial={{ opacity: 0, y: 20 }} 
                animate={{ opacity: 1, y: 0 }} 
                exit={{ opacity: 0, y: -20 }}
                className="space-y-8 max-w-7xl mx-auto"
              >
                {/* ── Top Bar: Summary + Sync Controls ── */}
                <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
                  <div>
                    <h1 className="text-2xl font-black text-white outfit tracking-tight mb-1">Dashboard SSoT</h1>
                    <p className="text-sm text-slate-500 font-medium">
                      Sistema de Catálogos Maestros · SCD2 Automático · 
                      {lastRefresh && <span className="text-slate-600"> Actualizado {lastRefresh.toLocaleTimeString('es-MX')}</span>}
                    </p>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <motion.button
                      whileHover={{ scale: 1.03 }}
                      whileTap={{ scale: 0.97 }}
                      onClick={() => { fetchStats(); fetchScd2History(); }}
                      className="flex items-center gap-2 px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-slate-300 hover:text-white text-[12px] font-bold uppercase tracking-wider transition-all"
                    >
                      <RefreshCw size={14} />
                      <span>Actualizar</span>
                    </motion.button>
                    <motion.button 
                      whileHover={{ scale: 1.04, boxShadow: '0 12px 32px -8px rgba(59,130,246,0.45)' }}
                      whileTap={{ scale: 0.96 }}
                      onClick={handleSync}
                      disabled={isSyncing}
                      className={`flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold text-[13px] transition-all ${isSyncing ? 'opacity-60 cursor-not-allowed' : ''}`}
                    >
                      {isSyncing ? <Loader2 className="animate-spin" size={16} /> : <Zap size={16} />}
                      {isSyncing ? 'Sincronizando...' : 'Forzar Sync'}
                    </motion.button>
                  </div>
                </div>

                {/* Sync feedback message */}
                <AnimatePresence>
                  {syncMessage && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className={`flex items-center gap-3 p-4 rounded-xl border text-sm font-bold ${
                        syncMessage.type === 'success' 
                          ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' 
                          : 'bg-red-500/10 border-red-500/20 text-red-400'
                      }`}
                    >
                      {syncMessage.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
                      {syncMessage.text}
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* ── Summary Micro-stats Row ── */}
                {stats?.summary && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.05 }}
                    className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3"
                  >
                    {[
                      { label: 'Total Registros', value: (stats.summary.total_current || 0).toLocaleString(), icon: Database, color: 'text-blue-400' },
                      { label: 'Historial SCD2', value: (stats.summary.total_historical || 0).toLocaleString(), icon: History, color: 'text-slate-400' },
                      { label: 'Códigos Postales', value: (stats.summary.codigos_postales || 0).toLocaleString(), icon: MapPin, color: 'text-blue-400' },
                      { label: 'Municipios', value: (stats.summary.municipios || 0).toLocaleString(), icon: Activity, color: 'text-cyan-400' },
                      { label: 'Estados', value: (stats.summary.estados || 0).toLocaleString(), icon: GitBranch, color: 'text-purple-400' },
                      { label: 'Sectores CASFIM', value: (stats.summary.sectores_casfim || 0).toLocaleString(), icon: Landmark, color: 'text-indigo-400' },
                    ].map((item, i) => (
                      <motion.div
                        key={item.label}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.04 }}
                        className="bg-slate-900/60 border border-white/5 rounded-xl p-4 flex flex-col gap-2"
                      >
                        <item.icon size={14} className={item.color} />
                        <span className="text-xl font-black text-white outfit">{item.value}</span>
                        <span className="text-[10px] text-slate-600 font-bold uppercase tracking-wider leading-tight">{item.label}</span>
                      </motion.div>
                    ))}
                  </motion.div>
                )}

                {/* ── SCD2 Catalog Cards ── */}
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <GitBranch size={16} className="text-blue-400" />
                    <h2 className="text-sm font-black text-white uppercase tracking-widest">Catálogos SCD2 — Estado en Tiempo Real</h2>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                    <SCD2CatalogCard data={stats?.geo}       color="blue"    icon={MapPin}    delay={0.1} />
                    <SCD2CatalogCard data={stats?.fiscal}    color="emerald" icon={FileJson}  delay={0.15} />
                    <SCD2CatalogCard data={stats?.financial} color="indigo"  icon={Landmark}  delay={0.2} />
                    <SCD2CatalogCard data={stats?.calendars} color="amber"   icon={Calendar}  delay={0.25} />
                  </div>
                </div>

                {/* ── SCD2 Change History Table ── */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="bg-slate-900/60 border border-white/5 rounded-2xl overflow-hidden"
                >
                  <div className="flex items-center justify-between px-6 py-4 border-b border-white/5">
                    <div className="flex items-center gap-3">
                      <History size={16} className="text-slate-400" />
                      <h2 className="text-sm font-black text-white uppercase tracking-widest">Historial de Cambios SCD2</h2>
                      <span className="px-2 py-0.5 bg-slate-800 border border-white/10 rounded-full text-[10px] font-bold text-slate-400">Últimos 30 días</span>
                    </div>
                    {historyLoading && <Loader2 size={14} className="animate-spin text-slate-500" />}
                  </div>

                  {scd2History.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-white/5">
                            <th className="px-6 py-3 text-left text-[10px] font-black text-slate-500 uppercase tracking-widest">Fecha Sync</th>
                            <th className="px-6 py-3 text-left text-[10px] font-black text-slate-500 uppercase tracking-widest">Catálogo</th>
                            <th className="px-6 py-3 text-left text-[10px] font-black text-slate-500 uppercase tracking-widest">Tabla</th>
                            <th className="px-6 py-3 text-right text-[10px] font-black text-slate-500 uppercase tracking-widest">
                              <span className="flex items-center justify-end gap-1"><Plus size={10} className="text-emerald-400" />Nuevos</span>
                            </th>
                            <th className="px-6 py-3 text-right text-[10px] font-black text-slate-500 uppercase tracking-widest">
                              <span className="flex items-center justify-end gap-1"><Edit3 size={10} className="text-amber-400" />Modificados</span>
                            </th>
                            <th className="px-6 py-3 text-right text-[10px] font-black text-slate-500 uppercase tracking-widest">Total</th>
                          </tr>
                        </thead>
                        <tbody>
                          {scd2History.map((row, i) => (
                            <motion.tr
                              key={i}
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: i * 0.03 }}
                              className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors"
                            >
                              <td className="px-6 py-3.5 text-slate-300 font-bold text-[13px]">{fmtDateShort(row.sync_date)}</td>
                              <td className="px-6 py-3.5">
                                <span className={`inline-flex items-center px-2.5 py-1 rounded-lg border text-[10px] font-black uppercase tracking-wider ${catalogBadgeColor(row.catalog)}`}>
                                  {row.catalog}
                                </span>
                              </td>
                              <td className="px-6 py-3.5 font-mono text-[11px] text-slate-500">{row.tabla}</td>
                              <td className="px-6 py-3.5 text-right">
                                {row.nuevos > 0 
                                  ? <span className="font-black text-emerald-400 text-[13px]">+{row.nuevos.toLocaleString()}</span>
                                  : <span className="text-slate-600 text-[13px]">—</span>
                                }
                              </td>
                              <td className="px-6 py-3.5 text-right">
                                {row.modificados > 0 
                                  ? <span className="font-black text-amber-400 text-[13px]">{row.modificados.toLocaleString()}</span>
                                  : <span className="text-slate-600 text-[13px]">—</span>
                                }
                              </td>
                              <td className="px-6 py-3.5 text-right">
                                <span className="font-black text-white text-[13px]">{row.total_cambios.toLocaleString()}</span>
                              </td>
                            </motion.tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="py-16 text-center">
                      {historyLoading 
                        ? <Loader2 className="animate-spin text-slate-600 mx-auto" size={32} />
                        : (
                          <div className="flex flex-col items-center gap-3 text-slate-600">
                            <History size={32} className="opacity-30" />
                            <p className="text-sm font-bold">Sin cambios registrados en los últimos 30 días</p>
                          </div>
                        )
                      }
                    </div>
                  )}
                </motion.div>

                {/* ── SCD2 Info Bar ── */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                  className="flex flex-col md:flex-row items-start md:items-center gap-4 p-5 bg-slate-900/40 border border-white/5 rounded-2xl"
                >
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                      <ShieldCheck size={16} className="text-blue-400" />
                    </div>
                    <div>
                      <p className="text-[11px] font-black text-white uppercase tracking-wider">SCD2 Automated Intelligence</p>
                      <p className="text-[10px] text-slate-600">Sincronización automática cada domingo 2:00 AM</p>
                    </div>
                  </div>
                  <div className="flex-1 hidden md:block h-px bg-white/5" />
                  <div className="flex flex-wrap gap-4 text-[11px]">
                    {[
                      { label: 'SEPOMEX', schedule: 'Semanal', color: 'text-blue-400' },
                      { label: 'SAT', schedule: 'Mensual', color: 'text-emerald-400' },
                      { label: 'CASFIM', schedule: 'Mensual', color: 'text-indigo-400' },
                      { label: 'Calendarios', schedule: 'Anual', color: 'text-amber-400' },
                    ].map(s => (
                      <div key={s.label} className="flex items-center gap-1.5">
                        <span className={`font-black ${s.color}`}>{s.label}</span>
                        <span className="text-slate-600">·</span>
                        <span className="text-slate-500 font-bold">{s.schedule}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>

              </motion.div>
            ) : activeCatalog === 'showcase' ? (
              <AuraShowcase key="showcase" />
            ) : activeCatalog === 'admin' ? (
              <AdminView
                key="admin"
                adminStatus={adminStatus}
                adminLoading={adminLoading}
                fetchAdminStatus={fetchAdminStatus}
                handleSync={handleSync}
                isSyncing={isSyncing}
                syncMessage={syncMessage}
              />
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
                        {item.asentamiento || item.nombre || item.descripcion || item.name || item.description}
                      </h4>
                      <div className="space-y-4">
                        {/* Geo Data */}
                        {(item.municipio || item.estado) && (
                          <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2 text-slate-400 font-bold text-xs uppercase tracking-wider">
                              <MapPin size={12} className="text-blue-500" />
                              <span>Ubicación</span>
                            </div>
                            <p className="text-sm font-semibold text-slate-300 pl-5">
                              {item.municipio}, {item.estado}
                            </p>
                          </div>
                        )}
                        {/* Fiscal Data */}
                        {item.clave_unidad && (
                          <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2 text-slate-400 font-bold text-xs uppercase tracking-wider">
                              <FileJson size={12} className="text-emerald-500" />
                              <span>Detalle Fiscal</span>
                            </div>
                            <p className="text-sm font-semibold text-slate-300 pl-5">
                              Unidad: {item.clave_unidad} | IVA: {item.impuesto_iva ? 'Sí' : 'No'}
                            </p>
                          </div>
                        )}
                        {/* Financial Data */}
                        {item.razon_social && (
                          <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2 text-slate-400 font-bold text-xs uppercase tracking-wider">
                              <Landmark size={12} className="text-indigo-500" />
                              <span>Razón Social</span>
                            </div>
                            <p className="text-sm font-semibold text-slate-300 pl-5">
                              {item.razon_social}
                            </p>
                          </div>
                        )}
                        {/* Status Label */}
                        <div className="flex items-center gap-3 mt-4">
                           <div className="inline-block px-3 py-1 bg-emerald-500/10 text-emerald-400 text-[9px] font-black uppercase tracking-[0.2em] rounded-md border border-emerald-500/20">
                             ACTIVO
                           </div>
                           <div className="inline-block px-3 py-1 bg-blue-500/10 text-blue-400 text-[9px] font-black uppercase tracking-[0.2em] rounded-md border border-blue-500/20">
                             SSOT VERIFIED
                           </div>
                        </div>
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
