from datetime import datetime

def create_session(userId: str, fileName: str, edi_text: str, parsed, errors, fixes) -> dict:
    """
    Returns a structured dictionary representing an EDI session,
    prepared for MongoDB insertion.
    """
    now = datetime.utcnow()
    
    return {
        "userId": userId,
        "fileName": fileName,
        
        "originalEDI": edi_text,
        "correctedEDI": None,
        
        "parsedJson": parsed,
        "modifiedJson": parsed,
        "validationErrors": errors,
        "fixSuggestions": fixes,
        
        "changesLog": [],
        
        "status": "uploaded",
        
        "createdAt": now,
        "updatedAt": now
    }
