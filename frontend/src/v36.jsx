import React,{useEffect,useState} from 'react';
import {Panel} from './v29_components.jsx';
const API=import.meta.env.VITE_API_URL||'http://localhost:8000';
const auth=()=>({Authorization:`Bearer ${sessionStorage.getItem('VEYRA_user_token')}`});
export function V36SecurityRadarView(){
 const [data,setData]=useState(null);
 useEffect(()=>{fetch(`${API}/api/v36/security-radar`,{headers:auth()}).then(r=>r.json()).then(setData).catch(()=>{})},[]);
 return <div className="content"><div className="sectionintro"><div><div className="eyebrow">VEYRA V3.6 · SECURITY RADAR</div><h2>Security Tool & Control Radar</h2><p>Continuously scout the ecosystem, distinguish mature recommendations from experimental candidates, and promote only what passes VEYRA evidence, provenance, licensing and worker-compatibility review.</p></div></div>
 <div className="grid3"><div className="card"><small>RADAR ITEMS</small><strong style={{fontSize:22}}>{data?.recommendations?.length||0}</strong></div><div className="card"><small>RECOMMENDED</small><strong style={{fontSize:22}}>{data?.recommendations?.filter(x=>x.maturity==='recommended').length||0}</strong></div><div className="card"><small>EXPERIMENTAL</small><strong style={{fontSize:22}}>{data?.recommendations?.filter(x=>x.maturity==='experimental').length||0}</strong></div></div>
 <Panel title="Latest recommendations"><div className="table">{(data?.recommendations||[]).map(x=><div className="row" key={x.id}><div><b>{x.name}</b><small>{x.kind.toUpperCase()} · {x.source}</small><small>{x.reason}</small><small>Maps to: {x.maps_to.join(' · ')}</small></div><span className={'badge '+(x.maturity==='experimental'?'critical':'')}>{x.maturity.toUpperCase()}</span></div>)}</div></Panel>
 <div className="callout"><b>Promotion rule:</b> a radar item is not automatically executable. VEYRA requires provenance, version pinning, SBOM, license review, worker compatibility, security review and a documented UI/terminal/evidence/remediation guide before promotion into the governed tool catalog.</div></div>
}
