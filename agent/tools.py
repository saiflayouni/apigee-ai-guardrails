"""Tool definitions.

Every tool call leaves the agent process through the Apigee X proxy
instead of hitting the external API directly. That gives trust boundary
#2 (agent -> gateway) and #3 (gateway -> tool) somewhere to enforce
spike arrest, API key validation, and a Model Armor pass on the
outbound/inbound payloads — see apigee/apiproxy and
apigee/sharedflows/model-armor-sf.
"""

from __future__ import annotations

import requests

from config import Config

_config = Config()


def _call_through_apigee(path: str, params: dict) -> dict:
    response = requests.get(
        f"{_config.APIGEE_PROXY_BASE_URL}{path}",
        params=params,
        headers={"x-api-key": _config.APIGEE_API_KEY},
        timeout=_config.REQUEST_TIMEOUT_SECONDS,
    )

    if response.status_code == 429:
        raise RuntimeError("Rate limited by Apigee spike arrest policy")
    if response.status_code == 401:
        raise RuntimeError("Rejected by Apigee API key validation policy")
    if response.status_code == 403:
        raise RuntimeError("Blocked by Apigee Model Armor shared flow")

    response.raise_for_status()
    return response.json()


def lookup_order_status(order_id: str) -> dict:
    """Example tool: look up an order status through the proxied backend."""
    return _call_through_apigee("/orders/status", {"order_id": order_id})


def search_knowledge_base(query: str) -> dict:
    """Example tool: query a backend search API through the proxy."""
    return _call_through_apigee("/kb/search", {"q": query})


AGENT_TOOLS = [lookup_order_status, search_knowledge_base]
