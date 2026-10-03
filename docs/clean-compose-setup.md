# Isolated Compose setup validation

The user selected a **separate Compose project on this host**, replacing the VM
requirement, then clarified that installation must follow a documented on-prem
operator workflow. Docker Compose is the only environment manager. The selected
workflow is now verified: see [setup evidence](../evidence/clean-compose-20261002/summary.md)
and the [operator runbook](on-prem-runtime.md).

The execution plan and observed disposition were:

1. Supply checksummed runtime artifacts, source/configuration and separate retained
   acceptance evidence. Use the existing approved JARs explicitly; do not require
   an operator to rebuild from sibling Git repositories or a Maven cache.
2. Install under `C:\opendev\clean-validation\20261002\equipment`, with project
   `equipment-onprem`, port offset 10000, fresh credentials/realm/databases and
   separate project network/volume. Preserve the original stack and evidence.
3. Verify exact supplied JARs, embedded Framework and business configuration before
   initializing local runtime. Install version-pinned Python dependencies into a
   fresh venv and Playwright Chromium through its documented install command.
4. Validate rendered Compose project, ports, bind sources, volume and disabled
   provider credential without printing secrets; start through the explicit
   project/overlay command. Run readiness and sequential Maya/Luis PKCE login.
5. Run full offline acceptance. Record and fix actual setup failures without
   changing approved replay or assertions. The first run exposed Python's missing
   initial database; application startup now creates the schema before health.
   Retain the failed run and deploy the fix only to the new project.
6. Verify both new database schemas were empty before the corrected acceptance.
   The run passed 311 checks, 56 assertions and 96 focused tests with zero paid
   calls. Export all 11 fresh-result directories and distinguish them from 2,512
   imported evidence files. Verify retained stack IDs, packages, rows and protected
   original files remain unchanged.

| Service | Isolated host port | Retained host port |
| --- | --- | --- |
| Keycloak | 28080 | 18080 |
| Java API | 28081 | 18081 |
| Python API | 28082 | 18082 |
| Sidecar API | 28083 | 18083 |
| Fixture control | 28090 | 18090 |
| Sidecar readiness | 29091 | 19091 |
| PKCE callback | 28765 | 18765 |

Both projects remain running and provider-disabled. The retained Python image
remains original; the schema-startup fix is active only in the new project. No VM,
cloud resource, Maven build, published release or paid model call was performed.

The host's Windows, Docker engine, Python installation and existing download/build/
browser caches are explicit prerequisites. This proves a fresh project runtime
installation from supplied artifacts; it does not prove a fresh Windows/toolchain
install, an uncached dependency download or source-build reproducibility. The user
will release Framework/Sidecar next so published assets can be pinned and
revalidated. Java's stronger continuity-priority response remains inconclusive,
and full delivery remains undeclared. Broader load/publication/restart/shutdown/CI
remain outside scope.
