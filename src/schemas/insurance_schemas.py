from pydantic import BaseModel, Field
from typing import List, Optional


class OrganisationSchema(BaseModel):
    name: str = Field(..., description="Name of the insurance company")
    phone: Optional[str] = ""


class TPAOrganisationSchema(BaseModel):
    name: Optional[str] = None
    identifier: Optional[str] = None


class ContactSchema(BaseModel):
    purpose: Optional[str] = ""
    phone: Optional[str] = ""


class SupportingInfoReqSchema(BaseModel):
    categoryCode: Optional[str] = ""
    categoryDisplay: Optional[str] = ""
    documentCode: Optional[str] = ""
    documentDisplay: Optional[str] = ""


class ExclusionSchema(BaseModel):
    categoryCode: Optional[str] = ""
    categoryDisplay: Optional[str] = ""
    statement: Optional[str] = ""


class BenefitSchema(BaseModel):
    typeCode: Optional[str] = ""
    typeDisplay: str
    limitValue: Optional[str] = ""
    limitUnit: Optional[str] = ""


class CoverageSchema(BaseModel):
    typeDisplay: str
    condition: Optional[str] = ""
    benefits: List[BenefitSchema] = []


class SpecificCostSchema(BaseModel):
    categoryCode: Optional[str] = ""
    categoryDisplay: Optional[str] = ""
    benefitTypeCode: Optional[str] = ""
    benefitTypeDisplay: Optional[str] = ""
    costType: Optional[str] = ""
    costValue: Optional[str] = ""
    costUnit: Optional[str] = ""


class PlanSchema(BaseModel):
    planTypeCode: str
    planTypeDisplay: str
    specificCosts: List[SpecificCostSchema] = []


class InsurancePlanSchema(BaseModel):
    status: Optional[str] = "active"
    name: str
    typeCode: str
    typeDisplay: str
    periodStart: Optional[str] = ""
    periodEnd: Optional[str] = ""
    coverageArea: List[str] = []
    networks: List[str] = []
    contacts: List[ContactSchema] = []
    supportingInfoRequirements: List[SupportingInfoReqSchema] = []
    exclusions: List[ExclusionSchema] = []
    coverages: List[CoverageSchema] = []
    plans: List[PlanSchema] = []


class InsuranceDataPayload(BaseModel):
    bundleType: str
    organisation: OrganisationSchema
    tpaOrganisation: Optional[TPAOrganisationSchema] = None
    insurancePlan: InsurancePlanSchema