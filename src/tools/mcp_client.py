from typing import Dict, Any
import json, requests

MCP_BASE = "http://127.0.0.1:3001"

def _post_mcp(tool_name: str, payload: Dict[str, Any]) -> str:
    url = f"{MCP_BASE}/tools/{tool_name}"
    try:
        r = requests.post(url, data=json.dumps(payload), headers={"Content-Type":"application/json"}, timeout=20)
        return r.text if r.status_code == 200 else f"Error: {r.status_code} - {r.text}"
    except Exception as e:
        return f"Error: {e}"