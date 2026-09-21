import React from 'react';
export function Panel({title,children}){return <section className="panel"><div className="panelhead"><h3>{title}</h3><span>V2.9</span></div>{children}</section>}
