# CUDA Docker Commands

Run all commands from the repository root after completing the environment setup in the [main README](../README.md).

## Images

| CUDA | Dockerfile | Image | Container |
| --- | --- | --- | --- |
| 12.0 | `others/Dockerfile_cuda120` | `codex-uv:cu120` | `codex-uv-cu120` |
| 12.9 | `others/Dockerfile_cuda129` | `codex-uv:cu129` | `codex-uv-cu129` |
| 13.0 | `others/Dockerfile_cuda130` | `codex-uv:cu130` | `codex-uv-cu130` |

## Build

### CUDA 12.0

```bash
docker build -f others/Dockerfile_cuda120 -t codex-uv:cu120 .
```

### CUDA 12.9

```bash
docker build -f others/Dockerfile_cuda129 -t codex-uv:cu129 .
```

### CUDA 13.0

```bash
docker build -f others/Dockerfile_cuda130 -t codex-uv:cu130 .
```

## Run

Choose the project directory mounted at `/app`:

```bash
export codexProjDir="updatepublic"
mkdir -p -- "../$codexProjDir"
```

### CUDA 12.0

```bash
docker run -it \
  --name codex-uv-cu120 \
  --gpus all \
  --env-file "$PWD/.env" \
  -p 18888:8888 \
  --volume "$PWD":/workspace \
  --volume "$PWD/../$codexProjDir":/app \
  codex-uv:cu120
```

### CUDA 12.9

```bash
docker run -it \
  --name codex-uv-cu129 \
  --gpus all \
  --env-file "$PWD/.env" \
  -p 18888:8888 \
  --volume "$PWD":/workspace \
  --volume "$PWD/../$codexProjDir":/app \
  codex-uv:cu129
```

### CUDA 13.0

```bash
docker run -it \
  --name codex-uv-cu130 \
  --gpus all \
  --env-file "$PWD/.env" \
  -p 18888:8888 \
  --volume "$PWD":/workspace \
  --volume "$PWD/../$codexProjDir":/app \
  codex-uv:cu130
```
