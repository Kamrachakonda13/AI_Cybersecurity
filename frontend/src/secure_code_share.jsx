import React, { useEffect, useState } from 'react';
import { Clipboard, LockKeyhole, ShieldCheck, Trash2 } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function SecureCodeShareView() {
    const [state, setState] = useState({ loading: true });
    useEffect(() => {
        const token = window.location.pathname.split('/').pop();
        fetch(`${API}/api/auth/secure-code-shares/${encodeURIComponent(token)}`)
            .then(async response => { const body = await response.json(); if (!response.ok) throw new Error(body.detail || 'Secure share unavailable'); return body; })
            .then(body => { setState({ code: body.code, hint: body.recipient_hint }); window.history.replaceState({}, '', '/'); })
            .catch(error => setState({ error: error.message }));
    }, []);
    const copy = async () => { if (state.code) await navigator.clipboard.writeText(state.code); setState(current => ({ ...current, copied: true })); };
    return <div className="content" style={{ maxWidth: 720, margin: '8vh auto' }}><Panel title="Secure one-time code"><div style={{ padding: 22, display: 'grid', gap: 14, textAlign: 'center' }}><LockKeyhole size={36} style={{ margin: '0 auto', color: '#62a0ff' }} />{state.loading ? <p>Retrieving and destroying this secure share...</p> : state.error ? <><h2>Share unavailable</h2><p>{state.error}</p><small>This link may have expired or already been opened.</small></> : <><div className="callout"><ShieldCheck size={16} /> This code was retrieved once and the server destroyed the share.</div><code style={{ fontSize: 22, padding: 16, wordBreak: 'break-all', background: '#0d1622', borderRadius: 8 }}>{state.code}</code>{state.hint && <small>Recipient: {state.hint}</small>}<button className="primary" onClick={copy}><Clipboard size={15} /> {state.copied ? 'Copied' : 'Copy code'}</button><small><Trash2 size={13} /> Do not forward this page or code.</small></>}</div></Panel></div>;
}

export function SecureCodeShareComposer() {
    const [code, setCode] = useState(''), [hint, setHint] = useState(''), [minutes, setMinutes] = useState(10), [url, setUrl] = useState(''), [message, setMessage] = useState('');
    const auth = () => ({ Authorization: `Bearer ${sessionStorage.getItem('VEYRA_user_token') || ''}`, 'Content-Type': 'application/json' });
    const create = async () => { setMessage(''); setUrl(''); const response = await fetch(`${API}/api/admin/secure-code-shares`, { method: 'POST', headers: auth(), body: JSON.stringify({ code, recipient_hint: hint, expires_in_minutes: Number(minutes) }) }); const body = await response.json(); if (!response.ok) return setMessage(body.detail || 'Unable to create secure share'); setUrl(body.url); setCode(''); setMessage('Share created. The code is encrypted at rest and will be destroyed on first open.'); };
    const copy = async () => { await navigator.clipboard.writeText(url); setMessage('One-time URL copied. Do not paste it into a public channel.'); };
    return <Panel title="Share a one-time secure code"><div style={{ padding: 16, display: 'grid', gap: 8 }}><div className="callout"><b>Privileged handoff.</b> The URL contains a random single-use token, not the code. Opening it consumes and destroys the server record.</div><input type="password" value={code} onChange={event => setCode(event.target.value)} placeholder="Code or temporary credential" /><input value={hint} onChange={event => setHint(event.target.value)} placeholder="Recipient hint (optional)" /><label style={{ fontSize: 12 }}>Expires in <select value={minutes} onChange={event => setMinutes(event.target.value)}><option value="5">5 minutes</option><option value="10">10 minutes</option><option value="30">30 minutes</option><option value="60">60 minutes</option></select></label><button className="primary" disabled={!code} onClick={create}><LockKeyhole size={15} /> Create one-time URL</button>{url && <div className="row"><code style={{ wordBreak: 'break-all' }}>{url}</code><button onClick={copy}><Clipboard size={15} /> Copy URL</button></div>}{message && <div className="callout">{message}</div>}</div></Panel>;
}

function Panel({ title, children }) { return <section className="panel"><div className="panelhead"><h3>{title}</h3></div>{children}</section>; }