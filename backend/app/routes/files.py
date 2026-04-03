from fastapi import APIRouter, File, UploadFile, Query, HTTPException
from bson import ObjectId
try:
    from app.database import sessions_collection
except ImportError:
    sessions_collection = None

# Adjust this import path based on where `run_pipeline` is actually defined
try:
    from app.services.pipeline import run_pipeline
except ImportError:
    # Dummy placeholder function if the module doesn't exist yet
    def run_pipeline(edi_text: str, userId: str):
        pass

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload")
async def upload_file(
    userId: str = Query(..., description="The ID of the user uploading the file"),
    file: UploadFile = File(...)
):
    """
    Endpoint for handling EDI file uploads.
    Reads the file to memory, converts it to a string, and triggers the processing pipeline.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Convert to string (assuming UTF-8 encoding for standard EDI text)
        edi_text = content.decode("utf-8")
        
        # Call the pipeline process logic
        # (Add 'await' if your actual run_pipeline is an async function)
        result = run_pipeline(edi_text, userId)
        
        return {
            "message": "File processed successfully",
            "data": result
        }

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400, 
            detail="Error decoding the file. Ensure the EDI file is encoded in UTF-8."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while handling the upload: {str(e)}"
        )

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Retrieve full EDI session data by its ID.
    """
    try:
        obj_id = ObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
        
    if sessions_collection is None:
        raise HTTPException(status_code=500, detail="Database connection not configured")
        
    session = sessions_collection.find_one({"_id": obj_id})
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Convert ObjectId to string to avoid JSON serialization errors
    session["_id"] = str(session["_id"])
    
    return session
