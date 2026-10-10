# Tagging a passed milestone

No tags or releases exist yet. Use the [publication checklist](publication.md)
before sharing a snapshot, and tag only evidence that has actually passed.

When a hardware milestone really passes, record its date, exact parts/code,
test setup and results in the issue and a short result file. Update the
changelog and commit those changes with your GitHub noreply identity. Inspect
any evidence for private information before sharing it.

Use these names:

| Tag | Meaning |
| --- | --- |
| `v0.0.1-sim` | Optional laptop simulation checkpoint; no hardware result |
| `p1-m0` through `p1-m8` | The matching actual setup/build milestone has passed |
| `v1.0.0` | Only after the complete Prototype 1 definition of done is met |

For example, **after Pi setup milestone 0 passes**, from a clean current main:

```powershell
git switch main
git pull --ff-only
git status --short
git config --get user.email
git tag -a p1-m0 -m 'prototype 1 milestone 0: Pi SSH setup passed'
git push origin p1-m0
```

The status should be clean and the email should be the GitHub noreply address.
Replace the tag and message for the actual milestone. An annotated tag records
the checkpoint and its message; pushing it creates a tag on GitHub. It does
not by itself create a written GitHub Release.

To make a Release, open the repo's Releases page, choose **Draft a new release**,
select the existing tag and write a short description of what actually passed.
Include the test result and remaining limitations. Mark simulation and incomplete
prototype milestones as **pre-release**. Do not reuse a passed tag for later code;
make a new checkpoint if a fix needs separate recording.

Prototype 1 is finished only when steps 0–8 pass, code and checked wiring are
recorded, a two-minute demo exists, and PID plus the purpose of a later Kalman
filter can be explained. None of that hardware evidence exists yet.

References: [Git annotated tags](https://git-scm.com/docs/git-tag)
and [GitHub release creation](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).
