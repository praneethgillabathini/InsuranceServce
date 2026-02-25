# FHIR Resource Types
BUNDLE = "Bundle"
ORGANIZATION = "Organization"
INSURANCE_PLAN = "InsurancePlan"

# Bundle Types
BUNDLE_TYPE_COLLECTION = "collection"

# Telecom Systems
TELECOM_SYSTEM_PHONE = "phone"

# ABDM (Ayushman Bharat Digital Mission) URLs
_ABDM_URL_BASE = "https://nrces.in/ndhm/fhir/r4"

# ABDM Structure Definitions
SD_CLAIM_SUPPORTING_INFO_REQ = f"{_ABDM_URL_BASE}/StructureDefinition/Claim-SupportingInfoRequirement"
SD_CLAIM_EXCLUSION = f"{_ABDM_URL_BASE}/StructureDefinition/Claim-Exclusion"
SD_CLAIM_CONDITION = f"{_ABDM_URL_BASE}/StructureDefinition/Claim-Condition"

# ABDM ValueSets
VS_INSURANCE_PLAN_TYPE = f"{_ABDM_URL_BASE}/ValueSet/ndhm-insuranceplan-type"
VS_PLAN_TYPE = f"{_ABDM_URL_BASE}/ValueSet/ndhm-plan-type"

# Placeholder/Example Systems
SYSTEM_EXAMPLE_IDENTIFIER = "http://example.org/identifiers"