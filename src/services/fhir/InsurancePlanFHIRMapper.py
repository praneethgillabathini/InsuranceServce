import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from . import fhir_constants as fhir

logger = logging.getLogger(__name__)


class InsurancePlanFHIRMapper:
    def __init__(self, extracted_data: Dict[str, Any]):
        self.data: Dict[str, Any] = extracted_data or {}
        self.bundle: Dict[str, Any] = {
            "resourceType": fhir.BUNDLE,
            "id": str(uuid.uuid4()),
            "type": fhir.BUNDLE_TYPE_COLLECTION,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "entry": []
        }

    def _add_to_bundle(self, resource: Dict[str, Any]):
        self.bundle["entry"].append({
            "fullUrl": f"urn:uuid:{resource['id']}",
            "resource": resource
        })

    def _get_required_value(self, data: Dict[str, Any], key: str, context: str, fallback: str = "Unknown") -> Any:
        value = data.get(key)
        if not value:
            logger.warning(f"Missing required field '{key}' in '{context}'. Using fallback: '{fallback}'")
            return fallback
        return value

    def _build_organization(self, org_data: Optional[Dict[str, Any]], is_tpa: bool = False) -> Optional[str]:
        if not org_data:
            return None
        try:
            org_id = str(uuid.uuid4())
            org_resource = {
                "resourceType": fhir.ORGANIZATION,
                "id": org_id,
                "name": self._get_required_value(org_data, "name", "organisation"),
                "telecom": [{"system": fhir.TELECOM_SYSTEM_PHONE, "value": org_data.get("phone")}] if org_data.get(
                    "phone") else []
            }

            if is_tpa and org_data.get("identifier"):
                org_resource["identifier"] = [{"value": org_data.get("identifier")}]

            self._add_to_bundle(org_resource)
            return f"Organization/{org_id}"
        except ValueError as e:
            context_name = "TPA Organisation" if is_tpa else "Organisation"
            logger.error(f"Skipping {context_name} resource due to missing data: {e}")
            return None

    def _build_complex_extension(self, url: str, sub_extensions: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "url": url,
            "extension": sub_extensions
        }

    def _add_plan_contacts(self, insurance_plan: Dict[str, Any], contacts_data: List[Dict[str, Any]]):
        if not contacts_data:
            return
        insurance_plan["contact"] = [
            {
                "purpose": {"text": contact.get("purpose")},
                "telecom": [{"system": fhir.TELECOM_SYSTEM_PHONE, "value": contact.get("phone")}]
            }
            for contact in contacts_data
        ]

    def _add_plan_coverage_areas(self, insurance_plan: Dict[str, Any], areas_data: List[str]):
        if not areas_data:
            return
        insurance_plan["coverageArea"] = [{"display": area} for area in areas_data]

    def _add_plan_extensions(self, insurance_plan: Dict[str, Any], plan_data: Dict[str, Any]):
        for req in (plan_data.get("supportingInfoRequirements") or []):
            ext = self._build_complex_extension(
                fhir.SD_CLAIM_SUPPORTING_INFO_REQ,
                [
                    {"url": "category", "valueCodeableConcept": {
                        "coding": [{"code": req.get("categoryCode"), "display": req.get("categoryDisplay")}]}},
                    {"url": "document", "valueCodeableConcept": {
                        "coding": [{"code": req.get("documentCode"), "display": req.get("documentDisplay")}]}}
                ]
            )
            insurance_plan["extension"].append(ext)

        for excl in (plan_data.get("exclusions") or []):
            ext = self._build_complex_extension(
                fhir.SD_CLAIM_EXCLUSION,
                [
                    {"url": "category", "valueCodeableConcept": {
                        "coding": [{"code": excl.get("categoryCode"), "display": excl.get("categoryDisplay")}]}},
                    {"url": "statement", "valueString": excl.get("statement")}
                ]
            )
            insurance_plan["extension"].append(ext)

    def _build_benefit_block(self, ben_data: Dict[str, Any]) -> Dict[str, Any]:
        benefit_type = {"coding": [{"code": ben_data.get("typeCode"), "display": ben_data.get("typeDisplay")}]}
        benefit_block = {"type": benefit_type}
        limit_value = ben_data.get("limitValue")

        if limit_value:
            benefit_block["limit"] = [{"value": {"value": limit_value, "unit": ben_data.get("limitUnit")}}]
        return benefit_block

    def _add_plan_coverages(self, insurance_plan: Dict[str, Any], coverages_data: List[Dict[str, Any]]):
        if not coverages_data:
            return
        for cov in coverages_data:
            coverage_block = {
                "type": {"coding": [{"display": cov.get("typeDisplay")}]},
                "extension": [
                    self._build_complex_extension(
                        fhir.SD_CLAIM_CONDITION,
                        [{"url": "statement", "valueString": cov.get("condition")}]
                    )
                ] if cov.get("condition") else [],
                "benefit": [self._build_benefit_block(ben) for ben in (cov.get("benefits") or [])]
            }
            insurance_plan["coverage"].append(coverage_block)

    def _build_specific_cost_block(self, cost: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            return {
                "category": {"coding": [{"code": self._get_required_value(cost, "categoryCode", "specificCost"),
                                         "display": cost.get("categoryDisplay")}]},
                "benefit": [{
                    "type": {"coding": [
                        {"code": self._get_required_value(cost, "benefitTypeCode", "specificCost.benefit"),
                         "display": cost.get("benefitTypeDisplay")}]},
                    "cost": [{
                        "type": {"coding": [{"code": self._get_required_value(cost, "costType", "specificCost.cost")}]},
                        "value": {"value": self._get_required_value(cost, "costValue", "specificCost.cost"),
                                  "currency": self._get_required_value(cost, "costUnit", "specificCost.cost")}
                    }]
                }]
            }
        except ValueError as e:
            logger.warning(f"Skipping a specificCost block due to missing data: {e}")
            return None

    def _add_plan_financial_tiers(self, insurance_plan: Dict[str, Any], plans_data: List[Dict[str, Any]]):
        if not plans_data:
            return
        for plan in plans_data:
            plan_block = {
                "type": {"coding": [{"system": fhir.VS_PLAN_TYPE, "code": plan.get("planTypeCode"),
                                     "display": plan.get("planTypeDisplay")}]},
                "specificCost": [cost_block for cost in (plan.get("specificCosts") or [])
                                 if (cost_block := self._build_specific_cost_block(cost)) is not None]
            }
            insurance_plan["plan"].append(plan_block)

    def _build_insurance_plan(self, plan_data: Optional[Dict[str, Any]], owned_by_ref: str,
                              admin_by_ref: Optional[str] = None):
        if not plan_data:
            return

        try:
            plan_id = str(uuid.uuid4())
            insurance_plan = {
                "resourceType": fhir.INSURANCE_PLAN,
                "id": plan_id,
                "status": plan_data.get("status", "active"),
                "name": self._get_required_value(plan_data, "name", "insurancePlan"),
                "ownedBy": {"reference": owned_by_ref},
                "period": {
                    "start": plan_data.get("periodStart"),
                    "end": plan_data.get("periodEnd")
                },
                "type": [{
                    "coding": [{
                        "system": fhir.VS_INSURANCE_PLAN_TYPE,
                        "code": self._get_required_value(plan_data, "typeCode", "insurancePlan.type"),
                        "display": plan_data.get("typeDisplay")
                    }]
                }],
                "identifier": [{"system": fhir.SYSTEM_EXAMPLE_IDENTIFIER, "value": f"PLAN-{uuid.uuid4().hex[:6]}"}],
                "extension": [],
                "coverage": [],
                "plan": []
            }

            if admin_by_ref:
                insurance_plan["administeredBy"] = {"reference": admin_by_ref}

            self._add_plan_contacts(insurance_plan, plan_data.get("contacts") or [])
            self._add_plan_coverage_areas(insurance_plan, plan_data.get("coverageArea") or [])
            self._add_plan_extensions(insurance_plan, plan_data)
            self._add_plan_coverages(insurance_plan, plan_data.get("coverages") or [])
            self._add_plan_financial_tiers(insurance_plan, plan_data.get("plans") or [])

            self._add_to_bundle(insurance_plan)
        except ValueError as e:
            logger.error(f"Skipping InsurancePlan resource due to missing mandatory data: {e}")

    def generate_dict(self) -> Dict[str, Any]:
        org_data = self.data.get("organisation") or self.data.get("organization") or {}

        owned_by_ref = self._build_organization(org_data)
        admin_by_ref = self._build_organization(self.data.get("tpaOrganisation"), is_tpa=True)

        if owned_by_ref:
            self._build_insurance_plan(self.data.get("insurancePlan"), owned_by_ref, admin_by_ref)
        else:
            logger.error("CRITICAL: owned_by_ref is still None. InsurancePlan will not be built.")

        return self.bundle

    def generate_json(self) -> str:
        return json.dumps(self.generate_dict(), indent=2)