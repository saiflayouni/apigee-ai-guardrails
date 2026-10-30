"""Runtime configuration for the agent, loaded from environment variables."""

import os


class Config:
    PROJECT_ID = os.environ["GCP_PROJECT_ID"]
    LOCATION = os.environ.get("GCP_LOCATION", "us-central1")

    # Model Armor template applied directly by the agent (input/output on the
    # model turn). The Apigee shared flow applies its own template to traffic
    # that leaves/enters the proxy — see apigee/sharedflows/model-armor-sf.
    MODEL_ARMOR_TEMPLATE_ID = os.environ["MODEL_ARMOR_TEMPLATE_ID"]

    # Apigee X proxy that fronts every external tool call made by the agent.
    APIGEE_PROXY_BASE_URL = os.environ["APIGEE_PROXY_BASE_URL"]
    APIGEE_API_KEY = os.environ["APIGEE_API_KEY"]

    REQUEST_TIMEOUT_SECONDS = float(os.environ.get("REQUEST_TIMEOUT_SECONDS", "10"))
