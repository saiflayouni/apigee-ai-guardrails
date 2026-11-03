# Application setup and deployment boundaries

## Existing dependencies

Before starting `app.py`, configure a Model Armor template, Gemini model access, and a reachable Toolbox server. The app loads the named toolset at process startup. Missing configuration or an unreachable Toolbox can prevent startup.

The SQL tools expect `products` and `shipments` tables with the columns referenced by `agent/tools.yaml`. This repository does not yet include their schema or seed data. Obtain the matching schema from your setup or add a reviewed migration before attempting a fresh environment.

## Local application

Copy `agent/.env.example` to `agent/.env`, configure it privately and use Application Default Credentials for Google Cloud APIs. Run `python app.py` inside `agent/`. `GOOGLE_API_KEY` is for the Gemini Developer API in this demo; Model Armor uses Google Cloud credentials separately.

## Toolbox credentials

The password in `agent/tools.yaml` uses `${DB_PASSWORD}` substitution at Toolbox startup. Inject it into the Toolbox server's environment using a secret reference. Do not put an actual value into the YAML or a committed `.env` file. Keep the existing Toolbox server version/schema compatible with this file.

Reference: https://codelabs.developers.google.com/agentic-rag-toolbox-cloudsql (environment substitution). Copy the idea, not a different configuration schema wholesale.

## Update an existing Cloud Run app

Review the currently deployed environment and secret references first. This command deploys source to an existing service; it does not provision SQL, Toolbox, Model Armor, Apigee or the load balancer:

```bash
cd agent
gcloud run deploy secure-scm-agent --source=. --region=YOUR_REGION --project=YOUR_PROJECT
```

No public-access flags are required here. Do not remove or replace existing environment/secret configuration unintentionally. An update to the GitHub source does not automatically update the Cloud Run app or the Toolbox service.

The app runtime image does not need local `.env` or backup files. `.dockerignore` and `.gcloudignore` exclude them from build uploads.

## Browser

Serve `templates/index.html` through the incoming proxy at `/secure-agent/`. Its POST path is `/secure-agent/chat`. Outside the configured demo host, sample preview is enabled by default. Adapt the hostname in the frontend before using another gateway. Real requests from a different origin require an explicit, tested CORS setup.
