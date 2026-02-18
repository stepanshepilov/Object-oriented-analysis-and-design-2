import React, { useState, useEffect } from 'react';
import { Drill, Save, PlusCircle, X } from 'lucide-react';

const API_URL = 'http://localhost:5000/api/wells';

function App() {
  const [wells, setWells] = useState([]);
  const [selectedWell, setSelectedWell] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);

  const emptyWell = {
    x: 0, y: 0, z: 0,
    pressure: 0, temperature: 0,
    rockType: 'Sandstone', isActive: true,
    fieldName: '', flowRate: 0
  };

  const [formData, setFormData] = useState(emptyWell);

  useEffect(() => { fetchWells(); }, []);

  const fetchWells = async () => {
    const res = await fetch(API_URL);
    const data = await res.json();
    setWells(data);
  };

  const handleMapClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.round(e.clientX - rect.left);
    const y = Math.round(e.clientY - rect.top);
    
    setFormData({ ...emptyWell, x, y });
    setSelectedWell(null);
    setIsFormOpen(true);
  };

  const saveWell = async () => {
    const method = selectedWell ? 'PUT' : 'POST';
    const url = selectedWell ? `${API_URL}/${selectedWell.id}` : API_URL;

    await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });

    setIsFormOpen(false);
    fetchWells();
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1>Geology Map Pro <sup>v10.0</sup></h1>
        <p>Manual Entry Mode (No Prototype Pattern)</p>
      </header>

      <div style={styles.main}>
        <div style={styles.mapContainer} onClick={handleMapClick}>
          <div style={styles.grid}></div>
          {wells.map(well => (
            <div 
              key={well.id}
              onClick={(e) => {
                e.stopPropagation();
                setSelectedWell(well);
                setFormData(well);
                setIsFormOpen(true);
              }}
              style={{...styles.wellMarker, left: well.x, top: well.y}}
            >
              <Drill size={20} color={well.isActive ? "#00ffcc" : "#ff4444"} />
              <span style={styles.wellLabel}>{well.fieldName || 'Well'}</span>
            </div>
          ))}
          <div style={styles.hint}>Click anywhere to place a new well</div>
        </div>

        {isFormOpen && (
          <div style={styles.sidebar}>
            <div style={styles.sidebarHeader}>
              <h3>{selectedWell ? 'Edit Well' : 'New Well'}</h3>
              <X onClick={() => setIsFormOpen(false)} cursor="pointer" />
            </div>
            
            <div style={styles.form}>
              <label>Field Name</label>
              <input value={formData.fieldName} onChange={e => setFormData({...formData, fieldName: e.target.value})} />
              
              <div style={styles.row}>
                <div><label>X</label><input type="number" value={formData.x} onChange={e => setFormData({...formData, x: +e.target.value})} /></div>
                <div><label>Y</label><input type="number" value={formData.y} onChange={e => setFormData({...formData, y: +e.target.value})} /></div>
              </div>

              <label>Depth (Z)</label>
              <input type="number" value={formData.z} onChange={e => setFormData({...formData, z: +e.target.value})} />

              <label>Pressure (bar)</label>
              <input type="number" value={formData.pressure} onChange={e => setFormData({...formData, pressure: +e.target.value})} />

              <label>Temperature (°C)</label>
              <input type="number" value={formData.temperature} onChange={e => setFormData({...formData, temperature: +e.target.value})} />

              <label>Rock Type</label>
              <select value={formData.rockType} onChange={e => setFormData({...formData, rockType: e.target.value})}>
                <option>Sandstone</option>
                <option>Basalt</option>
                <option>Limestone</option>
              </select>

              <label>Flow Rate (m³/d)</label>
              <input type="number" value={formData.flowRate} onChange={e => setFormData({...formData, flowRate: +e.target.value})} />

              <button style={styles.saveBtn} onClick={saveWell}>
                <Save size={16} /> Save Well Data
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: { height: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#1a1a1a', color: '#eee', fontFamily: 'sans-serif' },
  header: { padding: '1rem 2rem', background: '#252525', borderBottom: '1px solid #333' },
  main: { flex: 1, display: 'flex', position: 'relative', overflow: 'hidden' },
  mapContainer: { flex: 1, position: 'relative', backgroundColor: '#0f0f0f', cursor: 'crosshair', overflow: 'hidden' },
  grid: { position: 'absolute', width: '2000px', height: '2000px', backgroundImage: 'linear-gradient(#222 1px, transparent 1px), linear-gradient(90deg, #222 1px, transparent 1px)', backgroundSize: '40px 40px' },
  wellMarker: { position: 'absolute', transform: 'translate(-50%, -50%)', display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer', transition: 'all 0.2s' },
  wellLabel: { fontSize: '10px', marginTop: '4px', color: '#888' },
  sidebar: { width: '350px', backgroundColor: '#252525', borderLeft: '1px solid #333', padding: '1.5rem', overflowY: 'auto' },
  sidebarHeader: { display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' },
  form: { display: 'flex', flexDirection: 'column', gap: '10px' },
  row: { display: 'flex', gap: '10px' },
  saveBtn: { marginTop: '1rem', padding: '12px', backgroundColor: '#0066ff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' },
  hint: { position: 'absolute', bottom: '20px', left: '20px', color: '#555', pointerEvents: 'none' }
};

export default App;