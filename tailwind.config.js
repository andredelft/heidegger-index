module.exports = {
  content: ["templates/**/*.html", "**/templates/**/*.html", "*/settings.py"],
  theme: {
    extend: {
      fontFamily: {
        serif: ["Greek", "Crimson Pro"],
      },
      fontSize: {
        "1.5xl": ["1.375rem", "2rem"],
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
