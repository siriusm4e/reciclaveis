# Plataforma Nacional de Resíduos (PNR)

Marketplace B2B de resíduos recicláveis — backend FastAPI + frontend React + Capacitor (iOS/Android).

- **Backend:** Python 3.12 · FastAPI · SQLAlchemy 2.0 async · PostgreSQL 15 + PostGIS · Redis 7 · Celery 5
- **Frontend:** React 18 · Vite · TypeScript · Tailwind · TanStack Query · Zustand · Leaflet · Capacitor 6
- **Infra:** Docker Compose · Nginx · Prometheus · Grafana · Jaeger

> **Stack mobile:** o app iOS/Android é um wrapper Capacitor sobre a build web. Atualizações de UI/lógica não precisam de resubmissão à loja — só `npm run build` + `npx cap sync` em dev e re-deploy do servidor web. Resubmissão à loja só é necessária para mudança de permissões nativas, novos plugins Capacitor ou alteração do binário nativo.

---

## 1. Pré-requisitos

| Ferramenta | Versão | Para quê |
|---|---|---|
| Docker | ≥ 24 | Subir stack completa |
| Docker Compose | ≥ v2.20 (`docker compose`) | Orquestrar containers |
| Node | 20 LTS (ou 22) | Build do frontend + comandos Capacitor |
| npm | 10+ | Acompanha Node |
| Xcode | 15+ | iOS nativo (apenas macOS) |
| CocoaPods | 1.15+ | Dependências iOS nativas (apenas macOS) |
| Android Studio | Hedgehog+ | Android nativo (qualquer SO) |
| JDK | 17 | Build Android |

Você **não precisa** de Python local: tudo roda dentro do container `backend`.

---

## 2. Setup completo (10 minutos)

```bash
# 1. Clone o repositório e entre na pasta pnr
cd pnr

# 2. Copie o template de variáveis de ambiente
cp .env.example .env

# 3. (Recomendado) Gere uma chave forte para JWT
#    Em macOS/Linux:
openssl rand -hex 64 | sed -i.bak 's|JWT_SECRET_KEY=.*|JWT_SECRET_KEY='"$(cat -)"'|' .env
#    Em Windows PowerShell:
#    $key = -join ((48..57 + 97..102) | Get-Random -Count 128 | % {[char]$_})
#    (Get-Content .env) -replace 'JWT_SECRET_KEY=.*', "JWT_SECRET_KEY=$key" | Set-Content .env

# 4. Sobe a stack inteira
docker compose up -d --build

# 5. Aplica migrations (cria tabelas + PostGIS + enums + índices GIST)
docker compose exec backend alembic upgrade head

# 6. Popula seeds (categorias, planos, pacotes de crédito, superadmin)
docker compose exec backend python -m app.scripts.seed

# 7. Verifica que tudo está vivo
curl http://localhost/api/health
# {"status":"ok","env":"development","version":"0.1.0"}
```

Acesse:
- **App (mobile-first):** http://localhost — frame 390px centralizado em desktop
- **Backoffice (Web):** http://localhost/admin — login com superadmin (ver `.env`)
- **Docs OpenAPI:** http://localhost/api/docs
- **Grafana:** http://localhost:3001 (`admin` / `admin`)
- **Prometheus:** http://localhost:9090
- **Jaeger (traces):** http://localhost:16686

### Login do superadmin (criado pelo seed)

| Campo | Valor (default em `.env.example`) |
|---|---|
| E-mail | `admin@pnr.com.br` |
| Senha | `trocar_no_primeiro_login` |

> **Mude a senha** logo após o primeiro login. Vá em **Perfil → MFA Setup** para ativar 2FA.

---

## 3. Variáveis de ambiente

Todas documentadas em [`.env.example`](.env.example). Os blocos principais:

| Bloco | Variáveis-chave | Notas |
|---|---|---|
| **App** | `APP_ENV`, `DEBUG`, `LOG_LEVEL`, `TZ` | `APP_ENV=production` ativa logs JSON e exige `JWT_SECRET_KEY` forte |
| **Postgres** | `POSTGRES_*`, `DATABASE_URL`, `DATABASE_URL_SYNC` | Sync URL usada pelo Alembic; async pelo runtime |
| **Redis** | `REDIS_URL`, `CELERY_BROKER_URL`, `JWT_BLOCKLIST_REDIS_URL`, `WS_PUBSUB_REDIS_URL` | DBs separados por responsabilidade (cache, broker, blocklist, pubsub) |
| **Auth/JWT** | `JWT_SECRET_KEY`, `JWT_ACCESS_TOKEN_TTL_MINUTES`, `JWT_REFRESH_TOKEN_TTL_DAYS`, `ARGON2_*`, `MFA_*` | Defaults OWASP 2024 |
| **CORS** | `CORS_ALLOWED_ORIGINS` | Lista por vírgula. **Nunca usar `*` em produção** (validado em `config.py`) |
| **Uploads** | `UPLOAD_MAX_BYTES`, `UPLOAD_ALLOWED_MIME`, `STORAGE_BASE_PATH`, `STORAGE_PUBLIC_URL` | MIME real validado por `python-magic` |
| **Geo** | `GEO_OFFSET_URBANO_M`, `GEO_OFFSET_RURAL_M` | Offset mínimo de privacidade para `AnuncioVenda` (urbano ≥ 200m, rural ≥ 1km) |
| **Receita Federal** | `RECEITA_PROVIDER`, `RECEITA_API_TOKEN` | `stub` valida apenas dígitos; trocar para `hubdev`/`serpro` em produção |
| **Push (FCM)** | `FCM_CREDENTIALS_JSON_BASE64`, `FCM_PROJECT_ID` | Vazio = dry-run (loga, não envia) |
| **Alerta Pago** | `ALERTA_PAGO_COBERTURA_MINIMA` | Cobertura insuficiente → crédito reembolsado |
| **LGPD** | `LGPD_GRACA_EXCLUSAO_DIAS`, `AUDIT_LOG_RETENCAO_ANOS` | Graça 30 dias antes de anonimizar; auditoria 5 anos |
| **Observabilidade** | `METRICS_TOKEN`, `OTEL_*`, `RATE_LIMIT_*` | `/metrics` protegido em prod por `X-Metrics-Token` |
| **Superadmin seed** | `SUPERADMIN_EMAIL`, `SUPERADMIN_PASSWORD`, `SUPERADMIN_CPF` | Lidos pelo `app/scripts/seed.py` |

---

## 4. Comandos de desenvolvimento

### Stack inteira

```bash
docker compose up -d                  # subir todos os serviços
docker compose ps                     # status + health
docker compose logs -f backend        # logs tail
docker compose down                   # parar tudo (preserva volumes)
docker compose down -v                # parar e DELETAR volumes (reset DB)
docker compose restart backend        # reiniciar um serviço
docker compose up -d --build backend  # rebuild + restart
```

### Backend (FastAPI)

```bash
# Shell Python dentro do container
docker compose exec backend python

# Testes
docker compose exec backend pytest

# Lint/format (manual — não obrigatório)
docker compose exec backend python -m compileall app
```

### Frontend (Vite + Capacitor)

> Os comandos `cap` precisam rodar **fora** do container Docker (usam ferramentas do host).

```bash
cd frontend

npm install                  # primeira vez ou ao mudar package.json
npm run dev                  # Vite dev server em http://localhost:5173 (também acessível via nginx em http://localhost)
npm run build                # build de produção em dist/
npm run typecheck            # tsc --noEmit
npm run test                 # vitest
npm run lint                 # eslint
```

### Migrations Alembic

```bash
# Aplicar todas as migrations pendentes
docker compose exec backend alembic upgrade head

# Reverter para uma revisão específica (ou 'base' para tudo)
docker compose exec backend alembic downgrade <revision_id|-1|base>

# Status / histórico
docker compose exec backend alembic current
docker compose exec backend alembic history --verbose

# Gerar nova migration (autogenerate diff dos models)
docker compose exec backend alembic revision --autogenerate -m "descrição_curta"
# ⚠ Autogenerate pode reportar diffs falsos para enums e índices GIST
# já criados pela baseline 0001 — revise o arquivo gerado antes de commitar.
```

### Seeds

```bash
# Roda os 5 blocos: categorias/subcategorias, tipos de documento,
# planos por papel, pacotes de crédito, superadmin + perfil interno.
# Idempotente: upsert por slug/email — pode rodar quantas vezes quiser.
docker compose exec backend python -m app.scripts.seed
```

### Celery

```bash
# Listar tasks registradas
docker compose exec backend celery -A app.tasks.celery_app inspect registered

# Schedule do beat (lê /tmp/celerybeat-schedule)
docker compose logs -f celery_beat

# Worker status / ping
docker compose exec celery_worker celery -A app.tasks.celery_app inspect ping
```

---

## 5. Mobile (Capacitor)

> Toda a UI funciona no browser em http://localhost — Capacitor é apenas o wrapper nativo. Você pode desenvolver 100% da experiência web sem nunca abrir Xcode/Android Studio.

### 5.1 Pré-requisitos

| Plataforma | Ferramentas |
|---|---|
| **iOS** | macOS · Xcode 15+ · CocoaPods (`brew install cocoapods`) · Apple Developer account (para device físico/distribuição) |
| **Android** | Android Studio (qualquer SO) · JDK 17 · SDK Platform 34 · Emulador ou device USB com depuração ativada |
| **Ambos** | Node 20+ · `npx cap` (já em `devDependencies` do projeto) |

### 5.2 Build + sync (sempre que alterar o frontend)

```bash
cd frontend
npm run build      # gera dist/
npx cap sync       # copia dist/ → ios/App/App/public/ e android/app/src/main/assets/public/
```

`cap sync` também atualiza os plugins Capacitor caso você adicione/remova algum.

### 5.3 Abrir no IDE nativo

```bash
# iOS (apenas em macOS — abre Xcode)
npx cap open ios

# Android (qualquer SO — abre Android Studio)
npx cap open android
```

A partir daí, use o botão **Run** do IDE para rodar em emulador ou device físico.

### 5.4 Live reload mobile (desenvolvimento)

Por padrão o app empacota a build estática de `dist/`. Para hot reload no device, aponte o Capacitor para o seu dev server:

1. Descubra o IP da sua máquina na rede local (ex.: `192.168.0.10`).
2. Em `frontend/capacitor.config.ts`, descomente e ajuste:
   ```ts
   server: {
     androidScheme: 'https',
     url: 'http://192.168.0.10:5173',
     cleartext: true,
   },
   ```
3. Rode `npm run dev` e `npx cap sync`, depois abra no IDE.
4. **Lembre-se de remover `server.url` antes de fazer build de produção** — caso contrário o app vai tentar carregar do IP local.

### 5.5 Push notifications (FCM / APNs)

#### Android (FCM)

1. No [Firebase Console](https://console.firebase.google.com/), crie um projeto e adicione um app Android com package name **`com.pnr.app`**.
2. Baixe `google-services.json` e coloque em `frontend/android/app/google-services.json`.
3. No backend, exporte a chave de service account em base64 e configure:
   ```bash
   base64 -i firebase-service-account.json | tr -d '\n' > /tmp/fcm.b64
   # cole o conteúdo em FCM_CREDENTIALS_JSON_BASE64 no .env
   ```
4. Defina `FCM_PROJECT_ID` no `.env` com o ID do projeto Firebase.
5. `docker compose restart backend`.

#### iOS (APNs)

1. Habilite **Push Notifications** no Apple Developer (App ID = `com.pnr.app`).
2. Faça download do APNs Auth Key (`.p8`) e configure no Firebase Console (Project Settings → Cloud Messaging → APNs Auth Key).
3. Baixe `GoogleService-Info.plist` no Firebase e coloque em `frontend/ios/App/App/GoogleService-Info.plist`.
4. No Xcode: target App → Signing & Capabilities → **+ Capability** → Push Notifications, Background Modes (Remote notifications).

> **Arquivos sensíveis no `.gitignore`:** `google-services.json`, `GoogleService-Info.plist`, `firebase-service-account.json`. Nunca commitar.

#### Browser (fallback PWA)

O hook `usePushNotifications` (browser-first) usa a Web Notification API quando não está em Capacitor nativo. Vai pedir permissão na primeira tentativa do usuário em `/configuracoes/preferencias`. Sem FCM/APNs configurado, o disparo cai em dry-run silencioso no backend.

### 5.6 Deploy sem resubmissão à loja

A maior parte dos deploys **não** precisa de nova submissão para App Store/Play Store:

| Tipo de mudança | Resubmissão à loja? |
|---|---|
| Edição de UI/HTML/CSS | ❌ Não — só `npm run build`, `cap sync`, redeploy web |
| Alteração de lógica de tela / chamadas API | ❌ Não |
| Novo endpoint backend | ❌ Não |
| Adicionar/remover plugin Capacitor (`@capacitor/*`) | ✅ Sim |
| Adicionar permissão nativa (câmera, contatos) | ✅ Sim |
| Alterar `appId`, `appName`, ícone ou splash nativo | ✅ Sim |
| Alterar versão do SDK iOS/Android | ✅ Sim |

Em prod, o app instalado já carrega o WebView pelo seu domínio (ou pelo bundle `dist/` empacotado). Atualizou o `dist/`? Os usuários veem a nova versão na próxima sessão.

### 5.7 Backoffice é Web-only

O bundle de produção do app mobile **não** carrega as rotas `/admin/*`. Em desktop/web, qualquer Usuario com `PerfilInterno` ativo acessa o backoffice em `http://seu-dominio/admin`. Em mobile a navegação dessas rotas redireciona ou cai em fallback `/home`.

---

## 6. Troubleshooting

### Backend não sobe / fica unhealthy

```bash
docker compose logs backend --tail 100
```

Causas comuns:
- **Migration não aplicada:** rode `docker compose exec backend alembic upgrade head`.
- **`DATABASE_URL` errada no `.env`:** verifique se aponta para o host do compose (`postgres`, não `localhost`).
- **PostGIS não habilitado:** se a migration baseline foi pulada manualmente, rode `docker compose exec postgres psql -U pnr -d pnr -c "CREATE EXTENSION postgis;"` e re-rode `upgrade head`.

### Erro `EmailStr` ao seed/login: `is a special-use or reserved name`

Você está usando um TLD reservado (`.local`, `.test`, `.example`). Mude `SUPERADMIN_EMAIL` no `.env` para um domínio válido como `admin@pnr.com.br` e re-rode o seed (apague o usuário antigo se necessário com `DELETE FROM usuario`).

### Porta 80/5173/5432/6379 já está em uso

Edite `.env` e altere a porta exposta:
```
NGINX_PORT=8080
FRONTEND_PORT=5174
POSTGRES_PORT=5433
REDIS_PORT=6380
```
Depois `docker compose up -d`.

### MFA TOTP marca código inválido

- Cheque que o relógio do servidor e do dispositivo do usuário estão sincronizados (tolerância é ±30s).
- Para resetar MFA de um usuário: `UPDATE usuario SET mfa_ativo=false, mfa_secret=NULL WHERE email='...';`

### Login devolve `mfa_required: true` mas usuário não tem MFA

O backend retorna esse detalhe quando o usuário tem `mfa_ativo=true`. Confira no DB e reset se for legado.

### Push não chega no browser

1. Permissão concedida? `chrome://settings/content/notifications` → verifique seu domínio.
2. O backend está em dry-run? Confira `FCM_CREDENTIALS_JSON_BASE64` e `FCM_PROJECT_ID` no `.env`. Em dry-run, o log mostra `push_dry_run`.
3. O usuário tem `aceita_alerta_pago_de_terceiros=true` em `PreferenciaComunicacao`? Caso contrário, o disparo segmentado o ignora.

### WebSocket de chat não conecta

- Em dev local, o navegador conecta direto no backend. Em produção atrás do nginx, garanta que o bloco `/ws/` no `nginx.conf` tenha `proxy_set_header Upgrade $http_upgrade`.
- Token expirou? `useChatRealtime` reconecta automaticamente, mas o access token tem TTL de 15min — se a sessão estava parada muito tempo, faça refresh com `useAuth`.

### Capacitor: `cap sync` falha com "Skipping pod install"

Você está em Windows/Linux e iOS exige `pod install`, que só roda em macOS. O projeto `ios/` foi gerado mesmo assim — para builds reais de iOS, copie o repositório para um Mac e rode `cd ios/App && pod install`.

### Frontend não acha rotas após `npm run build`

O bundle de produção é uma SPA — qualquer rota não-API deve ser servida pelo `index.html`. O `nginx.conf` já trata isso via `try_files` implícito no proxy para o dev server, mas em produção configure o servidor estático para fallback no `index.html`.

### Reset completo de banco e Redis (perde tudo)

```bash
docker compose down -v
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.scripts.seed
```

---

## 7. Estrutura de pastas

```
pnr/
├── backend/                  FastAPI + Celery + Alembic
│   ├── app/
│   │   ├── api/              routes/ + admin/ + ws/ + middleware
│   │   ├── core/             config, security, deps, exceptions, redis_client, logging
│   │   ├── db/               session, base
│   │   ├── models/           36 entidades SQLAlchemy + enums
│   │   ├── schemas/          12 arquivos Pydantic v2
│   │   ├── repositories/     Repository Pattern por domínio
│   │   ├── services/         13 services com regras de negócio
│   │   ├── tasks/            Celery app + 14 tasks agendadas
│   │   ├── utils/            geo, upload, sanitize, notifications, audit, ws_pubsub
│   │   ├── scripts/seed.py   seed inicial idempotente
│   │   └── main.py           wiring FastAPI + OTEL + /metrics
│   ├── alembic/              env.py + versions/
│   ├── storage/              uploads (volume mount em runtime)
│   ├── tests/                pytest
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 Vite + React 18 + TS + Capacitor 6
│   ├── src/
│   │   ├── api/              client Axios + endpoints
│   │   ├── components/       ui/ (shadcn) + compartilhados
│   │   ├── hooks/            TanStack Query + Capacitor (browser-first)
│   │   ├── pages/            ~60 telas (mobile-first) + admin/ (Web)
│   │   ├── store/            Zustand (auth, conta, notificações)
│   │   ├── types/api.ts      types TS espelhando Pydantic
│   │   ├── utils/            dates, currency (máscaras BR), geo
│   │   └── styles/globals.css  Design System (tokens DS)
│   ├── ios/                  gerado por `cap add ios`
│   ├── android/              gerado por `cap add android`
│   ├── dist/                 output do build Vite (sincronizado por cap sync)
│   ├── capacitor.config.ts
│   ├── tailwind.config.js    tokens DS completos
│   ├── package.json
│   └── vite.config.ts
├── nginx/
│   ├── nginx.conf            proxy /api /ws /storage / · headers de segurança
│   └── prometheus.yml
├── .env.example              variáveis documentadas
├── .gitignore
├── design-system.md          fonte de verdade visual (Verde Floresta + Âmbar Mercado)
└── docker-compose.yml        10 serviços com healthchecks
```

---

## 8. Stack de observabilidade

- **Logs:** structlog com JSON em produção; tail via `docker compose logs -f backend`.
- **Métricas:** Prometheus em `/metrics` (protegido por `X-Metrics-Token` em prod). Dashboard Grafana em `:3001`.
- **Traces:** OpenTelemetry → OTLP → Jaeger em `:16686`. Spans automáticos de FastAPI, SQLAlchemy, Redis.
- **AuditLog:** tabela `audit_log` INSERT-only, retida 5 anos. Acessível via `/api/admin/audit-log/`.

---

## 9. Segurança em produção

Antes de ir para produção:

- [ ] `JWT_SECRET_KEY` ≥ 64 caracteres aleatórios (use `openssl rand -hex 64`).
- [ ] `APP_ENV=production` (ativa logs JSON, valida CORS sem `*`).
- [ ] HTTPS terminado em LB/CloudFront/Cloudflare antes do nginx.
- [ ] `CORS_ALLOWED_ORIGINS` apenas com domínios reais (incluindo `capacitor://localhost` se for app nativo).
- [ ] `METRICS_TOKEN` único e secreto.
- [ ] `SUPERADMIN_PASSWORD` trocada via UI (Perfil → Trocar senha) ou diretamente no DB.
- [ ] Backup automático do volume `pnr_postgres_data`.
- [ ] `RECEITA_PROVIDER` configurado para `hubdev`/`serpro` (não `stub`).
- [ ] FCM/APNs configurados.
- [ ] Rate limits revisados em `RATE_LIMIT_PUBLIC` e `RATE_LIMIT_AUTHENTICATED`.

---

## 10. Licença e contato

Plataforma proprietária — todos os direitos reservados.

Para reportar bugs ou solicitar features, abra issue no repositório interno do time.
