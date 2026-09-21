import React,{useEffect,useState} from 'react';
import {Panel} from './v29_components.jsx';
const API=import.meta.env.VITE_API_URL||'http://localhost:8000';
const auth=()=>({Authorization:`Bearer ${sessionStorage.getItem('VEYRA_user_token')}`});
const get=p=>fetch(`${API}${p}`,{headers:auth()}).then(r=>{if(!r.ok)throw new Error(String(r.status));return r.json()});
export function V34SecurityIntelligenceView(){
 const [o,setO]=useState(null),[p,setP]=useState(null);
 useEffect(()=>{Promise.all([get('/api/v34/intelligence/overview'),get('/api/v34/validation/plan')]).then(([a,b])=>{setO(a);setP(b)}).catch(()=>{})},[]);
 return <div className="content"><div className="sectionintro"><div><div className="eyebrow">VEYRA V3.4 · SECURITY INTELLIGENCE</div><h2>Continuous Security Validation</h2><p>Turn telemetry, inventory, documentation and security controls into repeatable, governed validation work.</p></div></div>
 <div className="grid3"><div className="card"><small>ASSETS</small><strong style={{fontSize:22}}>{o?.inventory?.assets||0}</strong></div><div className="card"><small>AI ASSETS</small><strong style={{fontSize:22}}>{o?.inventory?.ai_assets||0}</strong></div><div className="card"><small>CONTROL TESTS</small><strong style={{fontSize:22}}>{o?.control_tests?.length||0}</strong></div></div>
 <Panel title="Priority defensive signals"><div className="table">{(o?.signals||[]).map(s=><div className="row" key={s.id}><div><b>{s.id}</b><small>{s.message}</small></div><span className={'badge '+(s.priority==='high'?'critical':'')}>{s.priority.toUpperCase()}</span></div>)}{!o?.signals?.length&&<div className="empty">No priority signals currently generated.</div>}</div></Panel>
 <Panel title="Continuous validation plan"><div className="table">{(p?.tests||[]).map(t=><div className="row" key={t.id}><div><b>{t.name}</b><small>{t.frequency} · scope required · approval required</small><small>Evidence: {t.evidence.join(' · ')}</small></div><span className="badge">READY</span></div>)}</div></Panel>
 <div className="callout"><b>Execution boundary:</b> this page creates validation plans and evidence requirements. Actual testing remains on authorised managed workers behind scope, approval, Sudo and audit controls. VEYRA does not provide hack-back functionality.</div>
 </div>
}
