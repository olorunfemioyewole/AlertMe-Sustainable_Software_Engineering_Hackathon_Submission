/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // High-fidelity dark control center configurations
        controlBg: '#0B0F19',      // Rich deep midnight canvas backdrop
        controlCard: '#131A26',    // Matte console modules and panels
        controlBorder: '#222F43',  // Subdued tactical grid division line
        controlPrimary: '#E03616', // Dynamic Alert Crimson Accent
      },
      animation: {
        'pulse-fast': 'pulse 1.2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 4s linear infinite',
      },
    },
  },
  plugins: [],
}