# When to Use Each Script

Run host-side scripts from the repository root unless a script is explicitly
installed and invoked by a Docker image.

<table>
  <thead>
    <tr>
      <th rowspan="2">Name</th>
      <th colspan="2">Intended use</th>
    </tr>
    <tr>
      <th>Inputs, flags, and conditions</th>
      <th>Outputs and outcomes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>createcodexconfig.sh</code></td>
      <td>
        Run before building or starting a container. By default it reads
        <code>.env</code> from the repository root. An alternative env-file path
        may be supplied as a positional argument. Use <code>--yolo</code> to set
        <code>sandbox_mode = "danger-full-access"</code>, or
        <code>--help</code> for usage. The env file must contain a supported base
        URL; model-related values are optional.
      </td>
      <td>
        Creates or replaces <code>.codex/config.toml</code> and reports the chosen
        base URL. Exits with an error for a missing env file, unsupported flag,
        duplicate env-file arguments, or missing base URL.
      </td>
    </tr>
    <tr>
      <td><code>docker_entrypoint.sh</code></td>
      <td>
        Installed as the Docker image entrypoint; do not normally invoke it on
        the host. It uses <code>/app</code> when that mount exists, otherwise
        <code>/workspace</code>. Pass environment variables with Docker's
        <code>--env-file</code> option.
      </td>
      <td>
        Warns when the API key or Codex config is missing, runs
        <code>uv_setup.sh</code>, forwards supported variables to tmux, and opens
        or attaches to the <code>codex</code> tmux session in the target project.
      </td>
    </tr>
    <tr>
      <td><code>startjupyter.sh</code></td>
      <td>
        Run inside an image that includes JupyterLab. Optional environment
        variables are <code>JUPYTER_IP</code>, <code>JUPYTER_PORT</code>, and
        <code>JUPYTER_TOKEN</code>; defaults are <code>0.0.0.0</code>,
        <code>8888</code>, and no token.
      </td>
      <td>
        Creates links to available workspace and app mounts under
        <code>/home/jupyter</code>, then starts JupyterLab in the foreground. It
        does not create a repository file.
      </td>
    </tr>
    <tr>
      <td><code>user_verification_and_gitpush.sh</code></td>
      <td>
        Run during handoff to print manual review and integration guidance. The
        optional first argument is the repository path and defaults to
        <code>/app</code>. Set <code>ORIGINAL_BRANCH</code> to override the default
        comparison branch, <code>main</code>.
      </td>
      <td>
        Prints original/current branch names, a review diff command, changed
        files from committed branch history, and manual merge/push commands. It
        does not commit, merge, or push anything.
      </td>
    </tr>
    <tr>
      <td><code>uv_setup.sh</code></td>
      <td>
        Normally called by <code>docker_entrypoint.sh</code>. Its optional first
        argument is the project directory and defaults to <code>/workspace</code>.
        It recognizes <code>pipreqs.txt</code>, <code>requirements.txt</code>, or
        <code>reqs.txt</code>, in that priority order.
      </td>
      <td>
        Initializes <code>pyproject.toml</code> when absent. When a recognized
        requirements file has changed, imports it with <code>uv add</code> and
        records its hash in <code>.codex-cache/_uv_requirements.sha256</code>.
        This may also update uv's project and lock files.
      </td>
    </tr>
  </tbody>
</table>
