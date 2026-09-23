import React, { useEffect, useState } from 'react';
import { Activity, Database, MessageSquare, RefreshCw, ShieldAlert } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const auth = () => ({ Authorization: `Bearer ${sessionStorage.getItem('VEYRA_user_token') || ''}` });

export function EnterpriseIntelligenceView({ page = 'overview' }) {
    const [status, setStatus] = useState(null), [connectors, setConnectors] = useState(null), [answer, setAnswer] = useState(null);
    const [question, setQuestion] = useState('Summarize the highest-risk security signals and cite the source evidence.'), [message, setMessage] = useState(''), [loading, setLoading] = useState(false);
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
    return <div className="content"><div className="sectionintro"><div><div className="eyebrow">AGENTIC RAG PROJECT · RAG FABRIC</div><h2>{page === 'sources' ? 'Source connectors' : page === 'duplicates' ? 'Duplicate intelligence' : 'Enterprise Intelligence'}</h2><p>This workspace belongs to the Agentic RAG Ingestion Fabric project. VEYRA remains the security control plane; this surface owns enterprise knowledge ingestion, retrieval and data-quality operations.</p></div><button onClick={load}><RefreshCw size={15} /> Refresh fabric</button></div>
        {message && <div className="callout"><ShieldAlert size={16} /> {message}</div>}
        <div className="kpis"><div className="kpi"><small><Activity size={13} /> SERVICE</small><strong>{status ? 'Connected' : 'Offline'}</strong></div><div className="kpi"><small><Database size={13} /> SOURCES</small><strong>{connectors?.count ?? '—'}</strong></div>{metrics.slice(0, 2).map(([key, value]) => <div className="kpi" key={key}><small>{key.replaceAll('_', ' ')}</small><strong>{String(value)}</strong></div>)}</div>
        {page === 'overview' && <Panel title="Grounded enterprise query"><div style={{ display: 'grid', gap: 10, padding: 16 }}><textarea value={question} onChange={event => setQuestion(event.target.value)} rows={3} placeholder="Ask about governed evidence..." /><div><button className="primary" onClick={ask} disabled={loading || !question.trim()}><MessageSquare size={15} /> {loading ? 'Querying...' : 'Ask Agentic RAG'}</button></div>{answer && <div className="callout"><b>{answer.refused ? 'Query refused' : 'Grounded response'}</b><div style={{ whiteSpace: 'pre-wrap', marginTop: 8 }}>{answer.answer}</div><small>{answer.citations?.length || 0} citations · route: {answer.route || 'hybrid'}</small></div>}</div></Panel>}
        <Panel title={page === 'duplicates' ? 'Duplicate groups' : 'Ingestion sources'}><div className="table">{connectors?.connectors?.map(connector => <div className="row" key={connector.name}><div><b>{connector.display_name || connector.name}</b><small>{connector.source_system || 'source'} · {connector.document_count ?? 'unknown'} documents</small></div><span className={'badge ' + (connector.status === 'loaded' ? '' : 'critical')}>{connector.status}</span></div>) || <div className="empty">Connect the Agentic RAG service to inspect this project surface.</div>}</div></Panel>
        <div className="callout"><b>Project boundary:</b> This is the Agentic RAG Fabric UI inside the VEYRA shell. Use the RAG Fabric navigation group for ingestion and retrieval operations; use VEYRA navigation groups for security operations.</div>
    </div>;
}

function RagNativeSurface({ page }) {
    const base = import.meta.env.VITE_AGENTIC_RAG_URL || 'http://localhost:8100';
    const path = page === 'dashboard' ? '/dashboard' : `/dashboard/${page}`;
    return <div className="content"><div className="sectionintro"><div><div className="eyebrow">AGENTIC RAG PROJECT · NATIVE ADMIN</div><h2>{page.replaceAll('-', ' ')}</h2><p>This page is rendered by the original Agentic RAG project UI. It is intentionally framed and labeled separately from VEYRA security operations.</p></div><a className="primary" href={`${base}${path}`} target="_blank" rel="noreferrer">Open native RAG page</a></div><div className="callout"><b>Separate project surface.</b> The native dashboard uses the Agentic RAG project session and admin controls. VEYRA authentication does not silently impersonate that session.</div><div style={{ border: '1px solid #2a4056', borderRadius: 8, overflow: 'hidden', background: '#f8fafc', minHeight: 720 }}><iframe title={`Agentic RAG ${page}`} src={`${base}${path}`} style={{ width: '100%', height: 720, border: 0 }} /></div></div>;
}

function Panel({ title, children }) { return <section className="panel"><div className="panelhead"><h3>{title}</h3></div>{children}</section>; }