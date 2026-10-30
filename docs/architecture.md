# Architecture

Placeholder for a rendered architecture diagram. The source lives at
[diagrams/architecture.mmd](diagrams/architecture.mmd) (Mermaid); GitHub
renders it inline below. Swap this for an exported PNG/SVG under
`diagrams/` if you'd rather ship a static image — update the link here
when you do.

```mermaid
flowchart LR
    U([User / Client]) -->|"1 untrusted input"| A[ADK Agent]
    A -->|"Model Armor:\nsanitizeUserPrompt"| MA1[(Model Armor)]
    MA1 --> A

    A -->|"2 tool call + x-api-key"| P[Apigee X Proxy\nagent-tools-proxy]
    P --> VA[VerifyAPIKey]
    P --> SA[SpikeArrest]
    P --> SF[model-armor-sf\nshared flow]
    SF -->|"request + response"| MA2[(Model Armor)]
    SF --> CL[(Cloud Logging)]

    P -->|"3 proxied call"| T[External Tool / API]
    T -->|"3 raw tool response"| P
    P -->|"back through shared flow"| A

    A -->|"4 after_tool_callback\nre-check before model sees it"| MA3[(Model Armor)]
    MA3 --> A
    A -->|"sanitizeModelResponse"| MA4[(Model Armor)]
    MA4 --> U

    classDef boundary fill:#fff3cd,stroke:#b8860b,stroke-width:1px;
    class U,T boundary
```

See the README's [Architecture](../README.md#architecture) and
[Threat model](../README.md#threat-model-four-trust-boundaries) sections
for what each numbered boundary enforces.
