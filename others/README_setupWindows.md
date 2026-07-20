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

Create a fine-grained PAT at <https://github.com/settings/personal-access-tokens>,
limit it to the repositories you need, and grant `Contents: Read and write` only
when pushes are required. Then configure the credential file that can be mounted
into Docker:

```bash
git config --global credential.helper 'store --file=$HOME/.git-credentials-codex'

read -r -p "GitHub username: " githubUser
read -r -s -p "GitHub PAT: " githubPat
printf '\n'
printf 'protocol=https\nhost=github.com\nusername=%s\npassword=%s\n\n' \
  "$githubUser" "$githubPat" | git credential approve
unset githubPat
```

The PAT is saved in this plaintext file without being echoed in the terminal.
Keep the file private.

## 5) Clone and run this repo from Ubuntu terminal

```bash
git clone <THIS_REPO_URL>
cd <THIS_REPO_DIR>
mkdir -p .codex
cp ~/.codex/config.toml ./.codex/config.toml
```

Build and run are in the [main README](../README.md) and [archived Docker commands](README_dockercommands.md).
