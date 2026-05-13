import os
import json
import re
import uuid
import base64
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
MODEL_PROVIDER = "openai"
MODEL_NAME = "gpt-5.2"


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
    Analyze a blood test report image and extract liver markers etc.
    Returns: { markers: [{ name, value, unit, reference_range }], date, lab, raw_text }
    """
    system_message = (
        "You are a medical lab report extractor. Given a blood test report photo or PDF page, "
        "extract relevant markers (especially liver markers like ALT/SGPT, AST/SGOT, GGT, "
        "ALP, total/direct bilirubin, albumin, INR, MCV, and any others present). "
        "Return ONLY valid JSON. Schema: {"
        "\"date\": string, \"lab\": string, "
        "\"markers\": [ { \"name\": string, \"value\": number, \"unit\": string, \"reference_range\": string } ], "
        "\"notes\": string }"
    )
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"blood-test-{uuid.uuid4()}",
        system_message=system_message,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)

    image_content = ImageContent(image_base64=image_base64)
    user_message = UserMessage(
        text="Extract all lab markers from this blood test report. Return JSON only.",
        file_contents=[image_content],
    )
    response = await chat.send_message(user_message)
    data = _extract_json(response)
    markers = data.get("markers") or []
    # normalize each marker
    norm = []
    for m in markers:
        try:
            norm.append({
                "name": str(m.get("name", "")).strip(),
                "value": float(m.get("value") or 0),
                "unit": str(m.get("unit", "")).strip(),
                "reference_range": str(m.get("reference_range", "")).strip(),
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
