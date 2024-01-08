# qe-metrics

Thank you for your interest in the qe-metrics project! Please find some information about the project below.
If you don't find what you are looking for, please consider looking in the following documents:

- [CLI usage guide](docs/cli-usage-guide.md)
- [Configuration guide](docs/configuration-guide.md)
- [Development and contribution guide](docs/development-contribution-guide.md)

## What is qe-metrics?

This tool is used to populate a database with Jira issues based on the configuration provided to the tool. The database
should then be used to generate Grafana dashboards to display the metrics.

## Getting started

### Prerequisites

1. Install either Docker or Podman on the system you are using to execute the tool.
   - [Docker installation guide](https://docs.docker.com/get-docker/)
   - [Podman installation guide](https://podman.io/getting-started/installation)
2. Either build the image or pull it from quay.io
   - Building the image:
     1. Clone the repository and `cd` to the directory: `git clone git@github.com:RedHatQE/qe-metrics.git && cd qe-metrics`
     2. Build and run the image: `make container-build-run`
   - Pulling the image:
     - Docker: `docker pull quay.io/redhatqe/qe-metrics:latest`
     - Podman: `podman pull quay.io/redhatqe/qe-metrics:latest`

### Configuration

**Please see the [configuration guide](docs/configuration-guide.md) for more information about the configuration.**

This tool requires a configuration file to be provided to it. A template for this configuration file can be created using
the `qe-metrics init-config` command. This command will create a configuration file in the provided directory (`./qe-metrics.config` by default).

#### Creating a Team

**Please see the [CLI usage guide](docs/cli-usage-guide.md) for more information about the `qe-metrics new-team` command.**

The `gather_jira` section of the configuration file has a `team_name` field. This field is used as a way to relate the data
from Jira to a specific team in the database. If the team does not exist in the database, you will need to create it before
running the `qe-metrics gather-jira` command. This can be done using the `qe-metrics new-team` command. Example:

```bash
$ qe-metrics new-team --name your-team-name --email some-team@redhat.com
```

> Note: At this time, the `email` field is not used for anything within the tool. This is simply provided in the event that
> that team needs to be contacted for any reason. It is also a better way to identify a team than by name alone.

### Execution

**Please see the [CLI usage guide](docs/cli-usage-guide.md) for more information about the `qe-metrics gather-jira` command.**

After the configuration file has been created and the team has been created in the database, you are ready to start gathering data.
This can be done using the `qe-metrics gather-jira` command. Example:

```bash
# Providing the configuration file as an argument
$ qe-metrics gather-jira --config ./qe-metrics.config

# Using an environment variable to provide the configuration file
$ export QE_METRICS_CONFIG=./qe-metrics.config
$ qe-metrics gather-jira

# Add bugs to the database and remove records created more than x days ago.
# The number of days is defined as "data_retention_days" in the configuration file.
$ qe-metrics gather-jira --config ./qe-metrics.config --clean-db
```

## Contributing

Contributions are welcome! Please see the [development and contribution guide](docs/development-contribution-guide.md) for more information.

## License

qe-metrics is released under the [GNU Public License](LICENSE).

## Contact

If you have any questions, please use the following links to reach us:

- Issue Tracker: [RedHatQE/qe-metrics Issues](https://github.com/RedHatQE/qe-metrics/issues)
- Slack: [#quality-innovators](https://redhat.enterprise.slack.com/archives/C04PKKYF848)

We appreciate your interest in the qe-metrics project!
