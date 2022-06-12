### C4GT Discord Bot

Features
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

## Get Started

> **Dependencies**:
1. Flask
2. Discord.py
3. Discord.ext 
4. psycopg2
5. requests 

### Step 1
Setup your `.env` variables

### Step 2
Run The server file using `keep_alive.py` on repl.it to keep your bot alive

### *You are done!*
