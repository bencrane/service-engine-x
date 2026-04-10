FROM node:20-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl gnupg ca-certificates \
    && curl -Ls --tlsv1.2 --proto "=https" --retry 3 \
       https://cli.doppler.com/install.sh | sh \
    && apt-get purge -y gnupg \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json ./
RUN npm install --omit=dev

COPY start.sh ./
RUN chmod +x start.sh

EXPOSE 8080

CMD ["doppler", "run", "--", "./start.sh"]
