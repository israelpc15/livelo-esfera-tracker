import datetime
from app.partnersconfig_class import PartnerConfig

def test_analyze_legal_terms_for_points_empty():
    config = PartnerConfig("CEN", 2, 2, "", False)
    result = config.analyze_legal_terms_for_points()
    # When no legal terms are provided, expect an empty list.
    assert result == []

def test_analyze_legal_terms_for_points_with_points():
    legal_terms = "Ganhe 4 pontos por real em compras. Campanha válida de 1 a 30/12/2099."
    config = PartnerConfig("CEN", 2, 2, legal_terms, True)
    result = config.analyze_legal_terms_for_points()
    # Expect that at least one sentence contains the number 4 in its points list.
    assert any(4 in points for sentence, points in result)
    # Check that campaign dates were extracted.
    assert config.campaign_from is not None
    assert config.campaign_to is not None

def test_get_highest_point():
    legal_terms = "Ganhe 5 pontos por real; Ganhe 3 pontos por R$ 1."
    config = PartnerConfig("CEN", 2, 2, legal_terms, True)
    highest = config.get_highest_point()
    assert highest == 5

def test_has_active_campaign():
    # Set both campaign_from and campaign_to to today (active campaign)
    today = datetime.date.today()
    config_active = PartnerConfig("CEN", 2, 2, "Some terms", True, campaign_from=today, campaign_to=today)
    assert config_active.has_active_campaign() is True

    # Set campaign dates to yesterday (inactive campaign)
    yesterday = today - datetime.timedelta(days=1)
    config_inactive = PartnerConfig("CEN", 2, 2, "Some terms", True, campaign_from=yesterday, campaign_to=yesterday)
    assert config_inactive.has_active_campaign() is False
