import json
from typing import List, Dict, Union, Any
from .partnersconfig_class import PartnerConfig

class PartnerConfigList:
    """
    Class to load and manipulate a list of partner configurations from a JSON file.
    """
    def __init__(self, json_data: Union[str, List[Dict[str, Any]]]):
        """
        Initializes the class with the JSON data.

        Args:
            json_data (Union[str, List[Dict[str, Any]]]): JSON data.  Can be a file path (string) or a list of dictionaries.
        """
        self.configs: List[PartnerConfig] = self._load_configs(json_data)

    def _load_configs(self, json_data: Union[str, List[Dict[str, Any]]]) -> List[PartnerConfig]:
        """
        Loads the configurations from the JSON data and returns a list of PartnerConfig objects.

        Args:
            json_data (Union[str, List[Dict[str, Any]]]): JSON data.  Can be a file path (string) or a list of dictionaries.

        Returns:
            List[PartnerConfig]: List of partner configurations.
        """
        try:
            if isinstance(json_data, str):  # Assume it's a file path
                with open(json_data, 'r') as f:
                    data: List[Dict[str, Any]] = json.load(f)
            elif isinstance(json_data, list):  # Assume it's a list of dictionaries
                data = json_data
            else:
                print(f"Error: Invalid JSON data type: {type(json_data)}. Expected: str (file path) or list (JSON data).")
                return []

            return [PartnerConfig(**item) for item in data]

        except FileNotFoundError:
            print(f"Error: File not found: {json_data}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Failed to decode the JSON file: {json_data}")
            return []
        except (TypeError, KeyError) as e:
            print(f"Error: Invalid data in the JSON file: {e}")
            return []

    def get_config_by_partner_code(self, partner_code: str) -> Union[PartnerConfig, None]:
        """
        Returns the configuration of a specific partner by code.

        Args:
            partner_code (str): Partner code.

        Returns:
            PartnerConfig or None: Partner configuration, or None if not found.
        """
        for config in self.configs:
            if config.partner_code == partner_code:
                return config
        return None

    def get_promotional_partners(self, desired_points: int) -> List[PartnerConfig]:
        """
        Returns a list of partners that are on promotion and offer desired points.

        Args:
            desired_points (int): The minimum desired points.

        Returns:
            List[PartnerConfig]: List of partners on promotion.
        """
        promotional_partners = []
        for config in self.configs:
            if config.promotion and config.get_highest_point() >= desired_points:
                promotional_partners.append(config)
        return promotional_partners

    def print_all_configs(self) -> None:
        """
        Prints all partner configurations.
        """
        for config in self.configs:
            print(config)