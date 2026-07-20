# Ports Skill Reference

Use this file as the canonical port map for Docker runs in this repository.

## Host to Container Port Map

- `18888:8888` - JupyterLab UI (markdown preview, file browser, notebook editing)
- `18000:8000` - Flask/FastAPI app server
- `13000:3000` - React/Next.js dev server (common default)
- `15173:5173` - Vite dev server
- `17860:7860` - Gradio UI
- `18501:8501` - Streamlit UI
- `18080:8080` - `llama.cpp` HTTP API or other local web API on 8080
- `11434:11434` - Ollama API

## JupyterLab Multi-Repo Notes

- Mount setup repo at `/workspace`.
- Mount external/target repo at `/app`.
- Start JupyterLab with `--ServerApp.root_dir=/` so both mount points are visible in one tree.
- Recommended host URL: `http://localhost:18888`.
