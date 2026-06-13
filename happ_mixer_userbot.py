import asyncio
import re
import base64
import subprocess
import requests
from telethon import TelegramClient, events
import logging
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

logging.basicConfig(level=logging.INFO)

# ================== AYARLAR ==================
api_id = 26296032
api_hash = 'daff7fd01e17fb6ac5cfe241441475d7'

source_channels = ['@Happ_VPN_official', '@aboutmyselfalex']
target_channels = ['@vpnruss1']
LOG_CHANNEL = '@alexanderlogger'

DECRYPT_BINARY = './linux-x64_x86'  # binary yolu

MIX_MACROS = "https://script.google.com/macros/s/AKfycby6bSt2cNMil43ZIv0sHwXUnEHfMqN2hbjGETfPG1m_iwjkO_ih_yp6pXt-NVc48_6w/exec?url=https://mix-macros.alexanderoff.ru/mixed/@vpnruss1/?url="

last_proxy = "https://t.me/proxy?server=tproxy.mom&port=8090&secret=ee104462821249bd7ac519130220c25d09617669746f2e7275"

# ====================== TEMPLATE ======================
TEMPLATE = (
    "Happ VPN Поставьте Лайкусики❤️ 🏷Купить ВПН: @digitalservvicebot\n"
    "Внизу стоит бесплатный ключ для приложения HAPP 😎\n\n"
    "```\n"
    "happ://crypt4/{encrypted_code}\n"
    "```\n\n"
    "✈️ Телеграм прокси ✅\n"
    "{proxy}\n\n"
    "➡️ Купить в Боте: @digitalservvicebot🤖\n"
    "Используйте только последние ключи на канале 😎\n"
    "Каждые +500 ❤️ +24 часов работы!"
)

# ====================== RSA KEYS (crypt4 encrypt için) ======================
PUBLIC_KEYS = {
    "happ://crypt4/": """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA3UZ0M3L4K+WjM3vkbQnz
ozHg/cRbEXvQ6i4A8RVN4OM3rK9kU01FdjyoIgywve8OEKsFnVwERZAQZ1Trv60B
hmaM76QQEE+EUlIOL9EpwKWGtTL5lYC1sT9XJMNP3/CI0gP5wwQI88cY/xedpOEB
W72EmOOShHUm/b/3m+HPmqwc4ugKj5zWV5SyiT829aFA5DxSjmIIFBAms7DafmSq
LFTYIQL5cShDY2u+/sqyAw9yZIOoqW2TFIgIHhLPWek/ocDU7zyOrlu1E0SmcQQb
LFqHq02fsnH6IcqTv3N5Adb/CkZDDQ6HvQVBmqbKZKf7ZdXkqsc/Zw27xhG7OfXC
tUmWsiL7zA+KoTd3avyOh93Q9ju4UQsHthL3Gs4vECYOCS9dsXXSHEY/1ngU/hjO
WFF8QEE/rYV6nA4PTyUvo5RsctSQL/9DJX7XNh3zngvif8LsCN2MPvx6X+zLouBX
zgBkQ9DFfZAGLWf9TR7KVjZC/3NsuUCDoAOcpmN8pENBbeB0puiKMMWSvll36+2M
YR1Xs0MgT8Y9TwhE2+TnnTJOhzmHi/BxiUlY/w2E0s4ax9GHAmX0wyF4zeV7kDkc
vHuEdc0d7vDmdw0oqCqWj0Xwq86HfORu6tm1A8uRATjb4SzjTKclKuoElVAVa5Jo
oh/uZMozC65SmDw+N5p6Su8CAwEAAQ==
-----END PUBLIC KEY-----"""
}

# ====================== FONKSİYONLAR ======================

def extract_proxy(text):
    match = re.search(r'(https?://t\.me/proxy\?[^ \n]+)', text)
    return match.group(1) if match else None

def decrypt_crypt5(happ_link):
    """Отправляет crypt5 ссылку на удаленный сервер Render для дешифрации"""
    try:
        url = "https://happ-decrypt-server-ogry.onrender.com/decrypt"
        response = requests.post(url, json={"text": happ_link}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get("decrypted")
        else:
            print(f"Ошибка сервера Render: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка подключения к Render: {e}")
        return None

def encrypt_happ_link(url: str):
    """URL'yi MIX_MACROS üzerinden crypt4 olarak encrypt eder"""
    try:
        mixed_url = MIX_MACROS + requests.utils.quote(url)
        public_key = RSA.import_key(PUBLIC_KEYS["happ://crypt4/"])
        cipher = PKCS1_v1_5.new(public_key)
        return base64.b64encode(cipher.encrypt(mixed_url.encode('utf-8'))).decode('utf-8')
    except Exception as e:
        print(f"Encrypt Error: {e}")
        return None

# ====================== TELEGRAM ======================

client = TelegramClient('happ_mixer_session', api_id, api_hash)

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    global last_proxy
    text = event.message.text or ""

    # Proxy Yakalama
    proxy = extract_proxy(text)
    if proxy:
        last_proxy = proxy
        print(f"📡 Yeni Proxy Bulundu!")
        try:
            await client.send_message(LOG_CHANNEL, f"📡 Yeni Proxy Güncellendi:\n{proxy}")
        except:
            pass

    # crypt5 Kodu Yakalama
    if 'happ://crypt5/' not in text:
        return

    print("🔍 Yeni crypt5 kodu yakalandı!")
    try:
        print("🔍 КОД НАЙДЕН В ТЕКСТЕ!", flush=True)
    except:
        pass

    match = re.search(r'(happ://crypt5/[A-Za-z0-9+/=]+)', text)
    if not match:
        return

    happ_link = match.group(1)
    decrypted_url = decrypt_crypt5(happ_link)

    if not decrypted_url:
        print("❌ ОШИБКА: Сервер дешифрации вернул пустой ответ!", flush=True)
        return

    print(f"🔓 УСПЕШНО РАСШИФРОВАНО: {decrypted_url}", flush=True)

    encrypted_code = encrypt_happ_link(decrypted_url)
    if not encrypted_code:
        print("❌ ОШИБКА: Не удалось зашифровать в crypt4!", flush=True)
        return

    final_message = TEMPLATE.format(encrypted_code=encrypted_code, proxy=last_proxy)

    for target in target_channels:
        try:
            await client.send_message(target, final_message)
            print(f"✅ Gönderildi → {target}")
            await client.send_message(LOG_CHANNEL, f"✅ {target} kanalına gönderildi")
        except Exception as e:
            await client.send_message(LOG_CHANNEL, f"❌ Hata ({target}): {e}")

async def ping_render():
    while True:
        try:
            requests.post("https://happ-decrypt-server-ogry.onrender.com/decrypt", json={"text": "ping_test"}, timeout=5)
            print("🛰️ Пинг на Render успешно отправлен")
        except:
            pass
        await asyncio.sleep(300)

async def main():
    await client.start()
    print("🚀 Happ Mixer Userbot (crypt5→crypt4) ÇALIŞIYOR...")
    asyncio.create_task(ping_render())
    try:
        await client.send_message(LOG_CHANNEL, "🚀 **Bot Başlatıldı - crypt5 Desteği Aktif**")
    except:
        pass
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
