# GPT6 提示词优化大师

GPT6 Prompt Master

把提示词、SKILL.md 或 AGENTS.md 粘贴给 AI，检查重复、冲突和含糊的规则，获得保留原意的优化全文与修改理由。

适用于 **Codex** 和 **Claude Code**。

## 开始使用

**第一步：复制下面整段内容，发到 Agent 对话框。**

```text
请从这个 GitHub 仓库安装并加载 skill-prompt-auditor：
https://github.com/0lidaxiang/gpt6-prompt-master

使用 master 分支中的 skills/skill-prompt-auditor 目录，
按当前 Agent 的安装方式保留完整附件。
如果已经安装，先检查差异，不覆盖我的改动。

完成后，让我粘贴要优化的内容。
```

获取和安装由 Agent 完成，你不用手动下载或打开终端。

**第二步：粘贴你想优化的内容。**

```text
帮我优化下面这段指令，保留我明确要求的限制。
请给出问题说明、优化全文和修改理由。

［在这里粘贴原文］
```

提示词、Skill 内容和 Agent 规则都可以直接粘贴，不需要提供文件路径。

## 你会得到什么

- **问题说明**：哪些地方重复、冲突或表达不清。
- **优化全文**：可以直接复制使用的完整候选稿。
- **修改理由**：为什么改、会影响什么、哪些地方还需要确认。

只要求审查时不会自动重写。处理本地文件时，默认先给候选稿，获得明确授权后才写回原文件。

## 手动指定这个 Skill

安装后可以直接提出优化请求，让 Agent 匹配 Skill。需要明确指定时，复制对应内容：

**Codex**

```text
$skill-prompt-auditor
审计下面的内容，先给候选稿，不修改本地文件。

［粘贴原文］
```

**Claude Code**

```text
/skill-prompt-auditor
审计下面的内容，先给候选稿，不修改本地文件。

［粘贴原文］
```

## 它会检查什么

- 指令重复、前后冲突、目标模糊和输出条件缺失。
- Skill 触发范围过宽、正文和附件不一致。
- AGENTS.md 中不必要的固定流程与缺少适用条件的规则。
- 每条建议保留、压缩、删除或改写的理由，以及缺少依据的待确认项。

用户刻意设置的确认环节、踩坑后增加的有效约束、必要执行顺序会保留。优化不以越短越好为标准，也不以某代模型更强为理由机械删规则。

## 安装遇到问题

安装需要 Agent 能访问 GitHub，并具有对应目录的写入权限。遇到权限提示，按宿主提示处理。

- **Codex**：可明确要求使用 `$skill-installer`，从本仓库 `master` 分支安装 `skills/skill-prompt-auditor`。安装后仍未发现时，重启 Codex 再试。
- **Claude Code**：个人安装位置为 `~/.claude/skills/skill-prompt-auditor`。如果首次创建顶层 Skills 目录后没有识别到，重启 Claude Code 再试。

这里的 Claude 指 Claude Code；Claude 网页聊天、Cowork 和云端任务使用不同的安装入口。

## 名称与目录

| 名称 | 用途 |
|---|---|
| GPT6 提示词优化大师 | 产品展示名称 |
| `gpt6-prompt-master` | GitHub 仓库名 |
| `skill-prompt-auditor` | Skill 名称、安装目录名、调用名 |

仓库名可以与 Skill 名不同。安装的文件夹名与 `SKILL.md` 的 `name` 保持一致；保留这个标识也避免已有用户出现两个同功能 Skill。

```text
gpt6-prompt-master/
├── README.md
├── LICENSE
├── skills/
│   └── skill-prompt-auditor/      ← 安装这一整个目录
│       ├── SKILL.md
│       ├── LICENSE
│       ├── references/
│       │   ├── audit-principles.md
│       │   ├── output-format.md
│       │   ├── patterns.md
│       │   └── file-operations.md
│       └── scripts/
│           ├── file_guard.py
│           ├── backup.sh
│           └── rollback.sh
└── tests/
    └── test_file_guard.py
```

不要只下载 SKILL.md 而丢掉附件；也不要直接把整个 GitHub 仓库放进 Skill 目录。两端使用同一份 Skill，不需要重复维护 Codex 版和 Claude Code 版。本仓库是独立 Skill，未打包成两端插件，因此不提供 `/plugin install` 命令。

## 可选的文件辅助工具

对话审计无需安装 Python 或运行脚本。可选备份、应用和回滚工具使用 Python 3.7+ 标准库，Bash 包装器另需 Bash。

Agent 应根据已安装 SKILL.md 的位置解析脚本绝对路径，不依赖当前项目的工作目录。从源码仓库手动测试时：

```bash
python3 skills/skill-prompt-auditor/scripts/file_guard.py stage \
  '/项目/AGENTS.md' \
  '/候选稿/AGENTS.md' \
  '/本地备份目录'
```

返回结果包含快照位置及可执行的应用、回滚命令。源文件内容或权限发生变化、快照被改动时拒绝覆盖。

这些脚本不是安装器。一次处理一个普通 UTF-8 文件，不支持符号链接、硬链接、并发编辑或多文件原子事务，不保留 ACL 等特殊元数据。脚本在 macOS 上验证，未验证 Windows；仅对话审计不受这些脚本限制。详见 [文件操作说明](skills/skill-prompt-auditor/references/file-operations.md)。

## 验证与依据

```bash
python3 tests/test_file_guard.py
```

11 组文件行为检查覆盖快照、字节级恢复、后续编辑保护、权限及异常输入。使用独立临时目录，不修改业务文件。安装目录结构和附件解析经过检查；不据此声称跨模型优化效果已验证。

2026-09-16 核对的官方依据：

- [Codex：Build skills](https://learn.chatgpt.com/docs/build-skills) — 支持 `$skill-installer` 获取其他仓库的 Skill；公开分发也可进一步打包成插件。
- [Claude Code：Skills](https://code.claude.com/docs/en/skills) — 个人安装目录、自动匹配、`/skill-name` 显式调用与重新加载规则。
- [Agent Skills 标准](https://agentskills.io/specification) — `SKILL.md`、名称、description 及可选脚本和参考文档。

本项目未做 Codex 与 Claude Code 的完整对话端到端测评，不承诺同轮原生发现或固定触发率。建议保留原文，用相同任务比较修改前后的输出。

## 数据、反馈与许可证

独立创作者项目，无模型厂商官方隶属或认证关系；名称不代表限定模型。本 Skill 不内置遥测或外部 API。对话内容由所使用的 AI 宿主处理，适用宿主的数据政策；本地文件脚本不联网。

欢迎通过 Issues 提供脱敏的最小复现、预期行为、实际结果和使用环境。

[MIT](LICENSE) · Copyright © 2026 0lidaxiang
