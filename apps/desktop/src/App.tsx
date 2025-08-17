import './App.css';
import { useEffect, useState } from 'react';
import { getProject, getShots, getProxyUrl, getProxyStatus } from './lib/api';

type ShotItem = { id: string; video_path?: string };

export default function App() {
  const [name, setName] = useState('Animation Composer');
  const [shots, setShots] = useState<ShotItem[]>([]);
  const [activeShot, setActiveShot] = useState<string | undefined>(undefined);
  const [cacheBust, setCacheBust] = useState<number>(0);
  useEffect(() => {
    getProject().then((p) => setName(p.project?.name ?? 'Animation Composer')).catch(()=>{});
  }, []);
  useEffect(() => {
    getShots().then(setShots).catch(()=>{});
  }, []);
  return (
    <div style={{display:'grid',gridTemplateRows:'auto 1fr auto',height:'100vh'}}>
      <header style={{padding:8,borderBottom:'1px solid #222',display:'flex',gap:12}}>
        <strong>{name}</strong>
        <span style={{opacity:.7}}>Aspect:</span>
        <select defaultValue="16:9"><option>16:9</option><option>9:16</option><option>1:1</option></select>
        <span style={{marginLeft:'auto',opacity:.7}}>Proxy</span>
        <input type="checkbox" defaultChecked />
      </header>
      <main style={{display:'grid',gridTemplateColumns:'280px 1fr 320px'}}>
        <aside style={{borderRight:'1px solid #222',padding:8}}>
          <h4>Shots</h4>
          <ul>
            {shots.map((s) => (
              <li key={s.id}>
                <button onClick={() => setActiveShot(s.id)}>{s.id}</button>
              </li>
            ))}
          </ul>
        </aside>
        <section style={{padding:8}}>
          <div style={{border:'1px solid #222',height:'60%',display:'grid',placeItems:'center'}}>
            {activeShot ? (
              (shots.find(s=>s.id===activeShot)?.video_path)
                ? (
                  <video
                    key={`${activeShot}-${cacheBust}`}
                    src={`${getProxyUrl(activeShot)}?t=${cacheBust}`}
                    controls
                    style={{width:'100%',height:'100%',objectFit:'contain'}}
                    onCanPlay={() => { /* ready */ }}
                    onError={() => {
                      // if proxy missing or stale, bump cache bust next tick
                      setTimeout(() => setCacheBust(Date.now()), 100);
                    }}
                    autoPlay
                  />
                ) : <em>No source set for this shot</em>
            ) : <em>Select a shot</em>}
          </div>
          <div style={{marginTop:8,border:'1px solid #222',height:'35%',display:'grid',placeItems:'center'}}>
            <em>Timeline</em>
          </div>
        </section>
        <aside style={{borderLeft:'1px solid #222',padding:8}}>
          <h4>Inspector</h4>
          <p>Shot metadata & stage params (coming next)</p>
        </aside>
      </main>
      <footer style={{padding:8,borderTop:'1px solid #222'}}>
        <small>v0.1</small>
      </footer>
    </div>
  );
}


