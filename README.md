# Codex Docker Setup

## Setup

```bash
git clone <THIS_REPO_URL>
cd Docker-Codex-EditCopy
cp .env.example .env
```

Fill in `.env`:

```dotenv
CODEX_BASE_URL=<YOUR_API_ENDPOINT>
CODEX_API_KEY=<YOUR_API_KEY>
```

Create the Codex config and build the minimal image:

```bash
./scripts/createcodexconfig.sh
docker build -f Dockerfile_minimal -t codex-uv:minimal .
```

Choose a project directory and run the container:

```bash
export codexProjDir="updatepublic"
mkdir -p -- "../$codexProjDir"

docker run -it \
  --name codex-uv-min \
  --env-file "$PWD/.env" \
  -p 18888:8888 \
  --volume "$PWD":/workspace \
  --volume "$PWD/../$codexProjDir":/app \
  codex-uv:minimal
```

## More

| Guide | Location | Contents |
| --- | --- | --- |
| Docker commands | [`others/README_dockercommands.md`](others/README_dockercommands.md) | CUDA 12.0, 12.9, and 13.0 image build and run commands. |
| Git setup | [`others/README_gitsetup.md`](others/README_gitsetup.md) | Git credentials, authentication, and Docker credential mounts. |
| Windows setup | [`others/README_setupWindows.md`](others/README_setupWindows.md) | WSL2, Docker Desktop, Git, and repository setup. |

## Maintained Scripts

| Script | Purpose |
| --- | --- |
| `createcodexconfig.sh` | Generates `.codex/config.toml` from `.env`. |
| `docker_entrypoint.sh` | Validates the container environment, prepares Python dependencies, and starts tmux. |
| `uv_setup.sh` | Initializes a uv project when needed and imports a requirements file when present. |
| `startjupyter.sh` | Starts the JupyterLab server installed in the Docker images. |
| `user_verification_and_gitpush.sh` | Prints branch comparison and manual integration commands. |
