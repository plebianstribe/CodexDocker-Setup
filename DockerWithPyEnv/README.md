# Docker With Pyenv

This variant uses `pyenv` (main flow in repo root uses `uv`).

## Build
```bash
docker build -f DockerWithPyEnv/Dockerfile \
  --build-arg CUDA_TAG=12.9.0-cudnn-runtime-ubuntu24.04 \
  --build-arg TORCH_CUDA_CHANNEL=cu129 \
  --build-arg PYTHON_VERSION=3.12.12 \
  --build-arg PYENV_ENV_NAME=mainEnv \
  -t codex-pyenv:latest .
```

## Run
```bash
echo "Host home dir: $HOME"
echo "Repo dir mounted to /workspace: $PWD"

docker run -it \
  --name codex-pyenv \
  --gpus all \
  --env-file "$PWD/.env" \
  --volume "$PWD":/workspace \
  --volume "$PWD/.codex":/home/.codex \
  --volume "$PWD/docker_pyenv_root":/root/.pyenv \
  codex-pyenv:latest
```

More examples: `DockerWithPyEnv/dockercommands.txt`.
