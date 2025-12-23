import json
import re
from typing import Any

from app.core.config import settings

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def _fallback_split_goals(text: str) -> list[str]:
    # Split on "Goal 1:" patterns, semicolons, and new lines
    cleaned = re.sub(r"Goal\s*\d+\s*:\s*", "\n", text, flags=re.IGNORECASE)
    raw = cleaned.replace(";", "\n").splitlines()
    goals = [g.strip(" -•\t") for g in raw if g.strip()]
    return goals[:25]



def extract_goals(text: str) -> list[str]:
    if not settings.OPENAI_API_KEY or OpenAI is None:
        return _fallback_split_goals(text)

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""
You are helping an admin extract individual staff goals from messy text.
Return ONLY valid JSON in this format:
{{"goals":[{{"text":"..."}}]}}

Rules:
- Split combined paragraphs into separate goals when possible.
- Each goal should be one clear sentence or short phrase.
- Do not include numbering or bullets in the text.

INPUT:
{text}
""".strip()

    resp = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "Return only valid JSON. No extra text."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    content = resp.choices[0].message.content or ""
    try:
        data = json.loads(content)
        goals = [g["text"].strip() for g in data.get("goals", []) if g.get("text")]
        return [g for g in goals if g][:25]
    except Exception:
        return _fallback_split_goals(text)


def suggest_alignment(goal_text: str, catalog: list[dict[str, Any]]) -> tuple[str | None, float | None]:
    """
    catalog items should look like: {"code": "A1", "title": "...", "description": "..."}
    returns (suggested_code, confidence)
    """
    if not settings.OPENAI_API_KEY or OpenAI is None:
        return None, None

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    catalog_compact = [
        {"code": c["code"], "title": c.get("title", ""), "description": c.get("description", "")}
        for c in catalog
    ]

    prompt = f"""
Match this personal goal to the best strategic goal code.
Return ONLY valid JSON: {{"code":"A1","confidence":0.0}}

Personal goal:
{goal_text}

Strategic goal catalog:
{json.dumps(catalog_compact)}
""".strip()

    resp = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "Return only valid JSON. No extra text."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    content = resp.choices[0].message.content or ""
    try:
        data = json.loads(content)
        code = data.get("code")
        conf = data.get("confidence")
        return (code, float(conf) if conf is not None else None)
    except Exception:
        return None, None
