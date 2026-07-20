# Docker Commands (UV Main Flow)

Main flow uses dedicated Dockerfile variants + `uv`.

## Build

### CUDA 12.9 + torch (recommended)
```bash
docker build -f Dockerfile_cuda129 -t codex-uv:cu129 .
```

### CUDA 12.0 + torch
```bash
docker build -f Dockerfile_cuda120 -t codex-uv:cu120 .
```

### CUDA 13.0 + torch
```bash
docker build -f Dockerfile_cuda130 -t codex-uv:cu130 .
```

### Minimal (no torch)
```bash
docker build -f Dockerfile_minimal -t codex-uv:minimal .
```

Optional build override flags:

| Flag | Valid values |
| --- | --- |
| `-t`, `--tag` | Any valid Docker image tag, e.g. `codex-uv:cu129`, `codex-uv:minimal` |
| `--platform` | Docker platform values, e.g. `linux/amd64`, `linux/arm64` |
| `--pull` | `true` (include flag) or omitted |
| `--no-cache` | `true` (include flag) or omitted |
| `--progress` | `auto`, `plain`, `tty` |
| `--build-arg` | Not required for these variant files; omit by default |

## Run (base)
```bash
echo "Host home dir: $HOME"
echo "Repo dir mounted to /workspace: $PWD"

docker run -it \
  --name codex-uv \
  --gpus all \
  --env-file "$PWD/.env" \
  --volume "$PWD":/workspace \
  --volume "$PWD/.codex":/home/.codex \
  codex-uv:cu129
```

## Run (minimal + Jupyter)
```bash
docker run -it \
  --name codex-uv-min \
  --env-file "$PWD/.env" \
  -p 18888:8888 \
  --volume "$PWD":/workspace \
  --volume "$PWD/.codex":/home/.codex \
  codex-uv:minimal
```

Inside container:
```bash
startjupyter.sh
```

Open `http://localhost:18888`. File browser root is `/home/jupyter` and exposes only `workspace` and `app` (if mounted).

## Add-on flags

| Flag | Purpose |
| --- | --- |
| `--volume "$HOME/path/to/repo":/app` | Work on another mounted repo. |
| `--volume "$HOME/.gitconfig":/home/.gitconfig:ro` | Share host git config. |
| `--volume "$HOME/.git-credentials-codex":/home/.git-credentials:ro` | Share host HTTPS token store. |
| `--volume "$HOME/.ssh":/root/.ssh:ro` | Share SSH keys for git over SSH. |
| `-p 18888:8888` | JupyterLab |
| `-p 18000:8000` | Flask/FastAPI |
| `-p 13000:3000` | React/Next dev |
| `-p 15173:5173` | Vite |
| `-p 17860:7860` | Gradio |
| `-p 18501:8501` | Streamlit |
| `-p 18080:8080` | API/UI services |
| `-p 11434:11434` | Ollama |

## Notes

- Runtime scripts live in `scripts/` and are copied by the Dockerfiles.
- The entrypoint picks `/app` if mounted, otherwise `/workspace`.
- Pyenv variant moved to `DockerWithPyEnv/`.
