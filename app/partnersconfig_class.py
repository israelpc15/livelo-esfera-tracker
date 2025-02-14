"""

Classe para representar e manipular dados do arquivo retorno.json ou response_esfera.json.
"""
import re
from typing import List, Tuple, Optional
from datetime import datetime, date

class PartnerConfig:
    """
    Represents the configuration of a partner.
    """
    def __init__(self, partnerCode: str, parity: int,
                 parityClub: int, legalTerms: str, promotion: bool,
                 partnerName: str = "", currency: str = "", currencyValue: float = 1,
                 url: str = "", separator: str = "",
                 parityBau: int = 0, separatorSlug: str = "",
                 campaign_from: Optional[datetime] = None,
                 campaign_to: Optional[datetime] = None):
        """
        Initializes a PartnerConfig instance.

        Args:

            partnerCode (str): Partner code.
            parity (int): Parity.
            parityClub (int): Club parity.
            legalTerms (str): Legal terms.
            promotion (bool): Indicates if there is a promotion.
            currency (str): Currency used.




            currencyValue (float): Currency value.
            url (str): URL.
            separator (str): Separator.



            parityBau (int): BAU parity.
            separatorSlug (str): Separator slug.
            campaign_from (Optional[datetime]): Campaign start date.
            campaign_to (Optional[datetime]): Campaign end date.
        """
        self.partner_code = partnerCode
        self.partner_name = partnerName
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
        self.max_points = 1
        self.analyze_legal_terms_for_points()

    def __repr__(self):
        """
        String representation of the instance for debugging purposes.
        """
        from datetime import date
        campaign_from_str = self.campaign_from.strftime('%Y-%m-%d') if self.campaign_from else None
        campaign_to_str = self.campaign_to.strftime('%Y-%m-%d') if self.campaign_to else None
        return (f"PartnerConfig(partner_code='{self.partner_code}' , partner_name='{self.partner_name}'"
                f"parity_club={self.parity_club}, promotion={self.promotion}, campaign_from={campaign_from_str}, campaign_to={campaign_to_str})")

    def getParityClub(self) -> int:
        return self.parity_club

    def analyze_legal_terms_for_points(self): #-> List[Tuple[str, List[int]]]:
        """
        Analyzes the legal terms text, breaks it into sentences, and extracts integer points
        from each sentence, considering only points specified as "X points per real" or similar.
        Ignores numbers that are part of dates. Also, extracts campaign dates.

        Returns:
            List[Tuple[str, List[int]]]: A list of tuples. Each tuple contains a sentence
                                         and a list of integer points found in that sentence.
                                         Returns an empty list if legalTerms is empty.
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
                for pattern in patterns:
                    match = re.search(pattern, sentence)
                    if match:
                        points.append(int(match.group(1)))
                results.append((sentence, points))
                # Extract campaign dates, ex: "de 1 a 30/04/2023"
                date_match = re.search(r'de (\d{1,2}) a (\d{1,2}/\d{2}/\d{2,4})', sentence)
                print(sentence)
                if date_match:
                    try:
                        from_day = int(date_match.group(1))
                        to_date_str = date_match.group(2)
                        from_date_str = f"{from_day:02d}/{to_date_str.split('/')[1]}/{to_date_str.split('/')[2]}"
                        self.campaign_from = datetime.strptime(from_date_str, '%d/%m/%Y').date()
                        self.campaign_to = datetime.strptime(to_date_str, '%d/%m/%Y').date()
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing date in sentence '{sentence}': {e}")

        all_points = []
        for _, points in results:
            all_points.extend(points)
        self.max_points = max(all_points) if all_points else 0

    def get_highest_point(self) -> int:
        """
        Returns the highest point value found in the legal terms.
        """
        analysis_results = self.analyze_legal_terms_for_points()
        all_points = []
        for _, points in analysis_results:
            all_points.extend(points)
        return max(all_points) if all_points else 0

    def has_active_campaign(self) -> bool:
        """
        Checks if the partner has an active campaign based on the campaign dates.

        Returns:
            bool: True if the campaign is active, False otherwise.
        """
        if self.campaign_from is None or self.campaign_to is None:
            return False
        return self.campaign_from <= date.today() <= self.campaign_to

    @classmethod
    def from_esfera_dict(cls, data: dict) -> "PartnerConfig":
        """
        Factory method for creating a PartnerConfig from a response_esfera.json item.

        The data is expected to have the properties:
            'name' (from displayName) and 'legal_terms' (from esf_accumulationHowItWorks).

        Since response_esfera.json does not provide all required fields, defaults are used for the rest.

        Args:
            data (dict): A dictionary representing a partner from response_esfera.json.

        Returns:
            PartnerConfig: A PartnerConfig instance with mapped data.
        """
        return cls(
            partnerCode = "", 
            partnerName = data.get("partner_name", ""),   # Using name from esfera response as partner code
            parity = 0,                           # Default value; not present in esfera data
            parityClub = data.get("parity_club", ""),
            legalTerms = data.get("legal_terms", ""),
            promotion = False
        )

