# analisar pagina da livelo para ganho de pontos através de compras

from decimal import Decimal
from json import JSONDecodeError
from xmlrpc.client import ResponseError
from datetime import date
import requests
import re
from bs4 import BeautifulSoup
import json

def validate_api_info(responseJSON) -> bool:
    error = []
    if(not isinstance(responseJSON,list)):
        raise TypeError("the variable is not valid list")
    for item in responseJSON:
        if('parityClub' not in item):
            error.append('parityClub is not present on records')
        if('legalTerms' not in item):
            error.append('legalTerms is not present on records')

    if(len(error) > 0):
        error_str = "\n".join(error)
        raise Exception(error_str)

    return

def get_campaigns(partners):
    url_base = "https://apis.pontoslivelo.com.br/partners-campaign/v1/campaigns/active"
    
    params = {'partnersCodes':partners}
    try:
        response = requests.get(url_base, params=params)
        text = response.text
        list_data = response.json()
        
    except JSONDecodeError:
        print("JSON text error: ' "+str(text)+" '")
        exit()
    except ResponseError:
        print("URL error: "+url_base)
        exit()
    
    try:
        validate_api_info(list_data)
    except TypeError:
        print("The provided list is not valid")
    except Exception as e:
        print(e)
        exit()
    return list_data


# Ex: "Ganhe 4 pontos por real gasto na categoria de brinquedos e jogos e 1 ponto por real nas demais categorias para produtos vendidos e entregues por Amazon."
# terms = [":1"," por real"]
def validate_categories(sentences : list, categories : list, points_desired : Decimal) -> bool:
    valid = False
    index = 0
    previous_points = Decimal(0)
    points = Decimal(0)
    point_offered = []
    for terms in sentences:
        point_offered = []
        # check for numbers in terms
        points_in_term = re.findall(r'\d+', terms)

        # check the points provided in terms
        for points in points_in_term:
            point_offered.append(Decimal(points))
            literal_points = str(1)+" ponto"

            if(Decimal(points) > 1):
                literal_points = str(points) + " pontos"

            print(literal_points)
            previous_points = Decimal(points)

        # if doesn't have points in term, use the previous value
        if(len(points_in_term) == 0):
            point_offered.append(previous_points)

        # check if exists more than on condition of points on text
        if(len(point_offered) > 1):
            print("blah")
            points_matches = [" e "+literal_points, " e ganhe "+literal_points]
            search_for = points_matches[0]
            points_term_pos = re.search(search_for, terms)
            if(points_term_pos is None):
                search_for = points_matches[1]
                points_term_pos = re.search(search_for, terms)
                index = 0
                if(points_term_pos is None):
                    print(" It was not found texts with terms ' e x pontos ' either ' e ganhe x pontos' ")
                    continue

            subterm_part = [terms[:points_term_pos.start()],terms[points_term_pos.start():]]
            # check presence of categories and desired points on subterms
            for part in subterm_part:
                if(any(category in part for category in categories)  and point_offered[index] >= points_desired):
                    valid = True
                    break
                if 'demais categorias' in terms and point_offered[len(point_offered)-1] >=  points_desired:
                    valid = True
                    break
                index = index + 1
            if valid:
                #print("achou a categoria desejada")
                break
        else:
            # check for categories and points in term
            if(any(category in terms for category in categories) and point_offered[0] >= points_desired):
                valid = True
                print("category found")
                break
            
            # if no category was found, get the stardard points
            if ('demais categorias' in terms) and (len(point_offered) == 1 and point_offered[0] >=  points_desired):
                valid = True
                print(terms+" found categories")
                break

    
    return valid


def is_valid_legal_terms(legalTerms : str, points_desired : Decimal, max_amount : Decimal, categories : list) -> bool:
    is_valid = False
    # no specific points by categories 
    if(legalTerms is None):
        return True

    if('produtos selecionados' in legalTerms):
        return False
    
    # if has mininum price to earn points with specific text
    if 'compras acima de' in legalTerms:
        terms_part_pricestart = legalTerms.split('compras acima de ')
        value_start = Decimal(terms_part_pricestart[1].split(" ")[0].replace(",",".").replace("R$",""))
        
        # check if minimum price is acceptable
        if(value_start > max_amount):
            return False
    
    
    # if doesn't have categories, no need to continue processing
    if(len(categories) == 0):
        return True
    
    # normalyzing text to additional validations
    legalTerms = legalTerms.replace(". ",".").replace("1:1", "1 ponto por real").replace (":1", " pontos por real")
    
    legal_terms_sentences = legalTerms.split(".")
    for sentence in legal_terms_sentences:
        # check existance of specific text in term
        if(sentence.find("por real") == -1):
            continue
        
        # if has ',' on sentence, is identified as subsentence or terms
        subsentences = sentence.split(",")
        is_valid = validate_categories(subsentences, categories, points_desired)
        if(is_valid):
            return is_valid
        continue    
    
    return is_valid

def check_desiredstores_promotions(desired_stores_config : dict, stores_info : list) -> list:
    url_base = "https://www.livelo.com.br/ganhe-pontos-compre-pontue-"
    promotions_found = []
    for store in stores_info:
        config = dict(desired_stores_config[store['partnerCode']])
        store_dict = dict(store)
        parity_club = Decimal(store_dict['parityClub'])
        min_parity = Decimal(config['min_points'])
        max_amount = 99999
        if('max_amount' in config):
            max_amount = Decimal(config['max_amount'])
        legal_terms = ""
        if(store_dict['legalTerms'] is not None):
            legal_terms = store_dict['legalTerms']
        categories = []
        if('categories' in config):
            categories = config['categories']
        print("Observing "+str(config['name']))
        if parity_club >= min_parity and is_valid_legal_terms(legal_terms, min_parity, max_amount, categories) and can_send_notification(legal_terms):
            print("Promoção encontrada para "+str(config['name']))
            campaign_url = url_base+str(config['name']).lower().replace(" ","")
            print("Acessar URL: "+campaign_url)
            print("")
            config.update({"url": campaign_url})
            config.update({"legal_terms": legal_terms})
            promotions_found.append(config)
            
    
    return promotions_found

def can_send_notification(legal_terms: str) -> bool:
    if(legal_terms == ""):
        return True
    # extract date(s) in legal terms
    campaign_dates = re.findall('\d{2}[\/]\d{2}[\/]\d{2,4}', legal_terms)
    can_send = False
    if(len(campaign_dates) == 2):
        start_date = campaign_dates[0]
        end_date = campaign_dates[1]
        current_date = date.today().strftime("%d/%m/%Y")
        if(str(current_date) == str(start_date) or str(current_date) == str(end_date)):
            can_send = True
    else:
        # if has only one date with correct format, it will check fo additional number for day (dd)
        start_date = re.findall('[\ ]\d{2}[\ ]', legal_terms)
        end_date = campaign_dates[0]
        if(len(start_date) == 0):
            print("Campaign is lacking dates")
            can_send = False
        else: 
            current_day = date.today().strftime("%d")
            current_date = date.today().strftime("%d/%m/%Y")
            if(str(start_date[0]).rstrip().lstrip() == str(current_day) or str(current_date) == str(end_date)):
                can_send = True
    return can_send

def send_notification(to:list, campaigns : list):
    # formatting text for email
    texto = "<table align='center'><tr><th><h1>Livelo - "+date.today().strftime("%d/%m/%Y")+"</h1></th></tr>"
    text_categories = ""
    for campaign in campaigns:
        if('categories' not in campaign or len(campaign['categories']) == 0):
            text_categories = " No category"
        else:
            text_categories = ", ".join(campaign['categories'])
        
        text_lines = str(campaign['legal_terms']).split(". ")
        desired_points = campaign['min_points']
        full_terms = ".<br/>".join(text_lines)
        texto += "<tr><td><strong>"+campaign['name']+"</strong><br/><p>Search Terms: "+text_categories+"</p><p>Minimum amount of points: "+str(desired_points)+"</p><p>"+full_terms+"</p><p>URL Access: "+campaign['url']+"</p></td><tr/>"

    texto += "</table>"
    # sendinblue request information
    url = 'https://api.sendinblue.com/v3/smtp/email'
    key = "{ you-key }"
    headers = {'accept':'application/json','content-type': 'application/json','api-key':key}
    payload = {  
        "sender":{ "name":"Livelo Report","email":"{ your-sender }" },
        "to": to,
        "subject":"Analysis Report - Livelo",
        "htmlContent":texto
    }
    try:
        sib_request = requests.post(url, json=payload, headers=headers)
        print(sib_request.json())
    except ResponseError:
        print("API Error")
    except:
        print("Generic error")
    finally:
        sib_request.close()

# categories (portuguese) => livros; casa, mesa e banho; eletrodomésticos; eletroportáteis/portáteis; masculino; feminino; brinquedos; telefonia
# desired stores in relationship program
file_data = open("database/livelo.json")
desired_stores = json.load(file_data)

today = date.today()
print(today.strftime("%d/%m/%Y"))
available_campaigns = get_campaigns(desired_stores)
list_found = check_desiredstores_promotions(desired_stores, available_campaigns)
count_stores = len(list_found)
send_to = []
if(count_stores == 0):
    print("Nenhuma promoção encontrada!")
else:
    send_to.append({"email":"{ your-email }","name":"{ your-name }"})
    print(str(count_stores)+" stores found and a e-mail will be sent")
    send_notification(send_to, list_found)

