# =============================================================================
# Frontend Vite + React + Capacitor — dev container
# =============================================================================
# Em produção, este Dockerfile pode ser estendido com `npm run build`
# servindo dist/ via nginx. Aqui rodamos `vite --host` para hot reload.
# Para o app mobile (Capacitor), o build é feito FORA do container — ver README.
# =============================================================================

FROM node:20-alpine

WORKDIR /app

# Instalar dependências antes do código para cachear camada
COPY package.json ./
# package-lock.json adicionado quando o usuário rodar `npm install` pela 1ª vez
RUN npm install --no-audit --no-fund || true

# Código (montado por volume em dev)
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
