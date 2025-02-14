# analisar pagina da livelo para ganho de pontos através de compras

from decimal import Decimal
from json import JSONDecodeError
from typing import Type
from xmlrpc.client import ResponseError
from datetime import date
import requests
import re
from bs4 import BeautifulSoup
import json

def validate_api_info(responseJSON) -> bool:
    error = []
    if("items" not in responseJSON):
        raise TypeError("Lista não está presente no retorno")
    if(not isinstance(responseJSON['items'],list)):
        raise TypeError("Lista não está presente no retorno")
    for item in responseJSON['items']:
        if('seoUrlSlugDerived' not in item):
            error.append('"seoUrlSlugDerived" não está presente no registro')
        if('esf_accumulationAmount' not in item):
            error.append('"esf_accumulationAmount" não está presente no registro')
        if('esf_accumulationHowItWorks' not in item):
            error.append('"esf_accumulationHowItWorks" não está presente no registro')
            

    if(len(error) > 0):
        error_str = "\n".join(error)
        raise Exception(error_str)

    return

def get_campaigns():
    url_base = "https://www.esfera.com.vc/ccstoreui/v1/products"
    
    params = {'categoryId':'esf02163'}
    try:
        response = requests.get(url_base, params=params)
        text = response.text
        list_data = response.json()
        
    except JSONDecodeError:
        print("Erro ao ler JSON, texto retornado. ' "+str(text)+" '")
        exit()
    except ResponseError:
        print("Erro ao buscar na url :"+url_base)
        exit()
    
    try:
        validate_api_info(list_data)
    #except TypeError:
    #    print("Não foi retornado uma lista de dados válida")
    except Exception as e:
        print(e)
        exit()
    return list_data['items']

def validate_categories(sentences : list, categories : list, points_desired : Decimal) -> bool:
    valid = False
    index = 0
    previous_points = Decimal(0)
    points = Decimal(0)
    point_offered = []
    for terms in sentences:
        point_offered = []
        # procurando a pontuação numérica no termo
        points_in_term = re.findall(r'\d+', terms)
        #analisa os pontos presentes nos termos das sentencas
        for points in points_in_term:
            point_offered.append(Decimal(points))
            literal_points = str(1)+" ponto"
            if(Decimal(points) > 1):
                literal_points = str(points) + " pontos"
            #print(literal_points)
            previous_points = Decimal(points)
        # em caso de o termo não ter pontuação, irá utilizar a anterior
        if(len(points_in_term) == 0):
            point_offered.append(previous_points)

        if(len(point_offered) > 1):
            #print("achou mais de uma pontuação termo")
            #print("terms => "+terms)
            points_matches = [" e "+literal_points, " e ganhe "+literal_points]
            #print(any(term_match in terms for term_match in points_matches))
            # identificando subtermos dentro de um termo
            if(any(term_match in terms for term_match in points_matches)):
                search_for = points_matches[0]
                points_term_pos = re.search(search_for, terms)
                if(points_term_pos is None):
                    search_for = points_matches[1]
                    points_term_pos = re.search(search_for, terms)
                    subterm_part = [terms[:points_term_pos.start()],terms[points_term_pos.start():]]
                    index = 0
                else:
                    subterm_part = [terms[:points_term_pos.start()],terms[points_term_pos.start():]]
                    subterm_part = [terms]
                # analisando a presença de categorias e pontuação desejadas no subtermo
                for part in subterm_part:
                    if(any(category in part for category in categories)  and point_offered[index] > points_desired):
                        valid = True
                        break
                    index = index + 1
                if valid:
                    #print("achou a categoria desejada")
                    break
        else:
            #print(len(point_offered))
            # analisando a presença de categorias e pontuação desejadas no termo
            if(any(category in terms for category in categories) and point_offered[0] >= points_desired):
                valid = True
                #print("achou a categoria desejada")
                break
            # em de não encontrar a categoria específica, verifica a pontuação genérica
            if 'demais categorias' in terms and point_offered[0] >=  points_desired:
                valid = True
                break
    
    return valid

# terms = "<p data-renderer-start-pos=\"358\">&bull;&nbsp; &nbsp; Para juntar pontos, acesse o hotsite atrav&eacute;s do bot&atilde;o &ldquo;Ir para o site do parceiro&rdquo;, escolha seus produtos e utilize as op&ccedil;&otilde;es de pagamentos dispon&iacute;veis no site.<br />\n&bull;&nbsp;&nbsp; &nbsp;O ac&uacute;mulo padr&atilde;o &eacute; de 2&nbsp;pontos a cada R$ 1 gasto, podendo ser alterado durante per&iacute;odos promocionais.&nbsp;<strong>Em per&iacute;odos promocionais, o limite de ac&uacute;mulo &eacute; de 200.000 pontos por CPF.</strong><br />\n&bull;&nbsp;&nbsp; &nbsp;O ac&uacute;mulo de pontos s&oacute; &eacute; v&aacute;lido para produtos vendidos e entregues pelo parceiro.</p>\n\n<p>&bull;&nbsp; &nbsp;&nbsp;Compra de Cart&atilde;o Presente (Gift Card/Cart&atilde;o Virtual) atrav&eacute;s do hotsite n&atilde;o ser&aacute; v&aacute;lido para ac&uacute;mulo de pontos.</p>\n\n<p data-renderer-start-pos=\"358\">&bull;&nbsp;&nbsp; &nbsp;O cr&eacute;dito dos pontos Esfera ser&aacute; realizado em 45 dias ap&oacute;s o recebimento do produto e/ou a retirada do produto na loja f&iacute;sica.<br />\n&bull;&nbsp;&nbsp; &nbsp;Os pontos acumulados ser&atilde;o v&aacute;lidos por 24 meses a contar da data do cr&eacute;dito no extrato da conta.<br />\n&bull;&nbsp;&nbsp; &nbsp;A pontua&ccedil;&atilde;o &eacute; v&aacute;lida apenas para compras efetuadas com o CPF do titular do cart&atilde;o de cr&eacute;dito. <strong>O cliente deve ter uma conta ativa na Esfera para receber os pontos.</strong><br />\n&bull;&nbsp;&nbsp; &nbsp;Essa promo&ccedil;&atilde;o n&atilde;o &eacute; cumulativa com outras promo&ccedil;&otilde;es ou com pagamentos efetuados com cupons de desconto, gift cards e vale-compra.</p>\n\n<p>&bull;&nbsp; &nbsp;&nbsp;Todas as op&ccedil;&otilde;es de pagamento dispon&iacute;veis no ato da compra s&atilde;o v&aacute;lidas para esta campanha.<br />\n&bull;&nbsp;&nbsp; &nbsp;Para uma melhor experi&ecirc;ncia e garantia do ac&uacute;mulo de pontos, n&atilde;o feche o hotsite antes de finalizar a compra. Caso voc&ecirc; saia da p&aacute;gina, entre novamente pelo link dispon&iacute;vel no bot&atilde;o &ldquo;Ir para o site do parceiro&rdquo;.<br />\n&bull;&nbsp;&nbsp; &nbsp;Confira o regulamento completo em <a href=\"https://clube.lojasrenner.com.br/b2b/juntecomesfera\">https://clube.lojasrenner.com.br/b2b/juntecomesfera</a></p>"


def is_valid_legal_terms(legalTerms : str, points_desired : Decimal, max_amount : Decimal, categories : list) -> bool:
    valid = False
    # sem termos específicos, se supõe que não pontuação específica por categorias
    if(legalTerms is None):
        return True

    # em caso de pontuação condicionada a valor de compra
    if 'compras acima de' in legalTerms:
        terms_part_pricestart = legalTerms.split('compras acima de ')
        value_start = Decimal(terms_part_pricestart[1].split(" ")[0].replace(",",".").replace("R$",""))
        # verifica se o valor mínimo de compras presente nas regras é aceitável
        if(value_start > max_amount):
            return False

    # em caso de não ter categorias não é necessário realizar validações adicionais
    if(len(categories) == 0):
        return True
    # normalizando o texto para validações
    legalTerms = legalTerms.replace(". ",".").replace("1:1", "1 ponto por real").replace (":1", " pontos por real").replace(" a cada R$ 1,00"," por real")
    # Divide multiplas sentencas separadas por '.', em caso existente
    legal_terms_sentences = legalTerms.split(".")
    
    for sentence in legal_terms_sentences:
        # verifica a existencia do texto característico da pontuação
        if(sentence.find("por real") == -1):
            continue
        # em caso de ocorrer ',' nas sentenças, é identificado como subsentença
        subsentences = sentence.split(",")
        #print(len(subsentences))
        is_valid = validate_categories(subsentences, categories, points_desired)
        if(is_valid):
            return is_valid
        continue    
    
    return valid    

def check_desiredstores_promotions(desired_stores_config, stores_info) -> list:
    promotions_found = []
    for store in stores_info:
        if(store['seoUrlSlugDerived'] not in desired_stores_config):
            continue
        config = desired_stores_config[store['seoUrlSlugDerived']]
        store_dict = dict(store)
        # print(store_dict['esf_accumulationAmount'])
        print(store['seoUrlSlugDerived'])
        parity_club = Decimal(str(store_dict['esf_accumulationAmount']).replace("Até ","").replace("até ","").replace(" pts","").replace(" pt","").replace("de ","").replace(" a ",""))
        min_parity = Decimal(config['min_points'])
        print(config['min_points'])
        max_amount = 99999
        if('max_amount' in config):
            max_amount = Decimal(config['max_amount'])

        legal_terms = ""
        if(store_dict['esf_accumulationHowItWorks'] is not None):
            soup = BeautifulSoup(store_dict['esf_accumulationHowItWorks'], "lxml")
            legal_terms = soup.get_text().replace("•","")
        
        categories = []
        if('categories' in config):
            categories = config['categories']

        if parity_club >= min_parity and is_valid_legal_terms(legal_terms, min_parity, max_amount, categories) and can_send_notification(legal_terms):
            print("Promoção encontrada para "+str(config['name'])+", verificar produtos disponíveis")
            print("Acessar URL: "+str(store['esf_accumulationTargetURL']))
            print("")
            config.update({"legal_terms": store_dict['esf_accumulationHowItWorks']})
            config.update({"url": str(store['esf_accumulationTargetURL'])})
            promotions_found.append(config)

    return promotions_found

def can_send_notification(legal_terms: str) -> bool:
    if(legal_terms == ""):
        return True
    # extract date(s) in legal terms
    campaign_dates = re.findall('\d{2}[\/]\d{2}[\/]\d{2,4}', legal_terms)
    can_send = False
    if(len(campaign_dates) >= 2):
        start_date = campaign_dates[0]
        end_date = campaign_dates[1]
        current_date = date.today().strftime("%d/%m/%Y")
        if(str(current_date) == str(start_date) or str(current_date) == str(end_date)):
            can_send = True
    else:
        # achando apenas uma data com formato esperado, irá tentar encontrar apenas o número referente ao dia(dd)
        start_date = re.findall('[\ ]\d{2}[\ ]', legal_terms)
        end_date = campaign_dates[0]
        if(len(start_date) == 0):
            print("Validade da campanha não fornecida")
            can_send = False
        else: 
            current_day = date.today().strftime("%d")
            current_date = date.today().strftime("%d/%m/%Y")
            if(str(start_date[0]).rstrip().lstrip() == str(current_day) or str(current_date) == str(end_date)):
                can_send = True
    return can_send

def send_notification(to:list, campaigns : list):
    # formatando o texto a ser enviado por email
    texto = "<table align='center'><tr><th><h1>Esfera - "+date.today().strftime("%d/%m/%Y")+"</h1></th></tr>"
    text_categories = ""
    for campaign in campaigns:
        if('categories' not in campaign or len(campaign['categories']) == 0):
            text_categories = " Sem categoria definida"
        else:
            text_categories = ", ".join(campaign['categories'])
        texto += "<tr><td><strong>"+campaign['name']+"</strong><br/><p>Termos procurados: "+text_categories+"</p><p>"+campaign['legal_terms']+"</p><p>URL de acesso: "+campaign['url']+"</p><br/></td><tr/>"
    texto += "</table>"
    # sendinblue request information
    url = 'https://api.sendinblue.com/v3/smtp/email'
    key = "{your-key}"
    headers = {'accept':'application/json','content-type': 'application/json','api-key':key}
    payload = {  
        "sender":{ "name":"Esfera Report","email":"{your-sender}" },
        "to": to,
        "subject":"Relatório de análise - Esfera",
        "htmlContent":texto
    }
    try:
        sib_request = requests.post(url, json=payload, headers=headers)
    except ResponseError:
        print("Erro de resposta")
    except:
        print("erro genérico ao enviar")
    finally:
        sib_request.close()

# categories => livros; casa, mesa e banho; eletrodomésticos; eletroportáteis/portáteis; masculino; feminino; brinquedos; telefonia
# lista de desejos
file_data = open("database/esfera.json")
desired_stores = json.load(file_data)

today = date.today()
print(today.strftime("%d/%m/%Y"))
available_campaigns = get_campaigns()
list_found = check_desiredstores_promotions(desired_stores, available_campaigns)
count_stores = len(list_found)
send_to = []
if(count_stores == 0):
    print("Nenhuma promoção encontrada!")
else:
    send_to.append({"email":"{your-email}","name":"{ your-name }"})
    print(str(count_stores)+" encontrados e serão incluídas na notificação")
    send_notification(send_to, list_found)
