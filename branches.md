# Branch process

## Create a new branch

Each development step starts with creating a new branch. 
Naming conventions initials-[feature|fix]-[description]

    git checkout -b eh-feature-add-branch-description

## Work on branch and initial commit to remote

    git commit -a -m "Branch first commit
    git push --set-upstream origin eh-feature-add-branch-description

## Continue working on branch and committing changes

    git commit -a -m "More commits"
    git push

## Ready to merge

- Create a pull request on github.
- Teammembers review code and comment / ask questions.
- Work on comments in pull request.

Finally, the dedicated merge team member actually merges the branches. 

