import './App.css';

export default function App() {
  return (
    <div style={{display:'grid',gridTemplateRows:'auto 1fr auto',height:'100vh'}}>
      <header style={{padding:8,borderBottom:'1px solid #222',display:'flex',gap:12}}>
        <strong>Animation Composer</strong>
        <span style={{opacity:.7}}>Aspect:</span>
        <select defaultValue="16:9"><option>16:9</option><option>9:16</option><option>1:1</option></select>
        <span style={{marginLeft:'auto',opacity:.7}}>Proxy</span>
        <input type="checkbox" defaultChecked />
      </header>
      <main style={{display:'grid',gridTemplateColumns:'280px 1fr 320px'}}>
        <aside style={{borderRight:'1px solid #222',padding:8}}>
          <h4>Project</h4>
          <ul>
            <li>Shots</li>
            <li>Models</li>
            <li>Palettes</li>
            <li>Audio</li>
          </ul>
        </aside>
        <section style={{padding:8}}>
          <div style={{border:'1px solid #222',height:'60%',display:'grid',placeItems:'center'}}>
            <em>Viewer</em>
          </div>
          <div style={{marginTop:8,border:'1px solid #222',height:'35%',display:'grid',placeItems:'center'}}>
            <em>Timeline</em>
          </div>
        </section>
        <aside style={{borderLeft:'1px solid #222',padding:8}}>
          <h4>Inspector</h4>
          <p>Shot metadata & stage params</p>
        </aside>
      </main>
      <footer style={{padding:8,borderTop:'1px solid #222'}}>
        <small>v0.1</small>
      </footer>
    </div>
  );
}


