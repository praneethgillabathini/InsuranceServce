import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from . import constants
from .logging_config import request_id_var

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        start_time = time.time()
        logger.info(constants.LOG_REQUEST_STARTED.format(method=request.method, path=request.url.path))
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers[constants.HEADER_X_REQUEST_ID] = request_id
            logger.info(constants.LOG_REQUEST_FINISHED.format(method=request.method, path=request.url.path, status_code=response.status_code, process_time=process_time))
            return response
        except Exception:
            logger.exception(constants.LOG_REQUEST_FAILED.format(method=request.method, path=request.url.path))
            raise