# UniqueStudioRecruitment2024

联创团队hr系统选手端：https://join2024.hustunique.com/

技术栈：
- svelte@4
- tailwindCSS

❗注意  
为了让 eslint 对 .svelte 文件生效，请在 `.vscode/settings` 中添加
```json
"eslint.validate": [
    "javascript",
    "typescript",
    "svelte"
],
```

推荐的配置为
```json
{
  "eslint.enable": true,
  "eslint.validate": [
    "javascript",
    "typescript",
    "svelte"
  ],
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "editor.formatOnSave": false
}
```