import json
import re
from typing import List, Dict, Any, Union, Optional
from bs4 import BeautifulSoup
from .partnersconfig_class import PartnerConfig

class EsferaPartnersList:
    """
    Extracts specific fields from the response_esfera.json data.
    Only the 'legal_terms' (extracted from "esf_accumulationHowItWorks") and 'name'
    (extracted from "displayName") fields inside the items list will be extracted.
    
    If a list of watchstore names is provided, the extracted items will be filtered to 
    include only those whose "displayName" appears in the provided list.
    """
    def __init__(self, data: Union[str, List[Dict[str, Any]], Dict[str, Any]], 
                 watchstore_names: Optional[List[str]] = None) -> None:
        """
        Initializes the extractor with either the path to the JSON file or the JSON data,
        and an optional filter for watchstore names.

        Args:
            data (Union[str, List[Dict[str, Any]], Dict[str, Any]]): Either a file path (string) 
                for the JSON file or parsed JSON data.
            watchstore_names (Optional[List[str]]): If provided, only items with displayName 
                in this list will be extracted.
        """
        if isinstance(data, str):
            with open(data, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = data

        self.watchstore_names = watchstore_names if watchstore_names is not None else []

    def extract_data(self) -> List[Dict[str, Any]]:
        """
        Extracts only the 'legal_terms' and 'name' fields from each item in the items list.
        The 'name' field is obtained from "displayName" and 'legal_terms' from "esf_accumulationHowItWorks".
        
        If a list of watchstore names was provided during initialization, only items whose 
        "displayName" is in that list are included.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries with the extracted fields.
        """
        # Determine if the data is wrapped in an "items" key.
        items = self.data.get("items") if isinstance(self.data, dict) and "items" in self.data else self.data

        partners: List[PartnerConfig] = []

        for item in items:
            display_name = item.get("displayName")
            # If watchstore_names filter is provided, skip items not in the filter.
            if self.watchstore_names and display_name not in self.watchstore_names:
                continue

            # Extract and clean legal terms
            legal_terms = item.get("esf_accumulationHowItWorks")
            if legal_terms:
                # Remove HTML tags
                soup = BeautifulSoup(legal_terms, 'html.parser')
                legal_terms = soup.get_text()
                # Remove extra spaces
                legal_terms = re.sub(r'\s+', ' ', legal_terms).strip()
                
            transformed_item = {
                "partner_name": display_name,
                "legal_terms": legal_terms,
                "parity_club" : item.get("esf_accumulationAmount").lower()
                                                                  .replace("pts", "")
                                                                  .replace("pt", "")
                                                                  .replace("pontos", "")
                                                                  .strip()
            }
            # Create a PartnerConfig object using the factory method.
            partner = PartnerConfig.from_esfera_dict(transformed_item)
            partners.append(partner)
        return partners