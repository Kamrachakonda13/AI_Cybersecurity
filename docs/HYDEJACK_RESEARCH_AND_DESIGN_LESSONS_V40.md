# Hydejack investigation — what VEYRA should learn

## Finding

Hydejack is **not a cybersecurity or agent-security tool**. It is an open-source Jekyll publishing theme aimed at hackers, nerds and academics. Its value to VEYRA is primarily in knowledge presentation and durable documentation UX.

## Useful design lessons

- Markdown-first authoring keeps technical knowledge portable.
- Strong headings make long technical documents navigable and TOC-friendly.
- Syntax-highlighted code blocks improve runbook usability.
- Search, categories and tags reduce time-to-information.
- Dark mode and responsive layouts suit security operations users.
- Print/PDF-friendly presentation matters for assessments, evidence packages and training.
- Static/semantic HTML makes documentation durable and accessible.
- Portfolio-style project pages can turn VEYRA research into reusable case studies.
- Offline/static publishing is valuable for incident-response environments without internet access.

VEYRA v4.0 therefore adds a Documentation Hub rather than embedding Hydejack itself into the SaaS runtime. This preserves the React application architecture while adopting the strongest documentation ideas.
