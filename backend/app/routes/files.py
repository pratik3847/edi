"""
File Upload & Pipeline Trigger Routes
Endpoints handling the initial EDI file upload. These routes do NOT process files directly, 
they create a session and pass the session ID to the `pipeline.py` orchestrator.
"""
