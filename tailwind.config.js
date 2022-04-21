module.exports = {
  content: ["templates/**/*.html", "**/templates/**/*.html", "*/settings.py"],
  theme: {
    extend: {
      fontFamily: {
        serif: ["Greek", "Crimson Pro"],
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
