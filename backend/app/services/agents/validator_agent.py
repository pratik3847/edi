"""
Validator Agent
Represents the validation phase. Takes the parsed JSON from state, calls `services.validation.validator`,
and appends any validation errors/warnings back into the session document.
"""
