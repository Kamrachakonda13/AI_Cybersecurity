import React, { useEffect, useState } from 'react';
import { Activity, BookOpen, CheckCircle2, Database, LockKeyhole, MessageSquare, RefreshCw, Search, ShieldAlert, Sparkles } from 'lucide-react';
import './rag_fabric.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const auth = () => ({ Authorization: `Bearer ${sessionStorage.getItem('VEYRA_user_token') || ''}` });

export function EnterpriseIntelligenceView({ page = 'overview' }) {
    const [status, setStatus] = useState(null), [connectors, setConnectors] = useState(null), [answer, setAnswer] = useState(null);
    const [question, setQuestion] = useState(''), [message, setMessage] = useState(''), [loading, setLoading] = useState(false), [scope, setScope] = useState('All governed sources'), [mode, setMode] = useState('Hybrid retrieval');
    const load = async () => {
        setMessage('');
        try {
            const [statusResponse, connectorResponse] = await Promise.all([fetch(`${API}/api/v1/enterprise/rag/status`, { headers: auth() }), fetch(`${API}/api/v1/enterprise/rag/connectors`, { headers: auth() })]);
            if (!statusResponse.ok) throw new Error((await statusResponse.json()).detail || 'Agentic RAG service unavailable');
            setStatus(await statusResponse.json());
            if (connectorResponse.ok) setConnectors(await connectorResponse.json());
        } catch (error) { setStatus(null); setConnectors(null); setMessage(error.message); }
    };
    useEffect(() => { load(); }, []);
    const ask = async () => {
        setLoading(true); setMessage('');
        try {
            const response = await fetch(`${API}/api/v1/enterprise/rag/ask`, { method: 'POST', headers: { ...auth(), 'Content-Type': 'application/json' }, body: JSON.stringify({ question }) });
            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || 'Enterprise search failed');
            setAnswer(result);
        } catch (error) { setAnswer(null); setMessage(error.message); } finally { setLoading(false); }
    };
    const metrics = Object.entries(status?.metrics || {}).filter(([, value]) => typeof value !== 'object');
    const nativePage = page === 'native-admin' ? 'dashboard' : page;
    if (page !== 'overview' && page !== 'sources' && page !== 'duplicates') return <RagNativeSurface page={nativePage} />;
    const suggestions = ['What changed in our security policy this quarter?', 'Find evidence for the latest access review.', 'Explain the incident response workflow.'];
    const submit = event => { event?.preventDefault(); ask(); };
    const queryControls = <div className="rag-search-meta"><span className="rag-chip"><Database size={12} /> {scope}</span><span className="rag-chip"><Search size={12} /> {mode}</span><span className="rag-chip"><LockKeyhole size={12} /> ACL-filtered evidence</span></div>;
    if (page === 'overview') return <div className="content"><div className="rag-workspace"><div className="rag-landing"><section><div className="rag-kicker">AGENTIC RAG INGESTION FABRIC</div><h2 className="rag-title">Ask your enterprise knowledge base.</h2><p className="rag-lede">Search governed documents, security evidence, and operational decisions in one grounded workspace. Every answer is scoped to your access and traceable to source material.</p><form className="rag-searchbox" onSubmit={submit}><textarea value={question} onChange={event => setQuestion(event.target.value)} rows={2} placeholder="Ask a question about your enterprise evidence..." aria-label="Enterprise knowledge query" /><button type="submit" disabled={loading || !question.trim()}><MessageSquare size={16} /> {loading ? 'Searching' : 'Search evidence'}</button></form><div className="rag-quick">{suggestions.map(item => <button type="button" key={item} onClick={() => setQuestion(item)}>{item}</button>)}</div>{message && <div className="callout" style={{ marginTop: 14 }}><ShieldAlert size={16} /> {message}</div>}<div className="rag-statline" style={{ color: '#58708a', borderTopColor: '#d8e4ef' }}><div><strong style={{ color: '#12233b' }}>{connectors?.count ?? '—'}</strong><span style={{ display: 'block' }}>connected sources</span></div><div><strong style={{ color: '#12233b' }}>{status ? 'Live' : '—'}</strong><span style={{ display: 'block' }}>fabric status</span></div></div></section><aside className="rag-rail"><Sparkles size={22} color="#62d2b7" /><h3>Grounded by design.</h3><p>The RAG Fabric is the knowledge layer inside the VEYRA enterprise workspace. It retrieves first, answers second, and shows you what supports the result.</p><div className="rag-rail-item"><CheckCircle2 size={17} /><div><b>Evidence linked</b><small>See citations and source systems with every answer.</small></div></div><div className="rag-rail-item"><LockKeyhole size={17} /><div><b>Access aware</b><small>Retrieval honors clearance, tenant, and team boundaries.</small></div></div><div className="rag-rail-item"><BookOpen size={17} /><div><b>Built for operators</b><small>Move from a question to a defensible decision quickly.</small></div></div></aside></div>{answer && <section className="rag-answer" style={{ marginTop: 24 }}><h3><CheckCircle2 size={17} color="#2bbf9d" /> Grounded response</h3><div className="rag-search-meta" style={{ margin: '12px 0' }}>{queryControls}<span className="rag-chip">{answer.citations?.length || 0} citations</span><span className="rag-chip">Route: {answer.route || 'hybrid'}</span></div><div className="rag-answer-text">{answer.answer}</div><div className="rag-evidence">{(answer.citations || []).map((citation, index) => <div className="rag-evidence-card" key={citation.id || index}><b>{citation.source || `Evidence ${index + 1}`}</b><small>{citation.kind || 'retrieved chunk'} · clearance {citation.clearance_level || 'managed'} · score {citation.score ?? '—'}</small></div>)}</div></section>}</div></div>;
    return <div className="content"><div className="rag-workspace"><div className="rag-search-header"><div><div className="rag-kicker">AGENTIC RAG PROJECT · RAG FABRIC</div><h2>{page === 'sources' ? 'Source connectors' : 'Duplicate intelligence'}</h2><p className="rag-lede">Operational search context for the knowledge ingestion layer.</p></div><button onClick={load}><RefreshCw size={15} /> Refresh</button></div>{queryControls}<Panel title={page === 'duplicates' ? 'Duplicate groups' : 'Ingestion sources'}><div className="table">{connectors?.connectors?.map(connector => <div className="row" key={connector.name}><div><b>{connector.display_name || connector.name}</b><small>{connector.source_system || 'source'} · {connector.document_count ?? 'unknown'} documents</small></div><span className={'badge ' + (connector.status === 'loaded' ? '' : 'critical')}>{connector.status}</span></div>) || <div className="rag-empty">Connect the Agentic RAG service to inspect this project surface.</div>}</div></Panel></div></div>;
}

function RagNativeSurface({ page }) {
    const base = import.meta.env.VITE_AGENTIC_RAG_URL || 'http://localhost:8100';
    const path = page === 'dashboard' ? '/dashboard' : `/dashboard/${page}`;
    return <div className="content"><div className="sectionintro"><div><div className="eyebrow">AGENTIC RAG PROJECT · NATIVE ADMIN</div><h2>{page.replaceAll('-', ' ')}</h2><p>This page is rendered by the original Agentic RAG project UI. It is intentionally framed and labeled separately from VEYRA security operations.</p></div><a className="primary" href={`${base}${path}`} target="_blank" rel="noreferrer">Open native RAG page</a></div><div className="callout"><b>Separate project surface.</b> The native dashboard uses the Agentic RAG project session and admin controls. VEYRA authentication does not silently impersonate that session.</div><div style={{ border: '1px solid #2a4056', borderRadius: 8, overflow: 'hidden', background: '#f8fafc', minHeight: 720 }}><iframe title={`Agentic RAG ${page}`} src={`${base}${path}`} style={{ width: '100%', height: 720, border: 0 }} /></div></div>;
}

function Panel({ title, children }) { return <section className="panel"><div className="panelhead"><h3>{title}</h3></div>{children}</section>; }