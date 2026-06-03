# Governance

onot is an open source project jointly developed and maintained by **Kakao** and
**SK telecom**. This document describes how decisions are made and how the project is
run. It is intentionally lightweight and will evolve with the community.

## Roles

### Users

Anyone who uses onot. Users are encouraged to open issues, ask questions in
[Discussions](https://github.com/sktelecom/onot/discussions), and propose changes.

### Contributors

Anyone who contributes code, documentation, tests, or reviews. See
[CONTRIBUTING.md](CONTRIBUTING.md) for how to get started. There is no formal process
to become a contributor — opening a pull request is enough.

### Maintainers

Maintainers are responsible for reviewing and merging changes, triaging issues, and
shepherding releases. They are listed in [CODEOWNERS](.github/CODEOWNERS) and in the
README. The current maintainers are nominated by Kakao and SK telecom.

Maintainers are expected to:

- Review pull requests in their areas and uphold the quality gate (CI, tests,
  coverage, security checks).
- Act in the project's interest and follow the
  [Code of Conduct](CODE_OF_CONDUCT.md).

## Decision making

Most decisions are made by **lazy consensus**: a proposal (issue or pull request) that
receives no sustained objection within a reasonable period is considered accepted.

- **Code changes** require approval from at least one maintainer who is not the author,
  and all required CI checks must pass before merging (enforced by branch protection).
- **Significant changes** (architecture, public API, breaking changes, new
  dependencies, release policy) should be discussed in an issue first and require
  agreement between the Kakao and SK telecom maintainers.
- If consensus cannot be reached, the maintainers from both organizations decide
  together; ties are resolved by discussion rather than a casting vote.

## Becoming a maintainer

Contributors who have a sustained track record of high-quality contributions and
reviews may be invited to become maintainers by the existing maintainers, with
agreement from both organizations.

## Releases

Releases are tag-driven and automated; see the "Releasing" section of
[CONTRIBUTING.md](CONTRIBUTING.md). Any maintainer may cut a release once `main` is
green and the version and changelog are prepared.

## Changing this document

Changes to governance follow the same pull request process and require agreement
between the Kakao and SK telecom maintainers.
