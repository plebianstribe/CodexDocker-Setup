# Git Setup (Host + Container-Mountable Credentials)

Use this on the host machine before starting Docker.

## 1) Configure credential storage file

```bash
git config --global credential.helper 'store --file=$HOME/.git-credentials'

read -r -p "GitHub username: " githubUser
read -r -s -p "GitHub PAT: " githubPat
printf '\n'
printf 'protocol=https\nhost=github.com\nusername=%s\npassword=%s\n\n' \
  "$githubUser" "$githubPat" | git credential approve
unset githubPat
```

This writes the HTTPS credential to `$HOME/.git-credentials` before the clone.
The PAT is not echoed in the terminal.

## 2) Clone this repository

```bash
git clone <THIS_REPO_URL>
cd <THIS_REPO_DIR>
```

## 3) Confirm authentication

```bash
git fetch origin
```

The saved PAT will be used automatically.

## 4) Verify token is persisted in the exact file to mount

```bash
ls -l "$HOME/.git-credentials"
grep -n 'github.com' "$HOME/.git-credentials"
```

## 5) Mount the credentials file into Docker

```bash
--volume "$HOME/.git-credentials":/home/.git-credentials:ro
```

Also mount git config:

```bash
--volume "$HOME/.gitconfig":/home/.gitconfig:ro
```

## Security Warnings

- Scope PAT access to only this repository, plus any other repos you explicitly mount for editing in multi-repo runs.
- Use minimum permissions: repository read/write only as needed.
- Do not use broad org-wide or admin scopes unless strictly required.
- Keep backup copies/clones of critical repositories before large automated rebuild/refactor sessions.
