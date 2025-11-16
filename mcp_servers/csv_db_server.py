# server.py
# ==========================================================
# Purpose:
#   A compact "MultiTool" MCP server with a companion REST API
#   (FastAPI façade). It exposes:
#     - CSV tools: preview + grouped aggregations
#     - SQLite read-only querying
#     - Web search via DuckDuckGo (HTML scrape)
#     - Web/news search via Tavily API
#     - A tiny guarded Python eval for math expressions
#
# Teaches:
#   - Registering pure-Python functions as MCP tools
#   - Robust path resolution (relative to this file)
#   - Defensive error handling that always returns JSON
#   - Running both REST and MCP side-by-side
# ==========================================================

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import csv, json, os, re, sqlite3, math, requests
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# === FASTMCP SERVER (protocol) ===
# Create the MCP server instance. We pass `stateless_http=True` later in mcp.run().

mcp = FastMCP(name="MultiToolServer")  # pass stateless_http at run()

# ----------------------------------------------------------
# Account Lookup
# ----------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

def account_lookup_impl(account_id: Optional[str] = None, company: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve account plan, tier, CSM, and renewal details by account_id or company."""
    # Load data
    df = pd.read_csv("../data/tools/accounts.csv")

    # Validate input
    if not account_id and not company:
        return {"error": "Please provide either account_id or company name."}

    # Apply filter
    if account_id:
        result = df[df["account_id"].astype(str).str.lower() == str(account_id).lower()]
        flag = "account_id"
    else:
        result = df[df["company"].str.lower() == company.lower()]
        flag = "company"

    # Handle not found
    if result.empty:
        return {"flag": flag, "message": "No matching record found."}

    # Prepare response
    record = result.iloc[0]
    return {
        "flag": flag,
        "account_id": record["account_id"],
        "company": record["company"],
        "plan": record["plan"],
        "tier": record["tier"],
        "csm": record["csm"],
        "renewal_date": record["renewal_date"],
        "billing_cycle": record["billing_cycle"],
        "source": "accounts.csv"
    }

# ----------------------------------------------------------
# Invoice Lookup
# ----------------------------------------------------------
def invoice_status_impl(account_id:str, period_start:str, period_end:str, invoice_id:str):
    """
    Look up invoice details and status by account_id, period, or invoice_id.
    """
    # Load data
    df = pd.read_csv("../data/tools/invoices.csv")
    # If invoice_id provided, match directly
    if invoice_id:
        result = df[df['invoice_id'] == invoice_id]
    
    # If account_id + period provided
    elif account_id and period_start and period_end:
        try:
            result = df[
                (df['account_id'] == account_id) &
                (df['period_start'] >= period_start) &
                (df['period_end'] <= period_end)
            ]
        except Exception:
            return {"error": "Invalid date format for period."}
    
    # If only account_id provided
    elif account_id:
        result = df[df['account_id'] == account_id]
    
    else:
        return {"error": "Please provide at least one of: invoice_id, account_id, or period."}
    
    # If no match found
    if result.empty:
        return {"message": "No matching invoice found."}
    
    # Convert DataFrame to a readable structure
    invoices = result.to_dict(orient='records')
    return {"invoices": invoices, "source":"invoice.csv"}

# ----------------------------------------------------------
# Ticket Summary Lookup
# ----------------------------------------------------------
def ticket_summary_impl(account_id, top_n=5, window_days=90):
    """
    Fetch top N tickets and SLA risk tickets for a given account_id.

    Parameters:
        account_id (str/int): Account identifier to filter
        top_n (int): Number of most recent tickets to return
        window_days (int): Lookback window in days (default=90)

    Returns:
        dict: {
            "account_id": str,
            "recent_tickets": [ {...}, {...} ],
            "sla_risks": [ {...}, {...} ]
        }
    """

    # Load and clean data
    df = pd.read_csv("../data/tools/tickets.csv")
    df['opened_on'] = pd.to_datetime(df['opened_on'], errors='coerce')

    # Filter by account and time window
    cutoff_date = datetime.now() - timedelta(days=window_days)
    df_filtered = df[(df['account_id'] == account_id) & (df['opened_on'] >= cutoff_date)]

    # Sort by recency
    recent_tickets = df_filtered.sort_values(by='opened_on', ascending=False).head(top_n)

    # Define SLA risk logic
    sla_risks = df_filtered[
        ((df_filtered['priority'].str.lower() == 'high') & (df_filtered['status'].str.lower() != 'closed')) |
        ((datetime.now() - df_filtered['opened_on']).dt.days > 7)  # open >7 days = SLA risk
    ]

    # Format outputs
    result = {
        "account_id": account_id,
        "recent_tickets": recent_tickets.to_dict(orient='records'),
        "sla_risks": sla_risks.to_dict(orient='records'),
        "source":"tickets.csv"
    }

    return result

# ----------------------------------------------------------
# Usage Report Lookup
# ----------------------------------------------------------
def usage_report_impl(account_id: str, month: str):
    """
    Lookup API, email, and storage usage for a given account_id and month.
    """

    # Read usage CSV
    usage_df = pd.read_csv("../data/tools/usage.csv")

    # Filter by account_id and month
    usage = usage_df[
        (usage_df["account_id"] == account_id) &
        (usage_df["month"] == month)
    ]

    if usage.empty:
        return f"No usage record found for account_id={account_id} in month={month}"

    record = usage.iloc[0]

    return {
        "account_id": str(record["account_id"]),
        "month": str(record["month"]),
        "api_calls": int(record["api_calls"]),
        "email_sends": int(record["email_sends"]),
        "storage_gb": float(record["storage_gb"]),
        "source": "usage.csv"
    }


# ----------------------------------------------------------
# REGISTER functions as MCP tools (names shown to clients)
# ----------------------------------------------------------
mcp.tool(name="account_lookup", description="Account lookup")(account_lookup_impl)
mcp.tool(name="invoice_status", description="Invoice lookup")(invoice_status_impl)
mcp.tool(name="ticket_summary", description="Ticket summary lookup")(ticket_summary_impl)
mcp.tool(name="usage_report", description="Usage report lookup")(usage_report_impl)

# ----------------------------------------------------------
# REST FACADE (FastAPI) on port 3001
# ----------------------------------------------------------
def start_rest_facade():
    from fastapi import FastAPI, Body
    import uvicorn

    app = FastAPI(title="MCP MultiTool REST Facade")

    @app.post("/tools/account_lookup")
    def http_account_lookup(payload: Dict[str, Any] = Body(...)):
        return account_lookup_impl(**payload)

    @app.post("/tools/invoice_status")
    def http_invoice_status(payload: Dict[str, Any] = Body(...)):
        return invoice_status_impl(**payload)

    @app.post("/tools/ticket_summary")
    def http_ticket_summary(payload: Dict[str, Any] = Body(...)):
        return ticket_summary_impl(**payload)

    @app.post("/tools/usage_report")
    def http_usage_report(payload: Dict[str, Any] = Body(...)):
        return usage_report_impl(**payload)

    # Blocks the thread while serving; we'll run it in a daemon thread instead.
    uvicorn.run(app, host="127.0.0.1", port=3001, log_level="info")

# ----------------------------------------------------------
# Entry point: run REST façade (background) + MCP server
# ----------------------------------------------------------

if __name__ == "__main__":
    # Start REST facade in background
    import threading
    t = threading.Thread(target=start_rest_facade, daemon=True)
    t.start()

    # Start MCP server (new API wants stateless_http here)
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=3000
    )