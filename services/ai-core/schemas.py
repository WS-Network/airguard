from pydantic import BaseModel, Field
from typing import Literal, Any, List, Dict






Vendor = Literal["cisco","juniper","mikrotik","aruba","generic"]

class ParseConfigReq(BaseModel):
    deviceId: str; vendor: Vendor; raw: str

class NormalizedConfig(BaseModel):
    interfaces: Any = {}; vlans: Any = {}; routing: Any = {}; acls: Any = {}; meta: Any = {}

class ParseConfigRes(BaseModel):
    normalized: NormalizedConfig
    confidence: float = Field(ge=0,le=1)
    warnings: List[str] = []

class ExplainReq(BaseModel):
    siteId: str

class ExplainRes(BaseModel):
    markdown: str
    highlights: List[Dict[str,str]]

class DiagramReq(BaseModel):
    siteId: str
    format: Literal["drawio","mermaid"]="drawio"

class DiagramRes(BaseModel):
    format: Literal["drawio","mermaid"]
    data: str


class PlanChangesReq(BaseModel):
    siteId: str
    intent: str

class PlanChangesRes(BaseModel):
    diff: List[Dict[str, Any]]
    dryRun: Dict[str, Any]
    blastRadius: List[str]

class ValidateReq(BaseModel):
    siteId: str

class ValidateRes(BaseModel):
    ok: bool
    errors: List[str]

    metrics: Dict[str, float]
    
# Telemetry and Optimization schemas
from datetime import datetime

class TelemetryReq(BaseModel):
    device_id: str
    protocol: Literal["lorawan", "snmp", "mqtt"]

class TelemetryRes(BaseModel):
    timestamp: datetime
    data: Dict[str, Any]

class OptimizationReq(BaseModel):
    device_id: str
    protocol: Literal["lorawan", "snmp", "mqtt"]
    metrics: Dict[str, Any]

class OptimizationRes(BaseModel):
    suggestions: Dict[str, Any]
