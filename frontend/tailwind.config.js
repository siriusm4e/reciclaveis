/** @type {import('tailwindcss').Config} */
/**
 * Design tokens extraídos do canvas Paper aprovado (23 artboards).
 * Documentação completa em DESIGN_SYSTEM.md
 *
 * Mood: Verde floresta industrial × âmbar mercado, sobre grafite quente.
 */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // === PRIMÁRIA — Verde Floresta Industrial ===
        // CTAs, ícones ativos, headers de home, FAB nav, links primários
        primary: {
          50: '#f0f7f2',
          100: '#daeee0',
          200: '#b5ddc1',
          300: '#80c49a',
          400: '#4da872',
          500: '#1e8c4e', // base — CTAs, FAB, active state
          600: '#177a42', // hover
          700: '#116336', // texto sobre verde claro, preço em mono
          800: '#0d4d2a',
          900: '#082e19', // fundo escuro institucional, wordmark
        },

        // === ACCENT — Âmbar Mercado ===
        // Comprador, alertas pagos, destaque, premium
        accent: {
          400: '#f5b942',
          500: '#e09c1a', // base — badge DESTAQUE, slider, FAB localização
          600: '#c08215', // texto sobre âmbar
        },

        // === NEUTROS — Grafite Quente ===
        neutral: {
          0: '#ffffff',
          50: '#f7f7f5', // fundo do app
          100: '#eeede9',
          200: '#dddbd4',
          300: '#c5c2b8',
          400: '#9e9b90',
          500: '#77746a',
          600: '#5c5a52',
          700: '#433f38',
          800: '#302d27', // header dark institucional (Prefeitura)
          900: '#1e1c17', // texto principal
        },

        // === SEMÂNTICAS ===
        success: {
          light: '#dcfce7',
          DEFAULT: '#16a34a',
          dark: '#14532d',
        },
        warning: {
          light: '#fef9c3',
          DEFAULT: '#ca8a04',
          dark: '#854d0e',
        },
        error: {
          light: '#fee2e2',
          DEFAULT: '#dc2626',
          dark: '#991b1b',
        },
        info: {
          light: '#dbeafe',
          DEFAULT: '#2563eb',
          dark: '#1e3a8a',
        },

        // === SUPERFÍCIES (aliases semânticos) ===
        surface: {
          background: '#f7f7f5', // == neutral-50
          card: '#ffffff',
          input: '#f7f7f5',
          dark: '#302d27',
        },

        // === ALIAS RETROCOMPAT ===
        // Componentes dos módulos 1–8 foram escritos com classes `brand-*`
        // antes do redesign. O alias mantém o build verde e dá visual
        // equivalente ao tema primário. Refatorar para `primary-*` quando
        // tocar nesses componentes.
        brand: {
          50: '#f0f7f2',
          100: '#daeee0',
          200: '#b5ddc1',
          300: '#80c49a',
          400: '#4da872',
          500: '#1e8c4e',
          600: '#177a42',
          700: '#116336',
          800: '#0d4d2a',
          900: '#082e19',
        },
      },

      fontFamily: {
        // Inter — UI, labels, botões, headings, números de contador
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        // Source Serif 4 — vozes humanas, citações, taglines
        serif: ['"Source Serif 4"', 'Georgia', 'serif'],
        // JetBrains Mono — dados estruturados (preço, CPF, ID, contador)
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },

      fontSize: {
        // Escala mobile — 16px é mínimo para inputs (evita zoom iOS)
        'micro': ['11px', '14px'],
        'xs': ['12px', '16px'],
        'sm': ['14px', '20px'],
        'base': ['15px', '22px'],
        'lg': ['16px', '26px'],
        'xl': ['18px', '26px'],
        '2xl': ['22px', '28px'],
        '3xl': ['24px', '30px'],
        '4xl': ['30px', '36px'], // preço em destaque
      },

      letterSpacing: {
        tightest: '-0.04em', // wordmark PNR (display)
        tighter: '-0.025em', // headings ≥ 18px
        tight: '-0.02em',
        normal: '0',
        wide: '0.04em',
        wider: '0.05em', // status badges
        widest: '0.08em', // labels uppercase
        'label-lg': '0.1em', // section labels
        'brand': '0.15em', // wordmark subtitle
      },

      borderRadius: {
        'sm': '4px',
        DEFAULT: '8px',
        'md': '10px',
        'lg': '12px',
        'xl': '14px',
        '2xl': '18px',
        '3xl': '24px',
        'full': '9999px',
      },

      boxShadow: {
        'xs': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'sm': '0 1px 3px 0 rgb(0 0 0 / 0.10), 0 1px 2px -1px rgb(0 0 0 / 0.10)',
        DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.10), 0 1px 2px -1px rgb(0 0 0 / 0.10)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.10), 0 2px 4px -2px rgb(0 0 0 / 0.10)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.10), 0 4px 6px -4px rgb(0 0 0 / 0.10)',
        'xl': '0 16px 48px 0 rgb(0 0 0 / 0.25)', // bottom sheet
        // Sombras coloridas
        'primary': '0 6px 18px 0 rgb(30 140 78 / 0.40)',
        'accent': '0 4px 14px 0 rgb(224 156 26 / 0.35)',
        'nav-top': '0 -8px 24px 0 rgb(0 0 0 / 0.08)', // bottom nav
      },

      spacing: {
        // Safe areas Capacitor
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
        // Touch targets
        'tap': '44px', // mínimo Apple HIG
        // Layout mobile canônico
        'screen-x': '16px', // padding horizontal do container
        'topbar': '56px',
        'tabbar': '64px',
        'fab': '56px',
      },

      minHeight: {
        'tap': '44px',
        'btn': '52px',
        'screen-safe': ['100vh', '100dvh'],
      },

      minWidth: {
        'tap': '44px',
      },

      maxWidth: {
        'phone': '390px', // frame iPhone 14 Pro
      },

      zIndex: {
        'tabbar': '40',
        'topbar': '40',
        'fab': '45',
        'sheet': '50',
        'modal': '60',
        'toast': '70',
      },

      transitionTimingFunction: {
        'base': 'cubic-bezier(0.4, 0, 0.2, 1)', // ease-in-out canônico
      },

      transitionDuration: {
        'base': '200ms',
      },

      animation: {
        'shimmer': 'shimmer 1.5s ease-in-out infinite',
        'pulse-dot': 'pulse-dot 1.2s ease-in-out infinite',
      },

      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-400px 0' },
          '100%': { backgroundPosition: '400px 0' },
        },
        'pulse-dot': {
          '0%, 100%': { opacity: '0.4' },
          '50%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [
    // Animações para shadcn/ui (accordion, dialog, popover)
    require('tailwindcss-animate'),
  ],
};
