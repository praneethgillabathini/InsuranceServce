import sys
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.health_check import check_llm_health
from src.core.pdf_processor import PDFProcessor
from src.routes import claims, health, fhir
from src.services.llm.llm_factory import get_llm_service
from src.middleware import LoggingMiddleware
from src.logging_config import setup_logging
from src import constants
from src.config import settings

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(constants.LOG_APP_STARTUP_LOADING)
    is_llm_healthy = check_llm_health()
    if not is_llm_healthy:
        logger.critical(constants.LOG_APP_LLM_HEALTH_FAILED)
        logger.critical(constants.LOG_APP_LLM_HEALTH_FIX_HINT)
        sys.exit(1)
    logger.info(constants.LOG_APP_LLM_HEALTH_OK)
    app.state.pdf_processor = PDFProcessor()
    app.state.llm_service = get_llm_service()
    logger.info(constants.LOG_APP_STARTUP_SUCCESS)
    yield
    logger.info(constants.LOG_APP_SHUTDOWN)


app = FastAPI(
    title=settings.app.title,
    description=settings.app.description,
    version=settings.app.version,
    lifespan=lifespan
)

app.add_middleware(LoggingMiddleware)

app.include_router(
    claims.router,
    prefix=f"{settings.app.api_prefix}/insurance"
)

app.include_router(
    health.router,
    prefix=f"{settings.app.api_prefix}/insurance"
)

app.include_router(
    fhir.router,
    prefix=f"{settings.app.api_prefix}/fhir"
)


@app.get("/")
def read_root():
    return {"message": constants.LOG_APP_WELCOME.format(title=settings.app.title)}


if __name__ == "__main__":
    uvicorn.run("app:app", host=settings.server.host, port=settings.server.port, reload=True)