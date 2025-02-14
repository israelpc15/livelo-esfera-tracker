from app.partnersconfiglist_class import PartnerConfigList

# Exemplo de uso:
if __name__ == "__main__":
    config_list = PartnerConfigList("./app/database/response_livelo.json")

    # Obtém parceiros em promoção
    promotional_partners = config_list.get_promotional_partners(4)
    print("\nParceiros em promoção:")
    for partner in promotional_partners:
        print(partner.partner_code)
        if(partner.has_active_campaign()):
            print("Tem campanha ativa")
            print(str(partner.campaign_from) + " até "+ str(partner.campaign_to))
        
