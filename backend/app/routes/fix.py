from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime

try:
    from app.database import sessions_collection
except ImportError:
    sessions_collection = None

try:
    from app.services.pipeline.pipeline import validator_agent
except ImportError:
    def validator_agent(parsed_data: dict):
        return []

router = APIRouter(prefix="/fix", tags=["fix"])

class ApplyFixRequest(BaseModel):
    sessionId: str
    field: str
    newValue: str

def edi_generator(parsed: dict) -> str:
    """
    Regenerates raw EDI string from structured nested JSON.
    """
    if not isinstance(parsed, dict) or "segments" not in parsed:
        return ""
        
    result = ""
    for seg in parsed.get("segments", []):
        segment_id = seg.get("segmentId", "")
        elements = [str(el.get("value", "")) for el in seg.get("elements", [])]
        
        if elements:
            result += segment_id + "*" + "*".join(elements) + "~"
        else:
            result += segment_id + "~"
            
    return result

@router.post("/apply")
async def apply_fix(request: ApplyFixRequest):
    """
    Endpoint for accepting a suggested fix, updating the JSON mapping,
    logging the change, regenerating the EDI output, and persisting it to MongoDB.
    """
    # 1. Convert sessionId -> ObjectId
    try:
        obj_id = ObjectId(request.sessionId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    if sessions_collection is None:
        raise HTTPException(status_code=500, detail="Database connection not configured")

    # 2. Fetch session from MongoDB
    session = sessions_collection.find_one({"_id": obj_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 3. Modify "modifiedJson" assuming structured array configuration
    modified_json = session.get("modifiedJson") or {}
    segments = modified_json.get("segments", [])
    old_value = None
    
    # Safe array operation assuming simple mapping for the sake of the hackathon loop
    for seg in segments:
        if seg.get("segmentId") == request.field:
            if seg.get("elements"):
                old_value = seg["elements"][0].get("value")
                seg["elements"][0]["value"] = request.newValue
            break

    # 4. Append entry to "changesLog"
    changes_log = session.get("changesLog") or []
    changes_log.append({
        "field": request.field,
        "old": old_value,
        "new": request.newValue,
        "timestamp": datetime.utcnow()
    })

    # 5. Regenerate corrected EDI
    corrected_edi = edi_generator(modified_json)

    # 5.5 Re-run validation logic to catch outstanding or cleared errors
    errors = validator_agent(modified_json)

    # 6. Update Mongo
    sessions_collection.update_one(
        {"_id": obj_id},
        {"$set": {
            "modifiedJson": modified_json,
            "changesLog": changes_log,
            "correctedEDI": corrected_edi,
            "validationErrors": errors,
            "updatedAt": datetime.utcnow()
        }}
    )

    # 7. Return mapping
    return {
        "message": "Fix applied",
        "sessionId": request.sessionId
    }
