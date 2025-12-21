import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      // 将 src/constants/index.ts 中的 SERVER_DOMAIN 改为 "/api"
      // 通过代理解决本地调试跨域问题
      "^/api": {
        target: "https://dev.back.recruitment2023.hustunique.com",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
        cookieDomainRewrite: {
          // 返回的 cookie 的 domain 设置为 localhost
          "*": "localhost",
        },
        bypass(req, res) {
          if (!res) return;

          // const { origin } = req.headers;

          // 这两个 header 不对会 403，故直接删掉
          // 改成正确的可能更好，不过我懒
          delete req.headers.origin;
          delete req.headers.referer;

          // 以下代码处理跨域情况，不过现在不跨域了所以不需要了
          // if (origin) {
          //   res.setHeader('Access-Control-Allow-Headers', origin);
          // }
          // res.setHeader('Access-Control-Allow-Credentials', 'true');
        },
      },
    },
  }
});
