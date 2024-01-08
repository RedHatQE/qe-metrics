#!/bin/bash

qe-metrics init-db -l
qe-metrics new-team -n cspi -e caevans@redhat.com -l
qe-metrics gather-jira -l
