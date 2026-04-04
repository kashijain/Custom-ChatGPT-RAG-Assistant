/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Manrope", "sans-serif"]
      },
      boxShadow: {
        glow: "0 0 28px rgba(59,130,246,0.35)",
        "card-hover": "0 24px 70px rgba(15,23,42,0.6)"
      },
      colors: {
        ink: "#030712",
        panel: "rgba(15, 23, 42, 0.72)",
        line: "rgba(148, 163, 184, 0.18)",
        accent: "#3B82F6"
      }
    }
  },
  plugins: []
};
