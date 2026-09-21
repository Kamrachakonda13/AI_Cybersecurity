import React,{useEffect,useState} from 'react';
import {Panel} from './v29_components.jsx';
const API=import.meta.env.VITE_API_URL||'http://localhost:8000';
const auth=()=>({Authorization:`Bearer ${sessionStorage.getItem('VEYRA_user_token')}`});
const get=p=>fetch(`${API}${p}`,{headers:auth()}).then(r=>{if(!r.ok)throw new Error(String(r.status));return r.json()});
export function V33SecurityReadinessView(){
 const [o,setO]=useState(null),[track,setTrack]=useState('ai-security'),[ex,setEx]=useState([]);
 useEffect(()=>{get('/api/v33/readiness/overview').then(setO).catch(()=>{})},[]);
 useEffect(()=>{get(`/api/v33/readiness/exercises?track=${encodeURIComponent(track)}`).then(j=>setEx(j.exercises||[])).catch(()=>setEx([]))},[track]);
 const cov=o?.documentation||{};
 return <div className="content"><div className="sectionintro"><div><div className="eyebrow">VEYRA V3.3 · SECURITY READINESS</div><h2>Security Readiness Center</h2><p>Measure documentation coverage, security-control maturity and repeatable team exercises before production deployment.</p></div></div>
 <div className="grid3"><div className="card"><small>TOOL DOCUMENTATION</small><strong style={{fontSize:22}}>{cov.documented_tools||0}/{cov.registered_tools||0}</strong><small>{cov.coverage_percent||0}% documented</small></div><div className="card"><small>CONTROL DOMAINS</small><strong style={{fontSize:22}}>{o?.domains?.length||0}</strong><small>identity → AI runtime → recovery</small></div><div className="card"><small>TEAM EXERCISES</small><strong style={{fontSize:22}}>{o?.exercise_count||0}</strong><small>repeatable defensive scenarios</small></div></div>
 <Panel title="Control domains"><div className="table">{(o?.domains||[]).map(d=><div className="row" key={d.id}><div><b>{d.name}</b><small>{d.description}</small></div><span className="badge">CONTROL</span></div>)}</div></Panel>
 <div className="grid2"><Panel title="Exercise library"><div style={{padding:16,display:'grid',gap:10}}><select value={track} onChange={e=>setTrack(e.target.value)}><option value="ai-security">AI Security</option><option value="soc-defender">SOC / Blue Team</option><option value="cloud-k8s">Cloud & Kubernetes</option><option value="dfir">DFIR / Malware</option></select>{ex.map(x=><div className="card" key={x.id}><b>{x.name}</b><small>{x.goal}</small><small><b>Evidence:</b> {x.evidence.join(' · ')}</small></div>)}</div></Panel><Panel title="Readiness rule"><div style={{padding:16}} className="callout"><b>Production gate:</b> every registered tool should have current help documentation; every privileged workflow should have explicit scope and approval; every AI agent should have identity, tool policy and traceability; every incident exercise should produce evidence and recovery verification.</div></Panel></div>
 {cov.missing_tools?.length?<Panel title="Missing documentation"><div className="callout">{cov.missing_tools.join(', ')}</div></Panel>:<div className="callout"><b>Documentation coverage:</b> all registered tools have an individual Markdown help page. Continue using the documentation contract whenever a tool is added or changed.</div>}
 </div>
}
