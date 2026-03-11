"""AI engine for generating executive summaries from sales data."""

import asyncio
import json
import logging
import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a senior business analyst AI. You will receive structured sales data and statistics.
Produce a professional executive summary suitable for C-level stakeholders. Your summary MUST include:

1. **Revenue Overview** — Total revenue, trends, and key financial highlights.
2. **Top Performing Regions** — Identify the strongest regions and explain why.
3. **Product Performance** — Compare product categories, highlight bestsellers and underperformers.
4. **Anomalies & Concerns** — Flag any unusual patterns, outliers, or data quality issues.
5. **Strategic Recommendations** — Actionable insights for the sales leadership.

Format with clear headings and bullet points. Keep the tone professional and data-driven.
Limit the summary to roughly 400–600 words."""


async def generate_summary(parsed_data: dict) -> str:
    """Generate an AI executive summary from parsed sales data."""
    settings = get_settings()

    user_prompt = _build_user_prompt(parsed_data)

    if settings.AI_PROVIDER == "groq":
        return await _call_groq(user_prompt)
    elif settings.AI_PROVIDER == "gemini":
        return await _call_gemini(user_prompt)
    else:
        raise ValueError(f"Unsupported AI provider: {settings.AI_PROVIDER}")


def _build_user_prompt(parsed_data: dict) -> str:
    """Build the user prompt with sales data context (size-capped to avoid token limits)."""
    stats = parsed_data.get("stats", {})
    # Only send essential stats — drop large nested breakdowns beyond top 5 entries
    compact_stats: dict = {
        "primary_numeric_col": stats.get("primary_numeric_col", ""),
        "primary_total": stats.get("primary_total", 0),
        "numeric_summary": stats.get("numeric_summary", {}),
    }
    breakdowns = stats.get("breakdowns", {})
    compact_breakdowns = {}
    for cat, vals in list(breakdowns.items())[:4]:  # max 4 categories
        sorted_vals = sorted(vals.items(), key=lambda x: x[1], reverse=True)[:8]  # top 8
        compact_breakdowns[cat] = dict(sorted_vals)
    compact_stats["breakdowns"] = compact_breakdowns

    stats_json = json.dumps(compact_stats, indent=2, default=str)
    raw_text = parsed_data.get("raw_text", "No raw data available.")
    # Hard cap raw_text to 1500 chars
    if len(raw_text) > 1500:
        raw_text = raw_text[:1500] + "\n... (truncated)"

    return f"""Analyze the following data and generate an executive summary.

## Dataset Info
- Rows: {parsed_data.get('rows', 'N/A')}
- Columns: {', '.join(parsed_data.get('columns', []))}

## Key Statistics
{stats_json}

## Data Sample
{raw_text}

Generate a professional executive summary now."""


async def _call_groq(user_prompt: str) -> str:
    """Call the Groq API (OpenAI-compatible)."""
    settings = get_settings()

    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured.")

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    MODELS_TO_TRY = [settings.GROQ_MODEL, "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

    async with httpx.AsyncClient(timeout=120.0) as client:
        for model in MODELS_TO_TRY:
            payload["model"] = model
            last_error = None
            for attempt in range(3):
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if response.status_code == 429:
                    wait = (attempt + 1) * 15
                    logger.warning("Groq rate limited on %s (429), retrying in %ds (attempt %d/3)", model, wait, attempt + 1)
                    last_error = response
                    await asyncio.sleep(wait)
                    continue
                response.raise_for_status()
                data = response.json()
                logger.info("Groq summary generated with model %s", model)
                return data["choices"][0]["message"]["content"]
            logger.warning("All retries failed for model %s, trying next model", model)

        last_error.raise_for_status()


async def _call_gemini(user_prompt: str) -> str:
    """Call the Google Gemini API."""
    settings = get_settings()

    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured.")

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
    )
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048},
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    summary = data["candidates"][0]["content"]["parts"][0]["text"]
    logger.info("Gemini summary generated (%d chars)", len(summary))
    return summary
