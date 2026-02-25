import sys
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.health_check import check_llm_health
from src.core.pdf_processor import PDFProcessor
from src.routes import claims
from src.services.llm.llm_factory import get_llm_service
from src.middleware import LoggingMiddleware
from src.logging_config import setup_logging
from src import constants

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(constants.LOG_APP_STARTUP_LOADING)

    is_llm_healthy = check_llm_health()
    if not is_llm_healthy:
        logger.critical("LLM health check failed. The application cannot proceed.")
        logger.critical(
            "Please review the error logs above to diagnose and fix the configuration or connectivity issue.")
        sys.exit(1)

    logger.info("LLM is healthy. Starting the main OCR and analysis process...")

    app.state.pdf_processor = PDFProcessor()
    app.state.llm_service = get_llm_service()

    logger.info(constants.LOG_APP_STARTUP_SUCCESS)

    yield

    logger.info(constants.LOG_APP_SHUTDOWN)


# Initialize FastAPI
app = FastAPI(
    title="NHCX Insurance FHIR Utility API",
    description="An API to convert insurance claim PDFs into NHCX compliant FHIR bundles.",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(LoggingMiddleware)

# Register routes
app.include_router(
    claims.router,
    prefix="/api/v1"
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the NHCX Insurance FHIR Utility API"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)