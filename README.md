# math-rag

## Setup
- `export GITHUB_PERSONAL_ACCESS_TOKEN=...`
- `echo $GITHUB_PERSONAL_ACCESS_TOKEN | docker login ghcr.io -u Luka958Pixion --password-stdin`
- `mkdir -p .ssh`
- `ssh-keygen -t ed25519 -f .ssh/id_ed25519 -C "math-rag-key"`

## Environment
Create `.env` file with the following variables:
- `HOST=0.0.0.0`
- `API_PORT=7100`
- `MCP_PORT=7200`
- `JUPYTER_PORT=7035`
- `KATEX_PORT=7025`
- `APPTAINER_PORT=7015`
- `MINIO_ENDPOINT=minio:9000`
- `MINIO_ACCESS_KEY=admin`
- `MINIO_SECRET_KEY=password`
- `MONGO_HOST=mongodb://root:password@mongo:27017/`
- `MONGO_DEPLOYMENT=develop`
- `NEO4J_URI=neo4j://neo4j:7687`
- `NEO4J_USERNAME=neo4j`
- `NEO4J_PASSWORD=password`
- `QDRANT_URL=http://qdrant:6333`
- `HPC_USER`
- `HPC_HOST`
- `HPC_PASSPHRASE`
- `OPENAI_BASE_URL=https://api.openai.com/v1`
- `OPENAI_API_KEY`
- `HF_BASE_URL=https://huggingface.co`
- `HF_USERNAME`
- `HF_TOKEN`
- `MATHPIX_APP_ID`
- `MATHPIX_APP_KEY`
- `MATHPIX_URL=https://api.mathpix.com`

Create `.env.hpc` file with the following variables:
- `HF_USERNAME`
- `HF_TOKEN`
- `WANDB_API_KEY`
- `WANDB_PROJECT=math-rag`

## Run
- `poetry run python -m math_rag.main`

## Model Context Protocol

### Claude Desktop
- `npm install -g mcp-remote`

Open Claude Desktop and navigate `Claude` > `Settings` > `Developer` > `Edit Config` and add this to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mathrag_solver": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:7200/mcp/"]
    }
  }
}
```

