# preparing a source snapshot

this is a generic checklist for publishing a source-only project snapshot.
keep a candidate repository private until its files, identity, tests and online
state have been reviewed.

1. make and verify a local backup outside any working folder that gets pushed.
2. copy an explicit list of approved source files into an empty folder. leave
   out Git metadata, ignored output, recordings, credentials and environments.
3. read the documents and example data. examples must be clearly labelled as
   invented; do not describe proposed hardware work as a measured result.
4. initialise that folder and configure a non-identifying commit name plus the
   GitHub noreply address verified in the account settings.
5. make one initial commit and inspect both author and committer identities.
6. audit every candidate file and the complete candidate history, then run the
   simulation check. stop on a finding or an unverified result.
7. create an empty private repository with a distinct name. push only the
   approved candidate, then verify the commit, files and private visibility.
8. review the online issues and project text separately before publication.

from the candidate folder:

```powershell
git init -b main
git config --local user.name 'rover contributor'
git config --local user.email 'YOUR_VERIFIED_GITHUB_NOREPLY_EMAIL'
git add --all
git commit -m 'start with the laptop simulation'
git log --all --format='%h %an <%ae> | %cn <%ce> | %s'
python -m simulation.check
```

replace the email placeholder before committing. verify that both identities
use that address. audit reports and local backups stay outside the published
source. keep the repository private until publication is explicitly authorised.
