from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class DomainAvailability(BaseModel):
    domain: str
    available: bool
    price: Optional[float] = None
    currency: Optional[str] = "USD"

class CompanyInfo(BaseModel):
    name: str
    description: str
    website: Optional[str] = None
    industry: Optional[str] = None
    founded_year: Optional[int] = None

class DomainResearchRequest(BaseModel):
    domain_type: str = Field(..., description="Type of domain needed (e.g., tech startup, blog)")
    industry: Optional[str] = Field(None, description="Industry sector")
    max_length: Optional[int] = Field(15, description="Maximum length of domain name")
    include_numbers: Optional[bool] = Field(False, description="Whether to include numbers in domain")

class DomainVariation(BaseModel):
    name: str
    type: str  # e.g., "prefix", "suffix", "combination"
    score: float  # relevance score

class DomainValue(BaseModel):
    estimated_value: float
    factors: Dict[str, any]
    confidence_score: float

class TrademarkConflict(BaseModel):
    trademark: str
    owner: str
    registration_number: Optional[str]
    risk_level: str  # "LOW", "MEDIUM", "HIGH"

class DomainResearchResult(BaseModel):
    domain_name: str
    availability: DomainAvailability
    variations: List[DomainVariation]
    similar_companies: List[CompanyInfo]
    estimated_value: DomainValue
    trademark_conflicts: List[TrademarkConflict]
    timestamp: datetime = Field(default_factory=datetime.now)