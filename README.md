# qe-metrics

Queries Jira and stores results in a database for further analysis in Grafana.

<!-- TODO: Add step-by-step instructions for adding a service to the regular execution of this tool -->

## Configuration

### Credentials

The qe-metrics tool uses a YAML file passed to it using the `--config-file` option as its source of credentials and other
configuration values. The file holds these values for both the database and the Jira server used by the tool.
Here is an example of a configuration file:

```yaml
database:
    host: some.database.com
    user: my-user
    password: p@ssw0rd
    database: qe-metrics
    port: 1234
    provider: postgres
    local: false
    local_filepath: /tmp/my-db.sqlite
jira:
  token: some-token
  server: https://jira-server.com
````

#### Database Credentials and Configuration

- `host`: The FQDN or IP of the database server.
- `user`: The username used to connect to the database.
- `password`: The password used to connect to the database.
- `database`: The name of the database to connect to.

Optional values:

- `port`: The port number of the database service.
  - Default: `5432`.
- `provider`: Database provider. Please see [supported providers](https://ponyorm.readthedocs.io/en/latest/api_reference.html#supported-databases).
  - Default: `postgres`.
- `local`: A boolean value. If "true", a local SQLite database. If "false", the creds above are used.
  - Default: `false`
- `local_filepath`: Optional path to the local SQLite database file.
  - Default: `/tmp/qe_metrics.sqlite`

#### Jira Credentials and Configuration

- `token`: The API token used to authenticate with the Jira server.
- `server`: The FQDN or IP of the Jira server. Must include the protocol (e.g. `https://`).

### Services and Queries

The qe-metrics tool uses a YAML file passed to it using the `--services-file` option as its source of services and queries.
The file should hold a list of defined services, each with a list of Jira queries to be executed. Here is an example of a services file:

```yaml
some_service:
  blocker: "project = 'SERVICE' AND resolution = Unresolved AND Issuetype = bug AND priority = blocker"
  critical-blocker: "project = 'SERVICE' AND resolution = Unresolved AND Issuetype = bug AND priority = blocker AND labels = 'critical'"
another_service:
  blocker: "project = 'SERVICE2' AND resolution = Unresolved AND Issuetype = bug AND priority = blocker"
  critical-blocker: "project = 'SERVICE2' AND resolution = Unresolved AND Issuetype = bug AND priority = blocker AND labels = 'critical'"
```

The example above defines two "services", `some_service` and `another_service`, each with two queries. The queries have a 
"severity" of `blocker` and `critical-blocker`. The queries are written in [Jira Query Language (JQL)](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
and are used to define which issues should be associated with the `service` and `severity` in the database.

#### Severity

The severity of a query is used to define the severity of the issues returned by the query. Currently, the following
severities are supported:

- `blocker`
- `critical-blocker`

More severities may be added in the future, but those are the only two severities allowed in the "services" file currently.

<!-- TODO: Add DB schema and explanation -->

<!-- TODO: Add outline of how CI will work -->
