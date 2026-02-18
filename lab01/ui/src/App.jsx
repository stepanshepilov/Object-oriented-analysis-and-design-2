import React, { useState, useEffect } from 'react';
import { Drill, Save, Plus, Sun, Moon, X, Map as MapIcon, Settings2, Copy, Target } from 'lucide-react';

const API_URL = 'http://localhost:5000/api/wells';

function App() {
  const [wells, setWells] = useState([]);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [theme, setTheme] = useState('dark');
  const [cloningSource, setCloningSource] = useState(null); // ID скважины для клонирования
  
  const [formData, setFormData] = useState({
    type: 'prod', x: '', y: '', z: '', pressure: '', fieldName: '',
    oilQuality: '', gasCut: '', injectionRate: '', fluidType: ''
  });

  const themes = {
    dark: {
      bg: '#1a0f0a', card: 'rgba(43, 29, 22, 0.95)', accent: '#ff8c00', text: '#f5e6d3',
      mapBg: '#241a14', isoLine: '#3d2b1f', grid: 'rgba(255, 140, 0, 0.05)', glass: 'blur(12px)'
    },
    light: {
      bg: '#dcd1b3', card: 'rgba(255, 255, 255, 0.9)', accent: '#2b5a8c', text: '#2c1e14',
      mapBg: '#e8dfc5', isoLine: '#b5a68d', grid: 'rgba(0, 0, 0, 0.05)', glass: 'blur(12px)'
    }
  };

  const current = themes[theme];

  useEffect(() => { fetchWells(); }, []);

  const fetchWells = async () => {
    try {
      const res = await fetch(API_URL);
      const data = await res.json();
      setWells(data);
    } catch (e) { console.error("API Error"); }
  };

  const handleMapClick = async (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.round(e.clientX - rect.left);
    const y = Math.round(e.clientY - rect.top);

    if (cloningSource) {
      // РЕЖИМ КЛОНИРОВАНИЯ: Отправляем ID донора и новые координаты
      const res = await fetch(`${API_URL}/${cloningSource}/clone`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ x, y })
      });
      if (res.ok) {
        setCloningSource(null);
        fetchWells();
      }
    } else {
      // ОБЫЧНЫЙ РЕЖИМ: Открываем форму создания
      setFormData({ type: 'prod', x, y, z: '', pressure: '', fieldName: '', oilQuality: '', gasCut: '', injectionRate: '', fluidType: '' });
      setIsFormOpen(true);
    }
  };

  const saveWell = async () => {
    const payload = { ...formData, x: +formData.x, y: +formData.y, z: +formData.z, pressure: +formData.pressure, 
                      oilQuality: +formData.oilQuality, gasCut: +formData.gasCut, injectionRate: +formData.injectionRate };
    await fetch(API_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    setIsFormOpen(false);
    fetchWells();
  };

  const startCloning = () => {
    setCloningSource(formData.id);
    setIsFormOpen(false);
  };

  return (
    <div style={{...styles.container, backgroundColor: current.bg, color: current.text}}>
      
      {/* HEADER */}
      <div style={{...styles.floatHeader, backgroundColor: current.card, backdropFilter: current.glass}}>
        <div style={{display:'flex', alignItems:'center', gap: '15px'}}>
          <MapIcon color={current.accent} size={24} />
          <h1 style={styles.title}>TOPOGRAPHIC <span style={{color: current.accent}}>PROTOTYPE</span></h1>
        </div>
        <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} style={{...styles.themeBtn, backgroundColor: current.accent}}>
          {theme === 'dark' ? <Sun size={18}/> : <Moon size={18}/>}
        </button>
      </div>

      <div style={styles.mapCenterer}>
        <div 
            style={{...styles.mapCanvas, backgroundColor: current.mapBg, cursor: cloningSource ? 'crosshair' : 'default'}} 
            onClick={handleMapClick}
        >
          {/* ТОПОГРАФИЧЕСКИЙ ГЕНЕРАТОР */}
          <svg width="100%" height="100%" style={styles.isolinesSvg}>
            <filter id="topoNoise">
              <feTurbulence type="fractalNoise" baseFrequency="0.007" numOctaves="4" seed="42" result="noise" />
              <feColorMatrix in="noise" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 40 -20" result="iso" />
            </filter>
            <defs>
              <pattern id="mapGrid" width="60" height="60" patternUnits="userSpaceOnUse">
                <path d="M 60 0 L 0 0 0 60" fill="none" stroke={current.grid} strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" filter="url(#topoNoise)" opacity="0.4" fill="none" stroke={current.isoLine} strokeWidth="1" />
            <rect width="100%" height="100%" fill="url(#mapGrid)" />
          </svg>

          {/* WELL MARKERS */}
          {wells.map(well => (
            <div key={well.id} style={{...styles.wellMarker, left: well.x, top: well.y}} onClick={(e) => { e.stopPropagation(); setFormData(well); setIsFormOpen(true); }}>
              <div style={{...styles.markerPoint, backgroundColor: well.type === 'prod' ? current.accent : '#555'}}>
                <Drill size={12} color="#fff" />
              </div>
              <div style={{...styles.markerLabel, backgroundColor: current.card, color: current.text}}>
                {well.fieldName || 'Well'}
              </div>
            </div>
          ))}

          {/* HINTS */}
          <div style={{...styles.mapHint, color: current.accent}}>
            {cloningSource ? (
                <span style={{display:'flex', alignItems:'center', gap: '8px', color: '#fff', backgroundColor: current.accent, padding: '5px 15px', borderRadius: '10px'}}>
                    <Target size={16} /> РЕЖИМ КЛОНИРОВАНИЯ: ВЫБЕРИТЕ МЕСТО НА КАРТЕ
                    <X size={16} onClick={(e) => {e.stopPropagation(); setCloningSource(null)}} cursor="pointer" />
                </span>
            ) : "+ КЛИКНИТЕ ДЛЯ УСТАНОВКИ НОВОЙ СКВАЖИНЫ"}
          </div>
        </div>
      </div>

      {/* PARAMETERS PANEL */}
      {isFormOpen && (
        <div style={{...styles.sidePanel, backgroundColor: current.card, backdropFilter: current.glass}}>
          <div style={styles.panelHeader}>
            <div style={{display:'flex', alignItems:'center', gap: '10px'}}>
              <Settings2 size={20} color={current.accent} />
              <h2 style={{fontSize: '14px', margin:0, fontWeight: 900}}>ПАРАМЕТРЫ</h2>
            </div>
            <X onClick={() => setIsFormOpen(false)} cursor="pointer" size={18} />
          </div>

          <div style={styles.scrollArea}>
            <label style={styles.label}>ТИП СКВАЖИНЫ</label>
            <select style={{...styles.input, backgroundColor: current.input, color: current.text}} value={formData.type} onChange={e => setFormData({...formData, type: e.target.value})}>
              <option value="prod">Production (Добыча)</option>
              <option value="inj">Injection (Нагнетание)</option>
            </select>

            <label style={styles.label}>НАЗВАНИЕ</label>
            <input style={{...styles.input, backgroundColor: current.input, color: current.text}} value={formData.fieldName} onChange={e => setFormData({...formData, fieldName: e.target.value})} />

            <div style={styles.row}>
              <div style={{flex:1}}>
                <label style={styles.label}>X</label>
                <input style={{...styles.input, backgroundColor: current.input, color: current.text, opacity: 0.5}} value={formData.x} readOnly />
              </div>
              <div style={{flex:1}}>
                <label style={styles.label}>Y</label>
                <input style={{...styles.input, backgroundColor: current.input, color: current.text, opacity: 0.5}} value={formData.y} readOnly />
              </div>
            </div>

            <label style={styles.label}>ГЛУБИНА (Z)</label>
            <input style={{...styles.input, backgroundColor: current.input, color: current.text}} type="number" value={formData.z} onChange={e => setFormData({...formData, z: e.target.value})} />

            {formData.type === 'prod' ? (
              <div style={styles.typeSection}>
                <label style={styles.label}>КАЧЕСТВО НЕФТИ (API)</label>
                <input style={{...styles.input, backgroundColor: current.input, color: current.text}} type="number" value={formData.oilQuality} onChange={e => setFormData({...formData, oilQuality: e.target.value})} />
                <label style={styles.label}>ГАЗОСОДЕРЖАНИЕ (%)</label>
                <input style={{...styles.input, backgroundColor: current.input, color: current.text}} type="number" value={formData.gasCut} onChange={e => setFormData({...formData, gasCut: e.target.value})} />
              </div>
            ) : (
              <div style={styles.typeSection}>
                <label style={styles.label}>ПРИЕМИСТОСТЬ</label>
                <input style={{...styles.input, backgroundColor: current.input, color: current.text}} type="number" value={formData.injectionRate} onChange={e => setFormData({...formData, injectionRate: e.target.value})} />
                <label style={styles.label}>ТИП АГЕНТА</label>
                <input style={{...styles.input, backgroundColor: current.input, color: current.text}} value={formData.fluidType} onChange={e => setFormData({...formData, fluidType: e.target.value})} />
              </div>
            )}

            <button style={{...styles.saveBtn, backgroundColor: current.accent}} onClick={saveWell}>
              <Save size={18} /> СОХРАНИТЬ ДАННЫЕ
            </button>

            {formData.id && (
                <button 
                  style={{...styles.saveBtn, backgroundColor: 'transparent', border: `2px solid ${current.accent}`, color: current.accent, marginTop: '10px'}} 
                  onClick={startCloning}
                >
                  <Copy size={18} /> КЛОНИРОВАТЬ (ПРОТОТИП)
                </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { height: '100vh', width: '100vw', overflow: 'hidden', display: 'flex', flexDirection: 'column', fontFamily: '"Courier New", Courier, monospace', transition: 'all 0.4s' },
  floatHeader: { position: 'fixed', top: '20px', left: '50%', transform: 'translateX(-50%)', zIndex: 100, padding: '10px 25px', borderRadius: '15px', display: 'flex', alignItems: 'center', gap: '30px', boxShadow: '0 8px 32px rgba(0,0,0,0.3)' },
  title: { margin: 0, fontSize: '14px', letterSpacing: '3px', fontWeight: '400' },
  themeBtn: { border: 'none', width: '36px', height: '36px', borderRadius: '10px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' },
  mapCenterer: { flex: 1, padding: '15px', display: 'flex' },
  mapCanvas: { flex: 1, borderRadius: '25px', position: 'relative', overflow: 'hidden', border: '1px solid rgba(0,0,0,0.1)' },
  isolinesSvg: { 
    position: 'absolute', 
    top: 0, 
    left: 0, 
    width: '100%', 
    height: '100%',
    pointerEvents: 'none' // ДОБАВЬ ЭТУ СТРОКУ, чтобы клики проходили сквозь SVG
},
  wellMarker: { position: 'absolute', display: 'flex', flexDirection: 'column', alignItems: 'center', transform: 'translate(-50%, -100%)', cursor: 'pointer', zIndex: 5 },
  markerPoint: { width: '24px', height: '24px', borderRadius: '6px 6px 6px 0', transform: 'rotate(-45deg)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 10px rgba(0,0,0,0.3)' },
  markerLabel: { transform: 'rotate(0deg)', fontSize: '9px', padding: '2px 8px', borderRadius: '4px', fontWeight: 'bold', marginTop: '10px', textTransform: 'uppercase' },
  mapHint: { position: 'absolute', bottom: '20px', left: '50%', transform: 'translateX(-50%)', fontSize: '10px', fontWeight: 'bold', letterSpacing: '2px', opacity: 0.8 },
  sidePanel: { position: 'fixed', right: '30px', top: '90px', width: '300px', borderRadius: '20px', padding: '25px', display: 'flex', flexDirection: 'column', zIndex: 100, boxShadow: '0 10px 40px rgba(0,0,0,0.4)' },
  panelHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' },
  scrollArea: { display: 'flex', flexDirection: 'column', gap: '12px' },
  label: { fontSize: '9px', fontWeight: '800', opacity: 0.5, letterSpacing: '1px' },
  input: { border: 'none', padding: '10px 12px', borderRadius: '8px', fontSize: '13px', outline: 'none' },
  row: { display: 'flex', gap: '10px' },
  typeSection: { display: 'flex', flexDirection: 'column', gap: '10px', padding: '5px 0' },
  saveBtn: { border: 'none', color: '#fff', padding: '14px', borderRadius: '10px', fontWeight: '800', fontSize: '11px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }
};

export default App;