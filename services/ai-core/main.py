import os
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import ORJSONResponse
from schemas import *

AI_DEV_JWT = os.getenv("AI_DEV_JWT","dev-token")

app = FastAPI(title="AirGuard AI-Core", default_response_class=ORJSONResponse)

def check_auth(authorization: str|None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing auth")
    token = authorization.split(" ",1)[1]
    if token != AI_DEV_JWT:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.get("/healthz")
def health(): return {"ok": True, "service":"ai-core"}

@app.post("/parse-config", response_model=ParseConfigRes)
def parse_config(req: ParseConfigReq, authorization: str|None = Header(default=None)):
    check_auth(authorization)
    return ParseConfigRes(normalized=NormalizedConfig(meta={"vendor": req.vendor}), confidence=0.75, warnings=[])

@app.post("/explain-setup", response_model=ExplainRes)
def explain_setup(req: ExplainReq, authorization: str|None = Header(default=None)):
    check_auth(authorization)
    return ExplainRes(markdown="**Core → Access**. VLAN **20** trunked.", highlights=[{"text":"VLAN 20","type":"vlan","ref":"vlan:20"}])

@app.post("/generate-diagram", response_model=DiagramRes)
def generate_diagram(req: DiagramReq, authorization: str|None = Header(default=None)):
    check_auth(authorization)
    return DiagramRes(format=req.format, data='{"mxfile":{"diagram":[]}}')

@app.post("/plan-changes", response_model=PlanChangesRes)
def plan_changes(req: PlanChangesReq, authorization: str|None = Header(default=None)):
    check_auth(authorization)
    return PlanChangesRes(diff=[{"deviceId":"dev1","method":"cli","commands":["conf t","vlan 20"]}],
                          dryRun={"passed": True, "notes":[]}, blastRadius=[])

@app.post("/validate", response_model=ValidateRes)
def validate(req: ValidateReq, authorization: str|None = Header(default=None)):
    check_auth(authorization)
    return ValidateRes(ok=True, errors=[], metrics={"topology_valid":1.0})