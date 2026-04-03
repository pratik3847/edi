"""
Pipeline Orchestrator
The brain of the workflow. Calls the agents in a sequential or event-driven order:
ParserAgent -> ValidatorAgent -> FixAgent -> ExplainerAgent.
Never implements parsing or validation logic directly.
"""
