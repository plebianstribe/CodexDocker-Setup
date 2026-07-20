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
export codexProjDir="exampleCodexProject"
mkdir -p -- "../$codexProjDir"

docker run -it \
  --name codex-uv-min \
  --env-file "$PWD/.env" \
  -p 18888:8888 \
  --volume "$PWD":/workspace \
  --volume "$PWD/../$codexProjDir":/app \
  codex-uv:minimal
```

## Current Setup

You are now ready to run a local Codex sandbox with your project folder mounted
at `/app` and the Codex skills and helper scripts available under `/workspace`.

## More

Use these guides when you want to extend the basic local setup:

| Guide | Location | When to use it |
| --- | --- | --- |
| Docker commands | [`others/README_dockercommands.md`](others/README_dockercommands.md) | Use a CUDA image instead of the minimal image when your project needs GPU acceleration. The guide provides build and run commands for CUDA 12.0, 12.9, and 13.0. |
| Git setup | [`others/README_gitsetup.md`](others/README_gitsetup.md) | Use this when you want Codex to push local branches directly to a remote repository. Git needs the host's `.gitconfig` and `.git-credentials-codex` files mounted inside the container; the guide explains how to create and mount them. |
| Windows setup | [`others/README_setupWindows.md`](others/README_setupWindows.md) | Start here when your host is Windows and you need to prepare WSL2, Docker Desktop, Ubuntu, Git, and the repository before following the main setup. |
| Example project | [`others/README_exampleCodexProject.md`](others/README_exampleCodexProject.md) | Use this when you want a starter task for the `exampleCodexProject` folder. It explains how to copy in a brief for an author citation and PDF keyword explorer. |

## Maintained Scripts

| Script | Purpose |
| --- | --- |
| `createcodexconfig.sh` | Generates `.codex/config.toml` from `.env`. |
| `docker_entrypoint.sh` | Validates the container environment, prepares Python dependencies, and starts tmux. |
| `uv_setup.sh` | Initializes a uv project when needed and imports a requirements file when present. |
| `startjupyter.sh` | Starts the JupyterLab server installed in the Docker images. |
| `user_verification_and_gitpush.sh` | Prints branch comparison and manual integration commands. |
