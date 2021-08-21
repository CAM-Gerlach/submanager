# Contributing Guide

Sub Manager is part of the r/SpaceX Github org, and is developed with standard Github flow.
You should be familiar with the basics of using ``git`` and Github, though this guide walks you through most of the basics of what you need to know to contribute.



<!-- markdownlint-disable -->
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Reporting issues](#reporting-issues)
- [Setting Up a Development Environment](#setting-up-a-development-environment)
  - [Fork and clone the repo](#fork-and-clone-the-repo)
  - [Create and activate a fresh venv](#create-and-activate-a-fresh-venv)
  - [Install Sub Manager in editable mode](#install-sub-manager-in-editable-mode)
  - [Install the required Pre-Commit hooks](#install-the-required-pre-commit-hooks)
- [Running Tests](#running-tests)
- [Git Branches](#git-branches)
- [Submitting a Pull Request](#submitting-a-pull-request)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
<!-- markdownlint-restore -->



## Reporting issues

Discover a bug?
Want a new feature?
[Open](https://github.com/r-spacex/submanager/issues/new/choose) an [issue](https://github.com/r-spacex/submanager/issues)!
Make sure to describe the bug or feature in detail, with reproducible examples and references if possible, what you are looking to have fixed/added.
While we can't promise we'll fix everything you might find, we'll certainly take it into consideration, and typically welcome pull requests to resolve accepted issues.
Thanks!



## Setting Up a Development Environment

**Note**: You may need to substitute ``python3`` for ``python`` in the commands below on some Linux distros where ``python`` isn't mapped to ``python3`` (yet).

### Fork and clone the repo

First, navigate to the [project repository](https://github.com/r-spacex/submanager) in your web browser and press the ``Fork`` button to make a personal copy of the repository on your own Github account.
Then, click the ``Clone or Download`` button on your repository, copy the link and run the following on the command line to clone the repo:

```bash
git clone <LINK-TO-YOUR-REPO>
```

Finally, set the upstream remote to the official Sub Manager repo with:

```bash
git remote add upstream https://github.com/r-spacex/submanager.git
```


### Create and activate a fresh venv

While it can be installed in your system Python, particularly for development installs we highly recommend you create and activate a virtual environment to avoid any conflicts with other packages on your system or causing any other issues.
Using the standard tool ``venv``, you can create an environment as follows:

```bash
python -m venv your-env-name
```

And activate it with the following on Linux and macOS

```bash
source your-env-name/bin/activate
```

or on Windows (cmd),

```cmd
.\your-env-name\Scripts\activate.bat
```

Of course, you're free to use any environment management tool of your choice (conda, virtualenvwrapper, pyenv, etc).


### Install Sub Manager in editable mode

To get the consistent pinned versions of the development dependencies (optional, but recommended), first install the deps from the requirements file,

```bash
python -m pip -r requirements-dev.txt
```

To install the package in editable ("development") mode, where updates to the source files will be reflected in the installed package, and include any additional dependencies used for development, run

```bash
python -m pip install -e .[lint,test]
```

You can then run Sub Manager as normal with the ``submanager`` command, though running with ``python -b -X dev -m submanager`` is recommended to enable Python's development mode for easier debugging, as well as show any warnings your changes cause (note that any warnings, other than the unclosed socket error caused by PRAW, will fail the checks when submitting a pull request, and its usually much easier to find and resolve them early).
When you make changes in your local copy of the git repository, they will be reflected in your installed copy as soon as you re-run it.

While Windows and macOS are supported for development and use alongside Linux, built-in support for running as a system service is not currently included, and is left to the user.


### Install the required Pre-Commit hooks

You'll need to install the pre-commit hooks before committing any changes, as they both auto-generate/update specific files and run a comprehensive series of checks to help you find likely errors and enforce the project's code quality guidelines and style guide; they are also run in CI, and will fail the build if any don't pass or modify any files.
This repository uses [Pre-Commit](https://pre-commit.com/) to install, configure and update a suite of pre-commit hooks that check for common problems and issues, and fix many of them automatically.
Pre-commit itself is installed with the above command, and the hooks should be enabled by running the following from the root of this repo:

```bash
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

The hooks will be automatically run against any new/changed files every time you commit.
It may take a few minutes to install the needed packages the first time you commit, but subsequent runs should only take a few seconds.
If you made one or more commits before installing the hooks (not recommended), you can run them manually on all the files in the repo with:

```bash
pre-commit run --all-files
```

**Note**: Many of the hooks fix the problems they detect automatically (the hook output will say ``Files were modified by this hook``, but no errors/warnings will be listed), but they will still abort the commit so you can double-check everything first.
Once you're satisfied, ``git add .`` and commit again.



## Running Tests

This package uses the [Pytest](https://pytest.org) framework for its unit and integration tests, which are located inside the ``tests/`` directory in the root of the project.
As you might expect, unit tests, which mirror the structure of the package and test individual components, are found in the `unit` subdirectory, while integration tests, which test the functionality of the package as a whole, like in the `integration` subdirectory, and functional tests, which test the package's behavior though the user-facing CLI, are in the `functional` subdirectory.
We **strongly** suggest you run the full test suite before every commit (it should only take around 10 seconds without the online tests), as while our pre-commit suite catches most errors, it is impossible to statically determine whether the code does what it is intended to without a test suite.

Currently, given the project's development status, it has a substantial test suite but is primarily focused on high-level functional testing, with more granular unit and integration tests to be added later.
We ask that, at a minimum, any new commands or CLI options come with functional tests, and welcome contributions of all three kinds of tests for new or existing functionality to expand our coverage, increase reliability, and ensure we don't experience any regressions.
If you need help writing tests, please let us know, and we'll be happy to guide you.

To run the tests (minus the online ones that require network connectivity and an authorized Reddit account to interact with the test subreddit), install the development dependencies as above, and then simply execute

```bash
pytest
```

The ``pytest.ini`` config file sets up a variety of settings and command line options for you, so you shouldn't need to pass any further options to pytest unless you have a specific use case.
To skip the slower tests (most of them are online), run pytest ``-m "no slow"``

```bash
pytest -m "not slow"
```

Finally, to run the online tests, pass ``--run-online``

```bash
pytest --run-online
```

**Note**: The online tests require a PRAW ``site`` named ``testbot`` that has mod access to the r/SubManagerTesting sub and approved user access to the r/SubManagerTesting2 sub, with scopes `modconfig`, `read`, `wikiread`, `edit`, `modwiki`, `submit`, `structuredstyles`, and `wikiedit`, as well as optionally `identity` and `mysubreddits`.
As such, they are normally only run by the core team and the CIs, and you can exercise most of the code by running ``submanager validate-config`` on your local config.
However, if you would like to help with PRAW's development, we can consider giving a user account under your control access to the appropriate subs, so you can run the online tests locally as well by simply configuring the ``testbot`` site in your ``praw.ini`` with the credentials of your user.
Feel free to contact us if you're interested.



## Git Branches

When you start to work on a new pull request (PR), you need to be sure that your work is done on top of the correct branch, and that you base your PR on Github against it.

To guide you, issues on Github are marked with a milestone that indicates the correct branch to use.
If not, follow these guidelines:

* Use the latest release branch (e.g. ``0.3.x`` for bugfixes only (*e.g.* milestones ``v0.3.1`` or ``v0.3.2``)
* Use ``master`` to introduce new features or break compatibility with previous versions (*e.g.* milestones ``v0.4alpha2`` or ``v0.4beta1``).

You should also submit bugfixes to the release branch or ``master`` for errors that are only present in those respective branches.



## Submitting a Pull Request

To start working on a new PR, you need to execute these commands, filling in the branch names where appropriate (``<BASE-BRANCH>`` is the branch you're basing your work against, e.g. ``master``, while ``<FEATURE-BRANCH>`` is the branch you'll be creating to store your changes, e.g. ``fix-startup-bug`` or ``add-widget-support``:

```bash
git checkout <BASE-BRANCH>
git pull upstream <BASE-BRANCH>
git checkout -b <FEATURE-BRANCH>
```

Once you've made and tested your changes, commit them with a descriptive message of 74 characters or less written in the imperative tense, with a capitalized first letter and no period at the end (our pre-commit hooks will check that for you, so make sure to install them).
For example:

```bash
git commit -am "Fix bug reading configuration on Windows"
```

Finally, push them to your fork:

```bash
git push -u origin <FEATURE-BRANCH>
```

...and create a pull request to the r-spacex/submanager repository on Github, and we'll take it from there.
Thanks!
