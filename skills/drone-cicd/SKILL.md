---
name: drone-cicd
description: Configure Drone CI/CD pipelines for a self-hosted Docker runner and Compose deployment.
disable-model-invocation: true
---

# Drone CI/CD

Build a repository-specific pipeline from inspected local evidence. Read the project's ownership and deployment constraints before changing files. A request for configuration does not itself require publishing images, restarting production, or creating credentials.

## Inspect the target

Find sibling `.drone.yml`, Dockerfile, Compose and deployment scripts using `rg --files --hidden`, excluding `.git`, dependencies and secrets. Read at least one deployed sibling matching the intended stack. Inspect runner mounts and network names with selected `docker inspect` fields; avoid dumping environment variables or credential files.

For this machine's conventions and prior pitfalls, read [references/host-pattern.md](references/host-pattern.md). Treat its names as observations to verify, not universal defaults.

Identify these concrete inputs before finalizing dependent configuration:

- Runner type and location, host Docker access, registry namespace and credentials source.
- Events/branches that run checks versus deploy. Respect explicit user choices; feature branches must not accidentally deploy production.
- Build/runtime versions, lockfiles, test database lifecycle, and frontend build-time variables.
- Application ports, database network/address, deployment directory and environment file ownership.

Continue independent implementation while unknown values are clarified. Credential values belong in Drone secrets or protected host files; ask for readiness or paths rather than values in chat. Finish code and validation before requesting any remaining external setup.

## Implement

Use Drone's checkout as the build source. Tag releases by commit SHA and deploy that exact tag. A persistent host checkout is unnecessary when Compose deploys images; if a workflow needs one, a failed checkout must fail the release.

Keep multi-line shell logic in checked-in scripts with `set -eu`. Drone preprocesses `${...}` inside YAML, but not separate script files. Use `$${...}` for shell variables that must remain in YAML. Send registry passwords through stdin and put Docker login configuration in a temporary directory removed on exit.

Run checks before publication and deployment. With host socket access, limit execution to trusted repository code; enabling PR secrets does not make untrusted code safe. Validate host-volume pipelines with `drone lint --trusted`. Serializing the deployment pipeline prevents overlapping migrations; runner capacity alone is not a per-project release lock.

Separate build-time public frontend keys from backend runtime secrets. Containerized servers must listen on a reachable interface. Serve frontend assets with a same-origin API proxy when the application uses relative `/api` URLs.

Use existing database services through their reachable network, with separate production database/role. Apply committed migrations as an explicit one-shot step before starting the new release. Stop on migration failure. Preserve runtime secrets between releases. Health checks must traverse the deployed service path; describe what they do not verify, such as real OAuth login. Application rollback does not roll back database migrations.

## Validate and hand off

Validate YAML, shell syntax and Compose interpolation without printing secrets. Build the actual container targets and run database tests under the intended Docker topology. Check that runtime images exclude test authentication code and that `.dockerignore` excludes `.env`, dependencies and build artifacts. Prefer targeted temporary environments over running a production deployment to test configuration.

Record files changed, checks actually executed, branch/event behavior, required secret names, host preparation, and remaining activation steps. Distinguish generated configuration, locally exercised containers and an observed successful Drone deployment. Do not report one as another.

When installing this skill for Codex, maintain the source directory in `.cc-switch/skills` and use a directory symlink in `.codex/skills`; preserve an existing conflicting entry and resolve it explicitly instead of overwriting it.
