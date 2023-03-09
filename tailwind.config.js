const defaultTheme = require("tailwindcss/defaultTheme");

module.exports = {
  content: ["templates/**/*.html", "**/templates/**/*.html", "*/settings.py"],
  theme: {
    extend: {
      fontFamily: {
        serif: [
          "Alegreya Greek",
          "Crimson Pro",
          ...defaultTheme.fontFamily.serif,
        ],
      },
      fontSize: {
        "1.5xl": ["1.375rem", "2rem"],
      },
      typography: {
        DEFAULT: {
          css: {
            "blockquote a": {
              fontWeight: 600,
            },
          },
        },
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
