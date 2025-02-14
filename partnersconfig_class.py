"""
Classe para representar e manipular dados do arquivo retorno.json.
"""

import json
import re
from typing import List, Dict, Union, Tuple, Optional, Any
from datetime import datetime

class PartnerConfig:
    """
    Represents the configuration of a partner.
    """
    def __init__(self, partnerCode: str, parity: int,
                 parityClub: int, legalTerms: str, promotion: bool,
                 currency: str = "", currencyValue: float = 1,
                 url: str = "", separator: str = "",
                 parityBau: int = 0, separatorSlug: str = "",
                 campaign_from: Optional[datetime] = None,
                 campaign_to: Optional[datetime] = None):
        """
        Initializes a PartnerConfig instance.

        Args:
            partner_code (str): Partner code.
            currency (str): Currency used.
            currency_value (float): Currency value.
            parity (int): Parity.
            parity_club (int): Club parity.
            legal_terms (str): Legal terms.
            url (str): URL.
            separator (str): Separator.
            parity_bau (int): BAU parity.
            promotion (bool): Indicates if there is a promotion.
            separator_slug (str): Separator slug.
            campaign_from (Optional[datetime]): Campaign start date.
            campaign_to (Optional[datetime]): Campaign end date.
        """
        self.partner_code = partnerCode
        self.currency = currency
        self.currency_value = currencyValue
        self.parity = parity
        self.parity_club = parityClub
        self.legal_terms = legalTerms if legalTerms is not None else ""
        self.url = url
        self.separator = separator
        self.parity_bau = parityBau
        self.promotion = promotion
        self.separator_slug = separatorSlug
        self.campaign_from = campaign_from
        self.campaign_to = campaign_to

    def __repr__(self):
        """
        String representation of the instance for debugging purposes.
        """
        from datetime import date
        campaign_from_str = self.campaign_from.strftime('%Y-%m-%d') if self.campaign_from else None
        campaign_to_str = self.campaign_to.strftime('%Y-%m-%d') if self.campaign_to else None
        return (f"PartnerConfig(partner_code='{self.partner_code}', currency='{self.currency}', "
                f"parity={self.parity}, promotion={self.promotion}, campaign_from={campaign_from_str}, campaign_to={campaign_to_str})")

    def getParityClub(self) -> int:
        return self.parity_club

    def analyze_legal_terms_for_points(self) -> List[Tuple[str, List[int]]]:
        """
        Analyzes the legal terms text, breaks it into sentences, and extracts integer points
        from each sentence, considering only points specified as "X points per real" or similar.
        Ignores numbers that are part of dates. Also, extracts campaign dates.

        Args:
            legal_terms (str): The legal terms text to analyze.

        Returns:
            List[Tuple[str, List[int]]]: A list of tuples. Each tuple contains a sentence
                                         and a list of integer points found in that sentence.
                                         Returns an empty list if legal_terms is None or empty.
        """
        if not self.legal_terms:
            return []

        sentences = re.split(r'[.;]', self.legal_terms)
        results: List[Tuple[str, List[int]]] = []

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Find points using specific patterns, ignoring dates
                points = []
                patterns = [
                    r'(\d+)\s+pontos\s+por\s+real',
                    r'(\d+)\s+pontos\s+por\s+R\$\s*1',
                    r'(\d+)\s+pontos\s+a\s+cada\s+real',
                    r'(\d+)\s+pontos\s+a\s+cada\s+R\$\s*1'
                ]
                # Check for each pattern in the sentence
                for pattern in patterns:
                    match = re.search(pattern, sentence)
                    if match:
                        points.append(int(match.group(1)))

                results.append((sentence, points))
                # Extract campaign dates, ex: "de 1 a 30/04/2023"
                date_match = re.search(r'de (\d{1,2}) a (\d{1,2}/\d{2}/\d{2,4})', sentence)
                if date_match:
                    try:
                        from_day = int(date_match.group(1))
                        to_date_str = date_match.group(2)
                        from_date_str = f"{from_day:02d}/{to_date_str.split('/')[1]}/{to_date_str.split('/')[2]}"
                        self.campaign_from = datetime.strptime(from_date_str, '%d/%m/%Y').date()
                        self.campaign_to = datetime.strptime(to_date_str, '%d/%m/%Y').date()
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing date in sentence '{sentence}': {e}")

            return results

    def get_highest_point(self) -> int:
        """
        Returns the highest point value found in the legal terms.
        """
        analysis_results = self.analyze_legal_terms_for_points()
        all_points = []
        for _, points in analysis_results:
            all_points.extend(points)
        return max(all_points) if all_points else 0


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


# Exemplo de uso:
if __name__ == "__main__":
    config_list = PartnerConfigList("retorno.json")

    # Obtém parceiros em promoção
    promotional_partners = config_list.get_promotional_partners(4)
    print("\nParceiros em promoção:")
    for partner in promotional_partners:
        print(partner)
        print(str(partner.campaign_from) + " até "+ str(partner.campaign_to))
