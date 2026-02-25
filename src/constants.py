# Logging messages
LOG_APP_STARTUP_LOADING = "Application startup: Loading ML models and initializing clients..."
LOG_APP_STARTUP_SUCCESS = "Application startup: Resources loaded successfully."
LOG_APP_SHUTDOWN = "Application shutdown: Cleaning up resources."
LOG_REQUEST_STARTED = "Request started: {method} {path}"
LOG_REQUEST_FINISHED = "Request finished: {method} {path} - Status {status_code} - Completed in {process_time:.4f}s"
LOG_REQUEST_FAILED = "Request failed: {method} {path}"

# PDF Processor messages
LOG_PDF_PROCESSOR_INIT_DEVICE = "Initializing PDFProcessor on device: '{device}'"
LOG_PDF_PROCESSOR_LOADING_MODELS = "Loading Marker models... (this may take a while on first run)"
LOG_PDF_PROCESSOR_MODELS_LOADED = "Marker models loaded successfully."
LOG_PDF_CONVERTING = "Converting: {pdf_path}"
LOG_PDF_FP16_CPU_WARNING = "FP16 precision is not recommended for CPU inference; switching to FP32."
LOG_PDF_FILE_NOT_FOUND = "PDF file not found at: {pdf_path}"

# LLM Service messages
LOG_LLM_SERVICE_INIT = "Initializing {service_name}."
LOG_LLM_API_CALL_FAILED = "{service_name} API call failed: {error}"

# Claims processing messages
LOG_CLAIM_PROCESS_REQUEST = "Processing insurance claim request."
LOG_INVALID_FILE_TYPE_RECEIVED = "Invalid file type received: {content_type}. Filename: {filename}"
LOG_UPLOADED_FILE_SAVED = "Uploaded file '{filename}' saved to temporary path: {temp_path}"
LOG_PDF_CONVERSION_START = "Starting PDF-to-Markdown conversion for temporary file: {temp_path}"
LOG_PDF_CONVERSION_SUCCESS = "PDF conversion successful. Markdown length: {length} characters."
LOG_LLM_SENDING_MARKDOWN = "Sending markdown to LLM service: {service_name}"
LOG_LLM_RESPONSE_RECEIVED = "LLM response received successfully."
LOG_LLM_JSON_DECODE_FAILED = "Failed to decode JSON from LLM response. Raw response: '{raw_response}'"
LOG_CLAIM_PROCESS_ERROR = "An error occurred during the processing."
LOG_CLEANING_TEMP_FILE = "Cleaning up temporary file: {temp_path}"

# Error codes and messages (Backend)
ERROR_CODE_INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
ERROR_MESSAGE_INVALID_FILE_TYPE = "Invalid file type. Only PDFs are accepted."
ERROR_CODE_PROCESSING_ERROR = "PROCESSING_ERROR"
ERROR_MESSAGE_PROCESSING_ERROR = "An unexpected error occurred during processing."
ERROR_MESSAGE_LLM_API_ERROR = "LLM provider API error"
ERROR_MESSAGE_LLM_INVALID_JSON = "LLM did not return a valid JSON object."
ERROR_MESSAGE_LLM_OFFLINE = "LLM_IS_OFFLINE"
ERROR_MESSAGE_LLM_FAILED = "Health check on LLM failed."

# LLM Providers
LLM_PROVIDER_OPENAI = "openai"
LLM_PROVIDER_OLLAMA = "ollama"
LLM_PROVIDER_GEMINI = "gemini"
LLM_PROVIDER_GROK = "grok"
LLM_PROVIDER_BEDROCK = "bedrock"
LLM_PROVIDERS = [LLM_PROVIDER_OPENAI, LLM_PROVIDER_OLLAMA, LLM_PROVIDER_GEMINI, LLM_PROVIDER_GROK, LLM_PROVIDER_BEDROCK]

# HTTP Headers
HEADER_X_REQUEST_ID = "X-Request-ID"

# Frontend messages (for consistency, not directly imported by Python)
FE_ERROR_SELECT_FILE = "Please select a file first."
FE_ERROR_API_UNKNOWN = "An unknown error occurred."