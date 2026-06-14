import os
import json
import anthropic

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY environment variable not set.")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


_SYSTEM_PROMPT = """\
You are a senior commercial contracts attorney and AI compliance engine at a B2B software company.
You analyze customer redlines against historical precedents and internal policy.
You always respond with valid JSON only — no markdown, no explanation outside the JSON object.
"""

_USER_TEMPLATE = """\
CUSTOMER REDLINE (clause submitted by the customer for review):
{customer_clause}

HISTORICAL PRECEDENTS (retrieved from our signed contract database):
{precedents_block}

COMPANY POLICY:
{company_policy}

Evaluate the customer redline. Return ONLY a JSON object with these exact keys:
{{
  "match_category": "<Exact Match | Modified Precedent | New Phrasing>",
  "policy_violation": <true | false>,
  "explanation": "<2-4 sentences on the commercial/legal risk and how it compares to precedent>",
  "suggested_counter": "<pre-approved fallback clause language the company should propose>"
}}
"""


def analyze_redline(
    customer_clause: str,
    matched_precedents: list[dict],
    company_policy: str,
) -> dict:
    if matched_precedents:
        precedents_block = "\n\n---\n\n".join(
            f"[Precedent {i+1} | Contract: {p['contract_id']} | Similarity: {p['similarity']:.0%}]\n{p['text']}"
            for i, p in enumerate(matched_precedents)
        )
    else:
        precedents_block = "No historical precedents found in database."

    user_message = _USER_TEMPLATE.format(
        customer_clause=customer_clause,
        precedents_block=precedents_block,
        company_policy=company_policy,
    )

    client = _get_client()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()
    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)
