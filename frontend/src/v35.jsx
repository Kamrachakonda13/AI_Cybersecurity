import React,{useEffect,useState} from 'react';
import {Panel} from './v29_components.jsx';
const API=import.meta.env.VITE_API_URL||'http://localhost:8000';
const auth=()=>({Authorization:`Bearer ${sessionStorage.getItem('aegisx_user_token')}`});
const get=p=>fetch(`${API}${p}`,{headers:auth()}).then(r=>{if(!r.ok)throw new Error(String(r.status));return r.json()});
export function V35SecurityLifecycleView(){
 const [o,setO]=useState(null),[p,setP]=useState(null);
 useEffect(()=>{Promise.all([get('/api/v35/lifecycle/overview'),get('/api/v35/lifecycle/plan')]).then(([a,b])=>{setO(a);setP(b)}).catch(()=>{})},[]);
 return <div className="content"><div className="sectionintro"><div><div className="eyebrow">VEYRA V3.5 · SECURITY LIFECYCLE</div><h2>Security Operations Lifecycle</h2><p>Connect discovery, validation, investigation, response, proof and continuous revalidation into one governed operating model.</p></div></div>
 <div className="grid3"><div className="card"><small>STAGES</small><strong style={{fontSize:22}}>{o?.stages?.length||10}</strong></div><div className="card"><small>ATTENTION</small><strong style={{fontSize:22}}>{o?.stages?.filter(x=>x.status==='attention').length||0}</strong></div><div className="card"><small>EVIDENCE ITEMS</small><strong style={{fontSize:22}}>{o?.inventory?.evidence||0}</strong></div></div>
 <Panel title="Lifecycle"><div className="table">{(o?.stages||[]).map((s,i)=><div className="row" key={s.id}><div><b>{i+1}. {s.name}</b><small>{s.description}</small><small>Evidence: {s.evidence.join(' · ')}</small></div><span className={'badge '+(s.status==='attention'?'critical':'')}>{s.status.toUpperCase()}</span></div>)}</div></Panel>
 <Panel title="Current lifecycle plan"><div className="table">{(p?.stages||[]).map(s=><div className="row" key={s.id}><div><b>{s.name}</b><small>{s.description}</small></div><span className="badge">PLAN</span></div>)}</div></Panel>
 <div className="callout"><b>Governance boundary:</b> lifecycle planning never executes a tool. Validation and containment require explicit scope, Sudo/RBAC, approval, an isolated managed worker, signed contracts and evidence/audit capture. Hack-back is disabled.</div>
 </div>
}
