import os
import logging
from typing import Dict, Any, Optional
import torch

from ..config import settings
from .. import constants

logger = logging.getLogger(__name__)


def _get_pdf_text_via_pdftext(pdf_path: str) -> Optional[str]:
    try:
        from pdftext.extraction import plain_text_output
        text = plain_text_output(pdf_path, sort=True)
        return text or None
    except Exception as e:
        logger.debug(constants.LOG_PDF_PDFTEXT_FAILED.format(error=e))
        return None


def _is_text_rich(text: Optional[str]) -> bool:
    if not text:
        return False
    return len(text.strip()) >= settings.pdf_processor.min_chars_for_text_pdf


class PDFProcessor:

    _marker_loaded: bool = False
    _model_dict: Optional[Dict[str, Any]] = None
    _converter: Any = None

    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(constants.LOG_PDF_PROCESSOR_INIT_DEVICE.format(device=device))
        logger.info(constants.LOG_PDF_PROCESSOR_INIT_DONE)

    def _ensure_marker_loaded(self):
        if self._marker_loaded:
            return
        logger.warning(constants.LOG_PDF_PROCESSOR_MARKER_LAZY_LOADING)
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.config.parser import ConfigParser

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_precision = settings.marker.model_precision
        torch_dtype = torch.float32
        if model_precision == "fp16" and device == "cuda":
            torch_dtype = torch.float16
        elif model_precision == "fp16":
            logger.warning(constants.LOG_PDF_FP16_CPU_WARNING)

        logger.info(constants.LOG_PDF_PROCESSOR_LOADING_MODELS)
        self._model_dict = create_model_dict(device=device)

        config = ConfigParser({
            "workers":                       settings.marker.workers,
            "pdftext_workers":               settings.marker.pdftext_workers,
            "batch_multiplier":              settings.marker.batch_multiplier,
            "torch_dtype":                   torch_dtype,
            "exclude_images":                settings.marker.exclude_images,
            "disable_image_extraction":      settings.marker.exclude_images,
            "disable_image_captions":        settings.marker.exclude_images,
            "disable_links":                 settings.pdf_processor.disable_links,
            "disable_multicolumn_detection": settings.pdf_processor.disable_multicolumn_detection,
        })
        self._converter = PdfConverter(
            artifact_dict=self._model_dict,
            config=config.generate_config_dict(),
        )
        self._marker_loaded = True
        logger.info(constants.LOG_PDF_PROCESSOR_MODELS_LOADED)

    def _convert_with_marker(self, pdf_path: str) -> str:
        from marker.output import text_from_rendered
        self._ensure_marker_loaded()
        logger.info(constants.LOG_PDF_SLOW_PATH_RUNNING.format(pdf_path=pdf_path))
        rendered = self._converter(pdf_path)
        full_text, _, _ = text_from_rendered(rendered)
        return full_text

    def convert_to_markdown(self, pdf_path: str) -> str:
        if not os.path.exists(pdf_path):
            error_msg = constants.LOG_PDF_FILE_NOT_FOUND.format(pdf_path=pdf_path)
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(constants.LOG_PDF_CONVERTING.format(pdf_path=pdf_path))
        fast_text = _get_pdf_text_via_pdftext(pdf_path)

        if _is_text_rich(fast_text):
            char_count = len(fast_text.strip())
            logger.info(constants.LOG_PDF_FAST_PATH.format(char_count=f"{char_count:,}"))
            return fast_text

        char_count = len((fast_text or "").strip())
        logger.warning(constants.LOG_PDF_SLOW_PATH_FALLBACK.format(char_count=char_count))
        return self._convert_with_marker(pdf_path)