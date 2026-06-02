import os
import json
import re
import uuid
import base64
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
MODEL_PROVIDER = "openai"
MODEL_NAME = "gpt-5.2"
INSIGHTS_PROVIDER = "anthropic"
INSIGHTS_MODEL = "claude-sonnet-4-5-20250929"


def _extract_json(text: str) -> dict:
    """Best-effort extract a JSON object from LLM output."""
    if not text:
        return {}
    # try direct
    try:
        return json.loads(text)
    except Exception:
        pass
    # try fenced
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # find first { ... last }
    if "{" in text and "}" in text:
        start = text.find("{")
        end = text.rfind("}")
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            pass
    return {}


async def analyze_food_label(image_base64: str) -> dict:
    """
    Analyze a food label image and extract nutritional info.
    Returns: { name, serving_size, protein_g, salt_g, sodium_mg, calories, raw_text }
    """
    system_message = (
        "You are a precise nutritional label extractor for a recovery & wellness app. "
        "Given a food product photo or nutrition label, extract the key nutritional information. "
        "Return ONLY valid JSON, no commentary. "
        "Numeric fields must be numbers (use 0 if missing). "
        "Convert sodium to salt if needed (salt_g = sodium_mg * 2.5 / 1000). "
        "Schema: {\"name\": string, \"serving_size\": string, \"calories\": number, "
        "\"protein_g\": number, \"salt_g\": number, \"sodium_mg\": number, "
        "\"sugar_g\": number, \"fat_g\": number, \"notes\": string}"
    )
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"food-label-{uuid.uuid4()}",
        system_message=system_message,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)

    image_content = ImageContent(image_base64=image_base64)
    user_message = UserMessage(
        text="Extract the nutrition info from this food label/product. Return JSON only.",
        file_contents=[image_content],
    )
    response = await chat.send_message(user_message)
    data = _extract_json(response)
    # normalize
    return {
        "name": data.get("name") or "Unknown food",
        "serving_size": data.get("serving_size") or "",
        "calories": float(data.get("calories") or 0),
        "protein_g": float(data.get("protein_g") or 0),
        "salt_g": float(data.get("salt_g") or 0),
        "sodium_mg": float(data.get("sodium_mg") or 0),
        "sugar_g": float(data.get("sugar_g") or 0),
        "fat_g": float(data.get("fat_g") or 0),
        "notes": data.get("notes") or "",
        "raw_response": response,
    }


async def analyze_blood_test(image_base64: str) -> dict:
    """
    Generic document OCR for the Documents feature.
    Returns extracted text fields the user can save for a doctor visit.
    No medical interpretation — just OCR + light structuring.
    Keeps the same output shape for backward compatibility with the existing UI.
    """
    system_message = (
        "You are a personal document scanner for a private wellness journal app. "
        "Your job is to OCR the page and extract any clearly visible labelled values "
        "(e.g. 'Heart rate 72 bpm', 'Weight 78 kg', 'Cholesterol 4.2 mmol/L'). "
        "You DO NOT interpret, diagnose, or comment on the values. You simply transcribe what is on the page so the user can store a copy in their personal journal to take to their doctor. "
        "Return ONLY valid JSON. Schema: {"
        "\"date\": string (date on the document if visible, otherwise empty), "
        "\"lab\": string (name of issuing organisation if visible, otherwise empty), "
        "\"markers\": [ { \"name\": string, \"value\": number, \"unit\": string, \"reference_range\": string (leave empty — we do not interpret) } ], "
        "\"notes\": string (a short factual one-line transcription of the document title, e.g. 'Blood pressure log dated 12 Feb') }"
    )
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"document-scan-{uuid.uuid4()}",
        system_message=system_message,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)

    image_content = ImageContent(image_base64=image_base64)
    user_message = UserMessage(
        text="OCR this document and extract any clearly labelled values as a transcription. Do not interpret anything. Return JSON only.",
        file_contents=[image_content],
    )
    response = await chat.send_message(user_message)
    data = _extract_json(response)
    markers = data.get("markers") or []
    norm = []
    for m in markers:
        try:
            norm.append({
                "name": str(m.get("name", "")).strip(),
                "value": float(m.get("value") or 0),
                "unit": str(m.get("unit", "")).strip(),
                "reference_range": "",  # never returned to UI — we don't interpret
            })
        except Exception:
            continue
    return {
        "date": data.get("date") or "",
        "lab": data.get("lab") or "",
        "markers": norm,
        "notes": data.get("notes") or "",
        "raw_response": response,
    }


async def generate_weekly_insight(context: dict) -> str:
    """
    Generate a warm, reflective weekly summary from the user's diary + diet + meds.
    Context: { name, week_label, days_sober, diary_entries, diet_summary, missed_meds, goals_done, goals_total }
    Returns a markdown-friendly short reflection (~180-260 words).
    """
    system_message = (
        "You are a compassionate, non-clinical recovery companion writing a private weekly "
        "reflection for someone working on alcohol recovery. Tone: warm, grounded, kind, never "
        "preachy or saccharine. You speak directly to the person ('you'). You celebrate small "
        "wins concretely, gently name patterns, and offer ONE small, doable suggestion for next "
        "week — never a list of demands. Do not diagnose. Do not mention you are an AI. "
        "Output ~180-260 words in 2-3 short paragraphs. No headings, no bullet points, no emojis. "
        "Use the person's first name once near the start."
    )
    prompt = (
        "Write this week's reflection using the data below. Be specific — reference actual "
        "numbers and mood words from the data when relevant. End with one small, kind suggestion.\n\n"
        f"DATA:\n{json.dumps(context, indent=2, default=str)}"
    )
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"insight-{uuid.uuid4()}",
        system_message=system_message,
    ).with_model(INSIGHTS_PROVIDER, INSIGHTS_MODEL)
    response = await chat.send_message(UserMessage(text=prompt))
    return (response or "").strip()
