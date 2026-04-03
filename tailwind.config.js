/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkbg: "#050505",
        panelbg: "#0A0A0C",
        accentBlue: "#0050FF",
        accentCyan: "#00D6FF",
        accentRed: "#FF3B30",
        accentGreen: "#34C759"
      }
    },
  },
  plugins: [],
}
