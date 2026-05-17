# Design System — Plataforma Nacional de Resíduos

Tokens extraídos do canvas Paper aprovado (23 artboards, 20 mockups mobile + 3 docs).

**Mood:** Verde floresta industrial × âmbar mercado, sobre grafite quente. Inspirado por marketplaces B2B agrícolas/recicláveis, com toque editorial brasileiro.

---

## 1. Cores

### 1.1 Primária — Verde Floresta Industrial

Identidade da marca. Usada em CTAs, ícones ativos, headers de home, badges de status "Combinado", links primários, FAB do nav.

| Token | Hex | Onde aparece |
|---|---|---|
| `primary-50` | `#f0f7f2` | Fundo de chip categoria, badge sucesso leve, banner verde sutil |
| `primary-100` | `#daeee0` | Pílula de plano gratuito, gradient splash |
| `primary-200` | `#b5ddc1` | Border de upload dashed, chip clickable |
| `primary-300` | `#80c49a` | Gradient de thumbs decorativos |
| `primary-400` | `#4da872` | Ícones de perfil grandes, gradient mid |
| `primary-500` | `#1e8c4e` | **CTA principal**, FAB nav, header home, ícone ativo |
| `primary-600` | `#177a42` | Hover de botão primário |
| `primary-700` | `#116336` | **Texto sobre verde claro**, preço em mono, label secundário |
| `primary-800` | `#0d4d2a` | Badge sucesso text |
| `primary-900` | `#082e19` | Header dark institucional, wordmark, fundo planos |

### 1.2 Accent — Âmbar Mercado

Usada para comprador, alertas pagos, destaque de anúncios, badges de "ASSINANTE", elementos premium.

| Token | Hex | Onde aparece |
|---|---|---|
| `accent-400` | `#f5b942` | Border de destaque sutil, gradient de banner âmbar |
| `accent-500` | `#e09c1a` | **Badge DESTAQUE**, FAB de localização do mapa, slider thumb, pin de comprador |
| `accent-600` | `#c08215` | Texto sobre âmbar claro, contador de créditos |

### 1.3 Neutros — Grafite Quente

Texto, fundos, bordas, divisores.

| Token | Hex | Onde aparece |
|---|---|---|
| `neutral-0` | `#ffffff` | Superfície de card, input, header do feed |
| `neutral-50` | `#f7f7f5` | **Fundo do app** (surface-background), input neutro |
| `neutral-100` | `#eeede9` | Divisor sutil entre rows |
| `neutral-200` | `#dddbd4` | Border de input, divisor de card |
| `neutral-300` | `#c5c2b8` | Handle bar do bottom sheet, radio inativo |
| `neutral-400` | `#9e9b90` | Ícone de chip inativo, build version, caption tertiary |
| `neutral-500` | `#77746a` | Caption (data, raio, "/kg"), label uppercase |
| `neutral-600` | `#5c5a52` | Body small, dropdown chevron |
| `neutral-700` | `#433f38` | Subtítulo, link de privacy |
| `neutral-800` | `#302d27` | Título de card, **header dark Prefeitura** |
| `neutral-900` | `#1e1c17` | **Texto principal H1/H2** |

### 1.4 Semânticas

Estados de feedback e cores funcionais.

| Token | Hex | Uso |
|---|---|---|
| `success-light` | `#dcfce7` | Bg badge CONCLUÍDO, validação CPF |
| `success` | `#16a34a` | Check verde do toggle, ícone validado |
| `success-dark` | `#14532d` | Texto badge CONCLUÍDO |
| `warning-light` | `#fef9c3` | Bg badge EM NEGOCIAÇÃO, alerta documento |
| `warning` | `#ca8a04` | Border alerta vencimento |
| `warning-dark` | `#854d0e` | Texto badge EM NEGOCIAÇÃO |
| `error-light` | `#fee2e2` | Bg badge URGENTE/EXPIRA, banner doc vencendo |
| `error` | `#dc2626` | **Border-left de doc urgente**, contador de vencimento |
| `info-light` | `#dbeafe` | Bg badge INICIADO, chip de localização |
| `info` | `#2563eb` | Border quick-action localização chat |
| `info-dark` | `#1e3a8a` | Texto badge INICIADO |

### 1.5 Superfícies

Aliases para uso semântico.

| Token | Valor | Uso |
|---|---|---|
| `surface-background` | `neutral-50` (`#f7f7f5`) | Fundo geral do app |
| `surface-card` | `neutral-0` (`#ffffff`) | Card, list item, sheet |
| `surface-input` | `neutral-50` (`#f7f7f5`) | Input neutro, dropdown |
| `surface-dark` | `neutral-800` (`#302d27`) | Header Prefeitura |

---

## 2. Tipografia

### 2.1 Famílias (3 papéis distintos)

| Família | Papel | Onde |
|---|---|---|
| **Inter** | UI, labels, botões, headings, números de contador | 80% do app |
| **Source Serif 4** | Vozes humanas, citações, taglines, mensagens longas | Body de chat, preview de última mensagem, citação de munícipe, tagline do Splash, descrição do anúncio |
| **JetBrains Mono** | Dados estruturados, IDs, preços, CPF/CNPJ, contadores, telefone | Preços em destaque, `#A-2847`, badges numéricos, métricas, build version |

### 2.2 Escala de tamanho

| Token | Tamanho | Line-height | Peso típico | Uso |
|---|---|---|---|---|
| `text-display` | 30 px | 36 px | Inter 700 | Preço em destaque (Detalhe) |
| `text-h1` | 24 px | 30 px | Inter 700 | Título de tela principal |
| `text-h2` | 22 px | 28 px | Inter 700 | Saudação, "Meu perfil" |
| `text-h3` | 18 px | 26 px | Inter 600/700 | Seção de card, "Decisões de UX" |
| `text-body-lg` | 16 px | 26 px | Inter 400 / Source Serif 400 | Corpo de tagline, mensagem de chat |
| `text-body` | 15 px | 22 px | Inter 500 | Item de lista, preço inline |
| `text-body-sm` | 14 px | 20 px | Inter 400 | Label de input, item secundário |
| `text-body-xs` | 13 px | 18 px | Inter 500/600 | Subtítulo de card, botão sm |
| `text-caption` | 12 px | 16 px | Inter 500 | Caption, helper, breadcrumb |
| `text-micro` | 11 px | 14 px | Inter 500 | Timestamp, "/kg", "raio 25km" |
| `text-label` | 10 px | 14 px | Inter 500 + uppercase + tracking 0.08em | Label de seção, badge stretched |
| `text-pill` | 9–10 px | 1 | Inter 700 + uppercase + tracking 0.05em | Status badge (INICIADO, COMBINADO, etc) |

### 2.3 Heading editorial

```css
font-family: 'Inter';
font-weight: 700;
letter-spacing: -0.025em;
```

Aplica em todos os títulos ≥ 18px. Cria a "voz editorial" do app.

### 2.4 Mono para dados

```css
font-family: 'JetBrains Mono';
font-weight: 700; /* 600 para inline */
```

Sempre que houver dado numérico estruturado (preço, CPF, CEP, ID, contador). NUNCA usar em prosa.

---

## 3. Espaçamentos

Sistema base 4 px (tailwind default).

| Token | Valor | Uso |
|---|---|---|
| `space-1` | 4 px | Gap intra-elemento (ex.: ícone + label) |
| `space-2` | 8 px | Gap entre chips, gap em form-row |
| `space-3` | 12 px | Gap entre cards verticais, padding interno de card pequeno |
| `space-4` | 16 px | **Padding horizontal do container mobile** (default) |
| `space-5` | 20 px | Padding vertical de seção |
| `space-6` | 24 px | Padding vertical de hero |
| `space-7` | 28 px | Safe-area bottom de iOS |
| `space-8` | 32 px | Margem entre fluxos no índice |

### Touch targets

- **Mínimo:** 44 px (Apple HIG) → `min-h-tap min-w-tap`
- **Botão primário:** 52 px de altura
- **FAB nav central:** 56 px circular

### Safe areas (Capacitor)

```css
padding-top: env(safe-area-inset-top);
padding-bottom: env(safe-area-inset-bottom);
```

---

## 4. Border Radius

| Token | Valor | Uso |
|---|---|---|
| `rounded-sm` | 4 px | Tag/sticker pequeno (DESTAQUE) |
| `rounded` | 8 px | Botão pequeno, chip de filtro |
| `rounded-md` | 10 px | Input, button secondary |
| `rounded-lg` | 12 px | Card, input principal |
| `rounded-xl` | 14 px | Card grande, CTA primário |
| `rounded-2xl` | 16–18 px | Card popup do mapa, card de plano |
| `rounded-3xl` | 24 px | Sheet bottom, content card overlay (Detalhe) |
| `rounded-full` | 9999 px | Avatar, chip pill, FAB, toggle |

---

## 5. Sombras

| Token | Valor | Uso |
|---|---|---|
| `shadow-xs` | `0 1px 2px 0 rgb(0 0 0 / 0.05)` | Card leve, input com elevação sutil |
| `shadow-sm` | `0 1px 3px 0 rgb(0 0 0 / 0.10), 0 1px 2px -1px rgb(0 0 0 / 0.10)` | Card de listagem |
| `shadow-md` | `0 4px 6px -1px rgb(0 0 0 / 0.10), 0 2px 4px -2px rgb(0 0 0 / 0.10)` | Search bar elevada |
| `shadow-lg` | `0 10px 15px -3px rgb(0 0 0 / 0.10), 0 4px 6px -4px rgb(0 0 0 / 0.10)` | Card popup do mapa |
| `shadow-xl` | `0 16px 48px rgb(0 0 0 / 0.25)` | Bottom sheet |
| `shadow-primary` | `0 6px 18px 0 rgb(30 140 78 / 0.40)` | **Botão primário, FAB nav** |
| `shadow-accent` | `0 4px 14px 0 rgb(224 156 26 / 0.35)` | CTA secundário âmbar, slider thumb |
| `shadow-nav-top` | `0 -8px 24px 0 rgb(0 0 0 / 0.08)` | Bottom nav (sombra invertida) |

---

## 6. Componentes recorrentes

### 6.1 Status Badge

Inter 700, 10px, uppercase, tracking 0.05em, radius full, padding 4×11.

| Estado | Bg / Text |
|---|---|
| INICIADO | `info-light` / `info-dark` |
| EM NEGOCIAÇÃO | `warning-light` / `warning-dark` |
| COMBINADO | `primary-100` / `primary-700` |
| CONCLUÍDO | `success-light` / `success-dark` |
| CANCELADO | `neutral-100` / `neutral-600` |
| URGENTE | `error` / `neutral-0` |

### 6.2 Card de Anúncio (`ListingCard`)

- Container: bg `neutral-0`, radius 12 px, padding 12 px, `shadow-xs`
- Thumb: 72×72, radius 10 px, gradient por categoria
- Estado **Featured:** `border-left: 3px solid accent-500` + badge sticker absolute (top: -6px) + `shadow-accent` 15%

### 6.3 Botão Primário (`<Button variant="primary">`)

- Bg `primary-500` → hover `primary-600`
- Texto `neutral-0`, Inter 700, 15 px
- Padding 0×20, altura 52 px, radius 14 px
- `shadow-primary`
- Transition 200ms ease-in-out

### 6.4 Input

- Bg `surface-input`, border 1.5 px `neutral-200`
- Focus / valid: border `primary-500` + bg `primary-50`
- Error: border `error` + bg rgba(error/10%)
- Radius 12 px, padding 12×14
- Label acima: Inter 500, 12 px, `neutral-700`, mb 6 px

### 6.5 Bottom Navigation

- 5 itens, item central (`Publicar`) é FAB 56 px com `shadow-primary` e margin-top -16 px
- Ícones Lucide stroke 2 px
- Ativo: `primary-500` (filled + colored text)
- Inativo: `neutral-400` (stroke only + gray text)
- Container: bg `neutral-0`, `shadow-nav-top`, padding 12 / 16 / 28 (safe area)

### 6.6 Header Verde (Home)

- Bg `primary-500`, padding 16 px
- Location chip translúcido com ícone MapPin
- Saudação H2 branca
- Bell circular 40px `bg-white/15` com badge `accent-500` em mono

### 6.7 Toggle

- 44×24 px, padding 2 px, radius full
- Knob: 20 px branco com `shadow-sm`
- Active: `primary-500` / Inactive: `neutral-200`

### 6.8 Status Bar Mobile

Status bar oficial Apple (9:41 + ícones de sinal/wifi/bateria), height 44 px, padding 21/24/19.
- Sobre fundo claro: texto e ícones pretos
- Sobre fundo escuro/colorido: texto e ícones brancos

---

## 7. Transições

```css
--transition-base: 200ms ease-in-out;
```

Aplicar em hover de botão, focus de input, mudança de toggle. Não animar layout grande.

---

## 8. Iconografia

- **Biblioteca:** Lucide (open-source, stroke-based)
- **Stroke width:** 2 px (default), 2.5 px (ícone pequeno < 16 px), 2.2 px (ícone médio)
- **Tamanhos canônicos:** 11, 13, 16, 18, 20, 22, 26 px
- Nunca usar emoji como ícone funcional. Emoji pode aparecer em conteúdo (mensagens), não em UI.

---

## 9. Princípios

1. **Verde para venda, âmbar para compra.** Toda interface respeita esse pareamento.
2. **Mono em todo dado estruturado.** Preço, ID, CPF, contador. Nunca em prosa.
3. **Source Serif italic em vozes humanas.** Mensagens, citações, taglines. Separa "conteúdo gerado por pessoa" do "cromo de UI".
4. **Privacidade explicada onde aparece.** Toggle de localização tem caption explicando o raio. LGPD por design.
5. **Status como objeto de primeira classe.** As 5 badges aparecem em 4 telas. Reforça reputação ao longo do funil.

---

*Tokens extraídos de 23 artboards Paper · 17/05/2026*
