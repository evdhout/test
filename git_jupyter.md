# Problem committing git notebooks

Git notebooks with output are hard for version control.
So before committing a jupyter notebook, strip it. 

Set up a filter in the repository by running

    git config filter.strip-notebook-output.clean 'jupyter nbconvert --ClearOutputPreprocessor.enabled=True --to=notebook --stdin --stdout --log-level=ERROR'

Create a .gitattributes file inside the directory with the notebooks:

    *.ipynb filter=strip-notebook-output 

Works at least on MacOS with `pip install jupyter` in a `conda` environment    

## Remarks

- .gitattributes in repository
- every team member must add the filter 
- still need to check windows en VSCode
- to remove old outputs use `git add --renormalize .` and commit

## Problem with git pull

When pulling the repository which had jupyter notebooks with output, I got an error:

    Your local changes to the following files would be overwritten by merge:

A checkout of the source notebook, did not solve it. Fixed it with:

```git
    git fetch --all
    git checkout --hard origin/main
```

## Sources

- https://stackoverflow.com/questions/28908319/how-to-clear-jupyter-notebooks-output-in-all-cells-from-the-linux-terminal/58004619#58004619
- https://gist.github.com/33eyes/431e3d432f73371509d176d0dfb95b6e?permalink_comment_id=4662892
- https://saturncloud.io/blog/how-to-force-git-pull-to-overwrite-local-files/