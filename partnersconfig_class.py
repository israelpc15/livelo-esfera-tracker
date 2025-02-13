"""
Classe para representar e manipular dados do arquivo retorno.json.
"""

import json
import re
from typing import List, Dict, Union, Tuple, Optional
from datetime import datetime

class PartnerConfig:
    """
    Representa a configuração de um parceiro.
    """
    def __init__(self, partnerCode: str, parity: int, 
                 parityClub: int, legalTerms: str, promotion: bool, 
                 currency: str = "", currencyValue: float = 1,  
                 url: str = "", separator: str = "", 
                 parityBau: int = 0, separatorSlug: str = "",
                 campaign_from: Optional[datetime] = None,
                 campaign_to: Optional[datetime] = None):
        """
        Inicializa uma instância de PartnerConfig.

        Args:
            partner_code (str): Código do parceiro.
            currency (str): Moeda utilizada.
            currency_value (float): Valor da moeda.
            parity (int): Paridade.
            parity_club (int): Paridade no clube.
            legal_terms (str): Termos legais.
            url (str): URL.
            separator (str): Separador.
            parity_bau (int): Paridade BAU.
            promotion (bool): Indica se há promoção.
            separator_slug (str): Slug do separador.
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
        Representação em string da instância para fins de depuração.
        """
        return (f"PartnerConfig(partner_code='{self.partner_code}', currency='{self.currency}', "
                f"parity={self.parity}, promotion={self.promotion})")
    
    def getParityClub(self) -> int:
        return self.parity_club

    def analyze_legal_terms_for_points(self) -> List[Tuple[str, List[int]]]:
        """
        Analyzes the legal terms text, breaks it into sentences, and extracts integer points
        from each sentence, considering only points specified as "X pontos por real" or similar.
        Ignores numbers that are part of dates.

        Args:
            legal_terms (str): The legal terms text to analyze.

        Returns:
            List[Tuple[str, List[int]]]: A list of tuples. Each tuple contains a sentence
                                        and a list of integer points found in that sentence.
                                        Returns an empty list if legal_terms is None or empty.
        """
        legal_terms = self.legal_terms
        if not legal_terms:
            return []

        sentences = re.split(r'[.;]', legal_terms)
        results: List[Tuple[str, List[int]]] = []

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Find points using specific patterns, ignoring dates
                points = []
                # Match "X pontos por real"
                match = re.search(r'(\d+)\s+pontos\s+por\s+real', sentence)
                if match:
                    points.append(int(match.group(1)))
                # Match "X pontos por R$ 1"
                match = re.search(r'(\d+)\s+pontos\s+por\s+R\$\s*1', sentence)
                if match:
                    points.append(int(match.group(1)))
                # Match "X pontos a cada real"
                match = re.search(r'(\d+)\s+pontos\s+a\s+cada\s+real', sentence)
                if match:
                    points.append(int(match.group(1)))
                # Match "X pontos a cada R$ 1"
                match = re.search(r'(\d+)\s+pontos\s+a\s+cada\s+R\$\s*1', sentence)
                if match:
                    points.append(int(match.group(1)))

                results.append((sentence, points))
                # Extract campaign dates
                date_match = re.search(r'de (\d{1,2}) a (\d{1,2}/\d{2}/\d{2,4})', sentence)
                if date_match:
                    try:
                        from_day = int(date_match.group(1))
                        to_date_str = date_match.group(2)
                        from_date_str = f"{from_day:02d}/{to_date_str.split('/')[1]}/{to_date_str.split('/')[2]}"
                        self.campaign_from = datetime.strptime(from_date_str, '%d/%m/%Y').date()
                        self.campaign_to = datetime.strptime(to_date_str, '%d/%m/%Y').date()
                    except ValueError:
                        print(f"Invalid date format in sentence: {sentence}")
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
    Classe para carregar e manipular uma lista de configurações de parceiros a partir de um arquivo JSON.
    """
    def __init__(self, file_path: str):
        """
        Inicializa a classe com o caminho do arquivo JSON.

        Args:
            file_path (str): Caminho para o arquivo JSON.
        """
        self.file_path = file_path
        self.configs: List[PartnerConfig] = self._load_configs()

    def _load_configs(self) -> List[PartnerConfig]:
        """
        Carrega as configurações do arquivo JSON e retorna uma lista de objetos PartnerConfig.

        Returns:
            List[PartnerConfig]: Lista de configurações de parceiros.
        """
        try:
            with open(self.file_path, 'r') as f:
                data: List[Dict[str, Union[str, float, int, bool]]] = json.load(f)
            return [PartnerConfig(**item) for item in data]
        except FileNotFoundError:
            print(f"Erro: Arquivo não encontrado: {self.file_path}")
            return []
        except json.JSONDecodeError:
            print(f"Erro: Falha ao decodificar o arquivo JSON: {self.file_path}")
            return []
        except (TypeError, KeyError) as e:
            print(f"Erro: Dados inválidos no arquivo JSON: {e}")
            return []

    def get_config_by_partner_code(self, partner_code: str) -> Union[PartnerConfig, None]:
        """
        Retorna a configuração de um parceiro específico pelo código.

        Args:
            partner_code (str): Código do parceiro.

        Returns:
            PartnerConfig or None: Configuração do parceiro, ou None se não encontrado.
        """
        for config in self.configs:
            if config.partner_code == partner_code:
                return config
        return None

    def get_promotional_partners(self, desired_points: int) -> List[PartnerConfig]:
        """
        Retorna uma lista de parceiros que estão em promoção e offer desired points.

        Args:
            desired_points (int): The minimum desired points.

        Returns:
            List[PartnerConfig]: Lista de parceiros em promoção.
        """
        promotional_partners = []
        for config in self.configs:
            if config.promotion and config.get_highest_point() >= desired_points:
                promotional_partners.append(config)
        return promotional_partners

    def print_all_configs(self) -> None:
        """
        Imprime todas as configurações dos parceiros.
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
        
