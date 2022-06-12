# Contributing

We welcome contributions in several forms, e.g.
- Create a new command using for following sytax:
```python3
@client.command()
async def <command_name>(ctx):
	# Your code goes here
```
- Create a new event using the following syntax:
```python3
@client.event
async def <any_event>():
	# Your code goes here
```
> Note: your function name for event type are special names found [here](https://discordpy.readthedocs.io/en/latest/api.html#event-reference)

- Working on [Issues](https://github.com/Code4GovTech/discord-bot/issues)
- etc

## Reporting Bugs
Consider the usual best practice for writing issues, among them:
- More verbosity rather than one liners
- Screenshots are a great help
- Providing example files (in case for example scanning crashes)
- Please determine the version, better the commit id
- Details on the operating system you are using

### Workflow

We are using the [Feature Branch Workflow (also known as GitHub Flow)](https://guides.github.com/introduction/flow/),
and prefer delivery as pull requests.

Create a feature branch:

```sh
git checkout -B feat/tune-vagrant-vm
```

### Git Commit

The cardinal rule for creating good commits is to ensure there is only one
"logical change" per commit. Why is this an important rule?

- The smaller the amount of code being changed, the quicker & easier it is to
  review & identify potential flaws.

- If a change is found to be flawed later, it may be necessary to revert the
  broken commit. This is much easier to do if there are no other unrelated
  code changes entangled with the original commit.

- When troubleshooting problems using Git's bisect capability, small well
  defined changes will aid in isolating exactly where the code problem was
  introduced.

- When browsing history using Git annotate/blame, small well defined changes
  also aid in isolating exactly where & why a piece of code came from.

Things to avoid when creating commits

- Mixing whitespace changes with functional code changes.
- Mixing two unrelated functional changes.
- Sending large new features in a single giant commit.

### Git Commit Conventions

We use git commit as per [Conventional Changelog](https://www.conventionalcommits.org/en/v1.0.0/):

```none
<type>(<scope>): <subject>
```

Example:

```none
feat(vagrant): increase upload size
```

Allowed types:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, newline, line endings, etc)
- **refactor**: A code change that neither fixes a bug or adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests
- **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation

You can add additional details after a new line to describe the change in detail or automatically close an issue on Github.

```none
feat(CONTRIBUTING.md): create initial CONTRIBUTING.md

makes the following wiki Page obsolete:
- https://github.com/Samagra-Development/uci-pwa/wiki/Reporting-bugs

This closes #22
```
## Pull requests

Pull requests with patches, improvements, new features are a great help.
Please keep them clean from unwanted commits.

Follow the steps to get your work included in the project.

1. [Fork](https://help.github.com/fork-a-repo/) the project, clone your fork,
   and add the discord-bot remote:

   ```bash
   # Clone your fork of the repo into the current directory
   git clone https://github.com/<your-username>/discord-bot.git
   # Navigate to the cloned directory
   cd discord-bot
   # Assign the original repo to a remote called "upstream"
   git remote add upstream https://github.com/Code4GovTech/discord-bot.git
   ```

2. Get the latest changes from upstream:

   ```bash
   git checkout master
   git pull upstream master
   ```

3. Create a new branch from the master branch to contain your changes.
   Best way is to call is to follow the type described in **Git Commit Conventions**
   stated above: `<githubId>/#<issueNr>/<description/scope/topic>`

   ```bash
   git checkout -b <topic-branch-name>
   ```

   Example:

   ```bash
   git checkout -b john/138/buckets-undefined-index
   ```

   Or

   ```bash
   git checkout -b john/fix/138
   ```

4) It's coding time!
   Please respect the coding convention: [Coding guidelines](https://github.com/Samagra-Development/uci-pwa/wiki)

   Commit your changes in logical chunks. Please adhere to **Git Commit Conventions**
   and [Coding guidelines](https://github.com/Samagra-Development/uci-pwa/wiki)
   or your code is unlikely to be merged into the main project.
   Use Git's [interactive rebase](https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase)
   feature to tidy up your commits before making them public.

5) Locally rebase the upstream master branch into your topic branch:

   ```bash
   git pull --rebase upstream master
   ```

6) Push your topic branch up to your fork:

   ```bash
   git push origin <topic-branch-name>
   ```

7) [Open a Pull Request](https://help.github.com/articles/using-pull-requests/)
   with a clear title and description against the `master` branch.
