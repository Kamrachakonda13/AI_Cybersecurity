"""
Phase 8.4 — LLM triage for SIEM incidents.

Given an Incident, ask the LLM to:
  1. Classify it as ESCALATE or SUPPRESS
  2. Give a confidence score in [0.0, 1.0]
  3. Write a one-sentence reason

Design:
  - Grounded prompt: the LLM sees a compact incident summary, not the
    raw alert stream. Size-limited so a large incident doesn't blow
    the token budget.
  - Deterministic output schema: JSON with keys `decision`,
    `confidence`, `reason`.
  - Reuses src/confidence.py for the terminal gate (Phase 5 primitive).
  - Reuses src/generate.py for the LLM call (Phase 3 primitive).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional

from src.siem_correlate import Incident


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a senior SOC analyst triaging security alerts.
You will receive a correlated incident — a group of alerts sharing an
entity and a short time window.

Your job: decide whether this incident should be ESCALATED (sent to a
human analyst) or SUPPRESSED (marked as a false positive).

Decision guidance:
- ESCALATE if the incident contains HIGH or CRITICAL severity alerts
  AND the pattern is consistent with real attacker behavior.
- SUPPRESS if the incident is dominated by LOW severity alerts, or if
  the pattern is clearly benign (admin activity, scheduled jobs,
  patching, known-good service accounts).
- A cluster of many unrelated rules on one host is not automatically
  malicious — but a cluster of related rules is.

Respond with a JSON object ONLY. No prose. Format:
{
  "decision": "ESCALATE" | "SUPPRESS",
  "confidence": 0.0 to 1.0,
  "reason": "one sentence, no more than 200 characters"
}
"""


def _format_alert_brief(alert, full: bool) -> str:
    if full:
        # Compact: one line per alert. Drop raw dict to stay well under
        # Groq free-tier TPM limit (8,000). ~400 tokens/prompt vs ~1,500.
        return (
            f"  - [{alert.severity}] {alert.rule_id} {alert.rule_name} "
            f"({alert.source}, {alert.timestamp.isoformat()})"
        )
    else:
        return f"  - [{alert.severity}] {alert.rule_id} {alert.rule_name} ({alert.source})"


SEVERITY_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}

# Hard severity floors — never suppress at or above these unless the
# LLM is confident enough.
SUPPRESS_CONFIDENCE_FLOOR = {
    "CRITICAL": 1.01,   # effectively "never suppress"
    "HIGH":     0.90,
    "MEDIUM":   0.75,
    "LOW":      0.00,
}



def build_incident_prompt(incident: Incident, top_n_full: int = 3) -> str:
    """Build the user-facing prompt for one incident."""
    alerts_sorted = sorted(incident.alerts, key=lambda a: -SEVERITY_RANK[a.severity])
    top = alerts_sorted[:top_n_full]
    rest = alerts_sorted[top_n_full:]

    lines = []
    lines.append(f"Incident {incident.incident_id}")
    lines.append(f"Primary host: {incident.primary_entity.get('host')}")
    lines.append(f"Primary user: {incident.primary_entity.get('user')}")
    lines.append(f"Time window: {incident.window_start.isoformat()} → {incident.window_end.isoformat()}")
    lines.append(f"Alert count: {incident.size}")
    lines.append(f"Sources: {', '.join(sorted(incident.sources))}")
    lines.append(f"Max severity: {incident.severity}")
    lines.append("")
    lines.append(f"Top {len(top)} alerts (detail):")
    for a in top:
        lines.append(_format_alert_brief(a, full=True))
    if rest:
        lines.append("")
        lines.append(f"Remaining {len(rest)} alerts (summary):")
        for a in rest:
            lines.append(_format_alert_brief(a, full=False))
    lines.append("")
    lines.append("Return the JSON decision now.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output parsing
# ---------------------------------------------------------------------------
@dataclass
class TriageDecision:
    decision: str          # "ESCALATE" or "SUPPRESS"
    confidence: float
    reason: str
    raw_response: str = ""

    @property
    def is_escalate(self) -> bool:
        return self.decision == "ESCALATE"


_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_decision(text: str) -> Optional[TriageDecision]:
    """Parse the LLM output into a TriageDecision. Returns None on failure."""
    m = _JSON_RE.search(text)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None

    decision = str(obj.get("decision", "")).upper()
    if decision not in ("ESCALATE", "SUPPRESS"):
        return None

    try:
        conf = float(obj.get("confidence", 0.0))
    except (TypeError, ValueError):
        conf = 0.0
    conf = max(0.0, min(1.0, conf))

    reason = str(obj.get("reason", ""))[:200]

    return TriageDecision(
        decision=decision,
        confidence=conf,
        reason=reason,
        raw_response=text,
    )


# ---------------------------------------------------------------------------
# LLM call — reuse src.generate
# ---------------------------------------------------------------------------
def _call_llm(prompt: str) -> str:
    """
    Direct Groq call for triage.

    Triage is a classification task, not grounded Q&A — so we build our
    own prompt and call Groq directly, then record tokens via the same
    metrics primitive that src.generate uses.
    """
    import os
    from groq import Groq
    from dotenv import load_dotenv

    from src.metrics import record_llm_call

    load_dotenv()   # ensure .env is loaded in this process
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.startswith("placeholder"):
        raise RuntimeError("GROQ_API_KEY not set")

    client = Groq(api_key=api_key)
    model = os.getenv("SIEM_TRIAGE_MODEL", "openai/gpt-oss-20b")

    import time as _time
    from groq import RateLimitError as _RateLimit

    last_exc = None
    response = None
    for attempt in range(1, 4):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            break
        except _RateLimit as e:
            last_exc = e
            wait = 60 * attempt
            print(f"  [rate-limit] attempt {attempt}/3, sleeping {wait}s...")
            _time.sleep(wait)
    if response is None:
        raise last_exc or RuntimeError("LLM call failed after retries")

    # Record tokens in metrics (best-effort)
    try:
        usage = response.usage
        if usage:
            record_llm_call(
                model=model,
                prompt_tokens=getattr(usage, "prompt_tokens", 0),
                completion_tokens=getattr(usage, "completion_tokens", 0),
                tool="siem_triage",
            )
    except Exception:
        pass

    return response.choices[0].message.content or ""

def triage_incident(incident: Incident, *, top_n_full: int = 3) -> TriageDecision:
    """
    Triage a single incident. Returns a TriageDecision (never None —
    parse failures default to ESCALATE at low confidence as a fail-safe).
    """
    prompt = build_incident_prompt(incident, top_n_full=top_n_full)
    full_prompt = SYSTEM_PROMPT + "\n\n" + prompt

    try:
        text = _call_llm(full_prompt)
    except Exception as e:
        # Fail safe: if the LLM is unreachable, escalate with low confidence
        return TriageDecision(
            decision="ESCALATE",
            confidence=0.0,
            reason=f"LLM unavailable: {type(e).__name__}",
            raw_response="",
        )

    decision = parse_decision(text)
    if decision is None:
        return TriageDecision(
            decision="ESCALATE",
            confidence=0.0,
            reason="Parse failure — defaulting to escalate",
            raw_response=text,
        )

    # --- Severity floor: override SUPPRESS if the incident is too severe ---
    if decision.decision == "SUPPRESS":
        floor = SUPPRESS_CONFIDENCE_FLOOR.get(incident.severity, 0.0)
        if decision.confidence < floor:
            return TriageDecision(
                decision="ESCALATE",
                confidence=decision.confidence,
                reason=(
                    f"[severity floor] {incident.severity} incident; "
                    f"LLM suppress confidence {decision.confidence:.2f} "
                    f"below floor {floor:.2f}. Original: {decision.reason}"
                )[:200],
                raw_response=decision.raw_response,
            )

    return decision


if __name__ == "__main__":
    from src.siem_ingest import load_alerts
    from src.siem_correlate import correlate

    incidents = correlate(load_alerts())
    print(f"Loaded {len(incidents)} incidents")
    print()
    print("=== Building prompt for the largest incident (no LLM call yet) ===")
    largest = max(incidents, key=lambda i: i.size)
    print(build_incident_prompt(largest))
