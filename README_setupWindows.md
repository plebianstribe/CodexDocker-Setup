# Windows Setup (WSL2 Ubuntu + Docker + Git)

Simplest host setup path on Windows.

## 1) Install WSL2 + Ubuntu

In PowerShell (Admin):

```powershell
wsl --install -d Ubuntu
```

Reboot if prompted, then open Ubuntu and finish user setup.

## 2) Install Docker Desktop (Windows)

- Install Docker Desktop.
- Enable WSL2 backend in Docker Desktop settings.
- Enable integration for your Ubuntu distro.

## 3) Install git in Ubuntu

```bash
sudo apt update
sudo apt install -y git
```

## 4) Configure git credentials in Ubuntu

```bash
git config --global credential.helper 'store --file=$HOME/.git-credentials-codex'
```

## 5) Clone and run this repo from Ubuntu terminal

```bash
git clone <THIS_REPO_URL>
cd <THIS_REPO_DIR>
mkdir -p .codex
cp ~/.codex/config.toml ./.codex/config.toml
```

Build and run are in [README.md](README.md) and [README_dockercommands.md](README_dockercommands.md).
