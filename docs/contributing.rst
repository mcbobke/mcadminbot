Contributing
============

Pull requests are happily welcomed for any additions or improvements! Please be sure to update appropriate documentation as needed.

This project is managed through `Poetry <https://python-poetry.org/>`_. Please ensure that project dependences and metadata are managed with this tool.

How Release Versions are Determined
-----------------------------------

The `mathieudutour/github-tag-action <https://github.com/mathieudutour/github-tag-action>`_ GitHub Action to determine the next version on release. Read the `Bumping <https://github.com/mathieudutour/github-tag-action#bumping>`_ section to find details about the process and be sure to read `Anglular's Git Commit Guidelines <https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines>`_ for specifics about commit message format.

CI/CD Execution Path
--------------------

This project's GitHub Actions test/release/publish pipeline is driven by commit messages that start with a commit (merge or otherwise) into the master branch.

The steps are:

1. A commit is made to the master branch. If the commit message contains "!skipci" then execution stops.
2. For each specified version of Python:
    1. The master branch is checked out.
    2. Python is installed.
    3. Poetry is installed and virtual environments are disabled.
    4. The csystemd Python module's build dependencies are installed.
    5. Other project Python dependencies are installed.
    6. Tests are run.
3. If the commit message contains "!release" then the version of the project is incremented.
    1. The master branch is checked out using a GitHub personal access token to allow pushing to a protected branch.
    2. The next version is determined with the `mathieudutour/github-tag-action <https://github.com/mathieudutour/github-tag-action>`_ GitHub Action. A dry run is used to prevent tagging at this time.
    3. The old version is replaced with the new version in each file that includes it.
    4. The changes are committed to master with "!versionbump" and "!skipci" in the commit message.
4. If the version change commit that includes "!versionbump" in the message was made, finalize the new version.
    1. The master branch is checked out using a GitHub personal access token to allow pushing to a protected branch. Ensure that the ref "master" is targeted to include the latest commit; otherwise, this would only check out the commit that the current pipeline was triggered by.
    2. Tag the latest commit with the new version number.
5. The tag triggers a release workflow.
    1. Check out the tag.
    2. Install Python.
    3. Install Poetry.
    4. Turn off Poetry virtual environments.
    5. Build release binaries with Poetry.
    6. Create a draft release on GitHub using the tag.
    7. Upload the release binaries to the newly-created release.
6. When the release is published, a publish workflow is triggered.
    1. Check out the tag (commit) of the published release.
    2. Install Python.
    3. Install Poetry.
    4. Turn off Poetry virtual environments.
    5. Build release binaries with Poetry.
    6. Configure the PyPI API key in Poetry.
    7. Publish to PyPI with Poetry.