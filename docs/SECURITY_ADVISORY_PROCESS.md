# Handling a security advisory

How a maintainer takes a reported vulnerability from a private report to a released
fix. Reporters should read [SECURITY.md](../SECURITY.md) instead; this is the other
side of that process.

The order below is not a preference. GitHub's advisory tooling enforces most of it,
and the two places where people get it wrong have opposite costs: publishing too late
blocks nothing but leaves the fix sitting in the open, while syncing the public fork
too early hands the patch to anyone watching it.

Every command here was used on GHSA-qcgh-vq3j-cm8w, the first advisory this project
handled end to end.

## 1. Open a draft advisory

```bash
gh api --method POST repos/sktelecom/onot/security-advisories --input advisory.json
```

`advisory.json` carries `summary`, `description`, `cvss_vector_string`, `cwe_ids`, and
`vulnerabilities`. The advisory is created in `draft` state and stays private until
you publish it in step 4.

A report that arrived through GitHub's private vulnerability reporting is already a
draft advisory, so start from it rather than opening a second one.

## 2. Create the temporary private fork

```bash
gh api --method POST repos/sktelecom/onot/security-advisories/<ghsa-id>/forks
```

The response's `full_name` is `sktelecom/onot-<ghsa-id>`. This fork is private and
visible only to the advisory's collaborators. The web UI offers the same button, but
the API works and keeps the whole process scriptable.

## 3. Develop the fix in that fork

Branch off **the temporary fork's `main`**, not off whatever you have checked out.
That `main` mirrors this repository's `main`, so a branch based on anything else drags
unrelated files into the PR diff and makes the fix hard to review.

```bash
git remote add advisory https://github.com/sktelecom/onot-<ghsa-id>.git
git fetch advisory
git checkout -b fix/<slug> advisory/main
# write the fix, or cherry-pick it if you prototyped elsewhere
git push advisory fix/<slug>
gh api --method POST repos/sktelecom/onot-<ghsa-id>/pulls \
  -f base=main -f head=fix/<slug> -f title='fix: ...'
```

CI does not run on this fork. It belongs to the organization and is covered by the
same Actions outage described in [CONTRIBUTING.md](../CONTRIBUTING.md), and the public
fork used for normal verification is no help here because pushing the patch there
would disclose it. Verify locally instead: the checks under **Running checks**, plus a
reproduction of the reported behavior before and after the patch.

Keep the PR to the fix and its tests. Version bumps and the `CHANGELOG.md` entry go
with the release in step 5, where they belong to a version number that exists.

## 4. Merge, then publish immediately

Merging the temporary fork's PR lands the patch on **`sktelecom/onot`'s `main`**,
directly. It does not go to the temporary fork's `main`, and there is no later step
that moves it across.

The merge is also a precondition for publishing: GitHub refuses to publish an advisory
while a PR is still open on its temporary fork. So the sequence is merge first, then
publish, and no amount of care reverses it.

This means the patch sits on a public branch before the advisory exists. On
GHSA-qcgh-vq3j-cm8w the merge landed at 03:10:12Z and the advisory published at
03:12:39Z, a gap of two and a half minutes. The window cannot be removed, only kept
short, so publish as soon as the merge completes rather than moving on to other work.

## 5. Release

From here the ordinary release process applies. Bump the versions, add the
`CHANGELOG.md` entry, and follow **Releasing (maintainers)** in
[CONTRIBUTING.md](../CONTRIBUTING.md).

While Actions is unavailable on this repository the release runs from the public fork,
and syncing that fork is what publishes the patch to a wide audience. Do not sync it
before step 4 is complete. After publication the fix is disclosed anyway, so the
normal path is safe again.
