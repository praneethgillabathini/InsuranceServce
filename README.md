# NHCX Insurance FHIR Utility

This microservice utility is designed to convert insurance claim documents from PDF format into NHCX (National Health Claim Exchange) compliant FHIR (Fast Healthcare Interoperability Resources) bundles. It provides a simple, user-friendly interface for document uploads and a powerful backend for processing.

## Features

- **Web-Based Interface**: A clean, intuitive frontend built with React for easy PDF uploads.
- **PDF to FHIR Conversion**: Robust backend logic to parse PDFs, extract relevant data, and transform it into structured FHIR resources.
- **NHCX Compliance**: Ensures the generated FHIR bundles adhere to the specific profiles and standards set by the NHCX.
- **RESTful API**: Exposes endpoints for seamless integration with other systems.

## Architecture

The application follows a decoupled client-server architecture, ensuring scalability and maintainability.

### Frontend (Client)

- **Framework**: React/
- **Purpose**: Provides the user interface for uploading PDF documents. It communicates with the backend via REST API calls.

### Backend (Server)

- **Language**: Python
- **Framework**: FastAPI
- **Purpose**: Contains the core business logic. It handles:
    1.  Receiving the PDF file from the frontend.
    2.  Using PDF parsing libraries to extract text and data.
    3.  Mapping the extracted data to the appropriate FHIR resources (e.g., `Claim`, `Patient`, `Coverage`).
    4.  Bundling these resources into a single `Bundle` resource that is compliant with NHCX specifications.
    5.  Returning the resulting FHIR bundle to the client.

## Technology Stack

| Component | Technology                                |
| :--- |:------------------------------------------|
| **Frontend** | React, Axios                              |
| **Backend** | Python, FastAPI                           |
| **PDF Parsing** | `Marker`, `pdfplumber`                    |
| **FHIR Handling** | `fhir.resources`                          |
| **Package Manager** | `npm` (for frontend), `pip` (for backend) |

## Prerequisites

Ensure you have the following installed on your local development machine:

- Node.js (v18.x or newer)
- Python (v3.9 or newer)
- `pip` and `venv`

## Installation & Setup

Follow these steps to get the project running locally.

### Backend Setup

```bash
# 1. Navigate to the backend directory
cd path/to/your/backend

# 2. Create and activate a Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# 3. Install the required Python packages
pip install -r requirements.txt
```

### Frontend Setup

```bash
# 1. Navigate to the frontend directory
cd path/to/your/frontend

# 2. Install the required npm packages
npm install
```

## Running the Application

1.  **Start the Backend Server**:
    ```bash
    # From the backend directory
    python app.py
    ```
    The backend will typically be available at `http://localhost:5000`.

2.  **Start the Frontend Application**:
    ```bash
    # From the frontend directory
    npm start
    ```
    The frontend will open in your browser at `http://localhost:3000`.

## Usage

1.  Open your web browser and navigate to `http://localhost:3000`.
2.  Use the file upload component to select and upload an insurance claim PDF.
3.  The application will process the file and display the resulting NHCX compliant FHIR bundle, which you can then view or download.
