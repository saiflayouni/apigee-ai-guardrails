"""Thin client around the Model Armor API.

Used twice in this architecture's defense-in-depth:
  1. By the agent process itself, on the raw user prompt and the final
     model response (trust boundary #1 in the README).
  2. By the Apigee shared flow (apigee/sharedflows/model-armor-sf), on
     every request/response that crosses the proxy (trust boundary #3).

This module only covers the first case. The proxy-side call is a native
Apigee ServiceCallout, not Python — see
apigee/sharedflows/model-armor-sf/sharedflowbundle/policies/SC-ModelArmorCallout.xml.
"""

from __future__ import annotations

from dataclasses import dataclass

import google.auth
import google.auth.transport.requests
import requests

from config import Config


@dataclass
class SanitizeResult:
    blocked: bool
    reason: str | None
    sanitized_text: str


class ModelArmorClient:
    def __init__(self, config: Config):
        self._config = config
        self._endpoint = (
            f"https://modelarmor.{config.LOCATION}.rep.googleapis.com/v1/"
            f"projects/{config.PROJECT_ID}/locations/{config.LOCATION}/"
            f"templates/{config.MODEL_ARMOR_TEMPLATE_ID}:sanitizeUserPrompt"
        )
        self._response_endpoint = self._endpoint.replace(
            "sanitizeUserPrompt", "sanitizeModelResponse"
        )

    def _auth_headers(self) -> dict:
        credentials, _ = google.auth.default()
        credentials.refresh(google.auth.transport.requests.Request())
        return {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

    def sanitize_prompt(self, text: str) -> SanitizeResult:
        return self._sanitize(self._endpoint, "userPromptData", text)

    def sanitize_response(self, text: str) -> SanitizeResult:
        return self._sanitize(self._response_endpoint, "modelResponseData", text)

    def _sanitize(self, endpoint: str, field_name: str, text: str) -> SanitizeResult:
        payload = {field_name: {"text": text}}
        resp = requests.post(
            endpoint,
            json=payload,
            headers=self._auth_headers(),
            timeout=self._config.REQUEST_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        body = resp.json()

        match_state = body.get("sanitizationResult", {}).get("filterMatchState")
        blocked = match_state == "MATCH_FOUND"

        return SanitizeResult(
            blocked=blocked,
            reason=match_state if blocked else None,
            sanitized_text=text,
        )
