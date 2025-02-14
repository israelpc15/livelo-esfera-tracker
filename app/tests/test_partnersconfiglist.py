import datetime
import pytest
from app.partnersconfig_class import PartnerConfig
from app.partnersconfiglist_class import PartnerConfigList
from app.watchstore_class import WatchStore

@pytest.fixture
def sample_configs():
    # Create a list of partner configuration dictionaries
    return [
        {
            "partnerCode": "CEN",
            "currency": "R$",
            "currencyValue": 1,
            "parity": 2,
            "parityClub": 2,
            "legalTerms": "Ganhe 4 pontos por real. Campanha válida de 1 a 30/12/2099.", 
            "promotion": True,
            "url": "",
            "separator": "=",
            "parityBau": 2,
            "separatorSlug": "IGUAL"
        },
        {
            "partnerCode": "BOK",
            "currency": "U$",
            "currencyValue": 1,
            "parity": 4,
            "parityClub": 4,
            "legalTerms": "Não acumulam pontos.", 
            "promotion": False,
            "url": "",
            "separator": "=",
            "parityBau": 4,
            "separatorSlug": "IGUAL"
        }
    ]

@pytest.fixture
def config_list(sample_configs):
    return PartnerConfigList(sample_configs)

@pytest.fixture
def sample_watchstores():
    # Create a sample list of WatchStore objects, matching partner "CEN"
    watchstores_data = [
        {
          "code": "CEN",
          "name": "Centauro",
          "valid_until": "2099-12-31",
          "min_points": 4,
          "categories": []
        },
        {
          "code": "EXT",
          "name": "Extra",
          "valid_until": "2099-12-31",
          "min_points": 6,
          "categories": []
        }
    ]
    return [WatchStore.from_dict(item) for item in watchstores_data]

def test_get_promotional_partners_without_watchstores(config_list):
    partners = config_list.get_promotional_partners(4)
    # Only the "CEN" configuration is promotional and should be returned.
    assert len(partners) == 1
    assert partners[0].partner_code == "CEN"

def test_get_promotional_partners_with_watchstores(config_list, sample_watchstores):
    # When filtering with a watchstores list, only partners matching a store (by partnerCode) are returned.
    partners = config_list.get_promotional_partners(4, watchstores=sample_watchstores)
    # Only "CEN" matches between partner configurations and watchstore codes.
    assert len(partners) == 1
    assert partners[0].partner_code == "CEN"
