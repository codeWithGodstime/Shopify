/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html'
  ],
  theme: {
    colors: {
      "primary": {
        "soft": "#84D!87",
        "DEFAULT": "#00B207",
        "hard": "#2c742f"
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
      // Adding green-gray shades from Tailwind
      "greenGray": {
        "50": "#F3FAF9",
        "100": "#DDF3EC",
        "200": "#BDE5D9",
        "300": "#99D3C2",
        "400": "#66B59C",
        "500": "#439376",
        "600": "#367861",
        "700": "#285E4B",
        "800": "#1C4335",
        "900": "#0F281F"
      }
    },
    extend: {},
  },
  plugins: [
    require('flowbite/plugin') // Flowbite plugin for interactive components
  ],
}

