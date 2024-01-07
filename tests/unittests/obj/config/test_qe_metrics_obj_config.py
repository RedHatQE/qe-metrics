#
# Copyright (C) 2024 Red Hat, Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import json
import tempfile
import unittest

import pytest
from cli.obj.config import Config
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config_dict = {
            "jira_auth": {
                "token": "some-token",
                "server": "https://issues.redhat.com"
            },
            "database_auth": {
                "host": "loalhost",
                "database": "test",
                "username": "admin",
                "password": "password"
            },
            "gather_jira": {
                "team_name": "cspi",
                "rules": [
                    {"classification": "blocker", "query": "project = LPTOCPCI AND resolution = Unresolved AND Issuetype = bug"},
                    {"classification": "critical blocker", "query": "project = LPTOCPCI AND resolution = Unresolved AND Issuetype = bug"},
                    {"classification": "escaped bug", "query": "project = LPTOCPCI AND resolution = Unresolved AND Issuetype = bug"}
                ],
                "data_retention_days": 90
            }
        }

        # Create a temporary file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)

        # Write the configuration data to the temporary file
        with open(self.temp_file.name, 'w') as file:
            json.dump(self.config_dict, file)

    @patch('cli.obj.config.get_logger')
    @patch('cli.obj.config.Jira')
    @patch('cli.obj.config.Database')
    def test_config_initialization_with_valid_config(self, mock_get_logger, mock_jira, mock_database):
        mock_get_logger.return_value = MagicMock()
        mock_jira.return_value = MagicMock()
        mock_database.return_value = MagicMock()
        config = Config(filepath=Path(self.temp_file.name), check_team=False, init_db=True, local=True)
        assert config.filepath == Path(self.temp_file.name)
        assert isinstance(config.jira, MagicMock)
        assert isinstance(config.database, MagicMock)

    @patch('cli.obj.config.get_logger')
    def test_config_initialization_with_invalid_config(self, mock_get_logger):
        mock_get_logger.return_value = MagicMock()
        with pytest.raises(SystemExit):
            Config(filepath=Path('invalid_config.json'))

    @patch('cli.obj.config.get_logger')
    @patch('cli.obj.config.Jira')
    @patch('cli.obj.config.Database')
    def test_config_initialization_without_filepath(self, mock_get_logger, mock_jira, mock_database):
        mock_get_logger.return_value = MagicMock()
        mock_jira.return_value = MagicMock()
        mock_database.return_value = MagicMock()
        with patch('cli.obj.config.os.getenv', return_value=self.temp_file.name):
            config = Config(check_team=False, init_db=True, local=True)
            assert config.filepath == Path(self.temp_file.name)

    @patch('cli.obj.config.get_logger')
    def test_config_initialization_without_filepath_and_env_variable(self, mock_get_logger):
        mock_get_logger.return_value = MagicMock()
        with patch('cli.obj.config.os.getenv', return_value=None):
            with pytest.raises(SystemExit):
                Config()

    @patch('cli.obj.config.get_logger')
    @patch('cli.obj.config.Jira')
    @patch('cli.obj.config.Database')
    def test_config_initialization_with_invalid_jira_auth(self, mock_database, mock_jira, mock_get_logger):
        mock_get_logger.return_value = MagicMock()
        mock_jira.side_effect = Exception()
        mock_database.return_value = MagicMock()
        with pytest.raises(SystemExit):
            Config(filepath=Path('valid_config.json'))

    @patch('cli.obj.config.get_logger')
    @patch('cli.obj.config.Jira')
    @patch('cli.obj.config.Database')
    def test_config_initialization_with_invalid_database_auth(self, mock_database, mock_jira, mock_get_logger):
        mock_get_logger.return_value = MagicMock()
        mock_jira.return_value = MagicMock()
        mock_database.side_effect = Exception()
        with pytest.raises(SystemExit):
            Config(filepath=Path('valid_config.json'))
