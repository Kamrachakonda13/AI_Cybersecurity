# Enterprise Integration

VEYRA is the enterprise control-plane shell. The Agentic RAG ingestion fabric
is retained as a separately maintained FastAPI project and is vendored here at
`integrations/agentic-rag` with Git subtree. The VEYRA adapter exposes a small
facade for service status, grounded questions, and connector visibility; it
does not import the RAG service's database or startup lifecycle.

## Local stack

Create the required secrets in `.env`, then start both applications:

```bash
AGENTIC_RAG_JWT_SECRET='use-a-local-secret' \
AGENTIC_RAG_TOKEN='service-token-issued-by-the-rag-project' \
docker compose -f docker-compose.yml -f docker-compose.enterprise.yml up --build
```

The VEYRA console remains at `http://localhost:3000`. The optional RAG service
is exposed at `http://localhost:8100`; its private databases use separate host
ports so they do not collide with VEYRA's PostgreSQL service.

Without the enterprise override, VEYRA still runs independently. The
Enterprise Intelligence view reports the RAG service as unavailable rather
than bypassing authentication or executing local tools.

## Keeping both projects independent

The companion repository remains the upstream source of truth:

```bash
git subtree pull --prefix integrations/agentic-rag \
  https://github.com/Kamrachakonda13/AgenticRAG_Ingestion_Fabric_UI_SIEMTRIAGE_Injection_firewall.git \
  main --squash
```

Develop RAG-specific changes in its original repository, merge them there,
then pull the approved revision into VEYRA. Do not edit the vendored subtree
directly unless the change is intentionally being backported to the upstream
project. This keeps standalone deployment and enterprise integration on
separate release cadences while providing one customer-facing console.

## Adapter configuration

- `AGENTIC_RAG_URL`: service URL; defaults to `http://localhost:8100`.
- `AGENTIC_RAG_TOKEN`: bearer token used only for calls to the RAG service.
- `AGENTIC_RAG_JWT_SECRET`: required by the optional RAG container stack.

High-impact VEYRA routes still use the existing admin and approval gates. The
adapter is intentionally fail-closed when the service token is missing.