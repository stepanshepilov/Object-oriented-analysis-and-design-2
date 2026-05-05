/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dnsOrange: '#ff6700',
        dnsBlue: '#333333',
      }
    },
  },
  plugins: [],
}