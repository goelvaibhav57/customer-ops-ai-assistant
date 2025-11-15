def routing_request(state: AgentState):
    if state.intent == "DataLookup":
        return "rationale_node"
    else:
        return state.intents