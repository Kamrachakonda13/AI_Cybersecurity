import React,{useEffect,useState} from 'react';
import {Panel} from './v29_components.jsx';
const API=import.meta.env.VITE_API_URL||'http://localhost:8000';
const auth=()=>({Authorization:`Bearer ${sessionStorage.getItem('VEYRA_user_token')}`,'Content-Type':'application/json'});
const get=p=>fetch(`${API}${p}`,{headers:auth()}).then(r=>{if(!r.ok)throw new Error(String(r.status));return r.json()});
export function V32TeamAcademyView(){
 const [o,setO]=useState(null),[track,setTrack]=useState('ai-security'),[cur,setCur]=useState(null),[q,setQ]=useState('');
 useEffect(()=>{get('/api/v32/academy/overview').then(setO).catch(()=>{})},[]);
 useEffect(()=>{get(`/api/v32/academy/curriculum/${track}`).then(setCur).catch(()=>{})},[track]);
 const rows=(cur?.tools||[]).filter(t=>!q||`${t.name} ${t.category} ${t.purpose}`.toLowerCase().includes(q.toLowerCase()));
 return <div className="content"><div className="sectionintro"><div><div className="eyebrow">VEYRA V3.2 · TEAM ENABLEMENT</div><h2>Security Team Academy</h2><p>Role-based learning paths for operating the VEYRA security arsenal safely and consistently.</p></div></div>
 {o&&<div className="grid3">{o.levels.slice(0,3).map(x=><div className="card" key={x.id}><small>{x.name.toUpperCase()}</small><strong style={{fontSize:15}}>{x.goal}</strong></div>)}</div>}
 <div className="grid2"><Panel title="Learning track"><div style={{padding:16,display:'grid',gap:10}}><select value={track} onChange={e=>setTrack(e.target.value)}>{(o?.tracks||[]).map(t=><option key={t.id} value={t.id}>{t.name}</option>)}</select><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search tools in this curriculum…"/><div className="callout">Use the tool's individual Markdown help page for purpose, UI workflow, terminal starting point, evidence, interpretation, remediation and verification.</div></div></Panel><Panel title="Documentation contract"><div style={{padding:16}}>{(o?.documentation_contract||[]).map(x=><div className="row" key={x}><b>{x.replaceAll('_',' ')}</b><span className="badge">REQUIRED</span></div>)}</div></Panel></div>
 <Panel title={`${cur?.track||''} curriculum (${rows.length})`}><div className="table" style={{maxHeight:700,overflowY:'auto'}}>{rows.map(t=><div className="row" key={t.id}><div><b>{t.name}</b><small>{t.category} · {t.purpose}</small><small>{t.execution_profile} · {t.access_tier}</small></div><span className={'badge '+(t.access_tier==='privileged_admin'?'critical':'')}>OPEN HELP</span></div>)}</div></Panel>
 </div>
}
