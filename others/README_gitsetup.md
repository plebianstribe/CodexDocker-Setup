# Git Setup (Host + Container-Mountable Credentials)

Use this on the host machine before starting Docker.

## 1) Configure credential storage file

```bash
git config --global credential.helper 'store --file=$HOME/.git-credentials-codex'
```

This writes HTTPS credentials to `$HOME/.git-credentials-codex` after first authenticated git operation.

## 2) Clone this repository

```bash
git clone <THIS_REPO_URL>
cd <THIS_REPO_DIR>
```

## 3) Force first authenticated operation

```bash
git fetch origin
```

If prompted, use your PAT as password for HTTPS.

## 4) Verify token is persisted in the exact file to mount

```bash
ls -l "$HOME/.git-credentials-codex"
grep -n 'github.com' "$HOME/.git-credentials-codex"
```

## 5) Mount the credentials file into Docker

```bash
--volume "$HOME/.git-credentials-codex":/home/.git-credentials:ro
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
