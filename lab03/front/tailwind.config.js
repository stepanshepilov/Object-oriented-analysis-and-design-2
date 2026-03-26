/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'vs-dark': '#1E1E1E',
        'vs-black': '#0A0A0A',
        'vs-blue': '#007ACC',
        'vs-blue-light': '#0098FF',
        'vs-blue-dark': '#005A9E',
        'vs-gray': '#2D2D2D',
        'vs-gray-light': '#3C3C3C',
        'vs-gray-dark': '#252525',
        'vs-text': '#CCCCCC',
        'vs-text-light': '#FFFFFF',
      },
      fontFamily: {
        'mono': ['Fira Code', 'Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
}
