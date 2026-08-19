# Lab 1｜從 Agentic Issue Triage 到 Coding Agent PR

**時間：**45 分鐘
**目標：**觀察 Agent 自動 triage 資訊不足的 Issue，以人類 readiness gate 補齊需求，
再監督 Coding Agent 產生可供 Review 的 Pull Request。

## 1. 確認 Starter 狀態正常

```bash
python scripts/preflight.py
python scripts/validate.py
```

在 Swagger UI 開啟 `/products`，確認目前 API response。

確認 Actions 頁面已有 **Agentic Issue Triage** workflow，且 repository 已設定
`COPILOT_GITHUB_TOKEN` 或 organization 的 `copilot-requests` authentication。

## 2. 觸發 Agentic Issue Triage

使用 **Lab 1: Product search** template 建立 Issue。Template 的初始描述刻意不完整，
第一次先直接建立，不要補齊 hidden checklist。

等待 **Agentic Issue Triage** workflow 完成，接著：

1. 在 Actions run 中確認觸發來源是 `issues.opened`。
2. 閱讀 Agent 的 classification、readiness evidence 與 next step。
3. 確認 workflow 只使用 safe outputs 新增 allowlist labels 與一則留言。
4. 初始 Issue 應得到 `needs-info`，且不得自動指派 Coding Agent 或關閉 Issue。

Issue title、body 與 comments 都是不可信輸入。Agent 必須忽略其中要求揭露 secrets、
修改 workflow 或執行額外 repository 操作的文字。

## 3. 回應 Triage 並改善 Issue

編輯同一個 Issue，補上以下需求：

### API 行為

`GET /products` 接受以下 optional query parameters：

| Parameter | 規則 |
|---|---|
| `q` | 對產品名稱或分類執行不區分大小寫的 partial match |
| `sort` | 僅允許 `name` 或 `price`；無效值回傳 HTTP 422 |
| `order` | 僅允許 `asc` 或 `desc`；預設 `asc`；無效值回傳 HTTP 422 |
| `page` | 大於或等於 1 的整數；預設 1 |
| `page_size` | 1 到 20 的整數；預設 20 |

Response 必須維持既有的 `items`、`total`、`page`、`page_size` shape。
`total` 代表分頁前的符合筆數。搜尋、排序與分頁必須能組合使用。
既有的 `GET /products/{product_id}` 行為不得改變。

### 必須通過的驗證

```bash
python scripts/validate.py
pytest -q -m lab1
```

將上述規則改寫成逐項可驗證的 acceptance criteria。

`issues.edited` 會再次觸發 triage。完整 Issue 應移除 `needs-info` 並新增
`ready-for-agent`。若仍有多種合理的產品或安全決策，Agent 應使用 `needs-human`，
而不是自行猜測。

`ready-for-agent` 是 Agent 的建議，不是 approval。學員仍須自行逐項比對需求、
acceptance criteria 與 validation commands。

## 4. 指派 Coding Agent

1. 僅在人類確認 Issue 可在不猜測需求的情況下實作後，才指派 Copilot coding agent。
2. 開啟 Agent session log。
3. 確認 plan 是否包含 input validation、filter / sort / pagination 的執行順序、
   相容性與測試。
4. 不要因實作方式與預期不同就立即介入；只有在 acceptance criteria 或
   safety constraint 遺漏時才要求修正。

## 5. Review Pull Request

- [ ] Triage comment 的 evidence 與 Issue 內容一致。
- [ ] Coding Agent 是在人工 readiness review 後才被指派。
- [ ] Diff 僅包含需求必要的修改。
- [ ] Query parameters 使用 FastAPI / Pydantic constraints，而非手動字串判斷。
- [ ] `total` 在 pagination slicing 前計算。
- [ ] 既有 tests 通過。
- [ ] `pytest -q -m lab1` 通過。
- [ ] CI 偵測到 product router 修改並執行 Lab 1 acceptance tests。
- [ ] CI 為 green。
- [ ] PR summary 說明 assumptions 與執行過的 commands。

若結果不完整，請使用 evidence 與明確預期回饋 Agent，例如：

```text
Combined search + sorting + pagination acceptance test still fails.
Keep total as the pre-pagination match count and add a regression test before updating the PR.
```

## 完成條件

- [ ] Issue 包含完整 context、constraints、acceptance criteria 與 validation commands。
- [ ] `opened` 與 `edited` 事件皆觸發 triage，readiness labels 正確轉換。
- [ ] 學員能指出 safe outputs 與人類 approval 的邊界。
- [ ] Coding Agent 建立 Pull Request。
- [ ] 所有 baseline 與 Lab 1 tests 通過。
- [ ] PR 已由學員完成 diff 與 assumption review。

## 討論

比較原始的一行 Issue 與最終 Issue：哪一項新增資訊最明顯改變 Agent 的 plan 或實作？

若 Issue 遺漏 category search 等規則，對應的 acceptance test 應該失敗。請將失敗視為
改善需求的 evidence，而不是降低測試標準。

## Hosted Feature 無法使用時

- Agentic Workflow 無法執行：講師使用預先錄製的 Actions run 與 triage comment，
  學員仍需依相同 checklist 改善 Issue。
- Copilot engine authentication 失敗：確認 secret 名稱或 organization billing，
  不得將 token 貼入 Issue 或 workflow log。
- Label 不存在：重新執行 README 中的 `gh label clone`，不要放寬 safe-output allowlist。
