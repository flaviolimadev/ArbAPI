import pymysql
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager

# Configurações do Selenium e ChromeDriver usando webdriver-manager
options = Options()
# options.add_argument('--headless')  # Executar sem interface gráfica, opcional
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Inicializar o driver do Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Conectar ao banco de dados MySQL
conn = pymysql.connect(
    host='localhost',       # Seu host MySQL
    user='root',            # Seu usuário MySQL
    password='',            # Sua senha MySQL
    database='apiarb'       # Nome do banco de dados
)

cursor = conn.cursor()

# Lista para armazenar os dados para o JSON
data_list = []

def format_datetime(datetime_str):
    """Formata a string de data e hora removendo a quebra de linha e ajustando para o formato esperado."""
    try:
        # Remover a quebra de linha
        date_time = datetime_str.replace("\n", " ")
        # Converter para o formato esperado pelo MySQL
        formatted_date_time = time.strptime(date_time, "%d/%m %H:%M")
        return time.strftime("%Y-%m-%d %H:%M:%S", formatted_date_time)
    except Exception as e:
        print(f"Erro ao formatar data/hora: {e}")
        return None

try:
    # Acesse a página de login
    driver.get("https://pt.surebet.com/users/sign_in")

    # Aguarde o carregamento da página de login
    time.sleep(3)

    # Preencha os campos de login
    driver.find_element(By.ID, "user_email").send_keys("assmdx@gmail.com")  # Atualize com seu email
    driver.find_element(By.ID, "user_password").send_keys("32412426Aa")  # Atualize com sua senha

    # Clique no botão de login
    driver.find_element(By.NAME, "commit").click()

    # Aguarde o login ser processado e a próxima página carregar
    time.sleep(5)

    # Verifique se o login foi bem-sucedido e, em seguida, navegue para a página das Surebets
    driver.get("https://pt.surebet.com/surebets")

    # Aguarde a página de surebets carregar
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
            lucro = tbody.find_element(By.CLASS_NAME, 'profit').text if tbody.find_elements(By.CLASS_NAME, 'profit') else None
            evento = tbody.find_element(By.CLASS_NAME, 'event').text if tbody.find_elements(By.CLASS_NAME, 'event') else None
            quando_raw = tbody.find_element(By.CLASS_NAME, 'time').text if tbody.find_elements(By.CLASS_NAME, 'time') else None
            esporte = tbody.find_element(By.CLASS_NAME, 'minor').text if tbody.find_elements(By.CLASS_NAME, 'minor') else None

            # Formatar data/hora
            quando = format_datetime(quando_raw)

            # Dados da primeira casa de apostas (primeira linha)
            first_row = tbody.find_elements(By.TAG_NAME, 'tr')[0] if tbody.find_elements(By.TAG_NAME, 'tr') else None
            casa01 = first_row.find_element(By.CLASS_NAME, 'booker').text if first_row and first_row.find_elements(By.CLASS_NAME, 'booker') else None
            link01 = first_row.find_element(By.CLASS_NAME, 'value_link').get_attribute('href') if first_row and first_row.find_elements(By.CLASS_NAME, 'value_link') else None
            mercado01 = first_row.find_element(By.CLASS_NAME, 'coeff').text if first_row and first_row.find_elements(By.CLASS_NAME, 'coeff') else None
            descricao01 = first_row.find_element(By.TAG_NAME, 'abbr').get_attribute('data-bs-original-title') if first_row and first_row.find_elements(By.TAG_NAME, 'abbr') else None
            minorc01 = first_row.find_element(By.CLASS_NAME, 'minorc').text if first_row and first_row.find_elements(By.CLASS_NAME, 'minorc') else None
            odd01 = first_row.find_element(By.CLASS_NAME, 'value').text if first_row and first_row.find_elements(By.CLASS_NAME, 'value') else None

            # Dados da segunda casa de apostas (segunda linha)
            second_row = tbody.find_elements(By.TAG_NAME, 'tr')[1] if len(tbody.find_elements(By.TAG_NAME, 'tr')) > 1 else None
            casa02 = second_row.find_element(By.CLASS_NAME, 'booker').text if second_row and second_row.find_elements(By.CLASS_NAME, 'booker') else None
            link02 = second_row.find_element(By.CLASS_NAME, 'value_link').get_attribute('href') if second_row and second_row.find_elements(By.CLASS_NAME, 'value_link') else None
            mercado02 = second_row.find_element(By.CLASS_NAME, 'coeff').text if second_row and second_row.find_elements(By.CLASS_NAME, 'coeff') else None
            descricao02 = second_row.find_element(By.TAG_NAME, 'abbr').get_attribute('data-bs-original-title') if second_row and second_row.find_elements(By.TAG_NAME, 'abbr') else None
            minorc02 = second_row.find_element(By.CLASS_NAME, 'minorc').text if second_row and second_row.find_elements(By.CLASS_NAME, 'minorc') else None
            odd02 = second_row.find_element(By.CLASS_NAME, 'value').text if second_row and second_row.find_elements(By.CLASS_NAME, 'value') else None

            # Verifique se já existe um registro idêntico no banco de dados
            check_sql = """
                SELECT COUNT(*) FROM sures WHERE lucro = %s AND evento = %s AND quando = %s
                AND esport = %s AND casa01 = %s AND mercado01 = %s AND descricao01 = %s AND odd01 = %s
                AND casa02 = %s AND mercado02 = %s AND descricao02 = %s AND odd02 = %s
            """
            cursor.execute(check_sql, (lucro, evento, quando, esporte, casa01, mercado01, descricao01, odd01, casa02, mercado02, descricao02, odd02))
            result = cursor.fetchone()

            if result[0] == 0:  # Se não existir, insira o novo registro
                # Adicionar os dados ao banco de dados com as conversões necessárias
                lucro_float = float(lucro.replace("%", "").replace(",", ".")) if lucro else None
                odd01_int = int(float(odd01.replace(",", ".")) * 100) if odd01 else None
                odd02_int = int(float(odd02.replace(",", ".")) * 100) if odd02 else None

                sql = """
                    INSERT INTO sures (lucro, evento, quando, esport, casa01, link01, mercado01, descricao01, minorc01, Odd01, casa02, link02, mercado02, descricao02, minorc02, Odd02)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (lucro_float, evento, quando, esporte, casa01, link01, mercado01, descricao01, minorc01, odd01_int, casa02, link02, mercado02, descricao02, minorc02, odd02_int))
                conn.commit()

                # Adicionar o dicionário à lista para o JSON
                data = {
                    "lucro": lucro,
                    "evento": evento,
                    "quando": quando_raw,  # Armazena o valor original para o JSON
                    "esporte": esporte,
                    "casa01": casa01,
                    "link01": link01,
                    "mercado01": mercado01,
                    "descricao01": descricao01,
                    "minorc01": minorc01,
                    "odd01": odd01,
                    "casa02": casa02,
                    "link02": link02,
                    "mercado02": mercado02,
                    "descricao02": descricao02,
                    "minorc02": minorc02,
                    "odd02": odd02
                }

                data_list.append(data)

        except Exception as e:
            print(f"Erro ao processar tbody: {e}")

    # Escrever os dados em um arquivo JSON
    with open("sures_data.json", "w") as json_file:
        json.dump(data_list, json_file, indent=4)

finally:
    driver.quit()
    cursor.close()
    conn.close()
