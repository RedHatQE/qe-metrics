# qe-metrics CLI Usage Guide

## Table of Contents

- [`init-config`](#init-config)
- [`init-db`](#init-db)
- [`new-team`](#new-team)
- [`gather-jira`](#gather-jira)
- [`clean-db`](#clean-db)

## `init-config`

This command is used to create a template of the qe-metrics config at the provided path. If no path is provided,
the config will be created in the current working directory with the name `qe-metrics.config`.

### Help

```bash
Usage: qe-metrics init-config [OPTIONS] [FILEPATH]

  Creates an empty config file at the specified filepath.

Options:
  --help  Show this message and exit.
```

### Example(s)

```bash
# Create the config at /some/path/to/qe-metrics.config
$ qe-metrics init-config /some/path/to/qe-metrics.config

# Create the config in the current working directory with the default name
$ qe-metrics init-config
```

## `init-db`

This command should be used sparingly as it is used to initialize the database tables required for the tool to run.
This should only be used if the database is being created for the first time or if the database has been dropped. The
configuration file should be created before running this command.

### Help

```bash
Usage: qe-metrics init-db [OPTIONS]

  Used to initialize the database.

Options:
  -c, --config PATH  Defines the path to the config file.
  -l, --local        Use a local SQLite database instead of a real database.
  -v, --verbose      Verbose output of database connection.
  --help             Show this message and exit.
```

### Example(s)

```bash
# Initialize the database using the config at /some/path/to/qe-metrics.config
$ qe-metrics init-db --config /some/path/to/qe-metrics.config

# Initialize the database using the config at /some/path/to/qe-metrics.config and use verbose output
$ qe-metrics init-db --config /some/path/to/qe-metrics.config --verbose

# Initialize the database using the config at /some/path/to/qe-metrics.config and use a local SQLite database
$ qe-metrics init-db --config /some/path/to/qe-metrics.config --local
```

## `new-team`

This command is used to create a new team in the database. The team in the database is used to relate the data from Jira
to a team so that team can effectively display their data in Grafana without having to worry about other teams' data.

### Help

```bash
Usage: qe-metrics new-team [OPTIONS]

  Used to insert a new team in to the database

Options:
  -e, --email TEXT   Email for the team  [required]
  -n, --name TEXT    Name of team  [required]
  -c, --config PATH  Defines the path to the config file.
  -l, --local        Use a local SQLite database instead of a real database.
  -v, --verbose      Verbose output of database connection.
  --help             Show this message and exit.

```

### Example(s)

```bash
# Create a new team in the database using the config at /some/path/to/qe-metrics.config
$ qe-metrics new-team --config /some/path/to/qe-metrics.config --name your-team-name --email some-email@redhat.com

# Create a new team in the database using the config at /some/path/to/qe-metrics.config and use verbose output
$ qe-metrics new-team --config /some/path/to/qe-metrics.config --name your-team-name --email some-email@redhat.com --verbose

# Create a new team in the database using the config at /some/path/to/qe-metrics.config and use a local SQLite database
$ qe-metrics new-team --config /some/path/to/qe-metrics.config --name your-team-name --email some-email@redhat.com --local
```

## `gather-jira`

This command is used to gather data from Jira and insert it in to the database. This command should be run on a regular
basis to ensure that the data in the database is up-to-date. This command will gather data from Jira based on the provided
configuration file and insert it in to the database. The configuration file should be created before running this command.

### Help

```bash
Usage: qe-metrics gather-jira [OPTIONS]

  Gathers Jira data and saves it to the database.

Options:
  --clean-db         If set, the tool will remove any items in the JiraIssue
                     table that are older than the value of
                     "data_retention_days" in the configuration file. This is
                     the same functionality as running "qe-metrics clean-db".
  -c, --config PATH  Defines the path to the config file.
  -l, --local        Use a local SQLite database instead of a real database.
  -v, --verbose      Verbose output of database connection.
  --help             Show this message and exit.
```

### Example(s)

```bash
# Gather data from Jira using the config at /some/path/to/qe-metrics.config
$ qe-metrics gather-jira --config /some/path/to/qe-metrics.config

# Gather data from Jira using the config at /some/path/to/qe-metrics.config and use verbose output
$ qe-metrics gather-jira --config /some/path/to/qe-metrics.config --verbose

# Gather data from Jira using the config at /some/path/to/qe-metrics.config and use a local SQLite database
$ qe-metrics gather-jira --config /some/path/to/qe-metrics.config --local

# Gather data from Jira using the config at /some/path/to/qe-metrics.config and remove records older than x days
$ qe-metrics gather-jira --config /some/path/to/qe-metrics.config --clean-db

# Using an environment variable to provide the configuration file
$ export QE_METRICS_CONFIG=/some/path/to/qe-metrics.config
$ qe-metrics gather-jira
```

## `clean-db`

This command is used to remove any items in the JiraIssue table that are older than the value of "data_retention_days".
This command should be run on a regular basis to ensure that the data in the database is up-to-date. If you would like to run this
command on the same cadence as the `gather-jira` command, you can use the `--clean-db` flag on the `gather-jira` command.

### Help

```bash
Usage: qe-metrics clean-db [OPTIONS]

  Removes any items in the JiraIssue table that are older than the value of
  "data_retention_days" in the configuration file.

Options:
  -c, --config PATH  Defines the path to the config file.
  -l, --local        Use a local SQLite database instead of a real database.
  -v, --verbose      Verbose output of database connection.
  --help             Show this message and exit.

```

### Example(s)

```bash
# Remove records older than x days using the config at /some/path/to/qe-metrics.config
$ qe-metrics clean-db --config /some/path/to/qe-metrics.config

# Remove records older than x days using the config at /some/path/to/qe-metrics.config and use verbose output
$ qe-metrics clean-db --config /some/path/to/qe-metrics.config --verbose

# Remove records older than x days using the config at /some/path/to/qe-metrics.config and use a local SQLite database
$ qe-metrics clean-db --config /some/path/to/qe-metrics.config --local
```
