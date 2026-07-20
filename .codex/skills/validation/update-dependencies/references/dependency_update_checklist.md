# Dependency Update Checklist

- Confirm requested package name and version policy.
- Update all required manifests (`pyproject.toml`, `requirements.txt`).
- Install in active venv (`python -m pip install <pkg>`).
- Verify package/tool availability.
- Run target test command and capture logs.
- Document resulting artifact/log paths.
