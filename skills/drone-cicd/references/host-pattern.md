# Host observations and integration details

Observed 2026-09-13 on dev-2a1m, the ShareTally development/deployment machine; from another machine, reach it with `ssh dev-2a1m`. Recheck before reuse.

- Existing examples: `/home/simon/Dev/simianwang.me/.drone.yml`, `/opt/repo/who-in-dc-backend/.drone.yml`.
- Drone server 2.27.2 and Docker runner 1.8.5. Runner mounts `/var/run/docker.sock` and `/opt/repo`.
- Existing pattern: GHCR images, host Docker Compose, application directories under `/opt/repo/<project>`.
- PostgreSQL 17.6 container `1Panel-postgresql-kXBk`, network `1panel-network`. Published `127.0.0.1:5432` is for host clients; application containers use the database's Docker network and hostname.
- ShareTally example: `.drone.yml`, `Dockerfile`, `deploy/` under `/home/simon/Dev/share-tally`. The active worktree can contain newer files than that checkout; use `git worktree list` to locate it.
- ShareTally owner chose checks on pushes and deployment only on `main` pushes. Production database recommendation: `share_tally_production`, role `share_tally_app`. Database creation must be checked separately.

## Testcontainers from a Docker step

A Drone workspace path belongs to the step container and may not exist on the Docker host. Build an image containing the test source instead of bind-mounting `/drone/src` into sibling containers.

On this Linux host, the test image can run with `--network host`, the host Docker socket and `TESTCONTAINERS_HOST_OVERRIDE=127.0.0.1`. This lets the test process reach random host ports published by Testcontainers. Do not copy that override into bridge-network or remote-daemon configurations; inspect reachability and select the actual host address there.

Dispose of test containers and application processes even on failures. Keep test identities in a test-only entry point, outside production build output.

## Pitfalls in the older examples

- `latest` makes the deployed revision ambiguous. Use the tested commit SHA.
- `checkout ... || true` hides source mismatches. Build Drone's checkout or fail the synchronization.
- `${VAR}` in YAML is subject to Drone substitution before shell execution. Separate scripts avoid two competing substitution layers.
- Host volume access requires a Trusted repository. A socket grants Docker host control even if the step has no registry secrets.
- A frontend public key is embedded by Vite during build. Setting it only in the runtime container does not update the browser bundle.
- `docker compose up -d` does not prove the application is ready. Use health checks and `--wait`.

## Primary sources

- [Drone triggers](https://docs.drone.io/pipeline/docker/syntax/trigger/): event/branch matching; PR branch filters use the target branch.
- [Drone host volumes](https://docs.drone.io/pipeline/docker/syntax/volumes/host/): trusted-repository requirement.
- [Drone substitution](https://docs.drone.io/pipeline/environment/substitution/): `$${...}` escaping.
- [Drone repository secrets](https://docs.drone.io/secret/repository/): injection and PR defaults.
- [Drone Docker YAML specification](https://docs.drone.io/yaml/docker/): pipeline concurrency and structure.
- [Testcontainers container options](https://node.testcontainers.org/features/containers/): networking and bind-mount constraints.
- [Testcontainers configuration](https://node.testcontainers.org/configuration/): Docker and host overrides.

During ShareTally validation, this host's Docker Hub mirror returned manifest size mismatches for new Node images. The corresponding `public.ecr.aws/docker/library/node` and `nginx` images built successfully without changing Docker daemon settings. Treat this as a diagnosed fallback, not a reason to replace every registry or clear shared caches.
