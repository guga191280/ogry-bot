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

api_id = 26296032
api_hash = 'daff7fd01e17fb6ac5cfe241441475d7'

source_channels = ['@Happ_VPN_official', '@aboutmyselfalex']
target_channels = ['@vpnruss1']

DECRYPT_BINARY = './linux-x64_x86'
last_proxy = "https://t.me/proxy?server=tproxy.mom&port=8090&secret=ee104462821249bd7ac519130220c25d09617669746f2e7275"

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

def extract_proxy(text):
    match = re.search(r'(https?://t\.me/proxy\?[^ \n]+)', text)
    return match.group(1) if match else None

def decrypt_crypt5(happ_link):
    try:
        result = subprocess.run([DECRYPT_BINARY, happ_link], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        print(f"❌ Ошибка бинарника: {result.stderr.strip()}", flush=True)
        return None
    except Exception as e:
        print(f"❌ Не удалось запустить локальный бинарник: {e}", flush=True)
        return None

def encrypt_happ_link(url: str):
    try:
        if "Result" in url:
            lines = url.split("\n")
            for line in lines:
                if "https://" in line or "http://" in line:
                    url = line.strip()
                    break

        if "url=" in url:
            from urllib.parse import unquote
            pure_url = url.split("url=")[-1]
            pure_url = unquote(pure_url)
        else:
            pure_url = url

        # Шифруем чистый оригинальный URL подписки напрямую, без макросов
        pure_url = pure_url.strip()
        print(f"🔗 Шифруем оригинальный URL напрямую: {pure_url}", flush=True)
        
        public_key = RSA.import_key(PUBLIC_KEYS["happ://crypt4/"])
        cipher = PKCS1_v1_5.new(public_key)
        
        encrypted_bytes = cipher.encrypt(pure_url.encode('utf-8'))
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА RSA ШИФРОВАНИЯ: {e}", flush=True)
        try:
            return base64.b64encode(pure_url.encode('utf-8')).decode('utf-8')
        except:
            return None

client = TelegramClient('happ_mixer_session', api_id, api_hash)

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    global last_proxy
    text = event.message.text or ""

    proxy = extract_proxy(text)
    if proxy:
        last_proxy = proxy
        print(f"📡 Найдена прокси: {proxy}", flush=True)

    if 'happ://crypt5/' not in text:
        return

    print("🔍 Обнаружен crypt5 код!", flush=True)
    match = re.search(r'(happ://crypt5/[A-Za-z0-9+/=]+)', text)
    if not match:
        print("❌ Не удалось извлечь ссылку регуляркой.", flush=True)
        return

    happ_link = match.group(1)
    decrypted_url = decrypt_crypt5(happ_link)

    if not decrypted_url:
        print("❌ Дешифрация вернула пустой результат.", flush=True)
        return

    print(f"🔓 Успешная дешифрация!", flush=True)
    encrypted_code = encrypt_happ_link(decrypted_url)
    
    if not encrypted_code:
        print("❌ Не удалось закодировать в crypt4.", flush=True)
        return

    final_message = TEMPLATE.format(encrypted_code=encrypted_code, proxy=last_proxy)
    
    for target in target_channels:
        try:
            await client.send_message(target, final_message)
            print(f"✅ Gönderildi → {target}", flush=True)
        except Exception as e:
            print(f"❌ Hata ({target}): {e}", flush=True)

async def main():
    await client.start()
    print("🚀 Happ Mixer Userbot запущен и слушает каналы...", flush=True)
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
