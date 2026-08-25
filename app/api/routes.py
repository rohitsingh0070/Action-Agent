from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.request import CommandRequest, CommandResponse, RulesListResponse
from app.services.llm_parser import llm_parser_service
from app.services.validator import validator_service
from app.services.executor import executor_service
from app.store.memory_store import memory_store

router = APIRouter()

@router.post("/command", response_model=CommandResponse)
async def process_command(request: CommandRequest):
    """
    Main endpoint for processing natural language commands.
    Pipeline:
    Natural Language Text -> LLM Structured Parsing -> Pydantic Schema & Device Registry Validation -> Action Execution
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Command text cannot be empty.")

    # 1. LLM Understanding (Extract Structured Action JSON)
    understood_as = llm_parser_service.parse(request.text)

    # 2. Backend Validation (Schema + Device Registry)
    validation_res = validator_service.validate_action_dict(understood_as)

    if not validation_res.is_valid:
        return CommandResponse(
            status="validation_error",
            understood_as=understood_as,
            executed=False,
            message=validation_res.message,
            errors=validation_res.errors
        )

    # 3. Action Execution
    return executor_service.execute(validation_res.action, understood_as)

@router.get("/rules", response_model=RulesListResponse)
async def list_rules(device_id: Optional[str] = Query(None, description="Optional device filter")):
    """
    Retrieve created alert rules from in-memory store.
    """
    rules = memory_store.get_rules(device_id=device_id)
    return RulesListResponse(rules=rules, total=len(rules))

@router.get("/devices")
async def list_devices():
    """
    Retrieve fake device registry data.
    """
    return memory_store.get_devices()
