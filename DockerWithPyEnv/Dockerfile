# Build args let you align image CUDA + PyTorch wheel to your host driver support.
ARG CUDA_TAG=12.1.1-cudnn8-runtime-ubuntu22.04
FROM nvidia/cuda:${CUDA_TAG}

ARG PYTHON_VERSION=3.12.12
ARG PYENV_ENV_NAME=mainEnv
ARG TORCH_CUDA_CHANNEL=cu121

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home \
    CODEX_HOME=/home/.codex \
    PYENV_ROOT=/root/.pyenv \
    PATH=/root/.pyenv/shims:/root/.pyenv/bin:${PATH}

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git tmux nodejs npm rsync nano \
    python3 python3-pip python3-venv python-is-python3 \
    wget perl ripgrep tree jq less unzip zip procps file \
    net-tools iputils-ping build-essential pkg-config \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
    libffi-dev liblzma-dev libzstd-dev \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @openai/codex

RUN curl -fsSL https://pyenv.run | bash
RUN git clone https://github.com/pyenv/pyenv-virtualenv.git ${PYENV_ROOT}/plugins/pyenv-virtualenv
RUN echo 'export PYENV_ROOT=/root/.pyenv' >> /root/.bashrc && \
    echo 'export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"' >> /root/.bashrc && \
    echo 'eval "$(pyenv init -)"' >> /root/.bashrc && \
    echo 'eval "$(pyenv virtualenv-init -)"' >> /root/.bashrc

RUN bash -lc 'set -euo pipefail; \
    eval "$(pyenv init -)"; \
    eval "$(pyenv virtualenv-init -)"; \
    pyenv install -s "${PYTHON_VERSION}"; \
    if ! pyenv virtualenvs --bare | grep -x "${PYENV_ENV_NAME}" >/dev/null 2>&1; then \
      pyenv virtualenv "${PYTHON_VERSION}" "${PYENV_ENV_NAME}"; \
    fi; \
    pyenv global "${PYENV_ENV_NAME}"; \
    python -m pip install --upgrade pip; \
    pip install --index-url "https://download.pytorch.org/whl/${TORCH_CUDA_CHANNEL}" torch torchvision torchaudio; \
    python --version; \
    python -c "import torch; print(torch.__version__)"'

RUN bash -lc 'set -euo pipefail; pyenv global "${PYENV_ENV_NAME}"; pip install jupyterlab'

RUN mkdir -p /opt/pyenv_seed && cp -a ${PYENV_ROOT}/. /opt/pyenv_seed/

WORKDIR /workspace
RUN mkdir -p /home/.codex /root/.codex && chmod 700 /home/.codex /root/.codex
COPY tmux.conf /etc/tmux.conf
COPY scripts/envvar_checker.sh /usr/local/bin/envvar_checker.sh
COPY scripts/docker_entrypoint_pyenv.sh /usr/local/bin/docker_entrypoint_pyenv.sh
RUN chmod +x /usr/local/bin/envvar_checker.sh /usr/local/bin/docker_entrypoint_pyenv.sh

EXPOSE 8888 8000 3000 5173 7860 8501 8080 11434

ENTRYPOINT ["/usr/local/bin/docker_entrypoint_pyenv.sh"]
