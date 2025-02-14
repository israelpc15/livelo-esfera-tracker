import json
from app.services.restapi_class import RestApiClient
from app.partnersconfiglist_class import PartnerConfigList
from app.watchstore_class import WatchStore

if __name__ == "__main__":
    # Load watchstores data from JSON file and create WatchStore objects
    with open("./app/database/watchstoreslist.json", "r") as f:
        watchstores_data = json.load(f)
    watchstores = [WatchStore.from_dict(item) for item in watchstores_data]

    # Extract watchstore codes as a list and join them into a comma-separated string.
    watchstore_codes = [ws.code for ws in watchstores]
    partners_codes = ",".join(watchstore_codes)

    # Create a RestApiClient instance; optionally set base_url and headers
    client = RestApiClient(base_url="https://apis.pontoslivelo.com.br", headers={"accept": "application/json"})
    
    # Example GET request
    expected_json = client.get("/api-bff-partners-parities/v1/parities/active", params={"partnersCodes": partners_codes})

    # Load partner configurations from JSON file
    #config_list = PartnerConfigList("./app/database/response_livelo.json")
    config_list = PartnerConfigList(expected_json)
    
    # Obtain promotional partners by passing the watchstores list as an optional parameter
    promotional_partners = config_list.get_promotional_partners(4, watchstores=watchstores)
    print("\nPromotional Partners:")
    for partner in promotional_partners:
        print(partner.partner_code)
        if partner.has_active_campaign():
            print("Active campaign")
            print(f"{partner.campaign_from} until {partner.campaign_to}")
