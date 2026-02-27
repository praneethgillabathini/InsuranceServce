import os
import sys
import json
import asyncio
import logging
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.pdf_processor import PDFProcessor
from src.services.llm.llm_factory import get_llm_service
from src.services.policy_pruner import PolicyPruner
from src.core import prompts
from src.services.fhir.insurance_plan_fhir_mapper import InsurancePlanFHIRMapper
from src.routes.claims import _clean_and_parse_llm_response
from src import constants

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("batch_processor")


async def process_single_pdf(pdf_path: Path, output_dir: Path, pdf_processor, llm_service, pruner):
    logger.info(constants.LOG_BATCH_PROCESSING_FILE.format(filename=pdf_path.name))
    try:
        logger.info(constants.LOG_BATCH_EXTRACTING_TEXT)
        loop = asyncio.get_running_loop()
        markdown_text = await loop.run_in_executor(None, pdf_processor.convert_to_markdown, str(pdf_path))

        logger.info(constants.LOG_BATCH_PRUNING_TEXT)
        clean_markdown = pruner.prune(markdown_text)

        logger.info(constants.LOG_BATCH_SENDING_LLM)
        llm_response = await llm_service.process_text(
            system_prompt=prompts.SYSTEM_PROMPT_FHIR, user_prompt=clean_markdown
        )

        logger.info(constants.LOG_BATCH_PARSING_JSON)
        cleaned_json = _clean_and_parse_llm_response(llm_response)

        logger.info(constants.LOG_BATCH_GENERATING_FHIR)
        mapper = InsurancePlanFHIRMapper(cleaned_json)
        bundle = mapper.generate_dict()

        output_file = output_dir / f"{pdf_path.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(bundle, f, indent=2, ensure_ascii=False)

        logger.info(constants.LOG_BATCH_FILE_SUCCESS.format(output_filename=output_file.name))
        return True

    except Exception as e:
        logger.error(constants.LOG_BATCH_FILE_FAILED.format(filename=pdf_path.name, error=e), exc_info=False)
        return False


async def main():
    parser = argparse.ArgumentParser(description="Batch process PDFs into FHIR bundles.")
    parser.add_argument("--input", "-i", type=str, default="data/input", help="Directory containing input PDFs")
    parser.add_argument("--output", "-o", type=str, default="data/output", help="Directory where JSON bundles will be saved")
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent
    input_dir = root_dir / args.input
    output_dir = root_dir / args.output

    logger.info(constants.LOG_BATCH_INPUT_DIR.format(input_dir=input_dir))
    if not input_dir.exists():
        logger.info(constants.LOG_BATCH_INPUT_DIR_CREATING)
        input_dir.mkdir(parents=True, exist_ok=True)
        return

    logger.info(constants.LOG_BATCH_OUTPUT_DIR.format(output_dir=output_dir))
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.info(constants.LOG_BATCH_NO_PDFS)
        return

    logger.info(constants.LOG_BATCH_FOUND_PDFS.format(count=len(pdf_files)))

    pdf_processor = PDFProcessor()
    llm_service = get_llm_service()
    pruner = PolicyPruner()

    logger.info(constants.LOG_BATCH_START + "\n" + constants.LOG_BATCH_SEPARATOR)

    success_count = 0
    for file in pdf_files:
        success = await process_single_pdf(file, output_dir, pdf_processor, llm_service, pruner)
        if success:
            success_count += 1

    logger.info(constants.LOG_BATCH_SEPARATOR)
    logger.info(constants.LOG_BATCH_COMPLETE.format(success=success_count, total=len(pdf_files)))


if __name__ == "__main__":
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
