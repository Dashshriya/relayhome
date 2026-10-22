import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, Check, CircleAlert, ClipboardList, HeartHandshake, LoaderCircle, RefreshCw, ShieldCheck, Users } from 'lucide-react';
import './styles.css';

const demoPrompt = 'Mom has an appointment tomorrow. Confirm transport and pack her bag, then call to check in.';

function App() {
  const [overview, setOverview] = useState(null);
  const [message, setMessage] = useState(demoPrompt);
  const [plan, setPlan] = useState(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [mcpTools, setMcpTools] = useState([]);
  const [mcpStatus, setMcpStatus] = useState('checking');
  const [mcpLoading, setMcpLoading] = useState(false);
  const [mcpError, setMcpError] = useState('');

  async function loadOverview() {
    try {
      const response = await fetch('/api/overview');
      if (!response.ok) throw new Error('The API could not load the household overview.');
      setOverview(await response.json());
      setError('');
    } catch {
      setError('Could not connect to the local API. Start the MCP server and FastAPI service, then refresh.');
    }
  }

  async function loadMcpTools() {
    setMcpLoading(true);
    setMcpError('');
    try {
      const response = await fetch('/api/mcp/tools');
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Could not discover MCP tools.');
      setMcpTools(data.tools || []);
      setMcpStatus('connected');
    } catch (err) {
      setMcpTools([]);
      setMcpStatus('unavailable');
      setMcpError(err.message || 'MCP server unavailable. Start the MCP server and refresh discovery.');
    } finally {
      setMcpLoading(false);
    }
  }

  useEffect(() => { loadOverview(); loadMcpTools(); }, []);

  async function makePlan(event) {
    event.preventDefault();
    setBusy(true); setNotice(''); setError('');
    try {
      const response = await fetch('/api/plan', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Could not draft a plan.');
      setPlan(data);
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  async function approvePlan() {
    if (!plan?.steps?.length) return;
    setBusy(true); setNotice(''); setError('');
    try {
      const response = await fetch('/api/execute', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ steps: plan.steps })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Could not save the plan.');
      setNotice(`Saved ${data.executed} steps to the demo household.`);
      setPlan(null);
      await loadOverview();
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  async function completeTask(id) {
    setBusy(true); setNotice(''); setError('');
    try {
      const response = await fetch(`/api/complete/${encodeURIComponent(id)}`, { method: 'POST' });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Could not update the task.');
      setNotice('Task marked complete.');
      await loadOverview();
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  const tasks = overview?.tasks || [];
  const activity = overview?.activity || [];
  const context = overview?.context || {};

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-icon"><HeartHandshake size={21}/></span><span>RelayHome<small>CARE, COORDINATED</small></span></div>
      <div className="household"><Users size={16}/><span><small>HOUSEHOLD</small><strong>{context.household_name || 'Demo household'}</strong></span></div>
      <nav><span className="nav-heading">WORKSPACE</span><a className="nav-active"><ClipboardList size={17}/> Overview</a><a href="#planner"><HeartHandshake size={17}/> Care plan</a><a href="#mcp-tools"><Activity size={17}/> MCP tools</a><a href="#activity"><Activity size={17}/> Activity</a></nav>
      <div className="privacy"><ShieldCheck size={18}/><strong>Nothing happens without you.</strong><p>Review every plan before tasks are added. This demo uses fictional household data.</p></div>
      <div className="sidebar-foot">A LITTLE MORE IN SYNC.</div>
    </aside>

    <main className="main">
      <header className="topbar"><span>Household / Overview</span><span className="demo-pill"><span/> LOCAL DEMO</span></header>
      <section className="welcome">
        <div><p className="eyebrow">YOUR HOUSEHOLD AT A GLANCE</p><h1>Good to have you here.</h1><p className="subhead">Keep the small things moving, together.</p></div>
        <div className="date-note"><span>COORDINATION BOARD</span><strong>Today, together</strong></div>
      </section>

      {error && <div className="alert alert-error"><CircleAlert size={17}/>{error}</div>}
      {notice && <div className="alert alert-success"><Check size={17}/>{notice}<button onClick={() => setNotice('')} aria-label="Dismiss message">×</button></div>}

      <section className="stats">
        <article className="stat-card"><span className="stat-icon sage"><ClipboardList size={18}/></span><p>Open tasks</p><strong>{tasks.length}</strong><small>Things still to do</small></article>
        <article className="stat-card"><span className="stat-icon peach"><HeartHandshake size={18}/></span><p>Check-ins planned</p><strong>{overview?.checkins?.length ?? '—'}</strong><small>Small moments that matter</small></article>
        <article className="stat-card"><span className="stat-icon blue"><Activity size={18}/></span><p>Recent updates</p><strong>{activity.length}</strong><small>Visible follow-through</small></article>
      </section>

      <div className="content-grid">
        <section className="panel tasks-panel">
          <div className="panel-heading"><div><p className="eyebrow">THE SHARED LIST</p><h2>What's on the list</h2></div><span className="count">{tasks.length} active</span></div>
          {tasks.length ? <div className="task-list">{tasks.map(task => <article className="task" key={task.id}>
            <span className={`task-dot ${task.priority?.toLowerCase() || ''}`}></span><div className="task-copy"><strong>{task.title}</strong><span>{task.category} · {task.due}</span><small>With {task.assignee}</small></div><div className="task-end"><span className="status">{task.status}</span><button className="complete-btn" disabled={busy} onClick={() => completeTask(task.id)} title="Mark complete"><Check size={15}/></button></div>
          </article>)}</div> : <p className="empty">No open tasks right now.</p>}
          <button className="quiet-button" onClick={loadOverview} disabled={busy}><RefreshCw size={14}/> Refresh list</button>
        </section>

        <section className="panel planner-panel" id="planner">
          <div className="panel-heading"><div><p className="eyebrow">START WITH A REQUEST</p><h2>Make a small plan</h2></div><span className="spark">✳</span></div>
          <p className="panel-intro">Tell RelayHome what needs coordinating. You'll get a draft to review before anything is saved.</p>
          <form onSubmit={makePlan}>
            <label htmlFor="request">What's coming up?</label>
            <textarea id="request" value={message} onChange={e => setMessage(e.target.value)} minLength={3} maxLength={600} required/>
            <div className="form-foot"><span>Uses local planning rules</span><button className="primary" disabled={busy}>{busy ? <LoaderCircle size={15} className="spin"/> : null}{busy ? 'Working…' : 'Draft a plan'}</button></div>
          </form>
          {plan && <div className="draft">
            <div className="draft-head"><div><span className="eyebrow">READY FOR YOUR REVIEW</span><h3>{plan.steps.length} suggested steps</h3></div><span className="review-badge">Not saved</span></div>
            <p>{plan.summary}</p>
            {plan.steps.map((step, i) => <div className="draft-step" key={i}><span>{String(i + 1).padStart(2, '0')}</span><div><strong>{step.title || `${step.method} check-in with ${step.person}`}</strong><small>{step.type === 'task' ? `${step.category} · ${step.due} · ${step.assignee}` : `${step.method} · ${step.when}`}</small></div></div>)}
            <p className="safety-note">{plan.safety_note}</p>
            <div className="draft-actions"><button className="quiet-button" onClick={() => setPlan(null)} disabled={busy}>Discard</button><button className="primary" onClick={approvePlan} disabled={busy}>{busy ? 'Saving…' : 'Approve and save'}</button></div>
          </div>}
          <div className="suggestion" onClick={() => setMessage(demoPrompt)} role="button" tabIndex="0" onKeyDown={e => e.key === 'Enter' && setMessage(demoPrompt)}><span>TRY THIS</span><p>“Help me get ready for an appointment tomorrow.”</p><span className="suggestion-arrow">↗</span></div>
        </section>
      </div>

      <section className="panel mcp-panel" id="mcp-tools">
        <div className="panel-heading">
          <div><p className="eyebrow">ALEXA+ SIMULATION / PROTOCOL STATUS</p><h2>Live MCP tool discovery</h2></div>
          <span className={`mcp-status ${mcpStatus}`}><span/>{mcpStatus === 'connected' ? 'Connected' : mcpStatus === 'checking' ? 'Checking' : 'Unavailable'}</span>
        </div>
        <p className="panel-intro">This view reads the tools advertised by RelayHome's running MCP server. The dashboard uses a real Streamable HTTP session; the household data is fictional and stays in this local demo.</p>
        <div className="mcp-toolbar">
          <span><strong>Transport</strong> Streamable HTTP <span className="mcp-separator">·</span> <strong>Endpoint</strong> /mcp</span>
          <button className="quiet-button" onClick={loadMcpTools} disabled={mcpLoading}>{mcpLoading ? 'Discovering…' : '↻ Refresh discovery'}</button>
        </div>
        {mcpError && <div className="mcp-error" role="status">{mcpError}</div>}
        {!mcpError && mcpStatus === 'connected' && <p className="mcp-result">{mcpTools.length} tools returned by the live server's tools/list response.</p>}
        <div className="mcp-tool-grid">
          {mcpTools.map(tool => <article className="mcp-tool-card" key={tool.name}>
            <div><code>{tool.name}</code><span>{Object.keys(tool.input_schema?.properties || {}).length} inputs</span></div>
            <p>{tool.description || 'No description supplied by the server.'}</p>
          </article>)}
          {mcpStatus === 'checking' && <p className="empty">Discovering tools from the MCP server…</p>}
          {mcpStatus === 'unavailable' && <p className="empty">Start the MCP server and FastAPI service, then refresh discovery.</p>}
        </div>
      </section>

      <section className="panel activity-panel" id="activity"><div className="panel-heading"><div><p className="eyebrow">A RECORD OF WHAT CHANGED</p><h2>Recent activity</h2></div><Activity size={19} className="muted-icon"/></div>
        {activity.length ? <div className="activity-list">{activity.slice(0, 5).map((item, i) => <article className="activity-item" key={i}><span className="activity-mark"><Check size={13}/></span><div><strong>{item.event}</strong><p>{item.detail}</p></div><time>{item.time}</time></article>)}</div> : <p className="empty">Updates will appear here as tasks change.</p>}
      </section>
      <footer><span>RELAYHOME · EARLY PROTOTYPE</span><span>Fictional data. No messages sent. No medical advice.</span></footer>
    </main>
  </div>;
}

createRoot(document.getElementById('root')).render(<App />);
