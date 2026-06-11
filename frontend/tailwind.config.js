/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
      },
      colors: {
        surface: {
          950: '#08080f',
          900: '#0f0f1a',
          800: '#16162a',
          700: '#1e1e38',
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}

