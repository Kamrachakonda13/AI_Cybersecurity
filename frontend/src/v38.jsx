import React,{useEffect,useState} from 'react';
import {Panel} from './v29_components.jsx';
const API=import.meta.env.VITE_API_URL||'http://localhost:8000';
const auth=()=>({Authorization:`Bearer ${sessionStorage.getItem('aegisx_user_token')}`});
export function V38PostureTimeMachineView(){
 const [d,setD]=useState(null),[h,setH]=useState(null),[dr,setDr]=useState(null),[radar,setRadar]=useState(null),[msg,setMsg]=useState('');
 const load=()=>Promise.all([
  fetch(`${API}/api/v38/posture/current`,{headers:auth()}).then(r=>r.json()),
  fetch(`${API}/api/v38/posture/history`,{headers:auth()}).then(r=>r.json()),
  fetch(`${API}/api/v38/posture/drift`,{headers:auth()}).then(r=>r.json()),
  fetch(`${API}/api/v38/ai-endpoint-radar`,{headers:auth()}).then(r=>r.json())
 ]).then(([a,b,c,e])=>{setD(a);setH(b);setDr(c);setRadar(e)}).catch(e=>setMsg(e.message));
 useEffect(()=>{load()},[]);
 const snap=async()=>{const r=await fetch(`${API}/api/v38/posture/snapshot`,{method:'POST',headers:auth()}); const j=await r.json(); setMsg(`Snapshot ${j.snapshot_id||''} captured.`); load()};
 const inv=d?.inventory?.counts||{};
 return <div className="content"><div className="sectionintro"><div><div className="eyebrow">VEYRA V3.8 · POSTURE + AI/ENDPOINT INTELLIGENCE</div><h2>Security Posture Time Machine</h2><p>Track posture over time, prove remediation, correlate endpoint release exposure, and maintain a multi-provider AI security inventory. Vendor advisories remain authoritative; AI only ranks and explains.</p></div><button className="primary" onClick={snap}>Capture snapshot</button></div>
 {msg&&<div className="callout">{msg}</div>}
 <div className="grid3"><div className="card"><small>POSTURE SCORE</small><strong style={{fontSize:22}}>{d?.current?.posture_score??'—'}</strong></div><div className="card"><small>RISK SCORE</small><strong style={{fontSize:22}}>{d?.current?.risk_score??'—'}</strong></div><div className="card"><small>AI ASSETS</small><strong style={{fontSize:22}}>{inv.ai_assets??'—'}</strong></div></div>
 <Panel title="Posture history"><div className="table">{(h?.snapshots||[]).map(x=><div className="row" key={x.snapshot_id}><div><b>{x.snapshot_id}</b><small>{x.captured_at}</small><small>SHA-256 {x.hash_sha256}</small></div><span className="badge">{x.posture_score}</span></div>)}{!h?.snapshots?.length&&<div className="empty">No snapshots yet. Capture the first baseline.</div>}</div></Panel>
 <Panel title="What changed / drift"><div className="table">{(dr?.drift?.changes||[]).map((x,i)=><div className="row" key={i}><div><b>{x.target}</b><small>{x.category} · {x.change_type}</small><small>{x.summary}</small></div><span className={'badge '+(x.severity==='HIGH'?'critical':'')}>{x.severity}</span></div>)}{dr?.drift?.status==='insufficient_history'&&<div className="empty">{dr.drift.message}</div>}</div></Panel>
 <Panel title="AI provider security radar"><div className="table">{(radar?.providers||[]).map(x=><div className="row" key={x.id}><div><b>{x.provider} — {x.release}</b><small>{x.status} · {x.security_signal}</small><small>{x.maps_to.join(' · ')}</small></div><span className="badge">AI</span></div>)}</div></Panel>
 <Panel title="Windows / macOS / Linux endpoint radar"><div className="table">{(radar?.endpoint_platforms||[]).map(x=><div className="row" key={x.platform}><div><b>{x.platform} — {x.release}</b><small>{x.status} · {x.source}</small><small>{x.signal}</small></div><span className="badge">POSTURE</span></div>)}</div></Panel>
 <div className="callout"><b>Security boundary:</b> VEYRA does not infer that a host is vulnerable merely because it runs a named OS. Endpoint agents must report supported build/package/application evidence; advisory correlation then produces an exposure determination, with evidence receipts and human-approved remediation.</div>
 </div>
}
