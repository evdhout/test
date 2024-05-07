# Problem committing git notebooks

Git notebooks with output are hard for version control.
So before committing a jupyter notebook, strip it. 

Set up a filter in the repository by running

    git config filter.strip-notebook-output.clean 'jupyter nbconvert --ClearOutputPreprocessor.enabled=True --to=notebook --stdin --stdout --log-level=ERROR'

Create a .gitattributes file inside the directory with the notebooks:

    *.ipynb filter=strip-notebook-output 

Works at least on MacOS with `pip install jupyter` in a `conda` environment    

Remarks

- .gitattributes in repository
- every team member must add the filter 
- still need to check windows en VSCode


Source : https://stackoverflow.com/questions/28908319/how-to-clear-jupyter-notebooks-output-in-all-cells-from-the-linux-terminal/58004619#58004619

Source : https://gist.github.com/33eyes/431e3d432f73371509d176d0dfb95b6e?permalink_comment_id=4662892
