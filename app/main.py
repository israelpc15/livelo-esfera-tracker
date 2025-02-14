import json
from app.services.restapi_class import RestApiClient
from app.livelo_partners_list_class import LiveloPartnersList
from app.watchstore_class import WatchStore
from app.esfera_partners_list import EsferaPartnersList

if __name__ == "__main__":
    # Load watchstores data from JSON file and create WatchStore objects
    with open("./app/database/watchstoreslist.json", "r") as f:
        watchstores_data = json.load(f)
    watchstores = [WatchStore.from_dict(item) for item in watchstores_data]

    # Extract watchstore codes as a list and join them into a comma-separated string.
    watchstore_codes = [ws.code for ws in watchstores]
    partners_codes = ",".join(watchstore_codes)
    
    watchstore_names = [ws.name for ws in watchstores]
    partners_names = ",".join(watchstore_names)

    # Create a RestApiClient instance; optionally set base_url and headers
    # client = RestApiClient(base_url="https://apis.pontoslivelo.com.br", headers={"accept": "application/json"})
    client = RestApiClient(base_url="https://www.esfera.com.vc", headers={"accept": "application/json"})
    
    # Example GET request
    #expected_json = client.get("/api-bff-partners-parities/v1/parities/active", params={"partnersCodes": partners_codes})
    expected_json = client.get("/ccstoreui/v1/products", params={"categoryId": "esf02163"})
    # Extract data from response_esfera.json using the extractor
    extractor = EsferaPartnersList(expected_json, partners_names)
    partners_list = extractor.extract_data()

    # Load partner configurations from JSON file
    #config_list = PartnerConfigList("./app/database/response_livelo.json")
    # Obtain promotional partners by passing the watchstores list as an optional parameter
    #partners_list = config_list.get_promotional_partners(4, watchstores=watchstores)
    
    print("\nPromotional Partners:")
    for partner in partners_list:
        print(partner)
        print(partner.partner_name)
        if partner.has_active_campaign():
            print("Active campaign")
            print(f"{partner.campaign_from} until {partner.campaign_to}")
