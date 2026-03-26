/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': 'var(--bg-primary)',
        'secondary': 'var(--bg-secondary)',
        'tertiary': 'var(--bg-tertiary)',
        'card': 'var(--bg-card)',
        'hover': 'var(--bg-hover)',
        'border': 'var(--border-color)',
        'text-primary': 'var(--text-primary)',
        'text-secondary': 'var(--text-secondary)',
        'text-muted': 'var(--text-muted)',
        'accent': 'var(--accent-blue)',
        'accent-hover': 'var(--accent-blue-hover)',
        'accent-purple': 'var(--accent-purple)',
      }
    },
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  }
}

