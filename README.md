# GPT6 Prompt Master · GPT6 提示词优化大师

一个用于审计和优化现有提示词、SKILL.md、AGENTS.md 等指令文件的元 Skill。**直接把内容粘贴进对话，就能开始。**

它帮助你识别重复、冲突、含糊的要求和不合理的触发范围，给出保留原意的优化全文与修改理由。项目名称为 GPT6 Prompt Master；内部 Skill 标识保留为 `skill-prompt-auditor`，与已有分发版本一致。

这是独立创作者项目，与模型厂商无官方隶属或认证关系。规则没有绑定某个模型版本；不同宿主和模型的实际效果需要自行验证。

## 快速开始

### 在支持 Skill 的 AI 助手中使用

将本仓库目录按你的助手说明安装为 Skill，保留 `SKILL.md`、`references/` 和 `scripts/` 的相对位置。建议安装目录名使用 `skill-prompt-auditor`。不同助手的安装路径不同，请使用宿主提供的安装入口或文档。

加载后，把已有内容粘贴进对话：

```text
帮我审计下面这段指令，保留我明确要求的限制，
给出重要问题、优化全文和修改理由：

［粘贴提示词、SKILL.md 或 AGENTS.md 原文］
```

没有文件路径也能处理。Skill 会优先使用粘贴的材料，不会为猜测来源而搜索本机。

### 普通对话中使用

也可以把 [SKILL.md](SKILL.md) 的内容作为审计要求提供给 AI，再附上待审文本。核心文件包含独立处理粘贴稿所需的规则；引用附件不可用时，助手应说明限制并继续处理。普通聊天不因此获得本地文件操作能力。

### 处理本地文件

在具备文件读写能力的 Agent 中，提供明确路径，例如：

```text
审计 /你的项目/AGENTS.md，先给我修改建议和候选稿，暂时不要覆盖原文件。
```

默认交付候选稿。只有获得明确的写回授权后才修改原文件，并先保留完整备份。

## 会得到什么

- 重要问题、修改理由与行为影响。
- 可直接复制使用的完整优化稿。
- KEEP、TRIM、DELETE、REWRITE、NEEDS CONTEXT 分类。
- 实质变更摘要、待确认项和适用的检查案例。

只要求审查时，不自动重写。目标是改善指令的表达和适用范围，不强制缩短文本或降低 token 数。用户明确的审批偏好、真实故障约束及必要执行顺序不会因看起来啰嗦而被机械删除。

## 目录

```text
SKILL.md                       Skill 入口
references/
  audit-principles.md           判定与语义检查
  output-format.md              输出与验证口径
  patterns.md                   条件化改写示例
  file-operations.md            文件操作范围与限制
scripts/
  file_guard.py                 快照、应用、回滚
  backup.sh                     创建快照的 Bash 入口
  rollback.sh                   恢复快照的 Bash 入口
tests/
  test_file_guard.py            临时目录中的脚本行为测试
```

## 可选：本地备份、应用和回滚

仅对话审计无需运行脚本。文件辅助工具依赖 Python 3.7 或更高版本，Bash 包装器另需 Bash；无需第三方 Python 包。

先另存候选稿，然后从仓库目录执行：

```bash
python3 scripts/file_guard.py stage '/项目/AGENTS.md' '/候选稿/AGENTS.md' '/本地备份目录'
```

返回结果包含快照位置及实际应用、回滚命令。快照保存原文、候选稿、diff 和校验信息。示意：

```bash
python3 scripts/file_guard.py apply '/本地备份目录/audit-实际编号'
python3 scripts/file_guard.py rollback '/本地备份目录/audit-实际编号'
```

检查 diff 后再应用。源文件内容或权限发生变化、候选快照被修改时，脚本拒绝覆盖。备份应放在本地私有位置，不要提交到公开仓库。

脚本每次处理一个普通 UTF-8 文件，拒绝符号链接和硬链接，不支持并发编辑或多文件原子事务，也不保留 ACL 等特殊元数据。macOS 等环境若路径经过符号链接，需要明确核对后使用真实路径。详细说明见 [文件操作说明](references/file-operations.md)。

## 验证与效果边界

```bash
python3 tests/test_file_guard.py
```

脚本在独立临时目录中检查应用、字节级恢复、后续编辑保护、权限变化及异常输入等 11 组行为，不修改业务文件。

当前已完成 Skill 格式检查及文件脚本验证。尚无跨模型、跨宿主的触发率或优化收益测评；静态检查不等于模型实际执行结果。建议用相同任务比较原稿与优化稿，保留有效版本。

## 数据与权限

本 Skill 不内置遥测、外部 API 或自动上传功能。粘贴的内容由你使用的 AI 宿主处理，适用该宿主的数据政策；不能因此视为离线处理。本地脚本只处理指定文件，脚本本身不联网。

## 反馈

欢迎通过 GitHub Issues 提供经过脱敏的最小复现：待审指令、预期行为、实际结果，以及使用的宿主与模型。不要提交密钥、账号凭据或无权公开的项目材料。

## 许可证

[MIT](LICENSE) · Copyright © 2026 0lidaxiang
