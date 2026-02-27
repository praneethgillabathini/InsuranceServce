from fastapi import APIRouter, UploadFile, File, Depends, Request, Form
from fastapi.responses import JSONResponse
from ..core.pdf_processor import PDFProcessor
from src.services.llm.llm_service import LLMService
from src.services.fhir.insurance_plan_fhir_mapper import InsurancePlanFHIRMapper
from ..core import prompts
from ..services.policy_pruner import PolicyPruner
from src.health_check import check_llm_health
import tempfile
import os
import json
import asyncio
import re
from .. import constants
import logging

router = APIRouter()
pruner = PolicyPruner()
logger = logging.getLogger(__name__)

_JSON_MARKDOWN_REGEX = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.DOTALL)


def _clean_and_parse_llm_response(llm_response: str) -> dict:
    parsable_string = llm_response.strip()
    match = _JSON_MARKDOWN_REGEX.search(parsable_string)
    if match:
        parsable_string = match.group(1).strip()
    try:
        return json.loads(parsable_string)
    except json.JSONDecodeError as e:
        logger.error(constants.LOG_LLM_JSON_DECODE_FAILED.format(raw_response=llm_response))
        raise ValueError(constants.ERROR_MESSAGE_LLM_INVALID_JSON) from e


def get_pdf_processor(request: Request) -> PDFProcessor:
    return request.app.state.pdf_processor


def get_llm_service(request: Request) -> LLMService:
    return request.app.state.llm_service


@router.post("/process", tags=["Insurance Processing"])
async def process_insurance_claim(
    file: UploadFile = File(...),
    generate_fhir: bool = Form(True, description="Set to true to generate FHIR bundle, false to return cleaned JSON"),
    pdf_processor: PDFProcessor = Depends(get_pdf_processor),
    llm_service: LLMService = Depends(get_llm_service),
) -> JSONResponse:
    temp_pdf_path = None
    logger.info(constants.LOG_CLAIM_PROCESS_REQUEST)
    try:
        if file.content_type != "application/pdf":
            logger.warning(constants.LOG_INVALID_FILE_TYPE_RECEIVED.format(content_type=file.content_type, filename=file.filename))
            return JSONResponse(
                content={"error": {"code": constants.ERROR_CODE_INVALID_FILE_TYPE, "message": constants.ERROR_MESSAGE_INVALID_FILE_TYPE}},
                status_code=400
            )

        if not check_llm_health():
            return JSONResponse(
                content={"error": {"code": constants.ERROR_MESSAGE_LLM_OFFLINE, "message": constants.ERROR_MESSAGE_LLM_FAILED}},
                status_code=400
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(await file.read())
            temp_pdf_path = temp_pdf.name
        logger.info(constants.LOG_UPLOADED_FILE_SAVED.format(filename=file.filename, temp_path=temp_pdf_path))

        logger.info(constants.LOG_PDF_CONVERSION_START.format(temp_path=temp_pdf_path))
        loop = asyncio.get_running_loop()
        markdown_text = await loop.run_in_executor(None, pdf_processor.convert_to_markdown, temp_pdf_path)
        logger.info(constants.LOG_PDF_CONVERSION_SUCCESS.format(length=len(markdown_text)))

        clean_markdown = pruner.prune(markdown_text)
        logger.info(constants.LOG_LLM_SENDING_MARKDOWN.format(service_name=llm_service.__class__.__name__))
        full_llm_response = await llm_service.process_text(
            system_prompt=prompts.SYSTEM_PROMPT_FHIR, user_prompt=clean_markdown
        )
        logger.info(constants.LOG_LLM_RESPONSE_RECEIVED)

        cleaned_json = _clean_and_parse_llm_response(full_llm_response)
        response_payload = {"extracted_data": cleaned_json}
        logger.info(cleaned_json)

        if generate_fhir:
            logger.info(constants.LOG_CLAIM_GENERATING_FHIR)
            mapper = InsurancePlanFHIRMapper(cleaned_json)
            response_payload["fhir_bundle"] = mapper.generate_dict()

        return JSONResponse(content=response_payload, status_code=200)

    except Exception as e:
        logger.exception(constants.LOG_CLAIM_PROCESS_ERROR)
        return JSONResponse(
            content={"error": {"code": constants.ERROR_CODE_PROCESSING_ERROR, "message": f"{constants.ERROR_MESSAGE_PROCESSING_ERROR} Details: {e}"}},
            status_code=400
        )
    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            logger.info(constants.LOG_CLEANING_TEMP_FILE.format(temp_path=temp_pdf_path))
            os.remove(temp_pdf_path)


@router.post("/generate-fhir", tags=["Insurance Processing"])
async def generate_fhir_from_json(payload: dict) -> JSONResponse:
    try:
        mapper = InsurancePlanFHIRMapper(payload)
        fhir_bundle = mapper.generate_dict()
        return JSONResponse(content=fhir_bundle, status_code=200)
    except Exception as e:
        logger.exception(constants.LOG_CLAIM_FHIR_MAP_FAILED)
        return JSONResponse(
            content={"error": {"code": constants.ERROR_CODE_FHIR_MAPPING_ERROR, "message": constants.ERROR_MESSAGE_FHIR_MAPPING.format(error=str(e))}},
            status_code=400
        )


@router.post("/extract-only", tags=["Insurance Processing"])
async def extract_data_only(
    file: UploadFile = File(...),
    pdf_processor: PDFProcessor = Depends(get_pdf_processor),
    llm_service: LLMService = Depends(get_llm_service),
) -> JSONResponse:
    temp_pdf_path = None
    try:
        if file.content_type != "application/pdf":
            return JSONResponse(
                content={"error": {"code": constants.ERROR_CODE_INVALID_FILE_TYPE, "message": constants.ERROR_MESSAGE_INVALID_FILE_TYPE}},
                status_code=400
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            temp_pdf_path = tmp.name

        loop = asyncio.get_running_loop()
        markdown_text = await loop.run_in_executor(None, pdf_processor.convert_to_markdown, temp_pdf_path)
        clean_markdown = pruner.prune(markdown_text)

        full_llm_response = await llm_service.process_text(
            system_prompt=prompts.SYSTEM_PROMPT_FHIR, user_prompt=clean_markdown
        )
        extracted = _clean_and_parse_llm_response(full_llm_response)

        return JSONResponse(content={"extracted_data": extracted}, status_code=200)

    except Exception as e:
        logger.exception(constants.LOG_CLAIM_EXTRACT_ONLY_ERROR)
        return JSONResponse(
            content={"error": {"code": constants.ERROR_CODE_PROCESSING_ERROR, "message": str(e)}},
            status_code=400
        )
    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
