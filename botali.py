from telethon import TelegramClient, events
import requests
import json
import asyncio
import hashlib
import time
from urllib.parse import quote

# Dados Telegram (API ID e Hash)
api_id = 28622181
api_hash = '06cd29a358bad8b67fbf93cec7adb014'

# Dados AliExpress (AppKey e AppSecret)
app_key = '515092'
app_secret = 'RlHsRIns4vmoo3iRK0RN2r4k44VqE41r'

# Canais do Telegram
source_channel = 'promoimporta'
destination_channel = 'Promo_ali_Imperdiveis'

# Inicializa cliente Telegram
client = TelegramClient('session_name', api_id, api_hash)

# Função para gerar assinatura MD5
def generate_signature(params, secret):
    # Ordena os parâmetros alfabeticamente
    sorted_params = sorted(params.items())
    
    # Cria string concatenada
    param_string = ''.join([f'{key}{value}' for key, value in sorted_params])
    
    # Adiciona o secret no início e fim
    sign_string = f'{secret}{param_string}{secret}'
    
    # Gera hash MD5
    return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

# Função para gerar link afiliado usando a API correta
def gerar_link_afiliado(link_original):
    # Endpoint correto para Business interfaces
    url = 'https://gw.api.taobao.com/router/rest'
    
    # Timestamp no formato correto
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Parâmetros da requisição
    params = {
        'method': 'aliexpress.affiliate.link.generate',
        'app_key': app_key,
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
        'sign_method': 'md5',
        'promotion_link_type': '0',
        'source_values': link_original
    }
    
    # Gera assinatura
    signature = generate_signature(params, app_secret)
    params['sign'] = signature
    
    try:
        response = requests.post(url, data=params)
        if response.status_code == 200:
            data = response.json()
            if 'aliexpress_affiliate_link_generate_response' in data:
                result = data['aliexpress_affiliate_link_generate_response']['resp_result']
                if result['resp_code'] == 200:
                    return result['result']['promotion_links'][0]['promotion_link']
                else:
                    print(f'Erro na API: {result["resp_msg"]}')
                    return None
            else:
                print('Resposta inesperada da API:', data)
                return None
        else:
            print(f'Erro HTTP: {response.status_code} {response.text}')
            return None
    except Exception as e:
        print(f'Erro na requisição: {e}')
        return None

# Evento para capturar mensagens do canal de origem
@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    texto = event.message.message or ''
    fotos = event.message.photo

    # Busca link do AliExpress na mensagem
    links = [word for word in texto.split() if 'aliexpress' in word.lower()]

    if links:
        link_original = links[0]
        link_afiliado = gerar_link_afiliado(link_original)
        
        if link_afiliado:
            # Remove o link original completamente
            texto_sem_link = texto.replace(link_original, '')
            # Monta novo texto com link afiliado no lugar
            novo_texto = texto_sem_link.strip() + '\n\n' + link_afiliado
        else:
            novo_texto = texto + "\n\n*Erro ao gerar link afiliado*"
    else:
        novo_texto = texto

    if fotos:
        await client.send_file(destination_channel, fotos, caption=novo_texto)
    else:
        await client.send_message(destination_channel, novo_texto)

async def main():
    await client.start()
    print('Bot rodando...')
    await client.send_message(destination_channel, "Teste: bot funcionando!")
    await client.run_until_disconnected()

asyncio.run(main())
