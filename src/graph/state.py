from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    """
    Stores all information the graph needs to remember or share between nodes.
    """
    history: List[str] = Field(
        default_factory=list,
        description="Short summaries of previous turns in the conversation. Helps the graph remember context.",
        example=["User asked about payment", "Agent confirmed Paid"]
    )
    intent: Optional[Literal["FAQ", "DataLookup", "Escalation"]] = Field(
        default=None,
        description="The route or branch chosen for this query.",
        example="DataLookup"
    )
    query: str = Field(
        ...,
        description="The text of the current user message.",
        example="How many seats are left in Agentic AI - Pune?"
    )
    answer: Optional[str] = Field(
        default=None,
        description="The final response generated for this message.",
        example="12 seats left in Agentic AI - Pune."
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="Records data or tool outputs that led to the final answer (for debugging or auditing).",
        example=["sql_inventory → 12 seats left"]
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Captures list oof errors",
        example=["Error while getting payment details"]
    )
