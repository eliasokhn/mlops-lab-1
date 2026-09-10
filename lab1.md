Question 1:                             
pyproject.toml: the project configuration
README.md :describe the project how it works
.python-version : Python version used
.gitignore : indicator for git to ignore certain files/folders

Question 2:
uv.lock : 
.dvcignore : indicator to ignore files/folders

question 3:
When using --global, the DVC remote credentials are stored in the user's global DVC configuration rather than inside the project's Git-tracked .dvc/config. Other configuration levels include --local, which stores configuration specific to the current repository but is not committed to Git, and the default project/repository configuration. Credentials should never be pushed to GitHub, because they are secrets. The project can contain the non-secret remote configuration, while credentials should remain private.

question4:
After running dvc add data, DVC adds the /data directory to .gitignore. This prevents Git from tracking and uploading the actual image dataset. The dataset will instead be tracked by DVC. Git only tracks the DVC metadata/pointer file

question 5:
Yes. DVC creates a data.dvc file. It contains metadata describing the tracked data directory, including its hash/checksum, path, size and potentially the number of files. It acts as a pointer to the version of the dataset managed by DVC. The small data.dvc file is committed to Git, while the actual dataset is stored through DVC.
PS: the push failed many times

question 6:
Yes, the project code is visible on GitHub. The actual Food-11 dataset is not stored in Git because the data directory is ignored by Git. Instead, GitHub contains data.dvc, which contains metadata identifying the DVC-managed version of the data. After dvc push, the actual data is stored in the configured DagsHub DVC remote and can be accessed through DagsHub.

quwstion 7 :
A fresh Git clone does not contain the DVC-tracked dataset. dvc pull is used to retrieve it from the remote.

question 8:
No. The processed folders disappear when checking out the older Git/DVC version because that old data.dvc points to the earlier dataset state. Returning to main restores the latest version.
