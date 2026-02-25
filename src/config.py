import yaml
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Dict, Any
from . import constants

ROOT_DIR = Path(__file__).resolve().parent.parent


class OpenAISettings(BaseModel):
    model_name: str

class OllamaSettings(BaseModel):
    base_url: str
    model_name: str

class GeminiSettings(BaseModel):
    model_name: str

class GrokSettings(BaseModel):
    model_name: str

class BedrockSettings(BaseModel):
    region_name: str
    model_id: str

class MarkerSettings(BaseModel):
    workers: int = 1
    pdftext_workers: int = 1
    batch_multiplier: int = 1
    model_precision: Literal["fp32", "fp16"] = "fp32"
    exclude_images: bool = True

class LLMSettings(BaseModel):
    provider: Literal[*constants.LLM_PROVIDERS]
    openai: OpenAISettings
    ollama: OllamaSettings
    gemini: GeminiSettings
    grok: GrokSettings
    bedrock: BedrockSettings


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / '.env',
        env_file_encoding='utf-8',
        env_nested_delimiter='__',
        extra='ignore'
    )


    llm: LLMSettings
    marker: MarkerSettings


    openai_api_key: str = Field("not-set", alias="OPENAI_API_KEY")
    google_api_key: str = Field("not-set", alias="GOOGLE_API_KEY")
    grok_api_key: str = Field("not-set", alias="GROK_API_KEY")
    aws_access_key_id: str = Field("not-set", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field("not-set", alias="AWS_SECRET_ACCESS_KEY")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        def yaml_source() -> Dict[str, Any]:
            yaml_config_path = ROOT_DIR / "config.yaml"
            if not yaml_config_path.is_file():
                return {}
            try:
                with open(yaml_config_path, "r") as f:
                    return yaml.safe_load(f) or {}
            except (yaml.YAMLError, IOError) as e:
                print(f"ERROR: Could not load or parse config.yaml: {e}", file=sys.stderr)
                return {}

        return (init_settings, env_settings, dotenv_settings, yaml_source, file_secret_settings)


settings = Settings()