import os
import logging
from typing import Dict, Any
import torch
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.config.parser import ConfigParser
from ..config import settings
from .. import constants

logger = logging.getLogger(__name__)


class PDFProcessor:
    model_dict: Dict[str, Any]
    converter: PdfConverter

    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(constants.LOG_PDF_PROCESSOR_INIT_DEVICE.format(device=device))

        model_precision = settings.marker.model_precision
        torch_dtype = torch.float32
        if model_precision == "fp16":
            if device == "cuda":
                torch_dtype = torch.float16
            else:
                logger.warning(constants.LOG_PDF_FP16_CPU_WARNING)

        logger.info(constants.LOG_PDF_PROCESSOR_LOADING_MODELS)
        self.model_dict = create_model_dict(device=device)

        config = ConfigParser({
            "workers": settings.marker.workers,
            "pdftext_workers": settings.marker.pdftext_workers,
            "batch_multiplier": settings.marker.batch_multiplier,
            "torch_dtype": torch_dtype,
            "exclude_images": settings.marker.exclude_images,
            "disable_image_extraction": settings.marker.exclude_images,
            "disable_image_captions": settings.marker.exclude_images,
            "disable_links": True
        })
        self.converter = PdfConverter(
            artifact_dict=self.model_dict,
            config=config.generate_config_dict()
        )
        logger.info(constants.LOG_PDF_PROCESSOR_MODELS_LOADED)

    def convert_to_markdown(self, pdf_path: str) -> str:
        if not os.path.exists(pdf_path):
            # 3. Clean: Log error before raising for better traceability
            error_msg = constants.LOG_PDF_FILE_NOT_FOUND.format(pdf_path=pdf_path)
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(constants.LOG_PDF_CONVERTING.format(pdf_path=pdf_path))
        rendered = self.converter(pdf_path)
        full_text, _, _ = text_from_rendered(rendered)
        return full_text