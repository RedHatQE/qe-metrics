from typing import Dict, List

from pyaml_env import parse_config

from qe_metrics.libs.rule import Rule


class Service:
    def __init__(self, name: str, rules: Dict[str, str]) -> None:
        """
        Initialize the Service class
        Args:
            name (str): The name of the service
            rules (dict): The rules that define Jira queries to be executed
        """
        self.name = name
        self.rules = [Rule(classification, query) for classification, query in rules.items()]

    @classmethod
    def from_file(cls, services_file: str) -> List["Service"]:
        """
        Initialize the Service class from a file
        Args:
            services_file (str): Path to the yaml file holding service names and their rules
        """
        services_dict = parse_config(services_file)
        return [cls(name, rules) for name, rules in services_dict.items()]
