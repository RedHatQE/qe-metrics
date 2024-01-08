# qe-metrics Configuration Guide

## Configuration Example

The following is an example of a qe-metrics configuration file:

```json
{
    "jira_auth": {
        "token": "some-token",
        "server": "https://issues.redhat.com"
    },
    "database_auth": {
        "host": "db-host.redhat.com",
        "database": "qe-metrics-db",
        "username": "some-user",
        "password": "s00per-s3cr3t"
    },
    "gather_jira": {
        "team_name": "your-team-name",
        "rules": [
            {"classification": "blocker", "query": "project = TEST AND resolution = Unresolved AND Issuetype = bug"},
            {"classification": "critical blocker", "query": "JQL query"},
            {"classification": "escaped bug", "query": "JQL query"}
        ],
        "data_retention_days": 90
    }
}
```

## Configuration Values

### `jira_auth`

This section of the configuration file is used to authenticate with Jira and only contains two values:

- `token`: This is the token that will be used to authenticate with Jira.
- `server`: This is the URL of the Jira server. If you are using the Red Hat Jira instance, this value should be `https://issues.redhat.com`.

### `database_auth`

This section of the configuration file is used to authenticate with the database and contains four values:

- `host`: This is the hostname of the database server.
- `database`: This is the name of the database that will be used.
- `username`: This is the username that will be used to authenticate with the database.
- `password`: This is the password that will be used to authenticate with the database.
- `port`: This is the port that will be used to connect to the database. This value is optional and will default to `30327` if not provided.
- `provider`: This is the database provider that will be used. This value is optional and will default to `postgres` if not provided.

If you would only like to use a local SQLite database, you can use the `--local` flag when running the `qe-metrics gather-jira` command and
just use fake values in the `database_auth` section of the configuration file.

### `gather_jira`

This section of the configuration file is used to gather data from Jira and contains three values:

- `team_name`: This is the name of the team that will be used to relate the data from Jira to the database.
- `rules`: This is a list of rules that will be used to gather data from Jira. Each rule must contain a `classification` and a `query`.
    - `classification`: This is the classification that will be used to relate the data from Jira to the database. This value should be unique. The template comes with three default classifications: `blocker`, `critical blocker`, and `escaped bug` but more can be used if needed.
    - `query`: This is the JQL query that will be used to gather data from Jira.
- `data_retention_days`: This is the number of days that data will be retained in the database. Any data older than this value will be removed from the database.
