import React, { useState, useEffect } from 'react';
import { 
  MapPin, FileJson, Landmark, Search, ChevronRight, 
  Layers, AlertTriangle, HelpCircle, Loader2, Sparkles,
  Grid, Compass, ShieldAlert, ArrowRight, BookOpen, Calendar
} from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = '/api/v1';

export default function AuraShowcase() {
  const [activeTab, setActiveTab] = useState('geo'); // 'geo' | 'fiscal' | 'financial' | 'calendar'
  const [activeSubTab, setActiveSubTab] = useState('cascade'); // 'cascade' | 'cp' | 'fuzzy' for geo, 'tree' | 'search' for fiscal

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-20">
      {/* CÍVIKA Navigation Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-white/5 pb-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-[14px] bg-[#1a3a5c]/20 border border-[#1a3a5c]/30 flex items-center justify-center text-[#93c5fd]">
            <Compass size={24} className="animate-pulse" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white outfit leading-tight">Showcase de Integración SSoT</h1>
            <p className="text-[12px] text-slate-400 font-medium">Guía interactiva y demostrativa del consumo de catálogos maestros regulados.</p>
          </div>
        </div>
        
        {/* Main Tabs */}
        <div className="flex bg-slate-900/60 p-1.5 rounded-[14px] border border-white/5 self-stretch md:self-auto overflow-x-auto">
          {[
            { id: 'geo', label: 'SEPOMEX / INEGI', icon: MapPin },
            { id: 'fiscal', label: 'SAT / Fiscal', icon: FileJson },
            { id: 'financial', label: 'CASFIM / Bancos', icon: Landmark },
            { id: 'calendar', label: 'Calendario / Festivos', icon: Calendar }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => { setActiveTab(tab.id); setActiveSubTab(tab.id === 'geo' ? 'cascade' : tab.id === 'fiscal' ? 'tree' : tab.id === 'calendar' ? 'festivos' : 'bancos'); }}
              className={`flex-1 md:flex-none flex items-center justify-center gap-2 px-6 py-3.5 rounded-[10px] text-[13px] font-bold uppercase tracking-wider transition-all duration-200 ${
                activeTab === tab.id 
                  ? 'bg-[#1a3a5c] text-white shadow-lg shadow-[#1a3a5c]/30' 
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
              style={{ height: '44px' }}
            >
              <tab.icon size={16} />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Dynamic Content Frame */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Sidebar Info / Subtabs */}
        <div className="lg:col-span-1 space-y-6">
          <div className="civika-card p-6 border border-white/5">
            <h3 className="text-lg font-bold text-white mb-4 outfit flex items-center gap-2">
              <BookOpen size={18} className="text-blue-400" />
              Lineamientos
            </h3>
            
            {activeTab === 'geo' && (
              <div className="space-y-4 text-sm text-slate-400">
                <p>El Módulo Geográfico brinda consumo de **INEGI** (geometrías espaciales) con **SEPOMEX** (códigos postales) mediante relaciones geo-estadísticas.</p>
                <p className="border-t border-white/5 pt-4 text-xs">
                  <span className="font-bold text-slate-200">Búsquedas Soportadas:</span>
                  <ul className="list-disc list-inside mt-2 space-y-1.5">
                    <li>Cascada Gradual (4 pasos)</li>
                    <li>Búsqueda Inversa por CP</li>
                    <li>Autocomplete predictivo global</li>
                  </ul>
                </p>
              </div>
            )}

            {activeTab === 'fiscal' && (
              <div className="space-y-4 text-sm text-slate-400">
                <p>El Módulo Fiscal implementa los catálogos vigentes del **SAT**. Soporta indexación por clave y navegación de jerarquías multinivel.</p>
                <p className="border-t border-white/5 pt-4 text-xs">
                  <span className="font-bold text-slate-200">Jerarquía del Catálogo:</span>
                  <ul className="list-decimal list-inside mt-2 space-y-1.5">
                    <li>División (2 dígitos)</li>
                    <li>Grupo (4 dígitos)</li>
                    <li>Clase (6 dígitos)</li>
                    <li>Producto (8 dígitos)</li>
                  </ul>
                </p>
              </div>
            )}

            {activeTab === 'financial' && (
              <div className="space-y-4 text-sm text-slate-400">
                <p>El Módulo Financiero mapea las entidades vigentes y extinguidas de **CASFIM**. Implementa auditoría histórica mediante SCD dim-2.</p>
                <p className="border-t border-white/5 pt-4 text-xs">
                  <span className="font-bold text-slate-200">Reglas de Negocio:</span>
                  <ul className="list-disc list-inside mt-2 space-y-1.5">
                    <li>Mapeo de Absorción/Fusión</li>
                    <li>Filtrado bidireccional Sector/Entidad</li>
                    <li>Filtro histórico interactivo</li>
                  </ul>
                </p>
              </div>
            )}

            {activeTab === 'calendar' && (
              <div className="space-y-4 text-sm text-slate-400">
                <p>El Módulo de Calendarios expone el histórico y proyección de días festivos oficiales y no laborables de México según la regulación federal.</p>
                <p className="border-t border-white/5 pt-4 text-xs">
                  <span className="font-bold text-slate-200">Beneficios:</span>
                  <ul className="list-disc list-inside mt-2 space-y-1.5">
                    <li>Cálculo de nómina correcto</li>
                    <li>Vencimiento de plazos legales</li>
                    <li>Trazabilidad histórica</li>
                  </ul>
                </p>
              </div>
            )}
          </div>

          {/* Subtab selection for Geo & Fiscal */}
          {activeTab !== 'financial' && activeTab !== 'calendar' && (
            <div className="flex flex-col gap-2 bg-slate-900/40 p-2 rounded-[14px] border border-white/5">
              {activeTab === 'geo' ? (
                <>
                  {[
                    { id: 'cascade', label: 'Cascada Gradual' },
                    { id: 'cp', label: 'Búsqueda Inversa CP' },
                    { id: 'fuzzy', label: 'Predictivo Fuzzy' }
                  ].map(sub => (
                    <button
                      key={sub.id}
                      onClick={() => setActiveSubTab(sub.id)}
                      className={`w-full flex items-center justify-between px-4 rounded-[8px] text-[13px] font-bold transition-all ${
                        activeSubTab === sub.id 
                          ? 'bg-[#1a3a5c]/40 text-blue-400 border border-blue-500/20' 
                          : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent'
                      }`}
                      style={{ height: '44px' }}
                    >
                      <span>{sub.label}</span>
                      <ChevronRight size={14} className="opacity-40" />
                    </button>
                  ))}
                </>
              ) : (
                <>
                  {[
                    { id: 'tree', label: 'Árbol Jerárquico SAT' },
                    { id: 'search', label: 'Buscador Global GIN' }
                  ].map(sub => (
                    <button
                      key={sub.id}
                      onClick={() => setActiveSubTab(sub.id)}
                      className={`w-full flex items-center justify-between px-4 rounded-[8px] text-[13px] font-bold transition-all ${
                        activeSubTab === sub.id 
                          ? 'bg-[#1a3a5c]/40 text-blue-400 border border-blue-500/20' 
                          : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent'
                      }`}
                      style={{ height: '44px' }}
                    >
                      <span>{sub.label}</span>
                      <ChevronRight size={14} className="opacity-40" />
                    </button>
                  ))}
                </>
              )}
            </div>
          )}
        </div>

        {/* Right Content Showcase Area */}
        <div className="lg:col-span-3">
          <AnimatePresence mode="wait">
            {activeTab === 'geo' && activeSubTab === 'cascade' && <GeoCascade key="geo-cascade" />}
            {activeTab === 'geo' && activeSubTab === 'cp' && <GeoCPInverse key="geo-cp" />}
            {activeTab === 'geo' && activeSubTab === 'fuzzy' && <GeoFuzzySearch key="geo-fuzzy" />}
            
            {activeTab === 'fiscal' && activeSubTab === 'tree' && <FiscalHierarchy key="fiscal-tree" />}
            {activeTab === 'fiscal' && activeSubTab === 'search' && <FiscalFuzzySearch key="fiscal-search" />}
            
            {activeTab === 'financial' && <FinancialShowcase key="financial-main" />}
            {activeTab === 'calendar' && <CalendarShowcase key="calendar-main" />}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// Componente A.1: Búsqueda en Cascada Gradual (SEPOMEX)
// -------------------------------------------------------------
function GeoCascade() {
  const [countries, setCountries] = useState([]);
  const [states, setStates] = useState([]);
  const [municipalities, setMunicipalities] = useState([]);
  const [settlements, setSettlements] = useState([]);
  const [inegiLocalities, setInegiLocalities] = useState([]);
  const [loadingInegi, setLoadingInegi] = useState(false);

  const [selectedCountry, setSelectedCountry] = useState('');
  const [selectedState, setSelectedState] = useState('');
  const [selectedMunicipality, setSelectedMunicipality] = useState('');
  const [selectedSettlement, setSelectedSettlement] = useState('');
  const [settlementDetails, setSettlementDetails] = useState(null);

  // Cargar paises al inicio
  useEffect(() => {
    const fetchCountries = async () => {
      try {
        const res = await axios.get(`${API_BASE}/geo/paises`);
        const data = Array.isArray(res.data) ? res.data : [];
        setCountries(data);
        if (data.length > 0) {
          const mex = data.find(c => c.iso_alpha3 === 'MEX' || c.name.toLowerCase().includes('méxico'));
          if (mex) setSelectedCountry(mex.id);
        }
      } catch (err) {
        console.error(err);
        setCountries([]);
      }
    };
    fetchCountries();
  }, []);

  // Cargar Estados al cambiar País
  useEffect(() => {
    if (!selectedCountry) {
      setStates([]);
      return;
    }
    const fetchStates = async () => {
      try {
        const res = await axios.get(`${API_BASE}/geo/estados`, { params: { pais_id: selectedCountry } });
        setStates(Array.isArray(res.data) ? res.data : []);
        setSelectedState('');
        setSelectedMunicipality('');
        setSelectedSettlement('');
        setSettlementDetails(null);
      } catch (err) {
        console.error(err);
        setStates([]);
      }
    };
    fetchStates();
  }, [selectedCountry]);

  // Cargar Municipios al cambiar Estado
  useEffect(() => {
    if (!selectedState) {
      setMunicipalities([]);
      return;
    }
    const fetchMunicipalities = async () => {
      try {
        const res = await axios.get(`${API_BASE}/geo/municipios`, { params: { estado_id: selectedState } });
        setMunicipalities(Array.isArray(res.data) ? res.data : []);
        setSelectedMunicipality('');
        setSelectedSettlement('');
        setSettlementDetails(null);
      } catch (err) {
        console.error(err);
        setMunicipalities([]);
      }
    };
    fetchMunicipalities();
  }, [selectedState]);

  // Cargar Asentamientos al cambiar Municipio
  useEffect(() => {
    if (!selectedMunicipality) {
      setSettlements([]);
      return;
    }
    const fetchSettlements = async () => {
      try {
        const res = await axios.get(`${API_BASE}/geo/asentamientos`, { params: { municipio_id: selectedMunicipality } });
        setSettlements(Array.isArray(res.data) ? res.data : []);
        setSelectedSettlement('');
        setSettlementDetails(null);
      } catch (err) {
        console.error(err);
        setSettlements([]);
      }
    };
    fetchSettlements();
  }, [selectedMunicipality]);

  // Cargar Localidades de INEGI al cambiar Municipio
  useEffect(() => {
    if (!selectedMunicipality) {
      setInegiLocalities([]);
      return;
    }
    const fetchInegiLocalities = async () => {
      setLoadingInegi(true);
      try {
        const res = await axios.get(`${API_BASE}/inegi/localidades`, { params: { municipality_id: selectedMunicipality } });
        setInegiLocalities(Array.isArray(res.data) ? res.data : []);
      } catch (err) {
        console.error(err);
        setInegiLocalities([]);
      } finally {
        setLoadingInegi(false);
      }
    };
    fetchInegiLocalities();
  }, [selectedMunicipality]);

  // Cargar detalles cuando se selecciona el asentamiento
  const handleSettlementChange = (settlementId) => {
    setSelectedSettlement(settlementId);
    if (!settlementId) {
      setSettlementDetails(null);
      return;
    }
    const selected = settlements.find(s => s.id === settlementId);
    if (selected) {
      setSettlementDetails(selected);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="civika-card p-10 space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white mb-2 outfit flex items-center gap-2">
          <Layers className="text-blue-400" size={20} />
          Búsqueda en Cascada Gradual (SEPOMEX)
        </h2>
        <p className="text-slate-400 text-sm">Flujo de autocompletado en cascada. El payload final solo requiere el UUID del Asentamiento.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Selects */}
        <div className="space-y-5">
          <div className="flex flex-col gap-1.5">
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-widest pl-1">País</label>
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="civika-select w-full"
            >
              <option value="">Selecciona País...</option>
              {countries.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-widest pl-1">Estado</label>
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              disabled={!selectedCountry}
              className="civika-select w-full disabled:opacity-40"
            >
              <option value="">Selecciona Estado...</option>
              {states.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-widest pl-1">Municipio / Alcaldía</label>
            <select
              value={selectedMunicipality}
              onChange={(e) => setSelectedMunicipality(e.target.value)}
              disabled={!selectedState}
              className="civika-select w-full disabled:opacity-40"
            >
              <option value="">Selecciona Municipio...</option>
              {municipalities.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-widest pl-1">Asentamiento (Colonia)</label>
            <select
              value={selectedSettlement}
              onChange={(e) => handleSettlementChange(e.target.value)}
              disabled={!selectedMunicipality}
              className="civika-select w-full disabled:opacity-40"
            >
              <option value="">Selecciona Asentamiento...</option>
              {settlements.map(s => <option key={s.id} value={s.id}>{s.nombre} ({s.tipo})</option>)}
            </select>
          </div>
        </div>

        {/* Output Panel */}
        <div className="flex flex-col justify-center">
          {settlementDetails ? (
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }} 
              animate={{ scale: 1, opacity: 1 }}
              className="p-8 rounded-[14px] bg-[#1a3a5c]/10 border border-blue-500/20 space-y-6"
            >
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-[9px] font-black bg-blue-500/20 text-blue-300 px-2.5 py-1 rounded-full uppercase tracking-widest">
                    SSOT Geo-Match
                  </span>
                  <h4 className="text-2xl font-black text-white outfit mt-3">{settlementDetails.nombre}</h4>
                </div>
                <div className="text-right">
                  <span className="text-3xl font-black text-[#93c5fd] tracking-tighter outfit">{settlementDetails.codigo_postal}</span>
                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-0.5">Código Postal</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 border-t border-white/5 pt-4 text-sm">
                <div>
                  <p className="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Tipo Asentamiento</p>
                  <p className="text-slate-200 font-semibold mt-0.5">{settlementDetails.tipo || 'Colonia'}</p>
                </div>
                <div>
                  <p className="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Zona Habitacional</p>
                  <p className="text-slate-200 font-semibold mt-0.5">{settlementDetails.zona || 'Urbana'}</p>
                </div>
              </div>

              <div className="bg-slate-900/60 p-4 rounded-[8px] border border-white/5 text-xs font-mono space-y-1 text-slate-400">
                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest block mb-1">Payload a Enviar:</span>
                <div>{`{`}</div>
                <div className="pl-4 text-blue-300">"asentamiento_id": "{selectedSettlement}"</div>
                <div>{`}`}</div>
              </div>
            </motion.div>
          ) : (
            <div className="p-8 rounded-[14px] border border-dashed border-white/5 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
              <Layers size={40} className="text-slate-600 mb-4 opacity-40 animate-pulse" />
              <h4 className="text-white font-bold mb-2">Completado Automático SSoT</h4>
              <p className="text-slate-500 text-sm max-w-xs">Selecciona un asentamiento en la cascada para recuperar la geografía unificada e imprimir el CP.</p>
            </div>
          )}
        </div>
      </div>

      {/* Coordenadas y Georreferenciación INEGI */}
      {selectedMunicipality && (
        <div className="border-t border-white/5 pt-8 space-y-6">
          <div>
            <span className="text-[9px] font-black bg-emerald-500/20 text-emerald-300 px-2.5 py-1 rounded-full uppercase tracking-widest">
              Sincronización INEGI Geográfica
            </span>
            <h3 className="text-lg font-bold text-white mt-2 outfit">Coordenadas y Georreferenciación INEGI</h3>
            <p className="text-slate-400 text-xs mt-1">Localidades oficiales, coordenadas decimales de alta precisión y geometría espacial (PostGIS WKT).</p>
          </div>
          
          {loadingInegi ? (
            <div className="flex items-center gap-2 text-slate-400 py-4">
              <Loader2 size={16} className="animate-spin text-blue-500" />
              <span>Consultando georreferencias en caliente...</span>
            </div>
          ) : inegiLocalities.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {inegiLocalities.map((loc) => (
                <div key={loc.id} className="p-5 rounded-[14px] bg-slate-900/60 border border-white/5 flex flex-col justify-between hover:border-blue-500/30 transition-all duration-200">
                  <div>
                    <div className="flex justify-between items-start">
                      <h4 className="text-white font-bold">{loc.nombre}</h4>
                      <span className="text-[10px] font-mono bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded">Clave: {loc.clave_localidad}</span>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-2 mt-4 text-xs">
                      <div className="bg-slate-950/40 p-2.5 rounded-[8px] border border-white/5">
                        <span className="text-[9px] text-slate-500 font-bold block uppercase tracking-wider">Latitud</span>
                        <span className="text-slate-300 font-mono font-medium">{loc.latitud}° N</span>
                      </div>
                      <div className="bg-slate-950/40 p-2.5 rounded-[8px] border border-white/5">
                        <span className="text-[9px] text-slate-500 font-bold block uppercase tracking-wider">Longitud</span>
                        <span className="text-slate-300 font-mono font-medium">{loc.longitud}° W</span>
                      </div>
                      <div className="bg-slate-950/40 p-2.5 rounded-[8px] border border-white/5">
                        <span className="text-[9px] text-slate-500 font-bold block uppercase tracking-wider">Altitud</span>
                        <span className="text-slate-300 font-mono font-medium">{loc.altitud} msnm</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-500">
                    <span className="font-mono text-[9px] truncate max-w-[200px]">GEOM: POINT({loc.longitud} {loc.latitud})</span>
                    <span className="text-emerald-400 font-bold flex items-center gap-1">● Activo SSoT</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-6 rounded-[14px] bg-slate-900/40 border border-dashed border-white/5 text-center text-slate-500 text-xs">
              No se encontraron coordenadas INEGI para este municipio.
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
}

// -------------------------------------------------------------
// Componente A.2: Búsqueda Inversa por Código Postal (CP)
// -------------------------------------------------------------
function GeoCPInverse() {
  const [cp, setCp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);
  const [selectedSettlementId, setSelectedSettlementId] = useState('');
  const [selectedDetails, setSelectedDetails] = useState(null);

  const handleSearch = async (code) => {
    if (code.length !== 5 || isNaN(code)) {
      setData(null);
      setSelectedDetails(null);
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await axios.get(`${API_BASE}/geo/codigo-postal/${code}`);
      if (res.data && Array.isArray(res.data.asentamientos)) {
        setData(res.data);
      } else {
        setData(null);
        setError('Código Postal no tiene asentamientos válidos.');
      }
      setSelectedSettlementId('');
      setSelectedDetails(null);
    } catch (err) {
      console.error(err);
      setData(null);
      setError('Código Postal no registrado en el SSoT mexicano.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSettlement = (id) => {
    setSelectedSettlementId(id);
    if (!id || !data || !Array.isArray(data.asentamientos)) {
      setSelectedDetails(null);
      return;
    }
    const found = data.asentamientos.find(s => s.id === id);
    if (found) {
      setSelectedDetails(found);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="civika-card p-10 space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white mb-2 outfit flex items-center gap-2">
          <MapPin className="text-blue-400" size={20} />
          Búsqueda Inversa por Código Postal (CP)
        </h2>
        <p className="text-slate-400 text-sm">Al detectar 5 dígitos válidos, la API retorna la locación de nivel superior y una lista de asentamientos asociados.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="flex flex-col gap-2 relative">
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-widest pl-1">Código Postal (5 dígitos)</label>
            <div className="relative">
              <input
                type="text"
                maxLength={5}
                value={cp}
                onChange={(e) => { setCp(e.target.value); handleSearch(e.target.value); }}
                placeholder="Ej. 76000"
                className="civika-input w-full pr-12 text-lg font-mono tracking-widest"
              />
              {loading && <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 text-blue-500 animate-spin" size={20} />}
            </div>
            {error && <span className="text-xs text-red-400 font-bold mt-1 pl-1 flex items-center gap-1"><ShieldAlert size={12} />{error}</span>}
          </div>

          {data && (
            <motion.div initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
              <div className="flex flex-col gap-1.5">
                <label className="text-[11px] font-bold text-slate-400 uppercase tracking-widest pl-1">Asentamiento Asociado</label>
                <select
                  value={selectedSettlementId}
                  onChange={(e) => handleSelectSettlement(e.target.value)}
                  className="civika-select w-full"
                >
                  <option value="">Selecciona Colonia/Asentamiento...</option>
                  {(data.asentamientos || []).map(s => (
                    <option key={s.id} value={s.id}>{s.nombre} ({s.tipo})</option>
                  ))}
                </select>
              </div>

              <div className="space-y-3 bg-slate-900/60 p-6 rounded-[14px] border border-white/5 text-sm">
                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest block mb-2 border-b border-white/5 pb-2">Información Autopopulada</span>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase block">País</span>
                    <span className="text-white font-semibold">{data.pais}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase block">Estado</span>
                    <span className="text-white font-semibold">{data.estado}</span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-[10px] text-slate-500 font-bold uppercase block">Municipio</span>
                    <span className="text-white font-semibold">{data.municipio}</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Panel de detalles del Asentamiento Seleccionado */}
        <div>
          {selectedDetails ? (
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }} 
              animate={{ scale: 1, opacity: 1 }}
              className="p-8 rounded-[14px] bg-[#1a3a5c]/10 border border-blue-500/20 space-y-6"
            >
              <div>
                <span className="text-[9px] font-black bg-blue-500/20 text-blue-300 px-2.5 py-1 rounded-full uppercase tracking-widest">
                  Filtro Inverso Validado
                </span>
                <h4 className="text-2xl font-black text-white outfit mt-3">{selectedDetails.nombre}</h4>
                <p className="text-[#93c5fd] font-bold text-sm mt-1">{selectedDetails.tipo} — Zona {selectedDetails.zona}</p>
              </div>

              <div className="bg-slate-900/60 p-4 rounded-[8px] border border-white/5 text-xs font-mono space-y-1 text-slate-400">
                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest block mb-1">Payload Completo a Enviar:</span>
                <div>{`{`}</div>
                <div className="pl-4 text-blue-300">"cp": "{cp}",</div>
                <div className="pl-4 text-blue-300">"pais_id": "{data.pais_id}",</div>
                <div className="pl-4 text-blue-300">"estado_id": "{data.estado_id}",</div>
                <div className="pl-4 text-blue-300">"municipio_id": "{data.municipio_id}",</div>
                <div className="pl-4 text-blue-300">"asentamiento_id": "{selectedSettlementId}"</div>
                <div>{`}`}</div>
              </div>
            </motion.div>
          ) : (
            <div className="p-8 rounded-[14px] border border-dashed border-white/5 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
              <MapPin size={40} className="text-slate-600 mb-4 opacity-40" />
              <h4 className="text-white font-bold mb-2">Ingresa un CP Válido</h4>
              <p className="text-slate-500 text-sm max-w-xs">Escribe un Código Postal de 5 dígitos para disparar la llamada reversa.</p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// -------------------------------------------------------------
// Componente A.3: Búsqueda Predictiva de Asentamiento (Fuzzy Search)
// -------------------------------------------------------------
function GeoFuzzySearch() {
  const [q, setQ] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    if (q.length < 2) {
      setResults([]);
      setShowDropdown(false);
      return;
    }

    const delayDebounce = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${API_BASE}/geo/asentamientos`, { params: { q } });
        setResults(Array.isArray(res.data) ? res.data : []);
        setShowDropdown(true);
      } catch (err) {
        console.error(err);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [q]);

  const handleSelect = (item) => {
    setSelectedItem(item);
    setQ(item.nombre);
    setShowDropdown(false);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="civika-card p-10 space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white mb-2 outfit flex items-center gap-2">
          <Sparkles className="text-blue-400" size={20} />
          Búsqueda Predictiva Global (Fuzzy Search)
        </h2>
        <p className="text-slate-400 text-sm">Autocomplete predictivo por similitud de texto. Resuelve e indexa nombres o CPs en bases de datos masivas en milisegundos.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Search Input and autocomplete list */}
        <div className="space-y-4 relative">
          <div className="flex flex-col gap-2 relative">
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-widest pl-1">Buscar Colonia o Código Postal</label>
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input
                type="text"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Escribe asentamiento o CP (ej. Centro, 76000)..."
                className="civika-input w-full pl-12"
              />
              {loading && <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 text-blue-500 animate-spin" size={18} />}
            </div>

            {/* Suggestions list */}
            {showDropdown && results.length > 0 && (
              <ul className="absolute top-[82px] left-0 w-full bg-slate-900 border border-white/10 rounded-[10px] overflow-hidden shadow-2xl z-50 max-h-60 overflow-y-auto">
                {results.map((item) => (
                  <li
                    key={item.id || item.nombre}
                    onClick={() => handleSelect(item)}
                    className="px-4 py-3.5 hover:bg-[#1a3a5c]/30 cursor-pointer border-b border-white/5 flex items-center justify-between text-sm"
                  >
                    <div className="flex flex-col">
                      <span className="text-white font-semibold">{item.nombre}</span>
                      <span className="text-[10px] text-slate-500 font-medium">{item.municipio}, {item.estado}</span>
                    </div>
                    <span className="text-xs font-mono font-bold text-[#93c5fd] bg-blue-500/10 px-2 py-0.5 rounded">
                      {item.cp}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Selected Data Card */}
        <div>
          {selectedItem ? (
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }} 
              animate={{ scale: 1, opacity: 1 }}
              className="p-8 rounded-[14px] bg-[#1a3a5c]/10 border border-blue-500/20 space-y-6"
            >
              <div>
                <span className="text-[9px] font-black bg-blue-500/20 text-blue-300 px-2.5 py-1 rounded-full uppercase tracking-widest">
                  GIN Trigram Match
                </span>
                <h4 className="text-2xl font-black text-white outfit mt-3">{selectedItem.nombre}</h4>
                <p className="text-xs font-bold text-[#93c5fd] mt-1">{selectedItem.tipo} | {selectedItem.zona}</p>
              </div>

              <div className="grid grid-cols-2 gap-4 border-t border-white/5 pt-4 text-sm">
                <div>
                  <span className="text-[10px] text-slate-500 font-bold block uppercase">País</span>
                  <span className="text-slate-200 font-semibold">{selectedItem.pais}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 font-bold block uppercase">Código Postal</span>
                  <span className="text-[#93c5fd] font-mono font-bold">{selectedItem.cp}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 font-bold block uppercase">Estado</span>
                  <span className="text-slate-200 font-semibold">{selectedItem.estado}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 font-bold block uppercase">Municipio</span>
                  <span className="text-slate-200 font-semibold">{selectedItem.municipio}</span>
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="p-8 rounded-[14px] border border-dashed border-white/5 flex flex-col items-center justify-center text-center h-full min-h-[220px]">
              <Search size={40} className="text-slate-600 mb-4 opacity-40" />
              <h4 className="text-white font-bold mb-2">Autocomplete Fuzzy</h4>
              <p className="text-slate-500 text-sm max-w-xs">Empieza a escribir para que el trigrama filtre y devuelva la coincidencia.</p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// -------------------------------------------------------------
// Componente B.1: Jerarquía por Niveles SAT (Árbol Jerárquico)
// -------------------------------------------------------------
function FiscalHierarchy() {
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedNodes, setExpandedNodes] = useState({}); // code -> child array
  const [selectedProduct, setSelectedProduct] = useState(null);

  // Cargar divisiones iniciales
  useEffect(() => {
    const fetchDivisions = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${API_BASE}/fiscal/productos/hierarchy`);
        setNodes(Array.isArray(res.data) ? res.data : []);
      } catch (err) {
        console.error(err);
        setNodes([]);
      } finally {
        setLoading(false);
      }
    };
    fetchDivisions();
  }, []);

  const toggleNode = async (code) => {
    // Si ya está expandido, lo colapsamos
    if (expandedNodes[code]) {
      const updated = { ...expandedNodes };
      delete updated[code];
      setExpandedNodes(updated);
      return;
    }

    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/fiscal/productos/hierarchy`, { params: { parent_code: code } });
      if (Array.isArray(res.data)) {
        setExpandedNodes(prev => ({ ...prev, [code]: res.data }));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectProduct = (prod) => {
    setSelectedProduct(prod);
  };

  // Renderizador recursivo para los nodos del árbol
  const renderNode = (node, depth = 0) => {
    const code = node.code;
    const isExpanded = !!expandedNodes[code];
    const isLeaf = code.length === 8 && !code.endsWith('00'); // Un producto real de 8 digitos

    return (
      <div key={code} className="space-y-1">
        <div 
          onClick={() => isLeaf ? handleSelectProduct(node) : toggleNode(code)}
          className={`flex items-center gap-3 px-4 rounded-[8px] hover:bg-white/5 cursor-pointer text-sm transition-all group ${
            selectedProduct?.code === code ? 'bg-[#1a3a5c]/30 border-l-2 border-blue-500 text-white' : 'text-slate-300'
          }`}
          style={{ height: '44px', paddingLeft: `${Math.max(16, depth * 24)}px` }}
        >
          {!isLeaf && (
            <ChevronRight 
              size={16} 
              className={`text-slate-500 group-hover:text-white transition-transform ${isExpanded ? 'rotate-90 text-blue-400' : ''}`} 
            />
          )}
          {isLeaf && <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5"></div>}
          <span className="font-mono font-bold text-slate-500 group-hover:text-blue-400 w-24 flex-shrink-0">{code}</span>
          <span className="truncate font-medium">{node.description}</span>
        </div>

        {isExpanded && expandedNodes[code] && (
          <div className="space-y-1">
            {expandedNodes[code].map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="civika-card p-10 space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white mb-2 outfit flex items-center gap-2">
          <Layers className="text-blue-400" size={20} />
          Navegador Jerárquico SAT
        </h2>
        <p className="text-slate-400 text-sm">Explora las dependencias jerárquicas multinivel reguladas por el SAT mexicano (División ➜ Grupo ➜ Clase ➜ Producto).</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Hierarchical Tree Panel */}
        <div className="lg:col-span-3 border border-white/5 bg-slate-950/40 rounded-[14px] p-6 max-h-[500px] overflow-y-auto space-y-2">
          <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-3">
            <span className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Catálogo Jerárquico</span>
            {loading && <Loader2 className="animate-spin text-blue-400" size={16} />}
          </div>
          
          <div className="space-y-1">
            {nodes.map(node => renderNode(node, 0))}
          </div>
        </div>

        {/* Details Panel */}
        <div className="lg:col-span-2 flex flex-col justify-start">
          {selectedProduct ? (
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }} 
              animate={{ scale: 1, opacity: 1 }}
              className="p-8 rounded-[14px] bg-[#1a3a5c]/10 border border-blue-500/20 space-y-6"
            >
              <div>
                <span className="text-[9px] font-black bg-emerald-500/20 text-emerald-300 px-2.5 py-1 rounded-full uppercase tracking-widest">
                  Clave de 8 Dígitos SAT
                </span>
                <h4 className="text-2xl font-black text-white outfit mt-3">{selectedProduct.description}</h4>
              </div>

              <div className="space-y-3 border-t border-white/5 pt-4 text-sm">
                <div>
                  <span className="text-[10px] text-slate-500 font-bold uppercase block">Código SAT</span>
                  <span className="text-[#93c5fd] font-mono text-lg font-bold">{selectedProduct.code}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 font-bold uppercase block">Jerarquía</span>
                  <span className="text-slate-300 font-semibold block mt-1">
                    División: {selectedProduct.code.substring(0, 2)}000000<br/>
                    Grupo: {selectedProduct.code.substring(0, 4)}0000<br/>
                    Clase: {selectedProduct.code.substring(0, 6)}00
                  </span>
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="p-8 rounded-[14px] border border-dashed border-white/5 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
              <Layers size={40} className="text-slate-600 mb-4 opacity-40" />
              <h4 className="text-white font-bold mb-2">Selecciona Clave Producto</h4>
              <p className="text-slate-500 text-sm max-w-xs">Navega abriendo subniveles de división, grupo y clase hasta encontrar la clave final requerida.</p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// -------------------------------------------------------------
// Componente B.2: Búsqueda Global Indexada (Fuzzy Search SAT)
// -------------------------------------------------------------
function FiscalFuzzySearch() {
  const [prodQuery, setProdQuery] = useState('');
  const [unitQuery, setUnitQuery] = useState('');
  
  const [products, setProducts] = useState([]);
  const [units, setUnits] = useState([]);
  
  const [loadingProd, setLoadingProd] = useState(false);
  const [loadingUnit, setLoadingUnit] = useState(false);
  
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [selectedUnit, setSelectedUnit] = useState(null);

  // Búsqueda de Productos
  useEffect(() => {
    if (prodQuery.length < 2) {
      setProducts([]);
      return;
    }
    const delay = setTimeout(async () => {
      setLoadingProd(true);
      try {
        const res = await axios.get(`${API_BASE}/fiscal/productos`, { params: { q: prodQuery } });
        setProducts(Array.isArray(res.data) ? res.data : []);
      } catch (err) {
        console.error(err);
        setProducts([]);
      } finally {
        setLoadingProd(false);
      }
    }, 300);
    return () => clearTimeout(delay);
  }, [prodQuery]);

  // Búsqueda de Unidades
  useEffect(() => {
    if (unitQuery.length < 1) {
      setUnits([]);
      return;
    }
    const delay = setTimeout(async () => {
      setLoadingUnit(true);
      try {
        const res = await axios.get(`${API_BASE}/fiscal/unidades-medida`, { params: { q: unitQuery } });
        setUnits(Array.isArray(res.data) ? res.data : []);
      } catch (err) {
        console.error(err);
        setUnits([]);
      } finally {
        setLoadingUnit(false);
      }
    }, 250);
    return () => clearTimeout(delay);
  }, [unitQuery]);

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="civika-card p-10 space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white mb-2 outfit flex items-center gap-2">
          <Search className="text-blue-400" size={20} />
          Buscador Global Indexado (Productos y Unidades)
        </h2>
        <p className="text-slate-400 text-sm">Búsqueda veloz en catálogos fiscales masivos indexados en Postgres mediante operadores trigram GIN.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Productos Column */}
        <div className="space-y-4 relative">
          <div className="flex flex-col gap-2 relative">
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-widest pl-1">Buscador de Productos / Servicios</label>
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input
                type="text"
                value={selectedProduct ? selectedProduct.description : prodQuery}
                onChange={(e) => { setProdQuery(e.target.value); if (selectedProduct) setSelectedProduct(null); }}
                placeholder="Escribe descripción o código (ej. Carbón, 1010)..."
                className="civika-input w-full pl-12"
              />
              {loadingProd && <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 text-blue-500 animate-spin" size={18} />}
            </div>

            {prodQuery.length >= 2 && !selectedProduct && products.length > 0 && (
              <ul className="absolute top-[82px] left-0 w-full bg-slate-900 border border-white/10 rounded-[10px] overflow-hidden shadow-2xl z-50 max-h-48 overflow-y-auto">
                {products.map(p => (
                  <li
                    key={p.code}
                    onClick={() => { setSelectedProduct(p); setProdQuery(p.description); }}
                    className="px-4 py-3 hover:bg-[#1a3a5c]/30 cursor-pointer border-b border-white/5 flex items-center justify-between text-xs"
                  >
                    <span className="text-white font-medium truncate w-[75%]">{p.description}</span>
                    <span className="text-[10px] font-mono font-bold text-[#93c5fd] bg-blue-500/10 px-2 py-0.5 rounded">{p.code}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {selectedProduct && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-5 rounded-[10px] bg-emerald-500/5 border border-emerald-500/10 space-y-2">
              <span className="text-[9px] font-bold text-emerald-400 uppercase tracking-wider">Producto Seleccionado</span>
              <p className="text-white text-sm font-bold">{selectedProduct.description}</p>
              <p className="text-xs text-slate-400 font-mono">Clave SAT: <span className="text-[#93c5fd] font-bold">{selectedProduct.code}</span></p>
            </motion.div>
          )}
        </div>

        {/* Unidades Column */}
        <div className="space-y-4 relative">
          <div className="flex flex-col gap-2 relative">
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-widest pl-1">Buscador de Unidades de Medida</label>
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input
                type="text"
                value={selectedUnit ? selectedUnit.name : unitQuery}
                onChange={(e) => { setUnitQuery(e.target.value); if (selectedUnit) setSelectedUnit(null); }}
                placeholder="Escribe nombre o código de unidad (ej. Pieza, E48)..."
                className="civika-input w-full pl-12"
              />
              {loadingUnit && <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 text-blue-500 animate-spin" size={18} />}
            </div>

            {unitQuery.length >= 1 && !selectedUnit && units.length > 0 && (
              <ul className="absolute top-[82px] left-0 w-full bg-slate-900 border border-white/10 rounded-[10px] overflow-hidden shadow-2xl z-50 max-h-48 overflow-y-auto">
                {units.map(u => (
                  <li
                    key={u.code}
                    onClick={() => { setSelectedUnit(u); setUnitQuery(u.name); }}
                    className="px-4 py-3 hover:bg-[#1a3a5c]/30 cursor-pointer border-b border-white/5 flex items-center justify-between text-xs"
                  >
                    <span className="text-white font-medium truncate w-[75%]">{u.name}</span>
                    <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">{u.code}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {selectedUnit && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-5 rounded-[10px] bg-blue-500/5 border border-blue-500/10 space-y-2">
              <span className="text-[9px] font-bold text-blue-400 uppercase tracking-wider">Unidad de Medida Seleccionada</span>
              <p className="text-white text-sm font-bold">{selectedUnit.name}</p>
              <p className="text-xs text-slate-400 font-mono">Clave Unidad: <span className="text-emerald-400 font-bold">{selectedUnit.code}</span></p>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// -------------------------------------------------------------
// Componente C: CASFIM / Bancos (Merger Alerts y Filtros)
// -------------------------------------------------------------
function FinancialShowcase() {
  const [bancos, setBancos] = useState([]);
  const [tipos, setTipos] = useState([]);
  
  const [nombreFilter, setNombreFilter] = useState('');
  const [selectedTipoId, setSelectedTipoId] = useState('');
  const [soloActivas, setSoloActivas] = useState(true);

  const [loading, setLoading] = useState(false);
  const [selectedBanco, setSelectedBanco] = useState(null);

  // Cargar sectores (tipos de entidad)
  useEffect(() => {
    const fetchSectores = async () => {
      try {
        const res = await axios.get(`${API_BASE}/financial/tipos-entidad`);
        setTipos(Array.isArray(res.data) ? res.data : []);
      } catch (err) {
        console.error(err);
        setTipos([]);
      }
    };
    fetchSectores();
  }, []);

  // Cargar bancos al cambiar filtros
  useEffect(() => {
    const fetchBancos = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${API_BASE}/financial/instituciones`, {
          params: {
            nombre: nombreFilter,
            tipo_id: selectedTipoId,
            solo_activas: soloActivas
          }
        });
        setBancos(Array.isArray(res.data) ? res.data : []);
      } catch (err) {
        console.error(err);
        setBancos([]);
      } finally {
        setLoading(false);
      }
    };

    const delay = setTimeout(fetchBancos, 300);
    return () => clearTimeout(delay);
  }, [nombreFilter, selectedTipoId, soloActivas]);

  const handleSelectBanco = (banco) => {
    setSelectedBanco(banco);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="civika-card p-10 space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white mb-2 outfit flex items-center gap-2">
          <Landmark className="text-blue-400" size={20} />
          Catálogo CASFIM y Entidades Bancarias
        </h2>
        <p className="text-slate-400 text-sm">Selector bidireccional y filtro de estatus operativo histórico. Reporta alertas de fusión/absorción en tiempo real.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Filters and List */}
        <div className="lg:col-span-2 space-y-6">
          <div className="space-y-4 bg-slate-950/20 p-5 rounded-[14px] border border-white/5">
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest pl-1">Filtrar por Nombre o Clave</label>
              <input
                type="text"
                value={nombreFilter}
                onChange={(e) => setNombreFilter(e.target.value)}
                placeholder="Ej. Banamex, 002, SOFIPO..."
                className="civika-input w-full"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest pl-1">Filtrar por Sector</label>
              <select
                value={selectedTipoId}
                onChange={(e) => setSelectedTipoId(e.target.value)}
                className="civika-select w-full"
              >
                <option value="">Todos los Sectores...</option>
                {tipos.map(t => <option key={t.id} value={t.id}>{t.nombre}</option>)}
              </select>
            </div>

            {/* Toggle Status Switch */}
            <div className="flex items-center justify-between border-t border-white/5 pt-4">
              <span className="text-xs font-semibold text-slate-300">Mostrar Solo Activas</span>
              <button
                onClick={() => setSoloActivas(!soloActivas)}
                className={`relative inline-flex items-center rounded-full transition-colors duration-300 ${
                  soloActivas ? 'bg-blue-600' : 'bg-slate-800'
                }`}
                style={{ width: '48px', height: '24px' }}
              >
                <span
                  className={`inline-block w-4 h-4 transform rounded-full bg-white transition-transform duration-300 ${
                    soloActivas ? 'translate-x-7' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>

          {/* List panel */}
          <div className="border border-white/5 bg-slate-950/40 rounded-[14px] p-4 max-h-[300px] overflow-y-auto space-y-1.5">
            <div className="flex justify-between items-center mb-3 border-b border-white/5 pb-2 px-2">
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Instituciones ({bancos.length})</span>
              {loading && <Loader2 className="animate-spin text-blue-400" size={14} />}
            </div>
            
            {bancos.map(b => (
              <button
                key={b.id}
                onClick={() => handleSelectBanco(b)}
                className={`w-full flex items-center justify-between px-4 rounded-[8px] hover:bg-white/5 text-left transition-all ${
                  selectedBanco?.id === b.id ? 'bg-[#1a3a5c]/30 text-white' : 'text-slate-300'
                }`}
                style={{ height: '44px' }}
              >
                <div className="flex items-center gap-3 truncate">
                  <span className="font-mono font-bold text-slate-500 w-8">{b.clave}</span>
                  <span className="truncate text-sm font-semibold">{b.nombre}</span>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className={`text-[8px] font-black px-2 py-0.5 rounded uppercase tracking-wider ${
                    b.estatus === 'ACTIVA' 
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/10' 
                      : 'bg-red-500/10 text-red-400 border border-red-500/10'
                  }`}>
                    {b.estatus}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Selected Data details and alerts */}
        <div className="lg:col-span-2 flex flex-col justify-start">
          {selectedBanco ? (
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }} 
              animate={{ scale: 1, opacity: 1 }}
              className="p-8 rounded-[14px] bg-[#1a3a5c]/10 border border-blue-500/20 space-y-6"
            >
              <div>
                <span className="text-[9px] font-black bg-blue-500/20 text-blue-300 px-2.5 py-1 rounded-full uppercase tracking-widest">
                  Ficha de Identidad Bancaria SSoT
                </span>
                <h4 className="text-2xl font-black text-white outfit mt-3">{selectedBanco.nombre}</h4>
                <p className="text-xs font-bold text-[#93c5fd] mt-1">{selectedBanco.tipo_entidad || 'BANCA MÚLTIPLE'}</p>
              </div>

              {/* Status Alert for Merged / Inactive Banks */}
              {selectedBanco.estatus !== 'ACTIVA' && (
                <div className="p-4 rounded-[8px] bg-red-500/10 border border-red-500/20 flex gap-3 text-red-400 text-xs leading-relaxed">
                  <ShieldAlert size={20} className="flex-shrink-0" />
                  <div>
                    <span className="font-bold uppercase tracking-wider block mb-1">Entidad Fusionada o Absorbida</span>
                    Esta entidad financiera ya no opera de manera independiente.
                    {selectedBanco.sucesora_nombre && (
                      <div className="mt-2 font-black flex items-center gap-1.5 bg-red-500/20 px-2.5 py-1 rounded w-fit border border-red-500/30">
                        Sucesora Operativa: {selectedBanco.sucesora_nombre}
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 border-t border-white/5 pt-4 text-xs">
                <div>
                  <span className="text-[10px] text-slate-500 font-bold block uppercase">Clave Natural</span>
                  <span className="text-slate-200 font-semibold font-mono text-sm">{selectedBanco.clave}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 font-bold block uppercase">Nombre Corto</span>
                  <span className="text-slate-200 font-semibold">{selectedBanco.corto || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 font-bold block uppercase">Estatus Legal</span>
                  <span className={`inline-block font-semibold mt-1 ${
                    selectedBanco.estatus === 'ACTIVA' ? 'text-emerald-400' : 'text-red-400'
                  }`}>{selectedBanco.estatus}</span>
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="p-8 rounded-[14px] border border-dashed border-white/5 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
              <Landmark size={40} className="text-slate-600 mb-4 opacity-40 animate-pulse" />
              <h4 className="text-white font-bold mb-2">Detalle de Entidad Bancaria</h4>
              <p className="text-slate-500 text-sm max-w-xs">Selecciona un banco del listado para ver su ficha, sector y alertas de fusión histórica.</p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// -------------------------------------------------------------
// Componente D: Calendario / Festivos (Días de Descanso)
// -------------------------------------------------------------
function CalendarShowcase() {
  const [holidaysList, setHolidaysList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [year, setYear] = useState(new Date().getFullYear());

  useEffect(() => {
    const fetchHolidays = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${API_BASE}/catalogos/calendario/festivos`, { params: { year } });
        setHolidaysList(Array.isArray(res.data) ? res.data : []);
      } catch (err) {
        console.error(err);
        setHolidaysList([]);
      } finally {
        setLoading(false);
      }
    };
    fetchHolidays();
  }, [year]);

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="civika-card p-10 space-y-8">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-xl font-bold text-white mb-2 outfit flex items-center gap-2">
            <Calendar className="text-blue-400" size={20} />
            Calendario de Días Festivos Oficiales
          </h2>
          <p className="text-slate-400 text-sm">Días de descanso obligatorio y festivos oficiales en México regulados por la Ley Federal del Trabajo.</p>
        </div>
        
        <select 
          value={year} 
          onChange={(e) => setYear(Number(e.target.value))}
          className="civika-select font-mono font-bold"
          style={{ width: '120px' }}
        >
          <option value={2026}>2026</option>
          <option value={2025}>2025</option>
          <option value={2027}>2027</option>
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center gap-2 text-slate-400 py-12">
          <Loader2 size={24} className="animate-spin text-blue-500" />
          <span>Cargando calendario oficial...</span>
        </div>
      ) : holidaysList.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {holidaysList.map((h, idx) => (
            <div key={idx} className="p-6 rounded-[14px] bg-[#1a3a5c]/10 border border-blue-500/20 hover:border-blue-500/40 transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-center mb-4">
                  <span className="text-[9px] font-black bg-blue-500/20 text-blue-300 px-2.5 py-1 rounded-full uppercase tracking-widest">
                    OFICIAL LFT
                  </span>
                  <span className="text-xs font-mono font-bold text-slate-500">
                    MX
                  </span>
                </div>
                <h4 className="text-lg font-bold text-white outfit">{h.name}</h4>
              </div>
              
              <div className="mt-6 pt-4 border-t border-white/5 flex justify-between items-center">
                <div className="text-left">
                  <span className="text-slate-500 text-[10px] font-bold uppercase tracking-wider block">Fecha</span>
                  <span className="text-[#93c5fd] font-mono font-bold text-sm">
                    {new Date(h.date).toLocaleDateString('es-MX', { day: '2-digit', month: 'long', year: 'numeric', timeZone: 'UTC' })}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-12 rounded-[14px] border border-dashed border-white/5 flex flex-col items-center justify-center text-center">
          <Calendar size={40} className="text-slate-600 mb-4 opacity-40" />
          <h4 className="text-white font-bold mb-2">Sin Festivos Registrados</h4>
          <p className="text-slate-500 text-sm max-w-xs">No se encontraron días festivos oficiales para el año seleccionado.</p>
        </div>
      )}
    </motion.div>
  );
}
