from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

chrome_options = Options()
# Remover a linha abaixo para que o Chrome não seja executado em modo headless
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")

# Configurar o ChromeDriver automaticamente com webdriver-manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Acesse a página de login
driver.get('https://pt.surebet.com/users/sign_in')

# Aguarde a página carregar
time.sleep(2)

# Preencha o formulário de login
email_field = driver.find_element(By.ID, 'user_email')
password_field = driver.find_element(By.ID, 'user_password')

email_field.send_keys('assmdx@gmail.com')
password_field.send_keys('32412426Aa')

# Submeta o formulário
password_field.send_keys(Keys.RETURN)

# Aguarde o login ser processado
time.sleep(5)

# Acesse a página das surebets
driver.get('https://pt.surebet.com/surebets')

# Aguarde a página carregar completamente
time.sleep(5)

# Localize a tabela com id 'surebets-table'
surebets_table = driver.find_element(By.ID, 'surebets-table')

# Estrutura para armazenar os dados dos eventos
events = []

# Iterar pelos tbody elementos para coletar os dados
tbody_elements = surebets_table.find_elements(By.TAG_NAME, 'tbody')

for tbody in tbody_elements:
    event_data = {}
    
    try:
        lucro = tbody.find_element(By.CLASS_NAME, 'profit').text
        event = tbody.find_element(By.CLASS_NAME, 'event').text
        quando = tbody.find_element(By.CLASS_NAME, 'time').text
        esporte = tbody.find_element(By.CLASS_NAME, 'minor').text

        # Dados da primeira casa de apostas (primeira linha)
        first_row = tbody.find_elements(By.TAG_NAME, 'tr')[0]
        casa01 = first_row.find_element(By.CLASS_NAME, 'booker').text
        link01 = first_row.find_element(By.CLASS_NAME, 'value_link').get_attribute('href')
        mercado01 = first_row.find_element(By.CLASS_NAME, 'coeff').text
        descricao01 = first_row.find_element(By.TAG_NAME, 'abbr').get_attribute('data-bs-original-title')
        minorc01 = first_row.find_element(By.CLASS_NAME, 'minorc').text
        odd01 = first_row.find_element(By.CLASS_NAME, 'value').text

        # Dados da segunda casa de apostas (segunda linha)
        second_row = tbody.find_elements(By.TAG_NAME, 'tr')[1]
        casa02 = second_row.find_element(By.CLASS_NAME, 'booker').text
        link02 = second_row.find_element(By.CLASS_NAME, 'value_link').get_attribute('href')
        mercado02 = second_row.find_element(By.CLASS_NAME, 'coeff').text
        descricao02 = second_row.find_element(By.TAG_NAME, 'abbr').get_attribute('data-bs-original-title')
        minorc02 = second_row.find_element(By.CLASS_NAME, 'minorc').text
        odd02 = second_row.find_element(By.CLASS_NAME, 'value').text

        # Adicionar os dados coletados ao dicionário do evento
        event_data = {
            'Lucro': lucro,
            'Evento': event,
            'Quando': quando,
            'Esporte': esporte,
            'Casa01': casa01,
            'Link01': link01,
            'Mercado01': mercado01,
            'Descricao01': descricao01,
            'minorc01': minorc01,
            'Odd01': odd01,
            'Casa02': casa02,
            'Link02': link02,
            'Mercado02': mercado02,
            'Descricao02': descricao02,
            'minorc02': minorc02,
            'Odd02': odd02,
        }
        
        events.append(event_data)
    
    except Exception as e:
        print(f"Erro ao processar tbody: {e}")

# Converter os dados dos eventos em JSON
events_json = json.dumps(events, ensure_ascii=False, indent=4)

# Salvar o JSON em um arquivo na raiz do projeto
with open("surebets_data.json", "w", encoding="utf-8") as json_file:
    json_file.write(events_json)

# Feche o navegador
driver.quit()
