<p align="center">
  <img width="256" height="256" alt="Screenshot - 2026-04-01 20 09 39" src="https://github.com/user-attachments/assets/57860fe2-8166-4670-8a86-882c33668e6b" />
</p>

# 🐋 Orca — 全知研究助手

> *"在海洋最深处，虎鲸以智慧、好奇与精准导航——这正是每一次研究旅程的精神指引。"*

Orca 是一款**面向研究者、学生、工程师和终身学习者的 AI 驱动研究助手**。它融合了智能多源检索、LLM 驱动的深度分析，以及灵活的工作流系统，将零散的信息转化为结构化、可执行的知识。

无论你是撰写论文、综述文献、审计论文，还是只想用大白话弄懂一个复杂概念——Orca 都是你的同行者。

[![Tests](https://img.shields.io/badge/tests-179%20passed-brightgreen)](./tests)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

**English:** [README.md](README.md)

---

## 🌟 为什么是 Orca？

现代研究正被信息淹没。论文、博客、数据集和讨论散落在数十个平台上。Orca 诞生于一个朴素的信念：**研究应该是一场对话，而不是一场寻宝**。

- **一次查询，多源并行** — arXiv、Semantic Scholar、alphaXiv 和网页搜索一键触发
- **智能综合** — LLM 驱动的分析，串联跨来源的线索
- **工作流驱动** — 9 种专业研究模式，从深度调研到 ELI5 通俗解释
- **Agent 优先架构** — 基于 LangGraph 的智能体，自动识别你的意图并路由到正确工具
- **三端统一** — Python CLI、TypeScript CLI 和现代化 Next.js Web UI

---

## ✨ 核心功能

### 9 种研究工作流

| 工作流 | 说明 | 最佳场景 |
|---|---|---|
| **深度研究 (Deep Research)** | 多轮递归搜索 + 综合分析 | 论文选题、全面调研 |
| **文献综述 (Literature Review)** | 结构化学术论文调研 | 综述文章、技术现状 |
| **论文审计 (Paper Audit)** | 方法论、代码与结果审计 | 质量保障、可复现性验证 |
| **来源对比 (Source Compare)** | 跨数据库对比分析 | 评估矛盾观点 |
| **同行评审 (Peer Review)** | 结构化同行评审模拟 | 投稿前自评 |
| **论文写作 (Paper Writing)** | IMRaD 草稿生成 + 引用 | 初稿、基金申请 |
| **实验复现 (Replication)** | 分步复现规划 | 复现已发表论文 |
| **通俗解释 (ELI5)** | 大白话 + 类比解释 | 学习新概念 |
| **会话搜索 (Session Search)** | 检索历史研究会话 | 找回之前的研究 |

### 多源智能检索

Orca 同时查询 **4 个数据源**，支持自动降级：

- **arXiv** — 预印本论文，完整元数据
- **Semantic Scholar** — 学术搜索，引文图谱
- **alphaXiv** — 开放研究讨论平台（自动降级到 arXiv）
- **网页搜索** — DuckDuckGo 驱动的网络发现

### Agent 架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面                              │
│   Python CLI │ TypeScript CLI │ Next.js Web UI             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP / 直接调用
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI 网关                               │
│  /health │ /api/research/run │ /api/research/workflows      │
│  /api/research/sessions │ /api/skills │ /api/config          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                 LangGraph 主 Agent                           │
│         ┌──────────────┐    ┌──────────────┐               │
│         │   路由节点    │───▶│ 研究 Agent   │               │
│         │  (意图识别)   │    │              │               │
│         └──────────────┘    └──────┬───────┘               │
│              │                     │                        │
│              ▼                     ▼                        │
│         ┌──────────────┐    ┌──────────────┐               │
│         │  通用 Agent   │    │ 研究引擎      │              │
│         │  (LLM 对话)   │    │ 9 种工作流    │              │
│         └──────────────┘    │ 4 个数据源    │              │
│                             │ LLM 综合      │              │
│                             └───────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### Prompt 驱动的智能

12 个精心设计的提示模板引导 LLM 完成每种研究模式：

- `deepresearch` — 全面分析与证据综合
- `lit` — 结构化文献调研与主题分组
- `audit` — 方法论与可复现性评估
- `review` — 学术同行评审框架
- `draft` — IMRaD 学术写作结构
- `replicate` — 分步实验复现
- `eli5` — 通俗易懂的类比解释
- `compare` — 跨来源对比分析
- `autoresearch` — 自动巡航研究模式
- `watch` — 主题监控与趋势追踪
- `jobs` — 研究机会发现
- `log` — 会话历史分析

---

## 🚀 快速开始

### 前置条件

- Python 3.12+
- Node.js 18+（CLI 和 Web UI 需要）
- OpenAI API key（或兼容的 LLM 提供商）

### 安装

```bash
# 克隆仓库
git clone https://github.com/your-org/orca.git
cd orca

# 安装 Python 依赖
pip install -e ".[dev]"

# 配置
# 复制示例配置并填入你的 API key
cp config.example.yaml config.yaml
# 编辑 config.yaml 添加你的 OpenAI API key
```

### 启动网关服务

```bash
# 启动 FastAPI 网关
make run
# 或直接运行：
uvicorn orca.gateway.app:app --host 0.0.0.0 --port 8000
```

### 使用 Python CLI

```bash
# 列出可用研究工作流
orca workflows

# 执行深度研究
orca research "transformer 架构最新进展"

# 与 AI Agent 对话
orca chat "用量子计算解释一下"

# 列出可用技能
orca list-skills
```

### 使用 TypeScript CLI

```bash
cd cli
npm install
npm run build

# 执行研究
npx orca research "大语言模型对齐技术"

# 启动交互式对话
npx orca chat
```

### 启动 Web UI

```bash
cd web
npm install
npm run dev
# 打开 http://localhost:3000
```

---

## 📋 配置说明

从示例创建 `config.yaml`：

```yaml
research:
  default_depth: 2          # 默认搜索深度 (1-5)
  max_depth: 5
  default_max_sources: 10   # 每次查询来源数
  cache_enabled: true
  sources:
    arxiv:
      enabled: true
    semantic_scholar:
      enabled: true
    alphaXiv:
      enabled: true
      api_key: ${ALPHAXIV_API_KEY}
    web_search:
      enabled: true

gateway:
  host: 0.0.0.0
  port: 8000
  cors_origins: ["http://localhost:3000"]

llm:
  provider: openai
  model: gpt-4o
  temperature: 0.7
  max_tokens: 4096
  api_key: ${OPENAI_API_KEY}
```

环境变量自动解析（如 `${OPENAI_API_KEY}`）。

---

## 🐳 Docker 部署

```bash
# 构建
docker build -t orca:latest .

# 运行
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/config.yaml:/app/config.yaml \
  orca:latest
```

---

## 🧪 测试

Orca 配备了全面的测试套件，覆盖单元测试、集成测试和端到端测试。

### 运行全部测试

```bash
# 运行完整测试套件
make test
# 或：
python -m pytest tests/ -v
```

### 测试覆盖

| 测试套件 | 用例数 | 覆盖范围 |
|---|---|---|
| `test_api.py` | 8 | 网关端点（健康检查、配置、研究、技能） |
| `test_cli.py` | 6 | Python CLI 命令和帮助信息 |
| `test_config.py` | 5 | YAML 加载、环境变量、默认值 |
| `test_models.py` | 9 | 数据模型序列化往返 |
| `test_prompts.py` | 6 | 提示模板加载与缓存 |
| `test_llm_service.py` | 5 | LLM 初始化、调用、降级 |
| `test_research_engine.py` | 7 | 引擎初始化、工作流执行、会话 |
| `test_skills.py` | 7 | 技能市场与注册表 |
| `test_subagents.py` | 9 | 子代理属性与执行 |
| `test_workflows.py` | 13 | 全部 9 种工作流执行 |
| `test_integration.py` | 50 | 完整管道、适配器、Agent 图、网关 |
| `test_e2e_stress.py` | 48 | 用户旅程、并发、韧性、性能 |

**总计：179 个测试，全部通过**

### 性能基准

在标准开发机上实测：

| 基准测试 | 目标 | 实际 |
|---|---|---|
| 引擎初始化 | < 2s | ✅ ~0.3s |
| 单次工作流执行（模拟来源） | < 5s | ✅ ~0.1s |
| 网关 API 响应 | < 2s | ✅ ~0.05s |
| 20 并发 burst 查询 | 全部成功 | ✅ 100% |
| 10 并发异步会话 | 全部追踪 | ✅ 100% |

### 示例：测试研究工作流

```python
import asyncio
from orca.research.engine import ResearchEngine

async def test_research():
    engine = ResearchEngine()
    await engine.initialize()

    # 执行深度研究
    result = await engine.execute(
        workflow="deep_research",
        query="transformer 架构改进",
        depth=3,
        max_sources=15
    )

    print(f"摘要: {result.summary[:200]}...")
    print(f"找到来源: {len(result.sources)}")
    print(f"置信度: {result.confidence_score}")

asyncio.run(test_research())
```

---

## 🛠️ 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行代码检查
make lint
# 或：
ruff check orca/ tests/

# 运行测试（带覆盖率）
pytest tests/ -v --cov=orca

# 构建 Docker 镜像
make docker-build
```

---

## 📂 项目结构

```
orca/
├── orca/                    # Python 核心包
│   ├── agent/               # LangGraph Agent（主控 + 研究 + 通用）
│   ├── research/            # 研究引擎
│   │   ├── workflows/       # 9 种研究工作流
│   │   ├── sources/         # 4 个数据源适配器
│   │   └── subagents/       # 4 个专业子代理
│   ├── gateway/             # FastAPI 网关 + 路由
│   ├── cli/                 # Python CLI（Click + Rich）
│   ├── llm/                 # LLM 服务（LangChain OpenAI）
│   ├── prompts/             # 提示模板加载器
│   ├── models/              # Pydantic/dataclass 模型
│   ├── skills/              # 技能市场 + 注册表
│   └── config/              # 配置系统
├── cli/                     # TypeScript CLI
├── web/                     # Next.js Web UI
├── prompts/                 # 12 个提示模板 (.md)
├── skills/public/           # ~40 个技能定义
├── tests/                   # 179 个测试，分布在 12 个文件
├── docs/                    # 架构文档
├── Dockerfile
├── Makefile
└── pyproject.toml
```

---

## 🎯 应用场景

### 学生
- **论文选题**：用 `deep_research` 构建全面的文献库和综合分析
- **论文写作**：用 `paper_writing` 生成带引用的 IMRaD 结构初稿
- **概念学习**：用 `eli5` 用大白话弄懂复杂概念

### 研究者
- **文献综述**：用 `lit_review` 绘制领域技术现状全景图
- **投稿前自评**：用 `peer_review` 在投稿前进行自我评估
- **复现规划**：用 `replication` 规划实验复现步骤

### 工程师
- **技术评估**：用 `source_compare` 跨来源对比不同方案
- **方法论审计**：用 `paper_audit` 验证论文声明和可复现性
- **快速查找**：用 `session_search` 找回之前的研究会话

---

## 🤝 贡献指南

欢迎贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详情。

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 发起 Pull Request

---

## 📄 许可证

Orca 采用 [MIT 许可证](LICENSE) 发布。

---

## 🙏 致谢

Orca 站在巨人的肩膀上。感谢以下项目：

- [LangGraph](https://github.com/langchain-ai/langgraph) — Agent 编排
- [LangChain](https://github.com/langchain-ai/langchain) — LLM 集成
- [FastAPI](https://github.com/tiangolo/fastapi) — Web 框架
- [arXiv API](https://arxiv.org/help/api) — 学术预印本
- [Semantic Scholar](https://www.semanticscholar.org/) — 学术搜索

---

> *"海洋浩瀚，但虎鲸从不独行。"*
>
> 祝研究愉快！🐋
