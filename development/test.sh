#!/bin/bash

# Build Jira config
echo "${JIRA_TOKEN}" > /tmp/token
qe-metrics jira-config-gen --token-path /tmp/token --server-url "${JIRA_SERVER_URL}"
