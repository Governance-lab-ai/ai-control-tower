import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: { 950: "#020617" },
        midnight: { 925: "#06111F" },
        navy: { 900: "#081827" },
        panel: {
          875: "#0B1F33",
          825: "#10263D",
          750: "#17324F",
        },
        line: {
          700: "#24364D",
          600: "#2F4663",
        },
        trust: { teal: "#20D6B5" },
        signal: { cyan: "#38BDF8" },
        insight: { violet: "#8B5CF6" },
        risk: {
          low: "#22C55E",
          medium: "#F59E0B",
          high: "#F97316",
          critical: "#EF4444",
          blocked: "#F43F5E",
          unknown: "#64748B",
        },
      },
      boxShadow: {
        panel: "0 18px 60px rgba(0, 0, 0, 0.28)",
        trust: "0 0 28px rgba(32, 214, 181, 0.14)",
        risk: "0 0 28px rgba(239, 68, 68, 0.14)",
      },
      fontFamily: {
        sans: ["Geist", "Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["Geist Mono", "JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
