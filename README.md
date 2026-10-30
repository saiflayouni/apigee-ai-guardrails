# apigee-ai-guardrails

Defense-in-depth for AI agents on Google Cloud: three independent layers
that each assume the others might fail.

Built on top of the Google Codelab
[Secure your AI agent with Model Armor](https://codelabs.developers.google.com/secure-agent-modelarmor),
which covers layers 1 and 3. This repo adds **layer 2**: an Apigee X
proxy sitting between the agent and every external tool/API it calls,
enforcing its own content-safety, rate-limiting, and auth checks
independently of the agent process.

## Architecture

```
User ──▶ ADK Agent ──▶ Apigee X Proxy ──▶ External Tool / API
           │  ▲             │   ▲                 │
      Model Armor      VerifyAPIKey          (your backend)
      (direct API      SpikeArrest
       calls)          model-armor-sf shared flow
           │                 │
   after_tool_callback  Cloud Logging
   (re-check before
    model sees result)
```

| Layer | Where | What it does |
|---|---|---|
| 1. Model Armor (direct) | `agent/model_armor_client.py` | Sanitizes the raw user prompt before the model turn, and the final model response before it reaches the user. |
| 2. Apigee X | `apigee/` | Every tool call the agent makes is routed through an Apigee proxy that validates the API key, applies spike arrest, and runs request/response through a Model Armor shared flow — independently of whatever the agent process does. |
| 3. `after_tool_callback` | `agent/agent.py` | Intercepts raw tool output *after* it returns from the (already-proxied) tool call and *before* the model reads it, re-running Model Armor on it. Catches content that the proxy's template didn't flag, or that originates from a tool not yet routed through Apigee. |

A full diagram lives in [docs/architecture.md](docs/architecture.md).

## Threat model: four trust boundaries

Each layer above exists because a specific boundary can't be trusted to
sanitize itself.

**1. User → Agent (untrusted input).**
The user's prompt is attacker-controlled. Risk: direct prompt injection,
jailbreaks, unsafe content baked into the first turn. Mitigated by
Model Armor's `sanitizeUserPrompt` call before the agent does anything
with the input.

**2. Agent → Apigee proxy (agent-to-gateway).**
The agent process itself could be compromised, misconfigured, or simply
buggy — a bad deploy shouldn't mean tool calls go out unauthenticated or
unbounded. Mitigated by `VerifyAPIKey` (the agent must present a valid
Apigee app key) and `SpikeArrest` (caps call volume regardless of what
the agent's own code does).

**3. Apigee proxy → external tool (gateway-to-tool, both directions).**
The backend tool/API is not fully trusted either way: outbound
arguments could carry injected instructions meant for the backend
(SSRF-ish tool abuse), and the backend's response could carry a
prompt-injection payload meant for the model (e.g. a poisoned
knowledge-base article). Mitigated by the `model-armor-sf` shared flow
running on *both* the request and response legs, with every verdict
logged to Cloud Logging for audit.

**4. Tool output → model context (tool-to-model).**
Even after boundary 3, the proxy's Model Armor template may not match
the agent's own safety bar, and not every tool is guaranteed to be
routed through Apigee in every deployment. `after_tool_callback` is the
last checkpoint before tool output enters the model's context window —
it treats tool output as untrusted input one more time, independent of
what already ran upstream, and can withhold it entirely.

The point of running Model Armor three times (boundaries 1, 3, and 4) is
that each check is enforced by a *different* component, so one
misconfigured or bypassed layer doesn't take down the whole defense.

## Repo layout

```
agent/      ADK agent: after_tool_callback, Model Armor client, tool defs
apigee/     Apigee X proxy bundle + model-armor-sf shared flow bundle
terraform/  Optional: APIs, Model Armor template, Apigee KVM config
docs/       Architecture diagram source + rendered doc
```

## Setup

### Prerequisites

- A GCP project with billing enabled
- An existing Apigee X organization and environment (or set
  `create_apigee_org = true` in `terraform/variables.tf` for a from-scratch
  demo — see the caveats in `terraform/apigee.tf`)
- `gcloud`, [`apigeecli`](https://github.com/apigee/apigeecli), `terraform` (optional), Python 3.11+
- Model Armor API enabled (`modelarmor.googleapis.com`)

### 1. Infra (optional, via Terraform)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # fill in your project id
terraform init
terraform apply
```

This enables the required APIs, creates the Model Armor template, and
seeds the `model-armor-config` KVM the shared flow reads from. Skip it
and create those by hand (`gcloud model-armor templates create`,
`apigeecli kvms create`) if you'd rather not run Terraform against an
existing Apigee org.

### 2. Deploy the Apigee bundle

```bash
cd apigee

# shared flow first — the proxy's FlowCallout policies depend on it
apigeecli sharedflows create -f sharedflows/model-armor-sf/sharedflowbundle \
  --name model-armor-sf --org $APIGEE_ORG --token $(gcloud auth print-access-token)
apigeecli sharedflows deploy --name model-armor-sf --env $APIGEE_ENV \
  --org $APIGEE_ORG --token $(gcloud auth print-access-token) --ovr

apigeecli apis create -f apiproxy --name agent-tools-proxy \
  --org $APIGEE_ORG --token $(gcloud auth print-access-token)
apigeecli apis deploy --name agent-tools-proxy --env $APIGEE_ENV \
  --org $APIGEE_ORG --token $(gcloud auth print-access-token) --ovr
```

Then create an Apigee developer + app to get the API key the agent will
send as `x-api-key` (`apigeecli apps create` / the Apigee UI).

### 3. Run the agent

```bash
cd agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in project id, Model Armor template id,
                       # Apigee proxy URL, and the app key from step 2
adk run agent
```

## Reference

- Base codelab: [Secure your AI agent with Model Armor](https://codelabs.developers.google.com/secure-agent-modelarmor)
- [Model Armor overview](https://cloud.google.com/security-command-center/docs/model-armor-overview)
- [Apigee X shared flows](https://cloud.google.com/apigee/docs/api-platform/fundamentals/shared-flows)
- [ADK: tool callbacks](https://google.github.io/adk-docs/)
