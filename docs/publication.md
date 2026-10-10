# Preparing a source snapshot

This is a generic checklist for publishing a source-only project snapshot.
Keep a candidate repository private until its files, identity, tests and online
state have been reviewed.

1. Make and verify a local backup outside any working folder that gets pushed.
2. Copy an explicit list of approved source files into an empty folder. Leave
   out Git metadata, ignored output, recordings, credentials and environments.
3. Read the documents and example data. Examples must be clearly labelled as
   invented; do not describe proposed hardware work as a measured result.
4. Initialise that folder and configure a non-identifying commit name plus the
   GitHub noreply address verified in the account settings.
5. Make one initial commit and inspect both author and committer identities.
6. Audit every candidate file and the complete candidate history, then run the
   simulation check. Stop on a finding or an unverified result.
7. Create an empty private repository with a distinct name. Push only the
   approved candidate, then verify the commit, files and private visibility.
8. Review the online issues and project text separately before publication.

From the candidate folder:

```powershell
git init -b main
git config --local user.name 'rover contributor'
git config --local user.email 'YOUR_VERIFIED_GITHUB_NOREPLY_EMAIL'
git add --all
git commit -m 'start with the laptop simulation'
git log --all --format='%h %an <%ae> | %cn <%ce> | %s'
python -m simulation.check
```

Replace the email placeholder before committing. Verify that both identities
use that address. Audit reports and local backups stay outside the published
source. Keep the repository private until publication is explicitly authorised.
