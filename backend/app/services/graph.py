"""VEYRA v1.2 Security Graph.

Builds an in-memory directed graph from persisted telemetry:
  Assets, Services, Identities, Sessions, NetworkFlows, CloudResources, AIAssets, Findings.

Nodes: asset:<id>, identity:<username>, cloud:<resource_id>, ai:<name>, internet
Edges carry: relation, explanation.

Attack-path = BFS from internet-exposed entry points to sensitive data nodes
(sensitive = criticality 5 assets, vector-db, high data_sensitivity findings,
 public cloud storage / vaults, internal AI vector stores).
"""
from collections import deque


def _asset_node(a):
    """Canonical graph key for an asset row (`asset:<id>`). Used by every edge builder below."""
    return f"asset:{a.id}"


def build_graph(db):
    """Compile DB telemetry into `{nodes, edges}`.

    Reads (in order): Asset → Service → Identity → SessionEvent → NetworkFlow →
    CloudResource → AIAsset → Finding. Depends on: a live `Session` (routes pass
    the request session; tests build their own). Pure read — never writes.
    Consumed by: `attack_paths`, `answer_question`, `GET /api/graph`.
    """
    from ..models import Asset, Service, Identity, SessionEvent, NetworkFlow, CloudResource, AIAsset, Finding

    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def add_node(key, **attrs):
        nodes.setdefault(key, {"id": key, **attrs})

    def add_edge(src, dst, relation, detail=""):
        edges.append({"src": src, "dst": dst, "relation": relation, "detail": detail})

    add_node("internet", kind="internet", label="Internet")

    assets = db.query(Asset).all()
    by_id = {a.id: a for a in assets}
    for a in assets:
        key = _asset_node(a)
        sensitive = bool(a.criticality >= 5 or a.asset_type in ("vector-db", "database"))
        add_node(key, kind="asset", label=a.hostname, ip=a.ip_address,
                 asset_type=a.asset_type, criticality=a.criticality,
                 external_exposure=a.external_exposure, sensitive=sensitive)
        if a.external_exposure:
            add_edge("internet", key, "exposes",
                     f"{a.hostname} is internet-facing ({a.ip_address})")

    for s in db.query(Service).all():
        a = by_id.get(s.asset_id)
        if not a:
            continue
        svc = f"service:{s.id}"
        add_node(svc, kind="service", label=f"{a.hostname}:{s.port}",
                 port=s.port, process=s.process, user=s.user, expected=s.expected)
        add_edge(_asset_node(a), svc, "listens",
                 f"{s.process} as {s.user} on {s.port}/{s.protocol}"
                 + ("" if s.expected else " [UNEXPECTED]"))
        if not s.expected:
            add_edge(svc, _asset_node(a), "risks",
                     f"Unexpected {s.service} owned by {s.user} (PID {s.pid})")

    for ident in db.query(Identity).all():
        key = f"identity:{ident.username}"
        add_node(key, kind="identity", label=ident.username,
                 privilege=ident.privilege, mfa=ident.mfa_enabled,
                 identity_type=ident.identity_type)

    for se in db.query(SessionEvent).all():
        # identity -> asset : authenticated session
        src = f"identity:{se.username}"
        if src not in nodes:
            add_node(src, kind="identity", label=se.username)
        if se.asset_id and se.asset_id in by_id:
            dst = _asset_node(by_id[se.asset_id])
            add_edge(src, dst, "session",
                     f"{se.username} -> {by_id[se.asset_id].hostname} via {se.application} "
                     f"({se.auth_method})" + (" [PRIVILEGED]" if se.privileged else ""))

    for f in db.query(NetworkFlow).all():
        src = _asset_node(by_id[f.src_asset_id]) if f.src_asset_id in by_id else "internet" if f.src_ip else "unknown"
        dst = _asset_node(by_id[f.dst_asset_id]) if f.dst_asset_id in by_id else f"external:{f.dst_ip}"
        if dst.startswith("external:") and dst not in nodes:
            add_node(dst, kind="external", label=f.dst_ip)
        if src not in nodes:
            add_node(src, kind="external", label=str(src))
        add_edge(src, dst, "flow",
                 f"{f.src_ip} -> {f.dst_ip}:{f.dst_port}/{f.protocol} risk={f.risk_score}")

    for c in db.query(CloudResource).all():
        key = f"cloud:{c.resource_id}"
        add_node(key, kind="cloud", label=c.resource_id, provider=c.provider,
                 resource_type=c.resource_type, public=c.public_exposure,
                 risk=c.risk_score, sensitive=True)
        if c.public_exposure:
            add_edge("internet", key, "exposes", f"Public {c.resource_type}: {c.misconfiguration}")

    for ai in db.query(AIAsset).all():
        key = f"ai:{ai.name}"
        add_node(key, kind="ai", label=ai.name, asset_type=ai.asset_type,
                 exposure=ai.exposure, risk=ai.risk_score, sensitive=True)
        if ai.exposure == "internet":
            add_edge("internet", key, "exposes", f"Internet-facing {ai.asset_type}")
        # AI gateway reads vector store: heuristic link by naming/provider
        if ai.asset_type == "vector database":
            for other in db.query(AIAsset).all():
                if other.asset_type in ("AI application", "agent") and other.name != ai.name:
                    add_edge(f"ai:{other.name}", key, "retrieves",
                             f"{other.name} can retrieve data from {ai.name}")

    for fin in db.query(Finding).all():
        if fin.asset_id in by_id:
            add_edge(f"finding:{fin.id}" if f"finding:{fin.id}" in nodes else _asset_node(by_id[fin.asset_id]),
                     _asset_node(by_id[fin.asset_id]), "finding", fin.title)

    # Link AI assets to underlying infra assets by owner/type heuristic
    # (keeps graph connected for attack-path demo without new FKs)
    return {"nodes": nodes, "edges": edges}


def _adjacency(edges):
    """Index edges by source node for BFS. Depends on: edge dicts from `build_graph`."""
    adj: dict[str, list[dict]] = {}
    for e in edges:
        adj.setdefault(e["src"], []).append(e)
    return adj


def _is_sensitive(nodes, key):
    """True when a node is a data-crown-jewel: explicit `sensitive` flag, any cloud/AI node, or C5 asset."""
    n = nodes.get(key, {})
    if n.get("sensitive"):
        return True
    if n.get("kind") in ("cloud", "ai"):
        return True
    if n.get("kind") == "asset" and (n.get("criticality", 0) >= 5):
        return True
    return False


def attack_paths(db, max_paths=5, max_depth=6):
    """BFS from 'internet' to sensitive nodes. Returns list of {target, path}.

    Depends on: `build_graph` + `_adjacency` + `_is_sensitive`. Cycle-safe
    (never revisits a node in one path), one path per target. Served by
    `GET /api/graph/attack-path`; covered by `test_v12.py`.
    """
    g = build_graph(db)
    nodes, edges = g["nodes"], g["edges"]
    adj = _adjacency(edges)
    targets = [k for k in nodes if k != "internet" and _is_sensitive(nodes, k)]

    paths = []
    q = deque([["internet"]])
    seen_targets: set[str] = set()
    while q and len(paths) < max_paths:
        path = q.popleft()
        cur = path[-1]
        if cur in targets and len(path) > 1 and cur not in seen_targets:
            seen_targets.add(cur)
            steps = []
            for i in range(len(path) - 1):
                rel = next((e for e in edges if e["src"] == path[i] and e["dst"] == path[i + 1]), {})
                steps.append({"from": path[i], "to": path[i + 1],
                              "relation": rel.get("relation", "connected"),
                              "detail": rel.get("detail", "")})
            paths.append({"target": cur,
                          "target_label": nodes[cur].get("label", cur),
                          "length": len(path) - 1, "steps": steps})
            continue
        if len(path) - 1 >= max_depth:
            continue
        for e in adj.get(cur, []):
            if e["dst"] not in path:  # avoid cycles
                q.append(path + [e["dst"]])
    # Production hardening: per-path risk (max finding risk on target, else node
    # risk, else 50) + choke-point ranking (nodes on >1 path = fix-first targets).
    frisks: dict[str, float] = {}
    from ..models import Finding
    for fin in db.query(Finding).all():
        key = f"asset:{fin.asset_id}"
        frisks[key] = max(frisks.get(key, 0), fin.risk_score or 0)
    for p in paths:
        node_risk = nodes[p["target"]].get("risk")
        p["risk"] = frisks.get(p["target"],
                               node_risk if isinstance(node_risk, (int, float)) else 50)
    from collections import Counter
    cnt: Counter = Counter()
    for p in paths:
        for s in p["steps"]:
            for k in (s["from"], s["to"]):
                if k != "internet":
                    cnt[k] += 1
    chokepoints = [{"node": k, "label": nodes[k].get("label", k), "paths": c}
                   for k, c in cnt.most_common(5) if c > 1]
    return {"paths": paths, "sensitive_targets": len(targets), "chokepoints": chokepoints}


def answer_question(db, kind: str):
    """Pre-canned correlation answers for the 6 flagship questions.

    `kind` is one of: internet_to_data | connection_owner | port_owner |
    privileged_access | ai_data_access | cloud_exposure. Served by
    `GET /api/graph/answer`; each branch reads only the tables it needs.
    """
    from ..models import Asset, Service, Identity, SessionEvent, NetworkFlow, CloudResource, AIAsset

    assets = {a.id: a for a in db.query(Asset).all()}
    if kind == "internet_to_data":
        exposed = [a for a in assets.values() if a.external_exposure]
        flows = db.query(NetworkFlow).all()
        out = []
        for a in exposed:
            hops = [f for f in flows if f.src_asset_id == a.id]
            for h in hops:
                dst = assets.get(h.dst_asset_id)
                out.append({"entry": a.hostname, "entry_ip": a.ip_address,
                            "via": f"{h.src_ip}->{h.dst_ip}:{h.dst_port}",
                            "reaches": dst.hostname if dst else h.dst_ip,
                            "reaches_sensitive": bool(dst and (dst.criticality >= 5 or dst.asset_type in ("vector-db", "database")))})
        return out
    if kind == "connection_owner":
        rows = db.query(SessionEvent).order_by(SessionEvent.anomaly_score.desc()).limit(20).all()
        return [{"username": r.username, "application": r.application, "source_ip": r.source_ip,
                 "asset": assets[r.asset_id].hostname if r.asset_id in assets else None,
                 "privileged": r.privileged, "anomaly": r.anomaly_score} for r in rows]
    if kind == "port_owner":
        rows = db.query(Service).all()
        return [{"host": assets[r.asset_id].hostname if r.asset_id in assets else r.asset_id,
                 "port": r.port, "service": r.service, "process": r.process,
                 "pid": r.pid, "user": r.user, "expected": r.expected} for r in rows]
    if kind == "privileged_access":
        return [{"username": i.username, "privilege": i.privilege,
                 "mfa": i.mfa_enabled, "type": i.identity_type, "owner": i.owner}
                for i in db.query(Identity).filter(Identity.privilege >= 4).all()]
    if kind == "ai_data_access":
        return [{"name": a.name, "type": a.asset_type, "exposure": a.exposure,
                 "risk": a.risk_score} for a in db.query(AIAsset).all()]
    if kind == "cloud_exposure":
        return [{"resource": c.resource_id, "type": c.resource_type, "provider": c.provider,
                 "public": c.public_exposure, "issue": c.misconfiguration, "risk": c.risk_score}
                for c in db.query(CloudResource).all()]
    return []
