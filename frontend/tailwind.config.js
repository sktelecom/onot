/** @type {import('tailwindcss').Config} */
export default {
  // Colours, radii and the rest of the scale live in src/index.css (@theme), so a token is
  // defined once and both the CSS variables and the utilities read the same value.
  //
  // There is deliberately no darkMode setting: the two themes are carried by light-dark() inside
  // the tokens, driven by color-scheme. Write bg-surface / text-fg-muted and the right value
  // follows in either theme. A dark: variant would only see part of that picture, so avoid one.
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};
