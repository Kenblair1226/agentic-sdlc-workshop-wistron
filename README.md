# AI Coding Agent Workshop

這是一個可直接執行的 Python + FastAPI Workshop repository，用來練習完整的
Agentic Software Development Workflow：

```text
Issue → Agentic Issue Triage → Human Readiness Gate
      → Copilot coding agent → Pull Request → CI
      → CodeQL + Copilot Code Review → Agent 修復
      → Repository Instructions + Agent Skill + Hook
      → Repository Ruleset → Governed Merge
```

## Workshop Labs

| Lab | 時間 | 學習產出 |
|---|---:|---|
| [Lab 1：Agentic Issue to PR](docs/lab-1-agentic-workflow.md) | 45 分鐘 | 讓 Agent 自動 triage Issue，通過人工 readiness gate 後再交由 Coding Agent 實作 |
| [Lab 2：Secure Review](docs/lab-2-secure-review.md) | 30 分鐘 | 分析 CodeQL / Code Review findings，修復不安全的 API endpoint |
| [Lab 3：End-to-End Agent Guardrails](docs/lab-3-agent-guardrails.md) | 35 分鐘 | 串接 Agent context、deterministic validation、CI / CodeQL 與 Repository Ruleset |

講師準備與時間配置請參考
[講師操作手冊](docs/instructor-runbook.md)。

## 本機環境設定

需要 Python 3.10 或更新版本。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate.py
uvicorn app.main:app --reload
```

Windows PowerShell 請使用以下指令啟用 virtual environment：

```powershell
.\.venv\Scripts\Activate.ps1
```

開啟：

- API：<http://127.0.0.1:8000/products>
- Swagger UI：<http://127.0.0.1:8000/docs>
- Health check：<http://127.0.0.1:8000/health>

## Agentic Issue Triage 設定

`.github/workflows/issue-triage.md` 是可讀的 Agentic Workflow source；
`issue-triage.lock.yml` 是由 `gh-aw` 產生且實際由 GitHub Actions 執行的 workflow。

建立新的 workshop repository 後，先執行一次：

```bash
gh extension install github/gh-aw --pin v0.86.2
gh label clone Kenblair1226/agentic-sdlc-workshop-wistron --force
gh secret set COPILOT_GITHUB_TOKEN
gh aw compile issue-triage --validate
```

`COPILOT_GITHUB_TOKEN` 應使用 fine-grained PAT，僅授予 **Copilot Requests: Read**。
請透過 `gh secret set` 或 GitHub UI 輸入，不得放入 repository、Issue、log 或教材截圖。
若 organization 使用 centralized Copilot billing，可改依
[gh-aw Copilot authentication](https://github.github.com/gh-aw/engines/copilot/)
設定 `copilot-requests: write`。

Triage Agent 只有 read-only repository access。新增／移除 allowlist labels 與留言皆透過
safe outputs 執行；它不會關閉 Issue、修改 Issue body 或自動指派 Coding Agent。

## 驗證指令

```bash
python scripts/validate.py
pytest -q -m lab1
ruff check .
gh aw compile issue-triage --validate
```

一般測試指令會排除初始狀態下刻意失敗的 Lab 1 acceptance tests。
執行 Lab 1 時，請使用 `pytest -q -m lab1` 驗證實作。

## Workshop 重要設定

- 使用 repository 內建的 CodeQL advanced setup workflow；請勿同時啟用
  CodeQL default setup。
- Repository 與學員帳號必須已啟用 Copilot coding agent。
- Agentic Issue Triage 必須已設定 Copilot engine authentication 與必要 labels。
- Workshop organization 必須允許 GitHub Actions 與 Copilot Code Review。
- Repository 必須啟用 Code Scanning，Lab 3 學員需具備 repository admin 權限。
- 本 repository 不使用真實 credentials 或 production data。
