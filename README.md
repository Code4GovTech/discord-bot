## C4GT Discord Bot

### Running the Bot locally
1. Clone the repository onto your local system
2. [Optional+Recommended] Set up a python [virtual environment](https://docs.python.org/3/library/venv.html#:~:text=Creating%20virtual-,environments,-%C2%B6) and [activate](https://python.land/virtual-environments/virtualenv#Python_venv_activation) it before installing dependencies. A Python venv is an independent collection of python packages and is used for creating replicable dev environments and preventing versioning conflicts.
3. Use the [`pip install -r requirements.txt`](https://learnpython.com/blog/python-requirements-file/#:~:text=document%20and%20exit!-,Installing,-Python%20Packages%20From) command to install all dependencies.
4. Add the requisite `.env` file in the repository root.
5. Run the bot using `python3 main.py` or `python main.py` command in the terminal.


### Features
- [ ] Allow tagging a `discordId` to a `githubId` so that contributions can be managed. Everyone coming to the server will be required to register themselves on the bot. Ask every contributor to connect their Github to Discord. The bot will take this publicly available info and add it to the database.
- [ ] Seeing the list of projects and their quick links. Should allow for navigation to projects.
    - [ ] Documentation links
    - [ ] Repositories
    - [ ] Learning path
    - [ ] Gitpod setup links
    - [ ] View the deployed link for master branch
    - [ ] Link to github unclaimed issues
- [ ] Commands to do the following
    - [ ] Seeing the summary of proposals submitted by contributors
    - [ ] Listing contributions by profile
- [ ] Share a summary of contributions at the end of the day to each individual channel project wise
    - [ ] Total PR Raised by Contributors (not mentors)
    - [ ] Total PRs Merged by Contributors (not mentors)
    - [ ] Top 5 contributors
    - [ ] Contributions for the day (Issues list)
- [ ] Draft proposals
    - [ ] Share with mentors
    - [ ] Allow mentors ping contributors when the proposal is reviewed (not sure how this can be accomplished)
    - [ ] Dashboard to show all proposals a mentors needs to review
- [ ] Final proposals
    - [ ] Submission


### Registration Steps (WIP)

#### Step 1
Connect your Github with Discord. 

#### Step 2
Got to [this URL](https://discord.com/api/oauth2/authorize?client_id=982859834355499088&redirect_uri=https%3A%2F%2Fbot.c4gt.samagra.io&response_type=code&scope=identify%20connections%20email) to register yourself. This URL allows the discord bot to get
- email
- identity
- connections (githubId)
This registeres a token with us that we can use to check your GithubId that was connected in step 1.

