"""
utils/analyzer.py
-----------------
Multi-provider AI integration for radiology report quality auditing.
Supports: Google Gemini (gemini-2.0-flash) and Groq (llama-3.3-70b-versatile).
"""

import json
import os


SYSTEM_INSTRUCTION = (
    "You are a board-certified Quality Assurance Radiologist and Clinical Audit Specialist "
    "with 20+ years of experience. Your sole task is to AUDIT and EVALUATE radiology reports "
    "for quality, completeness, and clinical accuracy. "
    "CRITICAL DIRECTIVE: Do NOT generate a new radiology report. Do NOT write diagnoses. "
    "Do NOT add findings. Your role is purely evaluative — assess the existing report and "
    "provide structured quality feedback."
)


def _build_prompt(report_text: str, modality: str, mandatory_sections: list) -> str:
    sections_str = "\n".join(f"  - {s}" for s in mandatory_sections) or "  - (none specified)"
    return f"""
Audit the following radiology report with professional clinical QA standards.

EXAMINATION TYPE / MODALITY: {modality}

MANDATORY SECTIONS TO VERIFY:
{sections_str}

REPORT CONTENT:
\"\"\"
{report_text}
\"\"\"

AUDIT TASKS:
1. Quality Score: Rate the report 0–100 based on completeness, structure, clinical terminology, and finding-impression alignment.
2. Readiness Status: Classify as exactly one of: "ready_for_approval", "minor_revision_required", or "major_revision_required".
3. Quality Breakdown: Score each dimension 0–100: completeness, terminology, clinical_alignment, formatting, impression_quality.
4. Strengths: List 2–4 specific strengths observed in the report.
5. Missing Sections: List any mandatory sections that are absent.
6. Section Audit: For each mandatory section, indicate if present (true/false) and a brief note.
7. AI Suggestions organized into 6 categories:
   - missing_sections: what is absent and why it matters
   - template_compliance: structural/format deviations
   - medical_terminology: terminology improvements
   - formatting_improvements: readability and structure fixes
   - impression_suggestions: impression/conclusion quality
   - overall_remarks: final summary advice for the radiologist
8. Overall Remarks: A concise, constructive overall summary (2–3 sentences).

Return ONLY a valid JSON object matching this EXACT schema (no markdown, no extra text):
{{
  "quality_score": <integer 0-100>,
  "score_justification": "<string>",
  "readiness_status": "<ready_for_approval | minor_revision_required | major_revision_required>",
  "quality_breakdown": {{
    "completeness": <integer 0-100>,
    "terminology": <integer 0-100>,
    "clinical_alignment": <integer 0-100>,
    "formatting": <integer 0-100>,
    "impression_quality": <integer 0-100>
  }},
  "strengths": ["<strength 1>", "<strength 2>"],
  "missing_sections_list": ["<section name>"],
  "mandatory_sections": [
    {{
      "name": "<section name>",
      "present": <true|false>,
      "details": "<brief note>"
    }}
  ],
  "ai_suggestions": {{
    "missing_sections": ["<suggestion>"],
    "template_compliance": ["<suggestion>"],
    "medical_terminology": ["<suggestion>"],
    "formatting_improvements": ["<suggestion>"],
    "impression_suggestions": ["<suggestion>"],
    "overall_remarks": ["<suggestion>"]
  }},
  "overall_remarks": "<2-3 sentence constructive summary>"
}}
"""


def _parse_json(raw: str) -> dict:
    """Attempt to parse JSON, stripping markdown fences if needed."""
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        return json.loads(cleaned.strip())


# ── Gemini provider ────────────────────────────────────────────────────────────

def _audit_with_gemini(api_key: str, prompt: str) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    return _parse_json(response.text)


# ── Groq provider ──────────────────────────────────────────────────────────────

def _audit_with_groq(api_key: str, prompt: str) -> dict:
    from groq import Groq

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.2,
        max_tokens=4096,
        response_format={"type": "json_object"},
    )
    return _parse_json(response.choices[0].message.content)


# ── Public API ─────────────────────────────────────────────────────────────────

def audit_report(
    api_key: str,
    report_text: str,
    modality: str,
    mandatory_sections: list,
    provider: str = "gemini",
) -> dict:
    """
    Audit a radiology report using the selected AI provider.

    Args:
        api_key:            API key for the chosen provider.
        report_text:        Full text of the radiology report.
        modality:           Imaging modality (e.g. 'Chest X-Ray').
        mandatory_sections: Sections to check for presence.
        provider:           'gemini' or 'groq' (default: 'gemini').

    Returns:
        Parsed JSON dict with quality score, suggestions, etc.

    Raises:
        ValueError:  If API key missing or JSON parsing fails.
        RuntimeError: On AI API errors.
    """
    # Resolve key from env if not provided
    env_map = {
        "gemini": "GEMINI_API_KEY",
        "groq":   "GROQ_API_KEY",
    }
    if not api_key:
        api_key = os.environ.get(env_map.get(provider, "GEMINI_API_KEY"), "")
    if not api_key:
        raise ValueError(
            f"API key for '{provider}' is missing. "
            f"Enter it in Settings or set {env_map.get(provider, 'API_KEY')} environment variable."
        )

    prompt = _build_prompt(report_text, modality, mandatory_sections)

    try:
        if provider == "groq":
            return _audit_with_groq(api_key, prompt)
        else:
            return _audit_with_gemini(api_key, prompt)

    except (ValueError, RuntimeError):
        raise
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse AI response as JSON: {e}")
    except Exception as e:
        raise RuntimeError(f"{provider.title()} API Error: {str(e)}")
