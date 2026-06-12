FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc python3-dev --no-install-recommends && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pycryptodome telethon requests gunicorn fastapi uvicorn
COPY . .
RUN chmod +x linux-x64_x86
RUN echo '#!/bin/bash\npython3 server.py & \npython3 happ_mixer_userbot.py\nwait' > /app/run.sh && chmod +x /app/run.sh
CMD ["/app/run.sh"]
