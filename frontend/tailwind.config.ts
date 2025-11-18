import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./pages/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bluebrand: {
          50: "#eff6ff",   // bg-blue-50 - lightest blue background
          100: "#dbeafe",  // bg-blue-100 - light blue background, borders
          200: "#bfdbfe",  // bg-blue-200 - medium light blue
          300: "#93c5fd",  // bg-blue-300 - medium blue
          400: "#60a5fa",  // bg-blue-400 - medium dark blue
          500: "#3b82f6",  // bg-blue-500 - primary blue
          600: "#2563eb",  // text-blue-600 - dark blue text
          700: "#1d4ed8",  // text-blue-700 - darker blue text
          800: "#1e40af",  // text-blue-800 - very dark blue
          900: "#1e3a8a",  // text-blue-900 - darkest blue text
        },
        gray: {
          200: "#e5e7eb",  // border-gray-200 - light gray borders
          400: "#9ca3af",  // text-gray-400 - medium gray text
          500: "#6b7280",  // text-gray-500 - gray text
          600: "#4b5563",  // text-gray-600 - dark gray text
        },
      },
      borderRadius: {
        DEFAULT: "0.75rem",  // 12px - standard card/button radius
        xl: "1rem",           // 16px - extra large radius
      },
      boxShadow: {
        card: "rgba(0, 0, 0, 0.1) 0px 10px 15px -3px, rgba(0, 0, 0, 0.1) 0px 4px 6px -4px",  // Card shadow from dashboard
        DEFAULT: "rgba(0, 0, 0, 0.1) 0px 10px 15px -3px, rgba(0, 0, 0, 0.1) 0px 4px 6px -4px",
      },
    },
  },
  plugins: [],
};

export default config;

