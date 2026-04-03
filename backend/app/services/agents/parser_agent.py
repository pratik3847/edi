"""
Parser Agent
Represents the parsing phase of the pipeline. Its job is to take the raw EDI string,
call `services.parser.parser`, and update the session state with the structured JSON.
"""
