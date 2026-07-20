# Codex Docker Setup

Main flow uses `uv` (not pyenv) with dedicated Dockerfile variants.

## Base Prerequisites (Compulsory)

- Docker installed (`rootless` is OK).
- GitHub account.
- Git installed.
- `gh` CLI (optional, needed if you want to create repos from command line).

## Optional Bare-Metal GitHub Setup (Recommended)

### 1) Create a fine-grained PAT

Go to: `https://github.com/settings/personal-access-tokens`

Configure:
- Token type: Fine-grained.
- Repository access: `Only select repositories` and include this repo plus any other repos you plan to work on.
- Repository permissions: `Contents` = `Read and write`.

### 2) Configure git credential storage

Global (simple):
```bash
git config --global credential.helper 'store --file=$HOME/.git-credentials-codex'
```

Repo-local (isolated to this repo):
```bash
# run inside repo root
git config --local credential.helper 'store --file=.git/.git-credentials'
git config --local user.name "<YOUR_NAME>"
git config --local user.email "<YOUR_EMAIL>"
```

Notes:
- Yes, you can store credentials local to this repo by using a repo-local credential file like `.git/.git-credentials`.
- `git config --local` writes into this repo’s `.git/config` (not your global `~/.gitconfig`).

### 3) Verify config and files

```bash
# check active helpers
git config --show-origin --get-all credential.helper

# verify local repo config exists
test -f .git/config && echo ".git/config exists"

# verify optional local credentials file exists (after first authenticated push/fetch)
test -f .git/.git-credentials && echo ".git/.git-credentials exists"

# verify optional global credentials file exists (if using global helper)
test -f "$HOME/.git-credentials-codex" && echo "$HOME/.git-credentials-codex exists"
```

These are the files you can mount into Docker for direct branch creation, merge, and push from inside the container.

### 4) Create Codex config from `.env` (bare metal)

```bash
# From repo root (auto-reads ./.env)
./scripts/createcodexconfig.sh

# Or pass an explicit env file path
./scripts/createcodexconfig.sh /path/to/.env

# YOLO mode: also write full-permissions sandbox setting
./scripts/createcodexconfig.sh --yolo
```

The script writes `./.codex/config.toml` and auto-uses the first available URL key in this order:
- `CODEX_BASE_URL`
- `REMOTE_URL`
- `REMOTEURL`
- `AZURE_OPENAI_BASE_URL`

When `--yolo` is used, it also writes:
- `sandbox_mode = "danger-full-access"`

Warning:
- Full-permissions mode allows the Codex session to run without supervision.
- It can modify or delete any mounted files, including clearing the entire repo.
- If git credentials are available in the execution environment, it may also perform destructive git operations.
- Before running `--yolo`, create a backup first:
  - minimum: commit and push to a separate backup branch,
  - safer: copy the repo to a separate backup repo/folder that is not mounted into the Docker session.

## Optional: New Repo from CLI (`gh`)

Example project: `CodexProj`

```bash
mkdir CodexProj
cd CodexProj
git init
gh auth login
gh repo create CodexProj --private --source=. --remote=origin --push
```

## Quick Start

### 1) Git credentials and clone (host machine)
```bash
git config --global credential.helper 'store --file=$HOME/.git-credentials-codex'
git clone <THIS_REPO_URL>
cd Docker-Codex-EditCopy
cp .env.example .env
```

Run all remaining commands from the repo root on bare metal:
```bash
cd Docker-Codex-EditCopy
```

### 2) Build
```bash
# CUDA 12.9 + torch (recommended)
docker build -f Dockerfile_cuda129 -t codex-uv:cu129 .

# CUDA 12.0 + torch
docker build -f Dockerfile_cuda120 -t codex-uv:cu120 .

# CUDA 13.0 + torch
docker build -f Dockerfile_cuda130 -t codex-uv:cu130 .

# Minimal (no torch)
docker build -f Dockerfile_minimal -t codex-uv:minimal .
```

Optional build override flags:

| Flag | Valid values |
| --- | --- |
| `-t`, `--tag` | Any valid Docker image tag, e.g. `codex-uv:latest`, `codex-uv:cu129` |
| `--platform` | Docker platform values, e.g. `linux/amd64`, `linux/arm64` |
| `--pull` | `true` (include flag) or omitted |
| `--no-cache` | `true` (include flag) or omitted |
| `--progress` | `auto`, `plain`, `tty` |

### 3) Run (CPU-only image)
```bash
echo "Host home dir: $HOME"
echo "Repo dir mounted to /workspace: $PWD"
mkdir -p ../{codexProj}

docker run -it \
  --name codex-uv-min \
  --env-file "$PWD/.env" \
  -p 18888:8888 \
  --volume "$PWD":/workspace \
  --volume "$PWD/../{codexProj}":/app \
  codex-uv:minimal
```

### 4) Run (GPU-enabled image)
Note: delete `--gpus all` if you did not build a GPU-required/torch-enabled image.
```bash
docker run -it \
  --name codex-uv \
  --gpus all \
  --env-file "$PWD/.env" \
  -p 18888:8888 \
  --volume "$PWD":/workspace \
  --volume "$PWD/../{codexProj}":/app \
  codex-uv:cu129
```

### 5) Start JupyterLab inside container
```bash
/workspace/scripts/startjupyter.sh
```

Then open: `http://localhost:18888`

Jupyter file browser root is `/home/jupyter` and only shows:
- `/home/jupyter/workspace` -> `/workspace`
- `/home/jupyter/app` -> `/app` (when `/app` is mounted)

### Optional flags

| Flag | Use |
| --- | --- |
| `--volume "$HOME/path/to/repo":/app` | Edit another repo from the same container. |
| `--volume "$PWD/.codex":/home/.codex` | Persist Codex config/history on host (optional). |
| `--volume "$HOME/.gitconfig":/home/.gitconfig:ro` | Reuse host git identity/config. |
| `--volume "$HOME/.git-credentials-codex":/home/.git-credentials:ro` | Reuse stored HTTPS token in container. |
| `--volume "$HOME/.ssh":/root/.ssh:ro` | Use SSH auth instead of HTTPS token. |
| `-p 18888:8888 -p 18000:8000 -p 13000:3000 -p 15173:5173 -p 17860:7860 -p 18501:8501 -p 18080:8080 -p 11434:11434` | Common dev/API ports. |

## Read More

- [README_dockercommands.md](README_dockercommands.md): Full docker build/run commands for `Dockerfile_cuda120|129|130|minimal`.
- [README_gitsetup.md](README_gitsetup.md): Token storage, clone, and verification details.
- [README_setupWindows.md](README_setupWindows.md): WSL2 Ubuntu + Docker + Git setup.
- [DockerWithPyEnv/README.md](DockerWithPyEnv/README.md): Pyenv-based alternative flow.
- [PORTS_SKILL.md](PORTS_SKILL.md): Port mapping conventions.
