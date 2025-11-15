# 🧰 Wrap REST façade endpoints as LangChain tools
from langchain_core.tools import tool
from typing import List, Dict, Optional, Literal
from .mcp_client import _post_mcp

@tool
def account_lookup_tool(account_id: Optional[str] = None, company: Optional[str] = None) -> str:
    """ Account lookup via REST façade."""
    return _post_mcp("account_lookup", {"account_id": account_id, "company": company})

@tool
def invoice_status_tool(account_id:str, period_start:str, period_end:str, invoice_id:str) -> str:
    """ Invoice lookup via REST façade."""
    return _post_mcp("invoice_status", {"account_id": account_id, "period_start": period_start, "period_end": period_end, "invoice_id": invoice_id})

@tool
def ticket_summary_tool(account_id, top_n=5, window_days=90) -> str:
    """ Ticket summary lookup via REST façade."""
    return _post_mcp("ticket_summary", {"account_id": account_id, "top_n": top_n, "window_days": window_days})

@tool
def usage_report_tool(account_id: str, month: str) -> str:
    """ Usage lookup via REST façade."""
    return _post_mcp("usage_report", {"account_id": account_id, "month": month})

def get_tools():
    return [account_lookup_tool, invoice_status_tool, ticket_summary_tool, usage_report_tool]