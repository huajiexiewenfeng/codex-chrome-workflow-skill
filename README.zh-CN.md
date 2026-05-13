# Codex Chrome Workflow Skill

一个用于 **Codex Chrome 插件 + Skill** 的工作流自动化技能。

它的目标不是教你手动跑脚本，也不是让你自己去操作浏览器，而是让 Agent 在真实 Chrome 登录态下，按照已经沉淀好的规则，完成重复企业后台流程。

典型场景：

- 公司 OA / 工时系统依赖真实 Chrome 登录态
- 任务来源在 Excel 工作计划中
- 需要创建任务、登记工时、检查重复日期
- 需要把用户纠正过的规则沉淀到下一次执行

## 核心思想

很多重复工作真正消耗人的不是动作，而是判断。

比如：

- 哪些任务是具体任务，哪些只是计划？
- 哪些日期可以填，哪些日期已经填过？
- 遇到系统提示要跳过还是继续？
- 缺少工时日期时，能不能自动补？
- 用户纠正过的问题，下次能不能不再犯？

这个 Skill 的核心目标，是把这些判断显性化，让 Agent 在后续执行时遵守这些规则。

## 安装方式

使用 `npx skills add` 安装：

```bash
npx skills add https://github.com/huajiexiewenfeng/codex-chrome-workflow-skill
```

安装后，Codex/Agent 会在可用技能列表中识别这个 Skill。

> 注意：不要把真实 OA 地址、人员工号、项目 ID、内部系统名称提交到公开仓库。真实配置只保存在本地。

## 使用前配置

第一次使用前，不需要你手动复制配置文件，也不需要你手动运行 Python 脚本。

请先让 Agent 调用配置技能完成本地配置，例如：

```text
使用配置技能，帮我配置 codex-chrome-workflow-skill：
Excel 路径是 D:\work-plans\*.xlsx，
OA 登录地址是 https://sso.example.com/login，
OA 首页地址是 https://oa.example.com，
任务/工时模块地址是 https://oa.example.com/tasks，
项目名称是 xxx，
阶段是 xxx，
负责人是 xxx，
审核人是 xxx。
```

配置技能应该负责：

- 创建或更新本地 `config.json`
- 写入 Excel 路径
- 写入 OA / SSO / 任务模块入口地址
- 写入项目、阶段、月度父任务模板
- 写入负责人、审核人、资源角色等默认值
- 确保真实内部信息只存在于本地配置，不进入公开仓库

配置中的浏览器入口字段示例：

```json
"browser": {
  "login_url": "https://sso.example.com/login",
  "oa_home_url": "https://oa.example.com",
  "task_module_url": "https://oa.example.com/tasks"
}
```

字段含义：

- `login_url`：SSO 或 OA 登录入口
- `oa_home_url`：OA 首页或工作台入口
- `task_module_url`：任务 / 工时模块入口

## 使用方式

配置完成后，直接用自然语言让 Agent 执行即可。

例如：

```text
使用 codex-chrome-workflow-skill，帮我同步 3 月任务和工时。
```

或者：

```text
使用 codex-chrome-workflow-skill，检查 3 月还缺哪些工时日期，并提示我是否自动补填。
```

Agent 会根据 Skill 自动执行：

1. 读取本地配置
2. 抽取目标月份 Excel 任务
3. 过滤计划/预测任务
4. 使用 Codex Chrome 插件进入真实 OA 页面
5. 查找或创建月度父任务
6. 创建子任务
7. 登记工时
8. 遇到同人同日已填则跳过
9. 统计缺失日期，并在补填前询问用户

## 关于脚本

仓库中的 `scripts/extract_month_tasks.py` 是给 Agent 使用的内部辅助脚本。

正常使用时，你不需要手动执行：

```bash
python scripts/extract_month_tasks.py --month 3 --year 2026
```

这一步应该由 Agent 按 Skill 流程自动完成。

你只需要告诉 Agent 要处理哪个月份，以及确认配置是否正确。

## 缺失工时补填规则

如果同步后发现缺少日期，Agent 不应该直接编内容。

正确流程是：

```text
缺少工时日期：2026-03-13、2026-03-14。
是否自动找相关任务内容补填？
```

只有用户确认后，Agent 才能从相邻或相关任务中找内容补填。

## 自动化边界

推荐自动化：

- 创建任务
- 登记工时
- 检查同人同日重复
- 根据规则跳过冲突日期
- 统计缺失日期

需要用户确认：

- 自动补填缺失日期
- 生成或改写业务描述
- 发布、审批、删除、关闭任务等高风险动作

## 仓库结构

```text
.
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── config.example.json
├── scripts/
│   └── extract_month_tasks.py
└── .gitignore
```

## 适合的场景

适合：

- 内部系统没有开放 API
- 操作依赖真实浏览器登录态
- 工作流重复发生
- 规则可以逐步明确
- 用户希望把纠错沉淀成长期能力

不适合：

- 高风险审批流
- 强一致性核心交易系统
- 规则还完全不清楚的流程
- 不允许浏览器自动化的系统

## 许可

见 [LICENSE](LICENSE)。
