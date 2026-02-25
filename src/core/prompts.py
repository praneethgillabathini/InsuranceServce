from pathlib import Path
import logging

logger = logging.getLogger(__name__)

MAPPING_FILE_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "insurance_fhir_mapping.json"


def _load_mapping_template() -> str:
    if not MAPPING_FILE_PATH.exists():
        error_msg = f"CRITICAL: Cannot find JSON schema at {MAPPING_FILE_PATH.resolve()}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    with open(MAPPING_FILE_PATH, "r") as f:
        return f.read()


_ANNOTATED_JSON_TEMPLATE = _load_mapping_template()

SYSTEM_PROMPT_FHIR = f"""
You are an expert in healthcare data and FHIR (Fast Healthcare Interoperability Resources).
Your task is to analyze the provided markdown text extracted from an Indian health insurance claim PDF.

Extract the relevant information and map it EXACTLY to the JSON structure provided below. 
You MUST NOT invent new JSON keys, group data under new headers, or change the schema.

Rules:
1. Output ONLY the raw JSON object. Do not include any explanations or markdown fences.
2. Replace the instruction text inside the template values with the summarised data extracted from the document.
3. If any field or data is not found in the text, set it to an empty string "" or an empty array [] as appropriate. Do not omit the keys.

<expected_json_schema>
{_ANNOTATED_JSON_TEMPLATE}
</expected_json_schema>

Now analyze the markdown text below and return the JSON object:
"""