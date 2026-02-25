import logging
import requests
import json
import boto3
import openai
import google.generativeai as genai
from groq import Groq
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Callable, Dict, Any

from .config import settings

logger = logging.getLogger(__name__)


def _check_api_key(provider_name: str, api_key: str) -> bool:
    if not api_key or api_key == "not-set":
        logger.error(f"❌ {provider_name} API key is not configured in your .env file.")
        return False
    return True


def _check_openai() -> bool:
    logger.info("Checking OpenAI health...")
    if not _check_api_key("OpenAI", settings.openai_api_key):
        return False
    try:
        client = openai.OpenAI(api_key=settings.openai_api_key)
        client.models.list()
        logger.info("✅ OpenAI API is healthy.")
        return True
    except openai.AuthenticationError:
        logger.error("❌ OpenAI authentication failed. Please check your API key.")
        return False
    except Exception as e:
        logger.error(f"❌ An error occurred while checking OpenAI health: {e}", exc_info=False)
        return False


def _check_ollama() -> bool:
    base_url = settings.llm.ollama.base_url
    logger.info(f"Checking Ollama health at {base_url}...")
    try:
        health_check_url = base_url.removesuffix("/v1")
        response = requests.get(health_check_url, timeout=5)
        response.raise_for_status()
        if "Ollama is running" in response.text:
            logger.info("✅ Ollama service is running and accessible.")
            return True
        else:
            logger.warning(f"⚠️ Ollama is reachable, but the response was unexpected: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Could not connect to Ollama at {base_url}. Please ensure the service is running.", exc_info=False)
        return False


def _check_gemini() -> bool:
    logger.info("Checking Google Gemini health...")
    if not _check_api_key("Google Gemini", settings.google_api_key):
        return False
    try:
        genai.configure(api_key=settings.google_api_key)
        next(genai.list_models())
        logger.info("✅ Google Gemini API is healthy.")
        return True
    except Exception as e:
        logger.error(f"❌ An error occurred while checking Google Gemini health: {e}", exc_info=False)
        logger.error("Please check your Google API key and ensure the 'Generative Language API' is enabled.")
        return False


def _check_grok() -> bool:
    logger.info("Checking Groq health...")
    if not _check_api_key("Groq", settings.grok_api_key):
        return False
    try:
        client = Groq(api_key=settings.grok_api_key)
        client.models.list()
        logger.info("✅ Groq API is healthy.")
        return True
    except Exception as e:
        logger.error(f"❌ An error occurred while checking Groq health: {e}", exc_info=False)
        return False


def _get_bedrock_health_payload(model_id: str) -> Dict[str, Any]:
    """Returns a minimal health check payload based on the Bedrock model provider."""
    if "anthropic" in model_id:
        return {"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1, "messages": [{"role": "user", "content": "health"}]}
    if "amazon" in model_id:
        return {"inputText": "health", "textGenerationConfig": {"maxTokenCount": 1}}
    if "meta" in model_id:
        return {"prompt": "health", "max_gen_len": 1}
    if "cohere" in model_id:
        return {"prompt": "health", "max_tokens": 1}
    raise ValueError(f"Unsupported Bedrock model for health check: '{model_id}'. No payload available.")


def _check_bedrock() -> bool:
    logger.info("Checking AWS Bedrock health...")
    if (not settings.aws_access_key_id or settings.aws_access_key_id == "not-set") and (not settings.aws_secret_access_key or settings.aws_secret_access_key == "not-set"):
        logger.info("AWS credentials not set in .env, assuming IAM role or environment variables.")

    model_id = settings.llm.bedrock.model_id
    try:
        session = boto3.Session(
            aws_access_key_id=settings.aws_access_key_id if settings.aws_access_key_id != "not-set" else None,
            aws_secret_access_key=settings.aws_secret_access_key if settings.aws_secret_access_key != "not-set" else None,
            region_name=settings.llm.bedrock.region_name
        )
        bedrock_runtime_client = session.client('bedrock-runtime')

        payload = _get_bedrock_health_payload(model_id)
        body = json.dumps(payload)
        bedrock_runtime_client.invoke_model(body=body, modelId=model_id, contentType='application/json', accept='application/json')

        logger.info(f"✅ AWS Bedrock is healthy and model '{model_id}' is accessible.")
        return True
    except NoCredentialsError:
        logger.error("❌ AWS credentials not found. Configure via .env, environment variables, or an IAM role.")
        return False
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == 'AccessDeniedException':
            logger.error(f"❌ AWS access denied. The credentials lack 'bedrock:InvokeModel' permission for '{model_id}'.")
        elif error_code in ['ResourceNotFoundException', 'ValidationException']:
            logger.error(f"❌ AWS Bedrock model not found or invalid: '{model_id}'. Check the ID and region ('{settings.llm.bedrock.region_name}').")
        else:
            logger.error(f"❌ An AWS ClientError occurred: {e}", exc_info=False)
        return False
    except Exception as e:
        if isinstance(e, ValueError): # Catch our specific ValueError from the payload factory
            logger.error(f"❌ {e}", exc_info=False)
            return False
        logger.error(f"❌ An unexpected error occurred while checking AWS Bedrock health: {e}", exc_info=False)
        return False


_HEALTH_CHECKS: Dict[str, Callable[[], bool]] = {
    "openai": _check_openai, "ollama": _check_ollama, "gemini": _check_gemini,
    "grok": _check_grok, "bedrock": _check_bedrock,
}

def check_llm_health() -> bool:
    provider = settings.llm.provider
    logger.info(f"--- Starting LLM Health Check for provider: '{provider}' ---")
    check_function = _HEALTH_CHECKS.get(provider)
    if not (check_function and check_function()):
        logger.error(f"--- LLM Health Check for '{provider}' FAILED ---")
        return False
    logger.info(f"--- LLM Health Check for '{provider}' PASSED ---")
    return True