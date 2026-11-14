"""Single source of truth for JobZila's editorial bylines."""
EDITORIAL_BY_USERNAME = {
    "sadeed": "JobZila Editorial Team",
    "hazla": "Career Research Desk",
    "frank": "Technology Learning Team",
    "sara": "JobZila Editorial Team",
}


def editorial_team_for(user):
    return EDITORIAL_BY_USERNAME.get(user.username.lower(), "JobZila Editorial Team")
