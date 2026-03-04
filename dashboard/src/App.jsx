import { useState, useEffect, useCallback } from "react";

const API = "http://localhost:8000";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0a0b0f; --surface: #111318; --surface2: #181c23; --border: #1f2430;
    --accent: #00e5a0; --accent2: #7b61ff; --accent3: #ff6b35;
    --text: #e8eaf0; --muted: #5a6175; --danger: #ff4757; --warn: #ffa502;
  }

  html, body, #root { width: 100%; min-height: 100vh; margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: 'Syne', sans-serif; }

  .app { display: grid; grid-template-columns: 200px 1fr; grid-template-rows: 56px 1fr; min-height: 100vh; width: 100%; }

  .topbar { grid-column: 1/-1; background: var(--surface); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 28px; position: sticky; top: 0; z-index: 100; }
  .logo { font-size: 18px; font-weight: 800; letter-spacing: -0.5px; }
  .logo em { color: var(--accent); font-style: normal; }
  .topbar-right { display: flex; align-items: center; gap: 14px; }
  .status-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 6px var(--accent); animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1}50%{opacity:0.35} }
  .status-label { font-size: 11px; color: var(--muted); font-family: 'JetBrains Mono', monospace; }
  .refresh-btn { background: var(--accent); color: #000; font-family: 'Syne', sans-serif; font-weight: 700; font-size: 12px; border: none; padding: 7px 16px; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
  .refresh-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(0,229,160,0.3); }

  .sidebar { background: var(--surface); border-right: 1px solid var(--border); padding: 20px 0; position: sticky; top: 56px; height: calc(100vh - 56px); overflow-y: auto; }
  .nav-section { padding: 0 14px; margin-bottom: 6px; }
  .nav-label { font-size: 9px; letter-spacing: 1.8px; color: var(--muted); font-family: 'JetBrains Mono', monospace; padding: 0 8px 8px; text-transform: uppercase; }
  .nav-item { display: flex; align-items: center; gap: 9px; padding: 8px 10px; border-radius: 7px; cursor: pointer; font-size: 13px; font-weight: 600; color: var(--muted); transition: all 0.15s; margin-bottom: 2px; border: 1px solid transparent; }
  .nav-item:hover { color: var(--text); background: var(--surface2); }
  .nav-item.active { color: var(--accent); background: rgba(0,229,160,0.07); border-color: rgba(0,229,160,0.15); }
  .nav-icon { font-size: 14px; width: 18px; text-align: center; flex-shrink: 0; }
  .nav-badge { margin-left: auto; background: var(--accent); color: #000; font-size: 9px; font-weight: 700; padding: 2px 6px; border-radius: 10px; font-family: 'JetBrains Mono', monospace; }
  .nav-badge.warn { background: var(--warn); }
  .nav-divider { height: 1px; background: var(--border); margin: 10px 20px; }
  .nav-meta { padding: 6px 18px; font-size: 11px; color: var(--muted); font-family: 'JetBrains Mono', monospace; line-height: 2; }

  .main { padding: 28px 32px; overflow-y: auto; width: 100%; min-width: 0; }

  .page-header { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
  .page-title { font-size: 24px; font-weight: 800; letter-spacing: -0.5px; }
  .page-title span { color: var(--accent); }
  .page-sub { font-size: 12px; color: var(--muted); margin-top: 3px; font-family: 'JetBrains Mono', monospace; }

  .filters-bar { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .filter-label { font-size: 11px; color: var(--muted); font-family: 'JetBrains Mono', monospace; }
  .filter-select { background: var(--surface2); border: 1px solid var(--border); color: var(--text); font-family: 'JetBrains Mono', monospace; font-size: 11px; padding: 5px 10px; border-radius: 6px; cursor: pointer; transition: border-color 0.15s; }
  .filter-select:focus { outline: none; border-color: var(--accent2); }
  .filter-divider { width: 1px; height: 20px; background: var(--border); }

  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px; width: 100%; }
  .card-title { font-size: 10px; letter-spacing: 1.4px; text-transform: uppercase; color: var(--muted); font-family: 'JetBrains Mono', monospace; margin-bottom: 14px; }

  .stats-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 20px; width: 100%; }
  .stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px 20px; position: relative; overflow: hidden; transition: border-color 0.2s, transform 0.2s; }
  .stat-card:hover { border-color: var(--accent2); transform: translateY(-1px); }
  .stat-card::before { content:''; position: absolute; top:0; left:0; right:0; height:2px; background: var(--grad); }
  .stat-label { font-size: 10px; letter-spacing: 1px; color: var(--muted); text-transform: uppercase; font-family: 'JetBrains Mono', monospace; }
  .stat-value { font-size: 34px; font-weight: 800; margin: 6px 0 2px; letter-spacing: -1px; }
  .stat-icon { position: absolute; right: 16px; top: 16px; font-size: 26px; opacity: 0.08; }

  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; width: 100%; }
  .col-wide-narrow { display: grid; grid-template-columns: 3fr 2fr; gap: 16px; margin-bottom: 16px; width: 100%; }

  .funnel { display: flex; flex-direction: column; gap: 9px; }
  .funnel-row { display: flex; align-items: center; gap: 12px; }
  .funnel-label { font-size: 11px; color: var(--muted); width: 110px; flex-shrink: 0; font-family: 'JetBrains Mono', monospace; }
  .funnel-bar-wrap { flex:1; height:26px; background: var(--surface2); border-radius:6px; overflow:hidden; min-width:0; }
  .funnel-bar { height:100%; border-radius:6px; display:flex; align-items:center; padding-left:10px; font-size:11px; font-weight:700; font-family:'JetBrains Mono',monospace; transition: width 0.8s ease; white-space:nowrap; }
  .funnel-count { font-size:12px; font-weight:700; width:32px; text-align:right; flex-shrink:0; }

  .table-wrap { overflow-x: auto; width: 100%; }
  table { width: 100%; border-collapse: collapse; }
  th { font-size: 9px; letter-spacing: 1.4px; text-transform: uppercase; color: var(--muted); font-family: 'JetBrains Mono', monospace; padding: 8px 12px; text-align: left; border-bottom: 1px solid var(--border); white-space: nowrap; }
  td { padding: 10px 12px; font-size: 13px; border-bottom: 1px solid rgba(31,36,48,0.5); vertical-align: middle; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(255,255,255,0.018); }

  .badge { display: inline-flex; align-items: center; padding: 3px 8px; border-radius: 20px; font-size: 10px; font-weight: 600; font-family: 'JetBrains Mono', monospace; white-space: nowrap; }
  .badge-green  { background: rgba(0,229,160,0.1);  color: var(--accent);  border: 1px solid rgba(0,229,160,0.2); }
  .badge-yellow { background: rgba(255,165,2,0.1);  color: var(--warn);    border: 1px solid rgba(255,165,2,0.2); }
  .badge-red    { background: rgba(255,71,87,0.1);  color: var(--danger);  border: 1px solid rgba(255,71,87,0.2); }
  .badge-purple { background: rgba(123,97,255,0.1); color: var(--accent2); border: 1px solid rgba(123,97,255,0.2); }
  .badge-gray   { background: rgba(90,97,117,0.15); color: var(--muted);   border: 1px solid var(--border); }

  .score-bar { display: flex; align-items: center; gap: 8px; min-width: 120px; }
  .score-track { flex:1; height:4px; background: var(--border); border-radius:2px; overflow:hidden; }
  .score-fill  { height:100%; border-radius:2px; transition: width 0.5s ease; }
  .score-num   { font-size:11px; font-family:'JetBrains Mono',monospace; font-weight:600; min-width:34px; text-align:right; }

  .source-pill { display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-family: 'JetBrains Mono', monospace; font-weight: 600; }
  .pill-LinkedIn { background: rgba(0,119,181,0.15); color: #3a9fd6; }
  .pill-Naukri   { background: rgba(255,106,0,0.15); color: #ff8c42; }
  .pill-Indeed   { background: rgba(43,55,232,0.15); color: #6b76f5; }

  .status-select { background: var(--surface2); border: 1px solid var(--border); color: var(--text); font-family: 'JetBrains Mono', monospace; font-size: 10px; padding: 4px 7px; border-radius: 6px; cursor: pointer; }

  .unscored-header { display: flex; align-items: center; gap: 10px; padding: 14px 20px; cursor: pointer; border-top: 1px solid var(--border); }
  .unscored-header:hover { background: var(--surface2); }
  .chevron { font-size: 10px; color: var(--muted); transition: transform 0.2s; margin-left: auto; }
  .chevron.open { transform: rotate(90deg); }

  .top-job-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border); }
  .top-job-row:last-child { border-bottom: none; }
  .top-job-name { font-size: 13px; font-weight: 700; }
  .top-job-co   { font-size: 11px; color: var(--muted); margin-top: 2px; }

  .outreach-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px 20px; margin-bottom: 10px; width: 100%; }
  .outreach-actions { display: flex; gap: 7px; flex-wrap: wrap; margin-top: 12px; }
  .action-btn { background: var(--surface2); border: 1px solid var(--border); color: var(--muted); border-radius: 6px; padding: 5px 11px; font-size: 10px; font-family: 'JetBrains Mono', monospace; font-weight: 600; cursor: pointer; transition: all 0.15s; }
  .action-btn:hover { border-color: var(--accent); color: var(--accent); }
  .action-btn.active { background: var(--accent); border-color: var(--accent); color: #000; }
  .action-btn.open-link { color: var(--accent2); border-color: rgba(123,97,255,0.3); margin-left: auto; }
  .action-btn.open-link:hover { background: rgba(123,97,255,0.1); }

  .modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.7); z-index:200; display:flex; align-items:center; justify-content:center; padding:24px; }
  .modal { background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:28px; max-width:540px; width:100%; max-height:80vh; overflow-y:auto; position:relative; }
  .modal-title { font-size:18px; font-weight:800; margin-bottom:6px; }
  .modal-title span { color:var(--accent); }
  .modal-sub { font-size:12px; color:var(--muted); font-family:'JetBrains Mono',monospace; margin-bottom:20px; }
  .modal-close { position:absolute; top:16px; right:16px; background:var(--surface2); border:1px solid var(--border); color:var(--muted); width:28px; height:28px; border-radius:6px; cursor:pointer; font-size:14px; display:flex; align-items:center; justify-content:center; }
  .modal-close:hover { color:var(--text); border-color:var(--accent); }
  .modal-step { display:flex; gap:12px; margin-bottom:16px; }
  .modal-step-num { width:24px; height:24px; border-radius:6px; background:rgba(0,229,160,0.1); border:1px solid rgba(0,229,160,0.2); color:var(--accent); font-size:11px; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:2px; }
  .modal-step-content { flex:1; }
  .modal-step-title { font-size:13px; font-weight:700; margin-bottom:3px; }
  .modal-step-desc { font-size:12px; color:var(--muted); line-height:1.7; }
  .modal-code { background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:10px 14px; font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--accent2); margin:10px 0; line-height:1.8; }
  .modal-divider { height:1px; background:var(--border); margin:16px 0; }
  .info-btn { width:100%; display:flex; align-items:center; gap:8px; padding:8px 10px; border-radius:7px; cursor:pointer; font-size:12px; font-weight:600; color:var(--muted); transition:all 0.15s; background:none; border:1px solid transparent; font-family:'Syne',sans-serif; }
  .info-btn:hover { color:var(--text); background:var(--surface2); border-color:var(--border); }

  .error-banner { background: rgba(255,71,87,0.08); border: 1px solid rgba(255,71,87,0.25); border-radius: 8px; padding: 12px 16px; color: var(--danger); font-family: 'JetBrains Mono', monospace; font-size: 11px; margin-bottom: 20px; line-height: 1.8; }
  .loading { display: flex; align-items: center; gap: 10px; color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 12px; padding: 60px; justify-content: center; }
  .spinner { width: 15px; height: 15px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .empty-state { text-align: center; padding: 60px; color: var(--muted); font-size: 13px; font-family: 'JetBrains Mono', monospace; }

  @media (max-width: 1100px) { .stats-grid { grid-template-columns: repeat(2,1fr); } }
  @media (max-width: 800px)  { .two-col, .col-wide-narrow { grid-template-columns: 1fr; } .app { grid-template-columns: 1fr; } .sidebar { display: none; } }
`;

const STATUSES = ["New","Outreach Sent","Replied","Interview","Rejected","Skipped"];

function useFetch(url) {
  const [data, setData]    = useState(null);
  const [loading, setLoad] = useState(true);
  const [error, setError]  = useState(null);
  const load = useCallback(async () => {
    try {
      setLoad(true); setError(null);
      const r = await fetch(url);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setData(await r.json());
    } catch(e) { setError(e.message); }
    finally    { setLoad(false); }
  }, [url]);
  useEffect(() => { load(); }, [load]);
  return { data, loading, error, refetch: load };
}

async function patchStatus(hash_id, status) {
  await fetch(`${API}/api/jobs/${hash_id}/status`, {
    method: "PATCH", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
}

function scoreColor(s) {
  return s >= 80 ? "#00e5a0" : s >= 75 ? "#ffa502" : s >= 65 ? "#7b61ff" : "#5a6175";
}

function ScoreBar({ score }) {
  const c = scoreColor(score);
  return (
    <div className="score-bar">
      <div className="score-track">
        <div className="score-fill" style={{ width: `${Math.max(score,0)}%`, background: c }} />
      </div>
      <span className="score-num" style={{ color: c }}>{score > 0 ? score + "%" : "—"}</span>
    </div>
  );
}

function StatusBadge({ status }) {
  const map = { "Outreach Sent":"badge-purple","Replied":"badge-green","Interview":"badge-green","New":"badge-gray","Rejected":"badge-red","Skipped":"badge-gray" };
  return <span className={`badge ${map[status]||"badge-gray"}`}>{status||"New"}</span>;
}

function SourcePill({ source }) {
  return <span className={`source-pill pill-${source}`}>{source}</span>;
}

function postedDaysAgo(text) {
  if (!text) return null;
  const t = text.toLowerCase();
  if (t.includes("hour") || t.includes("today") || t.includes("just")) return 0;
  const m = t.match(/(\d+)\s*day/);
  return m ? parseInt(m[1]) : null;
}

function applyFilters(jobs, { minScore, source, posted, location }) {
  return (jobs || []).filter(j => {
    if (minScore > 0 && j.match_score < minScore) return false;
    if (source !== "All" && j.source !== source) return false;
    if (location !== "All" && !j.location?.toLowerCase().includes(location.toLowerCase())) return false;
    if (posted !== "All") {
      const days = postedDaysAgo(j.posted_text);
      if (posted === "Today"    && (days === null || days >= 1)) return false;
      if (posted === "3 Days"   && (days === null || days > 3))  return false;
    }
    return true;
  });
}

function Funnel({ stats }) {
  if (!stats) return null;
  const total = Math.max(stats.total_scraped, 1);
  const stages = [
    { label:"Scraped",    count: stats.total_scraped, color:"#7b61ff" },
    { label:"High Match", count: stats.high_match,    color:"#00b8ff" },
    { label:"Sent",       count: stats.outreach_sent, color:"#00e5a0" },
    { label:"Replied",    count: stats.replies,        color:"#ffa502" },
  ];
  return (
    <div className="funnel">
      {stages.map(s => (
        <div className="funnel-row" key={s.label}>
          <div className="funnel-label">{s.label}</div>
          <div className="funnel-bar-wrap">
            <div className="funnel-bar" style={{ width:`${Math.max((s.count/total)*100, s.count>0?3:0)}%`, background:s.color+"18", color:s.color, border:`1px solid ${s.color}30` }}>
              {s.count > 0 ? s.count : ""}
            </div>
          </div>
          <div className="funnel-count" style={{ color: s.color }}>{s.count}</div>
        </div>
      ))}
    </div>
  );
}

function JobRow({ job: j, onStatusChange }) {
  const [status, setStatus] = useState(j.status || "New");
  const handle = async (e) => {
    const s = e.target.value; setStatus(s);
    await patchStatus(j.hash_id, s); onStatusChange();
  };
  return (
    <tr>
      <td style={{ fontWeight:600, maxWidth:220 }}>
        <a href={j.url} target="_blank" rel="noreferrer" style={{ color:"var(--text)", textDecoration:"none" }} title={j.title}>
          {j.title.length > 38 ? j.title.slice(0,38)+"…" : j.title}
        </a>
      </td>
      <td style={{ color:"#a0a8bc", maxWidth:160 }}>{j.company}</td>
      <td><SourcePill source={j.source} /></td>
      <td style={{ minWidth:130 }}><ScoreBar score={j.match_score} /></td>
      <td style={{ color:"var(--muted)", fontFamily:"JetBrains Mono", fontSize:10, whiteSpace:"nowrap" }}>{j.posted_text||"—"}</td>
      <td>
        <select className="status-select" value={status} onChange={handle}>
          {STATUSES.map(s => <option key={s}>{s}</option>)}
        </select>
      </td>
      <td>
        <a href={j.url} target="_blank" rel="noreferrer">
          <button className="action-btn open-link">↗</button>
        </a>
      </td>
    </tr>
  );
}

function UnscoredSection({ jobs, onStatusChange }) {
  const [open, setOpen] = useState(false);
  if (!jobs.length) return null;
  return (
    <div style={{ marginTop:16, background:"var(--surface)", border:"1px solid var(--border)", borderRadius:12, overflow:"hidden" }}>
      <div className="unscored-header" onClick={() => setOpen(o => !o)}>
        <span style={{ fontSize:13, fontWeight:700, color:"var(--muted)" }}>Unscored Jobs</span>
        <span className="badge badge-gray">{jobs.length}</span>
        <span style={{ fontSize:11, color:"var(--muted)", fontFamily:"JetBrains Mono" }}>No description available - cannot score</span>
        <span className={`chevron ${open?"open":""}`}>▶</span>
      </div>
      {open && (
        <div className="table-wrap" style={{ padding:"0 0 8px" }}>
          <table>
            <thead><tr><th>Role</th><th>Company</th><th>Source</th><th>Posted</th><th>Status</th><th></th></tr></thead>
            <tbody>
              {jobs.map(j => (
                <tr key={j.hash_id}>
                  <td style={{fontWeight:600}}><a href={j.url} target="_blank" rel="noreferrer" style={{color:"var(--muted)",textDecoration:"none"}}>{j.title}</a></td>
                  <td style={{color:"var(--muted)",fontSize:12}}>{j.company}</td>
                  <td><SourcePill source={j.source} /></td>
                  <td style={{color:"var(--muted)",fontFamily:"JetBrains Mono",fontSize:10}}>{j.posted_text||"—"}</td>
                  <td><StatusBadge status={j.status}/></td>
                  <td><a href={j.url} target="_blank" rel="noreferrer"><button className="action-btn open-link">↗</button></a></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function SkippedSection({ jobs, onStatusChange }) {
  const [open, setOpen] = useState(false);
  if (!jobs.length) return null;
  return (
    <div style={{ marginTop:8, background:"var(--surface)", border:"1px solid var(--border)", borderRadius:12, overflow:"hidden" }}>
      <div className="unscored-header" onClick={() => setOpen(o => !o)}>
        <span style={{ fontSize:13, fontWeight:700, color:"var(--muted)" }}>Skipped Jobs</span>
        <span className="badge badge-gray">{jobs.length}</span>
        <span style={{ fontSize:11, color:"var(--muted)", fontFamily:"JetBrains Mono" }}>Marked as not relevant</span>
        <span className={`chevron ${open?"open":""}`}>▶</span>
      </div>
      {open && (
        <div className="table-wrap" style={{ padding:"0 0 8px" }}>
          <table>
            <thead>
              <tr><th>Role</th><th>Company</th><th>Source</th><th>Match</th><th>Posted</th><th>Status</th><th></th></tr>
            </thead>
            <tbody>
              {jobs.map(j => (
                <SkippedRow key={j.hash_id} job={j} onStatusChange={onStatusChange}/>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function SkippedRow({ job: j, onStatusChange }) {
  const [status, setStatus] = useState(j.status || "Skipped");
  const handle = async (e) => {
    const s = e.target.value;
    setStatus(s);
    await patchStatus(j.hash_id, s);
    onStatusChange();
  };
  return (
    <tr>
      <td style={{ fontWeight:600, maxWidth:220 }}>
        <a href={j.url} target="_blank" rel="noreferrer"
           style={{ color:"var(--muted)", textDecoration:"none" }} title={j.title}>
          {j.title.length > 38 ? j.title.slice(0,38)+"…" : j.title}
        </a>
      </td>
      <td style={{ color:"var(--muted)", fontSize:12 }}>{j.company}</td>
      <td><SourcePill source={j.source}/></td>
      <td style={{ minWidth:130 }}><ScoreBar score={j.match_score}/></td>
      <td style={{ color:"var(--muted)", fontFamily:"JetBrains Mono", fontSize:10, whiteSpace:"nowrap" }}>
        {j.posted_text||"—"}
      </td>
      <td>
        <select className="status-select" value={status} onChange={handle}>
          {STATUSES.map(s => <option key={s}>{s}</option>)}
        </select>
      </td>
      <td>
        <a href={j.url} target="_blank" rel="noreferrer">
          <button className="action-btn open-link">↗</button>
        </a>
      </td>
    </tr>
  );
}

function SettingsPanel({ onSave }) {
  const cfg = useFetch(`${API}/api/config`);
  const [form, setForm] = useState(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (cfg.data && !form) setForm(cfg.data);
  }, [cfg.data]);

  const handleSave = async () => {
    await fetch(`${API}/api/config`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
    onSave();
  };

  const updateList = (key, idx, value) => {
    const list = [...form[key]];
    list[idx] = value;
    setForm({ ...form, [key]: list });
  };

  const addItem = (key) =>
    setForm({ ...form, [key]: [...form[key], ""] });

  const removeItem = (key, idx) =>
    setForm({ ...form, [key]: form[key].filter((_, i) => i !== idx) });

  if (!form) return <div className="loading"><div className="spinner"/>Loading config...</div>;

  return (
    <>
      <div className="page-header">
        <div>
          <div className="page-title">Pipeline <span>Settings</span></div>
          <div className="page-sub">Changes apply on the next scheduled run</div>
        </div>
        <button
          className="refresh-btn"
          onClick={handleSave}
          style={{ background: saved ? "var(--accent2)" : "var(--accent)" }}
        >
          {saved ? "✓ Saved" : "Save Changes"}
        </button>
      </div>

      <div className="two-col">
        {/* Keywords */}
        <div className="card">
          <div className="card-title">Search Keywords</div>
          {form.keywords.map((kw, i) => (
            <div key={i} style={{ display:"flex", gap:8, marginBottom:8 }}>
              <input
                value={kw}
                onChange={e => updateList("keywords", i, e.target.value)}
                style={{ flex:1, background:"var(--surface2)", border:"1px solid var(--border)",
                         color:"var(--text)", padding:"6px 10px", borderRadius:6,
                         fontFamily:"JetBrains Mono", fontSize:12 }}
              />
              <button
                onClick={() => removeItem("keywords", i)}
                className="action-btn"
                style={{ color:"var(--danger)", borderColor:"rgba(255,71,87,0.3)" }}
              >✕</button>
            </div>
          ))}
          <button className="action-btn" onClick={() => addItem("keywords")}
            style={{ color:"var(--accent)", borderColor:"rgba(0,229,160,0.3)", marginTop:4 }}>
            + Add Keyword
          </button>
        </div>

        {/* Locations */}
        <div className="card">
          <div className="card-title">Locations</div>
          {form.locations.map((loc, i) => (
            <div key={i} style={{ display:"flex", gap:8, marginBottom:8 }}>
              <input
                value={loc}
                onChange={e => updateList("locations", i, e.target.value)}
                style={{ flex:1, background:"var(--surface2)", border:"1px solid var(--border)",
                         color:"var(--text)", padding:"6px 10px", borderRadius:6,
                         fontFamily:"JetBrains Mono", fontSize:12 }}
              />
              <button
                onClick={() => removeItem("locations", i)}
                className="action-btn"
                style={{ color:"var(--danger)", borderColor:"rgba(255,71,87,0.3)" }}
              >✕</button>
            </div>
          ))}
          <button className="action-btn" onClick={() => addItem("locations")}
            style={{ color:"var(--accent)", borderColor:"rgba(0,229,160,0.3)", marginTop:4 }}>
            + Add Location
          </button>
        </div>
      </div>

      {/* Thresholds */}
      <div className="card" style={{ marginTop:0 }}>
        <div className="card-title">Match Thresholds</div>
        <div className="two-col" style={{ marginBottom:0 }}>
          <div>
            <div style={{ fontSize:12, color:"var(--muted)", marginBottom:8, fontFamily:"JetBrains Mono" }}>
              Dashboard Threshold — jobs shown in Job Feed and email digest
            </div>
            <div style={{ display:"flex", alignItems:"center", gap:12 }}>
              <input type="range" min={50} max={95} value={form.match_threshold}
                onChange={e => setForm({...form, match_threshold: Number(e.target.value)})}
                style={{ flex:1, accentColor:"var(--accent)" }}
              />
              <span style={{ fontSize:20, fontWeight:800, color:"var(--accent)",
                             fontFamily:"JetBrains Mono", minWidth:48 }}>
                {form.match_threshold}%
              </span>
            </div>
          </div>
          <div>
            <div style={{ fontSize:12, color:"var(--muted)", marginBottom:8, fontFamily:"JetBrains Mono" }}>
              Outreach Threshold — jobs shown in Outreach Queue, triggers Hunter API
            </div>
            <div style={{ display:"flex", alignItems:"center", gap:12 }}>
              <input type="range" min={50} max={95} value={form.outreach_threshold}
                onChange={e => setForm({...form, outreach_threshold: Number(e.target.value)})}
                style={{ flex:1, accentColor:"var(--accent2)" }}
              />
              <span style={{ fontSize:20, fontWeight:800, color:"var(--accent2)",
                             fontFamily:"JetBrains Mono", minWidth:48 }}>
                {form.outreach_threshold}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Info box */}
      <div style={{ marginTop:16, padding:"12px 16px", background:"rgba(123,97,255,0.06)",
                    border:"1px solid rgba(123,97,255,0.2)", borderRadius:8,
                    fontSize:11, color:"var(--muted)", fontFamily:"JetBrains Mono", lineHeight:1.8 }}>
        ⚙ Keyword and location changes affect the <strong style={{color:"var(--text)"}}>next pipeline run</strong> only —
        existing jobs in the database are not affected. To rescrape with new settings, delete
        <strong style={{color:"var(--accent)"}}> data/coie.db</strong> and
        <strong style={{color:"var(--accent)"}}> data/seen_hashes.json</strong> before the next run.
      </div>
    </>
  );
}

function OutreachCard({ job: j, onStatusChange }) {
  const [status, setStatus]   = useState(j.status || "New");
  const [showDraft, setShowDraft] = useState(false);
  const [loading, setLoading] = useState(false);
  const [draft, setDraft]     = useState({
    subject:  j.email_subject || "",
    body:     j.email_body    || "",
    recruiter: j.recruiter    || "",
    email:    j.recruiter_email || "",
  });

  const handleStatus = async (s) => {
    setStatus(s);
    await patchStatus(j.hash_id, s);
    onStatusChange();
  };

  const handleOutreach = async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/jobs/${j.hash_id}/outreach`, { method: "POST" });
      const data = await r.json();
      if (data.error) {
        alert(data.error);
      } else {
        setDraft({
          subject:   data.email_subject,
          body:      data.email_body,
          recruiter: data.recruiter,
          email:     data.recruiter_email,
        });
        setShowDraft(true);
      }
    } catch(e) {
      alert("Outreach request failed — is the API running?");
    } finally {
      setLoading(false);
    }
  };

  const c = scoreColor(j.match_score);

  return (
    <div className="outreach-card" style={{ borderLeft:`3px solid ${c}` }}>
      {/* Header */}
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", gap:16 }}>
        <div style={{ minWidth:0 }}>
          <div style={{ fontSize:14, fontWeight:700, marginBottom:3 }}>{j.title}</div>
          <div style={{ fontSize:11, color:"var(--muted)" }}>
            {j.company} · {j.location} · <SourcePill source={j.source}/>
          </div>
          {draft.recruiter && (
            <div style={{ fontSize:11, marginTop:5, color:"var(--accent2)" }}>
              ◎ {draft.recruiter}
              {draft.email && <span style={{color:"var(--accent)"}}> · {draft.email}</span>}
            </div>
          )}
        </div>
        <div style={{ textAlign:"right", flexShrink:0 }}>
          <div style={{ fontSize:22, fontWeight:800, color:c }}>{j.match_score}%</div>
          <StatusBadge status={status}/>
        </div>
      </div>

      {/* JD snippet */}
      {j.description && j.description.trim() && (
        <div style={{ margin:"10px 0 0", fontSize:11, color:"var(--muted)", borderLeft:"2px solid var(--border)", paddingLeft:10, lineHeight:1.75, fontStyle:"italic" }}>
          {j.description.slice(0,200)}{j.description.length > 200 ? "…" : ""}
        </div>
      )}

      {/* Draft email — shown after outreach is triggered */}
      {draft.subject && (
        <div style={{ marginTop:12 }}>
          <div style={{ fontSize:10, letterSpacing:1, color:"var(--muted)", fontFamily:"JetBrains Mono", marginBottom:6 }}>
            DRAFT EMAIL
            <button onClick={() => setShowDraft(d => !d)} style={{ marginLeft:10, background:"none", border:"none", color:"var(--accent2)", fontSize:10, cursor:"pointer", fontFamily:"JetBrains Mono" }}>
              {showDraft ? "▲ hide" : "▼ show"}
            </button>
          </div>
          <div style={{ fontSize:12, color:"var(--warn)", fontFamily:"JetBrains Mono", marginBottom:6 }}>
            Sub: {draft.subject}
          </div>
          {showDraft && (
            <div style={{ fontSize:12, color:"var(--muted)", background:"var(--surface2)", border:"1px solid var(--border)", borderRadius:8, padding:12, lineHeight:1.8, whiteSpace:"pre-line" }}>
              {draft.body}
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="outreach-actions">
        {/* Perform Outreach button — only show if no draft yet */}
        {!draft.subject && (
          <button
            className="action-btn"
            onClick={handleOutreach}
            disabled={loading}
            style={{ color:"var(--accent)", borderColor:"rgba(0,229,160,0.3)",
                     opacity: loading ? 0.6 : 1 }}
          >
            {loading ? "⟳ Finding recruiter..." : "⚡ Perform Outreach"}
          </button>
        )}

        {/* Status buttons */}
        {["Outreach Sent","Replied","Interview","Skipped"].map(s => (
          <button key={s}
            className={`action-btn ${status===s?"active":""}`}
            onClick={() => handleStatus(s)}>
            {s}
          </button>
        ))}

        {/* Open in mail — only show if we have recruiter email */}
        {draft.email && draft.subject && (
          <a
            href={`https://mail.google.com/mail/?view=cm&to=${encodeURIComponent(draft.email)}&su=${encodeURIComponent(draft.subject)}&body=${encodeURIComponent(draft.body)}`}
            target="_blank"
            rel="noreferrer"
            style={{ marginLeft:"auto" }}
          >
            <button className="action-btn" style={{ color:"var(--accent)", borderColor:"rgba(0,229,160,0.3)" }}>
              ✉ Open in Gmail
            </button>
          </a>
        )}

        <a href={j.url} target="_blank" rel="noreferrer">
          <button className="action-btn open-link">↗ Job</button>
        </a>
      </div>
    </div>
  );
}

function FiltersBar({ filters, onChange, sources, locations, threshold }) {
  return (
    <div className="filters-bar">
      <span className="filter-label">Filter:</span>
      <select className="filter-select" value={filters.minScore} onChange={e => onChange({...filters, minScore:Number(e.target.value)})}>
        <option value={0}>Above threshold ({threshold}%)</option>
        <option value={60}>60%+</option>
        <option value={70}>70%+</option>
        <option value={75}>75%+</option>
        <option value={80}>80%+</option>
      </select>
      <div className="filter-divider"/>
      <select className="filter-select" value={filters.source} onChange={e => onChange({...filters, source:e.target.value})}>
        <option value="All">All sources</option>
        {sources.map(s => <option key={s}>{s}</option>)}
      </select>
      <div className="filter-divider"/>
      <select className="filter-select" value={filters.location}
        onChange={e => onChange({...filters, location: e.target.value})}>
        <option value="All">All locations</option>
        {locations.map(l => <option key={l}>{l}</option>)}
      </select>
      <div className="filter-divider"/>
      <select className="filter-select" value={filters.posted} onChange={e => onChange({...filters, posted:e.target.value})}>
        <option value="All">This week</option>
        <option value="Today">Today</option>
        <option value="3 Days">Last 3 days</option>
      </select>
    </div>
  );
}

export default function COIE() {
  const [nav,     setNav]     = useState("dashboard");
  const [lastRun, setLastRun] = useState(new Date().toLocaleTimeString());
  const [filters, setFilters] = useState({ minScore:0, source:"All", posted:"All", location:"All" });
  const [modal, setModal] = useState(null);

  const stats   = useFetch(`${API}/api/stats`);
  const allJobs = useFetch(`${API}/api/jobs?limit=500`);
  const skippedJobs = useFetch(`${API}/api/jobs/skipped`);
  console.log("Skipped jobs:", skippedJobs.data);

  const refresh = () => { 
    stats.refetch(); 
    allJobs.refetch(); 
    skippedJobs.refetch();
    setLastRun(new Date().toLocaleTimeString()); 
  };

  const downloadJobs = () => {
    window.open(`${API}/api/jobs/export`, "_blank");
  };

  const sources      = [...new Set((allJobs.data||[]).map(j => j.source))].filter(Boolean);
  const locations = [...new Set(
    (allJobs.data||[])
      .map(j => j.location?.split(",")[0].trim())
      .filter(Boolean)
  )].sort();
  const threshold    = stats.data?.threshold || 75;
  const outreachThreshold = stats.data?.outreach_threshold || 80;
  const scoredJobs   = (allJobs.data||[]).filter(j => j.match_score >= threshold && j.status !== "Skipped");
  const unscoredJobs = (allJobs.data||[]).filter(j => j.match_score <= 0);
  const filteredJobs = applyFilters(scoredJobs, {
    ...filters,
    minScore: Math.max(filters.minScore, threshold)  
  });  
  const apiError     = stats.error || allJobs.error;

  const navItems = [
    { id:"dashboard", icon:"◈", label:"Pipeline" },
    { id:"jobs",      icon:"⊞", label:"Job Feed",  badge:scoredJobs.length },
    { id:"outreach",  
      icon:"✉", 
      label:"Outreach",  
      badge: (allJobs.data||[]).filter(j => j.match_score >= (stats.data?.outreach_threshold||80)).length, 
      warn:true 
    },
    { id:"settings", icon:"⚙", label:"Settings" }
  ];

  return (
    <>
      <style>{styles}</style>
      <div className="app">
        <header className="topbar">
          <div className="logo">C<em>O</em>IE <span style={{fontSize:10,color:"var(--muted)",fontWeight:400,fontFamily:"JetBrains Mono",letterSpacing:1,marginLeft:8}}>career outreach engine</span></div>
          <div className="topbar-right">
            <div style={{display:"flex",alignItems:"center",gap:6}}>
              <div className="status-dot"/>
              <span className="status-label">synced {lastRun}</span>
            </div>
            <button className="refresh-btn" onClick={refresh}>↻ Refresh</button>
          </div>
        </header>

        <nav className="sidebar">
          <div className="nav-section">
            <div className="nav-label">Views</div>
            {navItems.map(n => (
              <div key={n.id} className={`nav-item ${nav===n.id?"active":""}`} onClick={() => setNav(n.id)}>
                <span className="nav-icon">{n.icon}</span>{n.label}
                {n.badge > 0 && <span className={`nav-badge ${n.warn?"warn":""}`}>{n.badge}</span>}
              </div>
            ))}
          </div>
          <div className="nav-divider"/>
          <div className="nav-meta">
            <div>Threshold: <span style={{color:"var(--accent)"}}>{threshold}%</span></div>
            <div>Sources: <span style={{color:"var(--text)"}}>LinkedIn + Naukri + Indeed</span></div>
            <div>Unscored: <span style={{color:"var(--warn)"}}>{unscoredJobs.length}</span></div>
          </div>
          <div className="nav-divider"/>
          <div className="nav-section">
            <div className="nav-label">How it works</div>
            <button className="info-btn" onClick={() => setModal("scoring")}>
              <span className="nav-icon">◎</span> Resume Scoring
            </button>
            <button className="info-btn" onClick={() => setModal("outreach")}>
              <span className="nav-icon">⚡</span> Outreach Flow
            </button>
          </div>
        </nav>

        <main className="main">
          {apiError && (
            <div className="error-banner">
              ⚠ Cannot connect to API at <strong>{API}</strong><br/>
              Run: <strong>uvicorn api.main:app --reload --port 8000</strong>
            </div>
          )}

          {nav === "dashboard" && (
            <>
              <div className="page-header">
                <div>
                  <div className="page-title">Pipeline <span>Overview</span></div>
                  <div className="page-sub">{stats.data ? `${stats.data.total_scraped} total · ${stats.data.high_match} above ${threshold}% · ${unscoredJobs.length} unscored` : "Loading..."}</div>
                </div>
              </div>
              {stats.loading ? <div className="loading"><div className="spinner"/>Loading...</div> : <>
                <div className="stats-grid">
                  {[
                    { label:"Total Scraped", value:stats.data?.total_scraped??"—", icon:"⊞", grad:"linear-gradient(90deg,#7b61ff,#00b8ff)" },
                    { label:`Match ${threshold}%+`, value:stats.data?.high_match??"—", icon:"◎", grad:"linear-gradient(90deg,#00e5a0,#00b8ff)" },
                    { label:"Outreach Sent", value:stats.data?.outreach_sent??"—", icon:"✉", grad:"linear-gradient(90deg,#ffa502,#ff6b35)" },
                    { label:"Reply Rate",    value:`${stats.data?.reply_rate??0}%`, icon:"↩", grad:"linear-gradient(90deg,#ff6b35,#ff4757)" },
                  ].map(s => (
                    <div key={s.label} className="stat-card" style={{"--grad":s.grad}}>
                      <div className="stat-icon">{s.icon}</div>
                      <div className="stat-label">{s.label}</div>
                      <div className="stat-value">{s.value}</div>
                    </div>
                  ))}
                </div>
                <div className="col-wide-narrow">
                  <div className="card">
                    <div className="card-title">Top Matches</div>
                    {stats.data?.top_jobs?.length === 0 && <div className="empty-state">No jobs above threshold yet</div>}
                    {stats.data?.top_jobs?.map((j,i) => (
                      <div key={i} className="top-job-row">
                        <div style={{minWidth:0}}>
                          <div className="top-job-name">{j.title}</div>
                          <div className="top-job-co">{j.company} <SourcePill source={j.source}/></div>
                        </div>
                        <div style={{display:"flex",alignItems:"center",gap:12,flexShrink:0}}>
                          <span style={{fontSize:16,fontWeight:800,color:scoreColor(j.match_score)}}>{j.match_score}%</span>
                          <StatusBadge status={j.status}/>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div style={{display:"flex",flexDirection:"column",gap:16}}>
                    <div className="card">
                      <div className="card-title">Conversion Funnel</div>
                      <Funnel stats={stats.data}/>
                    </div>
                    <div className="card">
                      <div className="card-title">By Source</div>
                      {stats.data?.by_source?.map(s => (
                        <div key={s.source} style={{display:"flex",justifyContent:"space-between",padding:"7px 0",borderBottom:"1px solid var(--border)",fontSize:13}}>
                          <SourcePill source={s.source}/>
                          <span style={{fontFamily:"JetBrains Mono",color:"var(--accent)",fontSize:13}}>{s.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>}
            </>
          )}

          {nav === "jobs" && (
            <>
              <div className="page-header">
                <div>
                  <div className="page-title">Job <span>Feed</span></div>
                  <div className="page-sub">{filteredJobs.length} scored · {unscoredJobs.length} unscored</div>
                </div>
                <div style={{ display:"flex", gap:20, alignItems:"center", flexWrap:"wrap" }}>
                  <FiltersBar filters={filters} onChange={setFilters} sources={sources} locations={locations} threshold={threshold}/>
                  <button
                    className="refresh-btn"
                    onClick={downloadJobs}
                    style={{ background:"var(--accent2)", display:"flex", alignItems:"center", gap:6 }}
                  >
                    ↓ Export
                  </button>
                </div>
              </div>
              {allJobs.loading ? <div className="loading"><div className="spinner"/>Loading...</div> : <>
                <div className="card">
                  <div className="table-wrap">
                    <table>
                      <thead><tr><th>Role</th><th>Company</th><th>Source</th><th>Match Score</th><th>Posted</th><th>Status</th><th></th></tr></thead>
                      <tbody>
                        {filteredJobs.map(j => <JobRow key={j.hash_id} job={j} onStatusChange={allJobs.refetch}/>)}
                        {filteredJobs.length === 0 && <tr><td colSpan={7}><div className="empty-state">No jobs match these filters</div></td></tr>}
                      </tbody>
                    </table>
                  </div>
                </div>
                <UnscoredSection jobs={unscoredJobs} onStatusChange={allJobs.refetch}/>
                 <SkippedSection 
                  jobs={skippedJobs.data || []} 
                  onStatusChange={() => { allJobs.refetch(); skippedJobs.refetch(); }}
                />
              </>}
            </>
          )}

          {nav === "outreach" && (
            <>
              <div className="page-header">
                <div>
                  <div className="page-title">Outreach <span>Queue</span></div>
                  <div className="page-sub">
                    {filteredJobs.filter(j => j.match_score >= outreachThreshold && j.status !== "Rejected" && j.status !== "Skipped").length} jobs above {outreachThreshold}% · review before sending
                  </div>
                </div>
                <FiltersBar filters={filters} onChange={setFilters} sources={sources} locations={locations} threshold={threshold}/>
              </div>
              {allJobs.loading ? <div className="loading"><div className="spinner"/>Loading...</div> : <>
                {filteredJobs
                  .filter(j => j.match_score >= outreachThreshold && j.status !== "Rejected" && j.status !== "Skipped")
                  .map(j => <OutreachCard key={j.hash_id} job={j} onStatusChange={allJobs.refetch}/>)
                }
              </>}
            </>
          )}

          {nav === "settings" && (
            <SettingsPanel onSave={() => { stats.refetch(); allJobs.refetch(); }} />
          )}
        </main>
      </div>

      {/* Modals */}
      {modal && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setModal(null)}>✕</button>

            {modal === "scoring" && <>
              <div className="modal-title">Resume <span>Scoring</span></div>
              <div className="modal-sub">How COIE ranks jobs against your resume</div>

              <div className="modal-step">
                <div className="modal-step-num">1</div>
                <div className="modal-step-content">
                  <div className="modal-step-title">Resume Parsing</div>
                  <div className="modal-step-desc">Your PDF resume is read and converted to plain text using pdfplumber. All 4,492 characters are extracted including experience, skills, and education.</div>
                </div>
              </div>

              <div className="modal-step">
                <div className="modal-step-num">2</div>
                <div className="modal-step-content">
                  <div className="modal-step-title">Semantic Embedding</div>
                  <div className="modal-step-desc">Both your resume and each job description are converted into 384-dimension vectors using the <strong style={{color:"var(--text)"}}>all-MiniLM-L6-v2</strong> sentence transformer model running locally on your machine.</div>
                  <div className="modal-code">
                    resume_text → [0.23, -0.41, 0.87, ...]<br/>
                    job_desc    → [0.21, -0.38, 0.91, ...]
                  </div>
                </div>
              </div>

              <div className="modal-step">
                <div className="modal-step-num">3</div>
                <div className="modal-step-content">
                  <div className="modal-step-title">Cosine Similarity</div>
                  <div className="modal-step-desc">The angle between the two vectors is measured. Unlike keyword matching, this understands semantic meaning — so "stakeholder management" and "cross-functional collaboration" score similarly.</div>
                  <div className="modal-code">
                    similarity = cos_sim(resume, jd)<br/>
                    score = ((similarity + 1) / 2) × 100
                  </div>
                </div>
              </div>

              <div className="modal-step">
                <div className="modal-step-num">4</div>
                <div className="modal-step-content">
                  <div className="modal-step-title">Thresholds</div>
                  <div className="modal-step-desc">Jobs above <strong style={{color:"var(--accent)"}}>{stats.data?.threshold || 75}%</strong> appear in your dashboard and daily email. Jobs above <strong style={{color:"var(--warn)"}}>{stats.data?.outreach_threshold || 80}%</strong> appear in the Outreach Queue.</div>
                </div>
              </div>

              <div className="modal-divider"/>
              <div style={{fontSize:11,color:"var(--muted)",fontFamily:"JetBrains Mono",lineHeight:1.8}}>
                ⚠ LinkedIn jobs often have short snippets due to the authwall — their scores are less reliable than Naukri jobs which return full descriptions.
              </div>
            </>}

            {modal === "outreach" && <>
              <div className="modal-title">Outreach <span>Flow</span></div>
              <div className="modal-sub">What happens when you click "Perform Outreach"</div>

              <div className="modal-step">
                <div className="modal-step-num">1</div>
                <div className="modal-step-content">
                  <div className="modal-step-title">Hunter.io — Recruiter Discovery</div>
                  <div className="modal-step-desc">COIE queries Hunter's Domain Search API with the company name. Hunter resolves it to a domain and returns HR/Talent Acquisition contacts with verified work emails.</div>
                  <div className="modal-code">
                    "Netcore Cloud" → netcorecloud.com<br/>
                    → Priya Sharma · Senior Recruiter<br/>
                    → p.sharma@netcorecloud.com
                  </div>
                </div>
              </div>

              <div className="modal-step">
                <div className="modal-step-num">2</div>
                <div className="modal-step-content">
                  <div className="modal-step-title">Groq — Email Generation</div>
                  <div className="modal-step-desc">The recruiter profile, job description, and your resume are sent to <strong style={{color:"var(--text)"}}>Llama 3.1</strong> via Groq's free API. It generates a 4-6 line personalized outreach email with a subject line.</div>
                </div>
              </div>

              <div className="modal-step">
                <div className="modal-step-num">3</div>
                <div className="modal-step-content">
                  <div className="modal-step-title">Human Review</div>
                  <div className="modal-step-desc">The draft appears in the card for your review. Nothing is sent automatically — you read it, adjust if needed, then click <strong style={{color:"var(--accent)"}}>Open in Gmail</strong> to send.</div>
                </div>
              </div>

              <div className="modal-step">
                <div className="modal-step-num">4</div>
                <div className="modal-step-content">
                  <div className="modal-step-title">Track & Follow Up</div>
                  <div className="modal-step-desc">Mark the job as <strong style={{color:"var(--accent2)"}}>Outreach Sent</strong> after sending. Update to <strong style={{color:"var(--accent)"}}>Replied</strong> or <strong style={{color:"var(--accent)"}}>Interview</strong> as things progress. The dashboard tracks your reply rate.</div>
                </div>
              </div>

              <div className="modal-divider"/>
              <div style={{fontSize:11,color:"var(--muted)",fontFamily:"JetBrains Mono",lineHeight:1.8}}>
                💡 Hunter credits are only consumed when you click the button — not on every pipeline run. Free tier gives 25 searches/month.
              </div>
            </>}
          </div>
        </div>
      )}
    </>
  );
}