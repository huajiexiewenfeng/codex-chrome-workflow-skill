# Codex Chrome Workflow Skill

一个用于 **Codex Chrome 插件 + Skill** 的工作流自动化示例。

它的目标不是教你“让 AI 点按钮”，而是把重复企业后台流程中的隐性判断、异常处理和用户确认点沉淀成可复用的工作流规则。

典型场景：

- 公司 OA / 工时系统依赖真实 Chrome 登录态
- 没有方便调用的公开 API
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

这个 Skill 的核心目标是把这些判断显性化，让 Agent 在后续执行时遵守这些规则。

## 仓库结构

```text
.
├── SKILL.md                  # Skill 主说明
├── README.zh-CN.md           # 中文说明
├── config.example.json       # 示例配置，不包含真实内部信息
├── scripts/
│   └── extract_month_tasks.py # Excel 月度任务抽取脚本
└── .gitignore
```

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/huajiexiewenfeng/codex-chrome-workflow-skill.git
```

### 2. 复制到 Codex Skill 目录

Windows 示例：

```powershell
Copy-Item -Recurse .\codex-chrome-workflow-skill "$env:USERPROFILE\.agents\skills\codex-chrome-workflow-skill"
```

如果你使用的是其他 Skill 目录，请复制到自己的 Codex/Agent Skill 路径下。

### 3. 创建本地配置

进入 Skill 目录，复制示例配置：

```powershell
Copy-Item config.example.json config.json
```

然后编辑 `config.json`，填入你自己的本地信息：

- Excel 文件路径
- 项目名称
- 阶段名称
- 月度父任务模板
- 默认角色
- 负责人
- 审核人
- Excel 表头映射

注意：`config.json` 已加入 `.gitignore`，不要把真实内部系统信息提交到公开仓库。

### 4. 安装 Python 依赖

脚本依赖 `openpyxl`。

```bash
pip install openpyxl
```

如果你使用 Codex Desktop 的内置 Python，通常已经包含常用表格依赖，也可以直接运行测试。

### 5. 确认 Codex Chrome 插件可用

这个 Skill 适合需要真实 Chrome 登录态的内部系统。

使用前请确认：

- 已安装 Codex Chrome Extension
- Chrome 已登录目标系统
- Codex 能通过 Chrome 插件接管或打开页面

## 使用步骤

### 1. 抽取某个月的 Excel 任务

```powershell
python scripts/extract_month_tasks.py --month 3 --year 2026
```

如果不想使用 `config.json` 里的路径，可以临时传入：

```powershell
python scripts/extract_month_tasks.py --month 3 --year 2026 --pattern "D:\work-plans\*.xlsx"
```

输出中会包含：

- `task_names`：去重后的任务名称
- `rows`：原始行数据
- `planning_block`：是否位于 `下周计划` / `后续任务` 等计划区块之后

### 2. 让 Codex 执行月度同步

可以对 Codex 说：

> 使用 `codex-chrome-workflow-skill`，帮我同步 3 月任务和工时。

Codex 应该按 Skill 规则执行：

1. 读取配置
2. 抽取目标月份任务
3. 过滤计划/预测任务
4. 使用 Codex Chrome 插件进入真实 OA 页面
5. 查找或创建月度父任务
6. 创建子任务
7. 登记工时
8. 遇到同人同日已填则跳过
9. 统计缺失日期并询问是否补填

### 3. 缺失工时补填

如果同步后发现缺少日期，Codex 不应该直接编内容。

正确流程是：

```text
缺少工时日期：2026-03-13、2026-03-14。
是否自动找相关任务内容补填？
```

用户确认后，才从相邻或相关任务中找内容补填。

## 配置说明

`config.example.json` 中的关键字段：

| 字段 | 说明 |
|---|---|
| `excel_pattern` | Excel 工作计划路径，支持 glob |
| `default_year` | 默认年份 |
| `oa_system_name` | 系统名称，仅用于描述 |
| `project_name` | 项目名称 |
| `stage_name` | 阶段名称 |
| `monthly_parent_template` | 月度父任务名称模板 |
| `task_type` | 默认任务类型 |
| `resource_role` | 默认资源角色 |
| `owner` | 默认负责人 |
| `reviewer` | 默认审核人 |
| `columns` | Excel 表头映射 |
| `planning_markers` | 计划/预测区块标记 |

## 安全建议

- 不要提交真实 `config.json`
- 不要在公开仓库中保留真实 OA URL
- 不要提交人员工号、项目 ID、内部系统名称
- 不要让 Agent 自动执行删除、发布、审批、付款等不可逆操作
- 涉及内容生成或业务责任的动作，应先让用户确认

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

