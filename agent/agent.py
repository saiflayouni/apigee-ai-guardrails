"""ADK agent wiring for the defense-in-depth demo.

Layer 1 (Model Armor, direct):  sanitize_user_input / sanitize_model_output
Layer 2 (Apigee X):              enforced inside tools.py's HTTP calls
Layer 3 (after_tool_callback):   intercept_tool_output, below

Each layer is independent: Apigee's shared flow already ran Model Armor
on this same payload in-flight, and the agent's own template may differ
(stricter categories, different confidence thresholds) from the one the
proxy applies. after_tool_callback is the last checkpoint before a tool
result reaches the model's context window, so it re-checks regardless of
what happened upstream.
"""

from __future__ import annotations

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from config import Config
from model_armor_client import ModelArmorClient
from tools import AGENT_TOOLS

_config = Config()
_model_armor = ModelArmorClient(_config)

SYSTEM_INSTRUCTION = """You are a support agent. Use the available tools to
answer questions about orders and the knowledge base. Never repeat raw tool
output verbatim if it has been flagged as unsafe."""


def sanitize_user_input(user_text: str) -> str:
    """Call this mentally before the model turn starts (see runner wiring)."""
    result = _model_armor.sanitize_prompt(user_text)
    if result.blocked:
        raise ValueError(f"Input blocked by Model Armor: {result.reason}")
    return result.sanitized_text


def sanitize_model_output(model_text: str) -> str:
    result = _model_armor.sanitize_response(model_text)
    if result.blocked:
        return "[response withheld: flagged by Model Armor]"
    return result.sanitized_text


def intercept_tool_output(
    tool,
    args: dict,
    tool_context: ToolContext,
    tool_response: dict,
) -> dict | None:
    """after_tool_callback: runs after a tool returns, before the model sees it.

    This is trust boundary #4 in the README's threat model. A tool sitting
    behind the Apigee proxy can still return attacker-controlled content
    (e.g. a knowledge-base article containing a prompt-injection payload),
    so the raw tool_response is treated as untrusted here exactly like
    external user input.

    Returning None lets ADK use the original tool_response unchanged.
    Returning a dict replaces what the model will see.
    """
    text_payload = str(tool_response)
    result = _model_armor.sanitize_response(text_payload)

    if result.blocked:
        return {
            "status": "blocked",
            "reason": result.reason,
            "detail": "Tool output withheld by after_tool_callback (Model Armor match).",
        }

    return None


root_agent = Agent(
    name="guarded_support_agent",
    model="gemini-2.0-flash",
    instruction=SYSTEM_INSTRUCTION,
    tools=AGENT_TOOLS,
    after_tool_callback=intercept_tool_output,
)
