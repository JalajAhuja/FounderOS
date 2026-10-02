# Deployment

Run the API from `founder` with `uvicorn founder.api.main:app --reload`, and the frontend from `frontend` with `npm install` followed by `npm run dev`. Qdrant and Neo4j are configured by the existing environment settings. Keep credentials in local environment/configuration files, never in source.