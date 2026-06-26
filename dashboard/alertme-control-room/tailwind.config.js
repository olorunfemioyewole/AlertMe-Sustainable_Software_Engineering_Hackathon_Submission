/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // High-fidelity light mode control center configurations
        controlBg: '#F8FAFC',      // Crisp, clean slate canvas backdrop
        controlCard: '#FFFFFF',    // Pure white floating modules and panels
        controlBorder: '#E2E8F0',  // Subdued, clean grid division lines
        controlText: '#0F172A',    // Deep slate for readable typography
        controlMuted: '#64748B',   // Balanced grey for secondary labels
        controlPrimary: '#E03616', // Dynamic Alert Crimson Accent remains active
      },
    },
  },
  plugins: [],
}