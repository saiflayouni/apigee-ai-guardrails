# Incoming Apigee proxy: configuration inventory

This document records the known running design. It is **not** an exported deployment bundle. Existing `/agent-tools` files in `apigee/` are an earlier scaffold.

## Known flow

- Base path: `/secure-agent`.
- Conditional protection: POST with suffix `/chat`. Keep GET `/` available for the web interface.
- Request steps: JS-PrepareArmor, RF-InvalidInput, SC-ModelArmor, JS-ArmorVerdict, RF-ArmorBlocked, RF-ArmorUnavailable.
- Input payload: the JSON `message` string, validated before inspection.
- SC-ModelArmor calls the configured regional Model Armor template's `sanitizeUserPrompt` operation, using a Google access token.
- The target forwards to the configured Cloud Run base URL, preserving the `/chat` suffix. Target authentication uses a Google ID token with the Cloud Run service URL as audience.
- Deploy the proxy with its designated service account. Configure its Model Armor access and Cloud Run invocation access. The Apigee service agent requires permission to generate tokens for that account.
- Known responses: empty/invalid input 400, `PROMPT_BLOCKED` 403, unavailable verdict 503. Runtime authentication faults may produce a separate 500.

## Export before making this reproducible

1. Identify the currently deployed `secure-agent` revision in the environment.
2. Download/export that revision using the Apigee console.
3. Inspect XML and JavaScript for credentials, environment-specific URLs, template paths and service-account references. Parameterize where needed. Never export tokens or private keys.
4. Store the reviewed bundle in a new clearly named path such as `apigee/secure-agent/apiproxy/`, separate from the older `/agent-tools` scaffold.
5. Record the source revision, required IAM, template configuration and import/deployment instructions.
6. Test it in a separate environment before describing it as reproducible.

Do not claim every model/tool call traverses this proxy. In the current app, Toolbox connections are direct from Cloud Run.
