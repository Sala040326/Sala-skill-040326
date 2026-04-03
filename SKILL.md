# WOW Agentic Ecology — SKILL（進階能力說明）

版本：1.0.0  
部署：Hugging Face Spaces（Streamlit）  
重點：Aesthetic Intelligence（美學智能）× Agentic Chains（代理鏈）× Human-in-the-loop（人類可編輯交接）

---

## 1) 系統定位與設計哲學

WOW Agentic Ecology 並非傳統聊天機器人，而是一個「前端主導的代理工作台」：  
你可以把大型語言模型當作 31 位不同職能的專業同事，依序執行「文件整理 → 結構化 → 分析 → 風險 → 產出 → 視覺化」的流水線。

核心哲學：
- **美學智能（Aesthetic Intelligence）**：20 種名畫家視覺風格（含 Jackpot 隨機），搭配 Light/Dark、玻璃擬態 UI，降低長時間處理文件的認知疲勞。
- **可控的代理鏈（Agentic Chains）**：每一步都可改 system prompt、user prompt、model、temperature、max tokens；輸出可手動編輯再交棒下一步，避免「一鍵黑箱」。
- **隱私優先（Privacy-first）**：API Key 只存在 Streamlit Session 記憶體；若偵測到環境變數就不在網頁顯示 Key，也不要求使用者再次輸入。

---

## 2) 主要能力（Skills）

### 2.1 文件匯入與前處理（Ingestion & Preprocessing）
- 支援：貼上文字 / 上傳檔案（以文字讀取為主）
- 能力：
  - 去雜訊（移除重複行、頁眉頁腳、過多空白）
  - 語言偵測與語氣統一（繁體中文為主）
  - 分段、重建標題層級（H1/H2/H3）
  - 專有名詞/縮寫表建立（Glossary）
  - 產生「Coral Markdown」：乾淨、可讀、可二次加工的 Markdown 內容

### 2.2 Coral Formatter（品牌化 Markdown 整理）
- 目標：把「雜亂文件」變成可維護、可視覺化、可串接代理鏈的標準 Markdown
- 標準輸出包含：
  - TL;DR
  - 大綱/章節
  - 重點條列
  - 術語表
  - 待補資訊/疑點清單（Questions & Gaps）

### 2.3 代理鏈編排（Agent Chain Orchestration）
- 每一步可設定：
  - system prompt（人格/角色）
  - user prompt（任務指令）
  - model（Gemini / OpenAI / Anthropic / Grok）
  - temperature、max tokens（預設 12000）
- **交接規則（Handoff）**：
  - 第 N 步的輸入，預設來自第 N-1 步的 `edited_output`（若有），否則用 `output`
  - 使用者可以在每一步把輸出改成更精準、更符合資料真實性的版本，再交給下一位代理

### 2.4 WOW 狀態與互動儀表板（Status & Dashboard）
- 每一步執行後紀錄：
  - latency（秒）
  - tokens（input/output，若供應商回傳可得）
  - status（idle / running / complete / error）
- 儀表板可用於：
  - 找出昂貴步驟（token 大、耗時長）
  - 迭代 prompt（縮短輸出、提高精準度）
  - 快速定位錯誤步驟（error）

### 2.5 AI Note Keeper（AI 筆記管家）
- 你可以貼上文字或 Markdown，系統會整理成「結構化 Markdown 筆記」
- 支援：
  - Text / Markdown 兩種編輯檢視
  - 歷史版本（可還原）
  - Keep Prompt：對筆記套用自訂指令（選模型）
  - AI Magics（至少 6 種）：
    - AI Formatting（排版潤飾）
    - AI Keywords（自選關鍵字＋顏色高亮）
    - AI Summary（摘要）
    - AI Action Items（待辦清單）
    - AI Flashcards（Q/A 記憶卡）
    - AI Risk Check（風險與缺口）

### 2.6 批次輸送帶（Batch Conveyor Belt，示範版）
- 多檔案佇列 UI（狀態欄位）
- Trim/Summarize/Build TOC 為 UI 模擬，可在未來升級為真實批次代理鏈

---

## 3) 供應商與模型策略（Providers & Models）

支援模型（可在 UI 逐步選擇）：
- OpenAI：gpt-4o-mini、gpt-4.1-mini
- Gemini：gemini-2.5-flash、gemini-2.5-flash-lite、gemini-3-flash-preview
- Anthropic：claude-3-5-sonnet-latest、claude-3-5-haiku-latest
- Grok：grok-4-fast-reasoning、grok-3-mini

建議策略：
- 大多數整理/抽取：**gemini-2.5-flash**（快、穩）
- 高精準規格/程式輸出：**gpt-4.1-mini**
- 審稿/風險/邏輯檢核：**claude-3-5-sonnet-latest**
- 快速推理或替代：**grok-4-fast-reasoning**

---

## 4) 安全與隱私（Security & Privacy）

- 若環境變數已有 Key（如 GOOGLE_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY / XAI_API_KEY）：
  - 網頁不顯示 Key
  - 設定頁只顯示「已從環境取得」
- 若環境沒有 Key：
  - 使用者可在網頁輸入 Key
  - Key 僅存於 Streamlit session（記憶體），不寫入硬碟、不持久化
- 文件內容僅在執行時送往所選 API 供應商，不另存備份（除非你自行加上匯出功能）

---

## 5) 31 位代理（Agents）能力地圖

本專案內建 31 位代理，覆蓋：
- 清理 → 結構化 → 抽取 → 分析 → 比對 → 風險 → 行動 → 產出 → 視覺化規格

你可以用它們處理：
- 規格書、會議記錄、研究報告、合約、客服對話、需求文件、設計筆記、程式說明

（代理詳細定義見 agents.yaml）
