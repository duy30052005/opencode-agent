/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Material You — Dark Surface Scale
        'surface-container-lowest': '#0e0e0e',
        'surface-container-low': '#1c1b1b',
        'surface-container': '#201f1f',
        'surface-container-high': '#2a2a2a',
        'surface-container-highest': '#353534',
        'surface-dim': '#131313',
        'surface-bright': '#3a3939',
        'surface-variant': '#353534',
        surface: '#131313',
        background: '#131313',

        // Material You — On-Surface
        'on-surface': '#e5e2e1',
        'on-surface-variant': '#c7c4d7',
        'on-background': '#e5e2e1',
        'inverse-surface': '#e5e2e1',
        'inverse-on-surface': '#313030',

        // Material You — Primary
        primary: '#c0c1ff',
        'primary-container': '#8083ff',
        'primary-fixed': '#e1e0ff',
        'primary-fixed-dim': '#c0c1ff',
        'on-primary': '#1000a9',
        'on-primary-container': '#0d0096',
        'on-primary-fixed': '#07006c',
        'on-primary-fixed-variant': '#2f2ebe',
        'inverse-primary': '#494bd6',
        'surface-tint': '#c0c1ff',

        // Material You — Secondary
        secondary: '#4edea3',
        'secondary-container': '#00a572',
        'secondary-fixed': '#6ffbbe',
        'secondary-fixed-dim': '#4edea3',
        'on-secondary': '#003824',
        'on-secondary-container': '#00311f',
        'on-secondary-fixed': '#002113',
        'on-secondary-fixed-variant': '#005236',

        // Material You — Tertiary
        tertiary: '#ffb2b7',
        'tertiary-container': '#ff516a',
        'tertiary-fixed': '#ffdadb',
        'tertiary-fixed-dim': '#ffb2b7',
        'on-tertiary': '#67001b',
        'on-tertiary-container': '#5b0017',
        'on-tertiary-fixed': '#40000d',
        'on-tertiary-fixed-variant': '#92002a',

        // Material You — Error
        error: '#ffb4ab',
        'error-container': '#93000a',
        'on-error': '#690005',
        'on-error-container': '#ffdad6',

        // Material You — Outline
        outline: '#908fa0',
        'outline-variant': '#464554',
      },
      borderRadius: {
        DEFAULT: '0.25rem',
        lg: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
        full: '9999px',
      },
      spacing: {
        'sidebar-width': '280px',
        unit: '4px',
        'node-gap': '2rem',
        'container-padding': '2rem',
        gutter: '1.5rem',
      },
      fontFamily: {
        'body-base': ['Inter', 'sans-serif'],
        'label-caps': ['Inter', 'sans-serif'],
        'body-sm': ['Inter', 'sans-serif'],
        'headline-md': ['Inter', 'sans-serif'],
        'code-base': ['JetBrains Mono', 'monospace'],
        'display-lg': ['Inter', 'sans-serif'],
      },
      fontSize: {
        'body-base': ['16px', { lineHeight: '1.6', fontWeight: '400' }],
        'label-caps': ['12px', { lineHeight: '1', letterSpacing: '0.05em', fontWeight: '600' }],
        'body-sm': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
        'headline-md': ['24px', { lineHeight: '1.3', fontWeight: '600' }],
        'code-base': ['14px', { lineHeight: '1.7', fontWeight: '450' }],
        'display-lg': ['48px', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '700' }],
      },
      keyframes: {
        'pulse-bg': {
          '0%': { transform: 'scale(1)', opacity: '0.5' },
          '100%': { transform: 'scale(1.2)', opacity: '0.8' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      animation: {
        'pulse-bg': 'pulse-bg 8s infinite alternate ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
      },
    },
  },
  plugins: [],
};
