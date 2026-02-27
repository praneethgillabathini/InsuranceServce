const API_URL = process.env.REACT_APP_API_URL || '';
const BASE_INSURANCE = `${API_URL}/api/v1/insurance`;
const BASE_FHIR = `${API_URL}/api/v1/fhir`;

async function _handleResponse(response) {
  const data = await response.json();
  if (!response.ok) {
    const msg = data?.error?.message
      ? `Error (${data.error.code}): ${data.error.message}`
      : `API Error (${response.status}): An unknown error occurred.`;
    throw new Error(msg);
  }
  return data;
}

export async function processClaim(file, generateFhir) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('generate_fhir', generateFhir);
  const response = await fetch(`${BASE_INSURANCE}/process`, { method: 'POST', body: formData });
  return _handleResponse(response);
}

export async function extractOnly(file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${BASE_INSURANCE}/extract-only`, { method: 'POST', body: formData });
  return _handleResponse(response);
}

export async function generateFhirBundle(jsonData) {
  const response = await fetch(`${BASE_INSURANCE}/generate-fhir`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(jsonData),
  });
  return _handleResponse(response);
}

export async function validateFhirBundle(fhirBundle) {
  const response = await fetch(`${BASE_FHIR}/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fhirBundle),
  });
  return _handleResponse(response);
}

export async function getBundleSummary(fhirBundle) {
  const response = await fetch(`${BASE_FHIR}/bundle-summary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fhirBundle),
  });
  return _handleResponse(response);
}

export async function getServiceHealth() {
  const response = await fetch(`${BASE_INSURANCE}/health`, { method: 'GET' });
  return _handleResponse(response);
}