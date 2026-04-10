FROM node:20-bookworm-slim

ENV NODE_ENV=production

WORKDIR /app

# Install Doppler CLI for runtime secret injection via DOPPLER_TOKEN.
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl ca-certificates gnupg \
  && curl -Ls https://cli.doppler.com/install.sh | sh \
  && apt-get purge -y --auto-remove gnupg \
  && rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.json ./
RUN npm ci

COPY tsconfig.json ./
COPY src ./src
RUN npm run build

EXPOSE 3011

# Railway should provide PORT; app defaults to 3011.
CMD ["doppler", "run", "--", "npm", "run", "start"]
