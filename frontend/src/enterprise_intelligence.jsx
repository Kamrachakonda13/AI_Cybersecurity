import React, { useEffect, useState } from 'react';
import { Activity, Database, MessageSquare, RefreshCw, ShieldAlert } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const auth = () => ({ Authorization: `Bearer ${sessionStorage.getItem('VEYRA_user_token') || ''}` });

export function EnterpriseIntelligenceView() {
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
    return <div className="content"><div className="sectionintro"><div><div className="eyebrow">ENTERPRISE INTELLIGENCE FABRIC</div><h2>One governed workspace for security evidence and knowledge</h2><p>VEYRA keeps the Agentic RAG ingestion fabric independent while presenting retrieval, source health and security operations through the same enterprise console.</p></div><button onClick={load}><RefreshCw size={15} /> Refresh fabric</button></div>
        {message && <div className="callout"><ShieldAlert size={16} /> {message}</div>}
        <div className="kpis"><div className="kpi"><small><Activity size={13} /> SERVICE</small><strong>{status ? 'Connected' : 'Offline'}</strong></div><div className="kpi"><small><Database size={13} /> SOURCES</small><strong>{connectors?.count ?? '—'}</strong></div>{metrics.slice(0, 2).map(([key, value]) => <div className="kpi" key={key}><small>{key.replaceAll('_', ' ')}</small><strong>{String(value)}</strong></div>)}</div>
        <Panel title="Grounded enterprise query"><div style={{ display: 'grid', gap: 10, padding: 16 }}><textarea value={question} onChange={event => setQuestion(event.target.value)} rows={3} placeholder="Ask about governed evidence..." /><div><button className="primary" onClick={ask} disabled={loading || !question.trim()}><MessageSquare size={15} /> {loading ? 'Querying...' : 'Ask Agentic RAG'}</button></div>{answer && <div className="callout"><b>{answer.refused ? 'Query refused' : 'Grounded response'}</b><div style={{ whiteSpace: 'pre-wrap', marginTop: 8 }}>{answer.answer}</div><small>{answer.citations?.length || 0} citations · route: {answer.route || 'hybrid'}</small></div>}</div></Panel>
        <Panel title="Ingestion sources"><div className="table">{connectors?.connectors?.map(connector => <div className="row" key={connector.name}><div><b>{connector.display_name || connector.name}</b><small>{connector.source_system || 'source'} · {connector.document_count ?? 'unknown'} documents</small></div><span className={'badge ' + (connector.status === 'loaded' ? '' : 'critical')}>{connector.status}</span></div>) || <div className="empty">Connect the Agentic RAG service to inspect ingestion sources.</div>}</div></Panel>
    </div>;
}

function Panel({ title, children }) { return <section className="panel"><div className="panelhead"><h3>{title}</h3></div>{children}</section>; }