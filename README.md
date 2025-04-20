# math-rag

## Setup
- `export GITHUB_PERSONAL_ACCESS_TOKEN=...`
- `echo $GITHUB_PERSONAL_ACCESS_TOKEN | docker login ghcr.io -u Luka958Pixion --password-stdin`
- `mkdir -p .ssh`
- `ssh-keygen -t ed25519 -f .ssh/id_ed25519 -C "math-rag-key"`

## Environment
Create `.env` file with the keys defined in `.env.example`.
