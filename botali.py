from telethon import TelegramClient, events
import requests
import time

# Dados Telegram (API ID e Hash)
api_id = 28622181
api_hash = '06cd29a358bad8b67fbf93cec7adb014'

# Dados AliExpress (AppKey e AppSecret)
app_key = '515092'
app_secret = 'RlHsRIns4vmoo3iRK0RN2r4k44VqE41r'

# Canais do Telegram
source_channel = 'promoimporta'       # exemplo: '@canaldepromocoes'
destination_channel = 'Promo_ali_Imperdiveis' # exemplo: '@meucanalafiliado'

# Inicializa cliente Telegram
client = TelegramClient('session_name', api_id, api_hash)

# Função para obter token OAuth da API AliExpress (simplificado)
def get_access_token():
    url = 'https://gw.api.alibaba.com/openapi/http/1/system.oauth2/getToken/' 
    params = {
        'grant_type': 'client_credentials',
        'client_id': app_key,
        'client_secret': app_secret
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('access_token')

# Função para gerar link afiliado pelo AliExpress API
def gerar_link_afiliado(access_token, link_original):
    url = 'https://gw.api.alibaba.com/openapi/param2/2/portals.open/api.getPromotionLinks/' 
    params = {
        'access_token': access_token,
        'site': 'ali', 
        'traceId': 'trace123',  # pode gerar um ID aleatório
        'promotionType': 1,
        'urls': [link_original]
    }
    response = requests.post(url, json=params)
    data = response.json()
    try:
        return data['result']['promotionUrls'][0]['url']
    except:
        return None

@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    texto = event.message.message or ''
    fotos = event.message.photo

    # Busca link do AliExpress na mensagem
    links = [word for word in texto.split() if 'aliexpress' in word.lower()]

    if links:
        link_original = links[0]
        access_token = get_access_token()
        if access_token:
            link_afiliado = gerar_link_afiliado(access_token, link_original)
            if link_afiliado:
                novo_texto = texto.replace(link_original, link_afiliado)
            else:
                novo_texto = texto + "\n\n*Erro ao gerar link afiliado*"
        else:
            novo_texto = texto + "\n\n*Erro ao obter token*"

        if fotos:
            await client.send_file(destination_channel, fotos, caption=novo_texto)
        else:
            await client.send_message(destination_channel, novo_texto)

async def main():
    await client.start()
    print('Bot rodando...')
    await client.send_message(destination_channel, "Teste: bot funcionando!")
    await client.run_until_disconnected()

import asyncio
asyncio.run(main())

