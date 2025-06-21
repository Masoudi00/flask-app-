/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'finance-primary': '#2563eb',
        'finance-secondary': '#1e40af',
        'finance-accent': '#3b82f6',
        'dark-primary': '#1e293b',
        'dark-secondary': '#334155',
        'dark-accent': '#475569'
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
} 