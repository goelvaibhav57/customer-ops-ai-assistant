from langgraph.graph import END, START, StateGraph
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from .state import AgentState
from .nodes import router_node, faq_node, data_lookup_node, escalate_node, synthesize_node, rationale_node, routing_request

def build_graph():
    conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
    checkpointer = SqliteSaver(conn=conn)

    workflow = StateGraph(AgentState)

    workflow.add_node("Router", router_node)
    workflow.add_node("FAQ", faq_node)
    workflow.add_node("DataLookup", data_lookup_node)
    workflow.add_node("Escalate", escalate_node)
    workflow.add_node("Synthesize", synthesize_node)
    workflow.add_node("rationale_node",rationale_node)
    workflow.set_entry_point("Router")
    workflow.add_conditional_edges("Router",routing_request)
    workflow.add_edge("rationale_node", "DataLookup")
    workflow.add_edge("Escalate", END)
    workflow.add_edge("Synthesize", END)

    # compile
    return workflow.compile(checkpointer=checkpointer)
