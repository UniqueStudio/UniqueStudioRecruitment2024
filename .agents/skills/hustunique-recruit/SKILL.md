---
name: hustunique-recruit
description: 通过对话引导用户完成 HUST 联创团队招新的完整流程(SSO 登录、注册、报名、资料修改、笔试、面试选时、查看进度),与网页端平行,用户无需打开浏览器。当用户想报名/查看/修改 HUST 联创团队招新信息、或已完成网页报名但想用命令行管理时使用。所有请求与加密只用 Python 标准库,登录态加密存于用户主目录 SQLite。
---

# HustUnique Recruit

引导用户全程在对话中完成 HUST 联创团队(Unique Studio)招新流程。所有操作通过本 skill 的 Python CLI 完成,CLI 实现了全部选手端接口 + SSO 登录/注册/个人资料接口(管理端 getAllUsers/permission 不在范围内)。

## 定位

- 与网页端(join2024.hustunique.com)平行的交互方式:agent 问、用户答、agent 执行。
- skill 目录:仓库内 `.agents/skills/hustunique-recruit/`;CLI 入口:`python3 -m scripts.cli`(必须在 skill 目录下运行)。
- 全程零第三方 Python 依赖(urllib/hashlib/sqlite3 等 stdlib)。

## 前置检查

1. 确认 python3 可用。`python3 --version` 需 ≥ 3.9。
2. 端点配置(默认 dev,可改):先跑一次 `config` 查看 sso_base / hr_base / departments_url;如用户要求用生产环境,询问并用 `config --set <key>=<value>` 修改(或指导用户设 env,优先级更高)。

## 工作流

### 1. 开局:查看状态

```
cd 仓库根目录/.agents/skills/hustunique-recruit
python3 -m scripts.cli status
```

- 退出码 4:未登录 → 进入第 2 步引导登录。
- 退出码 0:正常,根据输出继续。
- 退出码 2:服务端与本地缓存冲突 → 进入第 5 步合并流程。
- 退出码 3:会话过期 → 重新执行第 2 步登录。

### 2. 登录/注册(用户不离开对话)

**推荐方式——凭据文件(免交互输密码)**:
1. 初始化:`python3 -m scripts.cli credentials --init`,生成 `credentials.json` 模板;
2. 让用户在编辑器中填入 `username`(手机号或邮箱)与 `password`(数字开头自动按手机号登录,否则按邮箱);
3. 直接 `python3 -m scripts.cli login`,无需任何参数。
4. **登录成功后提醒用户删除凭据文件(明文密码):`python3 -m scripts.cli credentials --wipe`**(或手动删除该文件)。

备选(临时账号/不走文件):`login --method phone --phone <手机号>`(密码走 env `HUST_PASSWORD` 或交互输入;也可 `--method email --email <邮箱>`;`--method sms` 需 `--phone` + `--email` + 验证码)。
- 未注册:
  1. `code --phone <手机号> --email <邮箱>` 发验证码,把验证码转述给用户;
  2. `register --name <姓名> --gender 1|2|3 --phone <手机号> --email <邮箱> --qq <QQ>`(密码/验证码同样走 env 或交互输入);
  3. 再 `login`。
- 登录成功后 CLI 只打印"登录成功",**不会也不得打印 cookie**。

### 3. 填表报名

agent 逐项向用户询问表单字段(可一次问多项):

- `--group`:可选组 `web lab ai game pm design mobile blockchain`(android/ios 已废弃)。规则:1 个常规组,或仅 blockchain,或 1 常规 + blockchain。可传多个 `--group`。
- `--grade`:`大一|大二|大三|大四|研究生`
- `--rank`:`暂无|10%|25%|50%|100%`
- `--institute` / `--major`:学院与专业。**填写之前先提前 fetch 一次供用户选择**:
  1. `python3 -m scripts.cli departments --colleges` — 列出全部学院(带专业数),把列表给用户选学院;不要凭空问"你是什么学院"。
  2. 用户选定学院后:`python3 -m scripts.cli departments --college "<学院名>"` — 列出该学院专业,让用户从中选。
  3. 用户口述的学院/专业对不上时(DEPARTMENTS.json 是 `Record<学院, 专业[]>` 精确匹配),**AI 用 `python3 -m scripts.cli departments --search "<关键词>"` 查正确归属**,把正确学院-专业对展示给用户确认后再填,不得自作主张。
  4. 提交前仍**必须**用 `validate` 子命令预检(该命令每次动态 fetch;fetch 失败则校验失败,不得跳过)。
  - `departments`(不带参数)列出完整树;`--json` 输出原始 JSON 便于精确解析。
- `--intro`:自我介绍(必填)。
- 可选:`--referrer <推荐人>`、`--qq <QQ>`、`--is-quick`(快速通道)、`--resume <文件路径>`(简历)。

提交:

```
python3 -m scripts.cli apply --recruitment-id <rid> --group web [--group blockchain] --grade 大二 --institute 计算机学院 --major 计算机科学与技术 --rank 10% --intro "..." [--referrer ...] [--qq ...] [--is-quick] [--resume /path/to/resume.pdf]
```

`<rid>` 从 `status` 输出取得。多组报名每组一次 POST;若部分失败,CLI 会提示"部分成功",此时用 `status` 查看服务端真值。

### 4. 后续维护

- 改资料:`update`(参数同 apply,**无** `--group`、无 `--recruitment-id`;对当前招募的所有申请逐个更新)。
- 看报名:`applications`。
- 笔试:`written-test --rid <rid> --group web`(type=2 打印问卷链接,type=1 下载文件,type=0 无笔试);`written-test-upload --aid <aid> --file <path>` 上传作答。
- 简历:`resume-download --aid <aid> [--out file.pdf]`。
- 面试时间:`interview-times --rid <rid> --name web`(组面传组名小写)或 `--name unique`(群面)。
  - 单选(确定一个时间):`interview-select --aid <aid> --type group|team --iid <时间id>`,先征得用户同意再执行。
  - 多选(候补列表):`interview-slots --aid <aid> --type group|team --iids <id1,id2>`。
- 放弃报名:`abandon --aid <aid>`,**必须先在对话中向用户二次确认**。
- 退出:`logout`。

### 5. 冲突处理(每次读取前强制)

任何读操作(`status`/`applications`/`written-test`/`resume-download`/`interview-times`)都会先拉服务端状态并与本地缓存比对:

- 一致 → 正常继续;
- 不一致 → CLI 打印逐字段 diff(字段、缓存值、服务端值)并以退出码 2 退出。

此时 **agent 必须询问用户合并策略**,不得自行决定:

- 保留服务端:`sync --strategy server`(缓存按服务端重写,本地草稿被覆盖)
- 保留本地:`sync --strategy local`(草稿不变,仅刷新缓存认可当前服务端状态;用户后续本地修改可再 update 推上去)
- 逐字段:`sync --strategy fields=grade,institute`

合并完成后重发原命令。

### 6. 安全硬规则(不可违反)

- **永不打印/回显/转发 `SSO_SESSION` cookie 或密码**;永不把 cookie 写入对话、日志、markdown 或任何模型可见的文件。
- 密码/验证码只能来自凭据文件(见第 2 步)、env(`HUST_PASSWORD`/`HUST_CODE`)或 CLI 交互输入;**禁止**把它们作为命令行参数传入(会进进程列表)。
- 凭据文件 `credentials.json` 含**明文**密码,仅 0600 权限,位于本地状态目录(默认 `~/.local/share/hustunique-recruit/`);**每次登录成功后必须提醒用户删除该文件**(`credentials --wipe`),下次登录再重新填写。
- cookie 只存在于本机 `~/.local/share/hustunique-recruit/state.db`(混淆级加密 + 0600 权限,由 storage.py 读写);**model 永远不能直接读取该文件**、不能看 cookie 字节;登录态只依据 CLI 退出码判断。
- 数据库路径可由 env `HUST_RECRUIT_DIR` 覆盖,用于测试;不要用真实主目录库做实验。
- 用户明确在本对话中给出的密码/验证码,用完即忘,不得复述。

## 退出码约定

| 码 | 含义 | agent 动作 |
|---|---|---|
| 0 | 成功 | 继续 |
| 1 | 校验/业务错误 | 修正参数后重试 |
| 2 | 服务端与缓存冲突 | 问用户合并策略,`sync` 后重试 |
| 3 | 会话过期 | 引导重新 login |
| 4 | 未登录 | 引导 login |

## 边界与说明

- 学院/专业校验**总是动态 fetch** `DEPARTMENTS.json`(默认 join2024.hustunique.com,可配置);fetch 失败 = 校验失败,不得绕过。
- `is_project_c` 网页端只校验不上报,CLI 同样不上报。
- 组面/群面单选与多选:网页详情页用单选分配(`interview-select`);候补列表用 `interview-slots`。不确定时询问用户是要"确定一个时间"还是"填候补列表"。
- 多组报名部分失败属正常(网页同样行为),以 `status` 为准。