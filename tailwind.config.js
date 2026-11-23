/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html'
  ],
  theme: {
    colors: {
      "primary": {
        "soft": "#84D187",
        "DEFAULT": "#00B207",
        "hard": "#2C742F"
      },
      "danger": "#EA4B48",
      "white": "#FFFFFF",
      "warning": "#FF8A00",
      // Adding gray shades from Tailwind
      "gray": {
        "50": "#F9FAFB",
        "100": "#F3F4F6",
        "200": "#E5E7EB",
        "300": "#D1D5DB",
        "400": "#9CA3AF",
        "500": "#6B7280",
        "600": "#4B5563",
        "700": "#374151",
        "800": "#1F2937",
        "900": "#111827"
      },
      "greenGray": {
        "50": "#EDF2EE",
        "100": "#DAE5DA",
        "200": "#B4CCB4",
        "300": "#96B297",
        "400": "#7A997C",
        "500": "#618062",
        "600": "#406B42",
        "700": "#2B572E",
        "800": "#173B1A",
        "900": "#002603"
      }
    },
    extend: {
      fontFamily: {
        sans: ['Poppins', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Poppins', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        pill: '43px',
      },
      boxShadow: {
        featured: '0px 8px 20px rgba(0, 38, 3, 0.08)',
      },
      colors: {
        ink: '#1A1A1A',
        muted: '#999999',
      },
    },
  },
  plugins: [
    require('flowbite/plugin') // Flowbite plugin for interactive components
  ],
}

