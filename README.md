# qe-metrics

Queries Jira and stores results in a database for further analysis in Grafana.

<!-- TODO: Add step-by-step instructions for adding a service to the regular execution of this tool -->

## Configuration

### Credentials

The qe-metrics tool uses a YAML file passed to it using the `--creds-file` option as its source of credentials. The file
holds credentials for both the database and the Jira server used by the tool. Here is an example of a credentials file:

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
  server: jira-server.com
````

#### Database Credentials

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

#### Jira Credentials

- `token`: The API token used to authenticate with the Jira server.
- `server`: The FQDN or IP of the Jira server.

<!-- TODO: Add configuration details for services and queries -->

<!-- TODO: Add DB schema and explanation -->

<!-- TODO: Add outline of how CI will work -->
