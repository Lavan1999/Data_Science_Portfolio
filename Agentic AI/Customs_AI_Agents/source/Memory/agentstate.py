from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# DECLARATION DETAILS
class DeclarationDetails(BaseModel):
    hs_code: Optional[str] = None
    goods_description: Optional[str] = None
    hs_code_duty_fee: Optional[str] = None

    goods_value: Optional[str] = None
    static_quantity_unit: Optional[int] = None
    currency: Optional[str] = None
    deposit: Optional[str] = None

    country: Optional[str] = None


# TARIFF MODELS
class TariffExtractedData(BaseModel):
    hs_code: Optional[str] = None
    description: Optional[str] = None
    duty_percentage: Optional[str] = None


class TariffFeedback(BaseModel):
    status: str = Field(
        ...,
        description="ACCEPTED / INCORRECT HS CODE / DESCRIPTION MISMATCH / DUTY PERCENTAGE MISMATCH / NEED REVIEW"
    )

    explanation: str = Field(
        ...,
        description="Short technical explanation of the tariff verification result"
    )

    failed_field: Optional[str] = Field(
        None,
        description="Field that failed verification: hs_code / description / duty_percentage"
    )

    correct_value: Optional[str] = Field(
        None,
        description="Official correct value from tariff database for the failed field"
    )

# VALUATION MODELS
class ValuationExtractedData(BaseModel):
    price_id: Optional[int] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    product_id: Optional[str] = None
    description: Optional[str] = None
    variation_percentage: Optional[float] = None
    unit_of_measurement_id: Optional[int] = None
    unit_name: Optional[str] = None
    total_price: Optional[float] = None


class ValuationFeedback(BaseModel):
    status: str = Field(
        ...,
        description="ACCEPTED / UNDERVALUED / OVERVALUED / DECLINED / NEED REVIEW"
    )
    explanation: str = Field(
        ...,
        description="Short technical justification for the valuation status"
    )
    failed_field: Optional[str] = Field(
        None,
        description="Field that failed verification (e.g., goods_value) if UNDERVALUED or OVERVALUED"
    )
    correct_value: Optional[str] = Field(
        None,
        description="Correct valuation value based on database reference for auto-correction"
    )
    discrepancy_percentage: Optional[float] = Field(
        None,
        description="Absolute percentage difference between declared total price and database reference price"
    )


# INSPECTION MODELS 
class InspectionExtractedData(BaseModel):
    goods_description: Optional[str] = None
    
class InspectionFeedback(BaseModel):
    status: str = Field(
        ...,
        description="ACCEPTED / MANUAL INSPECTION REQUIRED / NEED REVIEW"
    )

    explanation: str = Field(
        ...,
        description="Short justification for inspection decision"
    )

    matched_category: Optional[str] = Field(
        None,
        description="Alcohol / Tobacco / Illegal Drugs / Prohibited Items / None"
    )


# RISK PROFILE
class RiskProfile(BaseModel):
    risk_id: Optional[str] = None
    risk_type: Optional[str] = None
    risk_description: Optional[str] = None
    risk_confidence_score: Optional[str] = None
    risk_recommended_action: Optional[str] = None
    status: Optional[str] = Field(None, description="resolved / unresolved")


# CDM INPUT
class CDMInput(BaseModel):
    declaration_id: Optional[str] = None 
    risk_profile: Optional[RiskProfile] = None


# CDM EXTRACTED
class CDMExtracted(BaseModel):
    declaration_details: Optional[DeclarationDetails] = None
    tariff_extracted_data: Optional[TariffExtractedData] = None
    valuation_extracted_data: Optional[ValuationExtractedData] = None
    inspection_extracted_data: Optional[InspectionExtractedData] = None


# CDM DECISION
class CDMDecision(BaseModel):
    risk_id: str
    tariff_feedback: Optional[TariffFeedback] = None
    valuation_feedback: Optional[ValuationFeedback] = None
    inspection_feedback: Optional[InspectionFeedback] = None   # ← ADDED (No change to existing fields)

    cdm_decision: Optional[str] = Field(
        None,
        description="ACCEPTED / CORRECTION / INSPECTION / DECLINED"
    )
    cdm_feedback: Optional[str] = None

    failed_field: Optional[str] = None
    correct_value: Optional[str] = None

# ORCHESTRATOR AGENT STATE
class OrchestratorAgentState(BaseModel):
    """
    MAIN STATE shared across all nodes.
    """

    cdm_input: Optional[CDMInput] = None
    cdm_extracted: Optional[CDMExtracted] = None
    cdm_decision: Optional[CDMDecision] = None
    orchestrator_status: str = Field(
        default="INIT",
        description="INIT / EXECUTING / DECIDING / COMPLETED"
    )