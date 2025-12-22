/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{svelte,js,ts,jsx,tsx}"],
  theme: {
    screens: {
      sm: "640px",
      md: "768px",
      "md-lg": "910px",
      lg: "1024px",
      xl: "1280px",
      "2xl": "1536px",
    },
    colors: {
      transparent: "transparent",
      current: "currentColor",
      black: "#000000",
      blue: {
        100: "#F2F6FF",
        400: "#165DFF", //主题蓝
        300: "#0A84FF", //蓝色
        dash: "#BDD3FF", //timeline dash
      },
      border: {
        2: "#E5E6EB",
      },
      gray: {
        50: "#FAFAFA",
        100: "#F3F3F5",
        150: "#F2F3F5", //浅底色
        200: "#E5E6EB", //描边色
        250: "#B9B9B9",
        300: "#8D8D8D",
        blue: "#F2F6FF", //蓝底色
        red: "#FFEEE7", //红底色
        green: "#E8FFEA", //绿底色
        orange: "#FFF3E8",
        border: "#E5E6EB",
      },
      red: {
        warning: "#F53F3F", //警示红
      },
      green: {
        300: "#00B42A",
      },
      white: "#FFFFFF",
      text: {
        1: "#1D2129", //一级文字
        2: "#282828",
        3: "#86909C",
        4: "#4E5969",
      },
      orange: "#F77234",
    },
    boxShadow: {
      card: "0px 4px 20px 0px #1A1B2B1A",
      drop: "0px 4px 28px 0px #1A1B2B52",
      1: "0px 4px 10px 0px #0000001A",
    },
    keyframes: {
      "fly-in": {
        from: {
          opacity: 0,
          transform: "translateX(-50%) translateY(20px)",
        },
        to: {
          opacity: 1,
          transform: "translateX(-50%) translateY(0px)",
        },
      },
      spin: {
        from: {
          transform: "rotate(0deg)",
        },
        to: {
          transform: "rotate(360deg)",
        },
      },
    },
    animation: {
      "fly-in": "fly-in 0.5s forwards",
      spin: "spin 1s linear infinite",
    },
  },
  plugins: [],
};
