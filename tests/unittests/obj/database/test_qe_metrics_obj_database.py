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

import unittest
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from cli.obj.database import Database, Team, JiraIssue


class TestDatabase(unittest.TestCase):

    @patch('cli.obj.database.get_logger')
    @patch('cli.obj.database.connection')
    def test_database_initialization_with_valid_config(self,mock_connection, mock_get_logger):
        mock_get_logger.return_value = MagicMock()
        mock_connection.bind.return_value = MagicMock()
        database = Database(host='localhost', username='user', password='pass', db_name='test_db', debug_mode=False,
                            provider='postgres', init_db=False, local_mode=False)
        assert isinstance(database.connection, MagicMock)

    @patch('cli.obj.database.get_logger')
    def test_database_initialization_with_invalid_config(self, mock_get_logger):
        mock_get_logger.return_value = MagicMock()
        with pytest.raises(Exception):
            Database(host='localhost', username='user', password='pass', db_name='test_db', debug_mode=False,
                     provider='invalid_provider', init_db=False, local_mode=False)

    @patch('cli.obj.database.get_logger')
    @patch('cli.obj.database.connection')
    def test_database_initialization_without_filepath(self, mock_connection, mock_get_logger):
        mock_get_logger.return_value = MagicMock()
        mock_connection.bind.return_value = MagicMock()
        database = Database(host='localhost', username='user', password='pass', db_name='test_db', debug_mode=False,
                            provider='postgres', init_db=False, local_mode=True)
        assert isinstance(database.connection, MagicMock)

    @patch('cli.obj.database.get_logger')
    @patch('cli.obj.database.connection')
    def test_database_initialization_with_invalid_database_auth(self, mock_connection, mock_get_logger):
        mock_get_logger.return_value = MagicMock()
        mock_connection.bind.side_effect = Exception()
        with pytest.raises(Exception):
            Database(host='localhost', username='user', password='invalid_pass', db_name='test_db', debug_mode=False,
                     provider='postgres', init_db=False, local_mode=False)