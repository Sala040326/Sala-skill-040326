import os
import re
import time
import json
import uuid
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import requests
import yaml
import pandas as pd
import streamlit as st
import altair as alt


# =========================
# Page / App Config
# =========================
st.set_page_config(
    page_title="WOW Agentic Ecology",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "1.0.2"
DEFAULT_MAX_TOKENS = 12000

MODEL_OPTIONS = [
    "gpt-4o-mini",
    "gpt-4.1-mini",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview",
    "claude-3-5-sonnet-latest",
    "claude-3-5-haiku-latest",
    "grok-4-fast-reasoning",
    "grok-3-mini",
]

TAB_KEYS = ["workspace", "notes", "batch", "settings", "about"]


# =========================
# i18n
# =========================
I18N = {
    "en": {
        "app_title": "WOW Agentic Ecology",
        "sidebar_controls": "Controls",
        "theme_mode": "Theme Mode",
        "light": "Light",
        "dark": "Dark",
        "language": "Language",
        "painter_style": "Painter Style",
        "jackpot": "Jackpot (Random Style)",
        "nav": "Navigation",
        "workspace": "Workspace",
        "notes": "AI Note Keeper",
        "batch": "Batch Conveyor",
        "settings": "Settings",
        "about": "About",
        "api_status": "API Key Status",
        "env_detected": "From environment",
        "needs_key": "Needs input",
        "running": "RUNNING",
        "complete": "COMPLETE",
        "idle": "IDLE",
        "error": "ERROR",
        "dashboard": "WOW Dashboard",
        "doc_ingest": "Ingestion",
        "agent_chain": "Agent Chain",
        "run_all": "Run All Steps",
        "run_step": "Run Step",
        "reset_chain": "Reset Chain Outputs",
        "input_doc": "Document Input",
        "upload_files": "Upload file(s)",
        "paste_text": "Paste text",
        "coral_format": "Coral Formatter",
        "apply_coral": "Apply Coral Formatting",
        "step_config": "Step Configuration",
        "system_prompt": "System Prompt",
        "user_prompt": "User Prompt",
        "model": "Model",
        "temperature": "Temperature",
        "max_tokens": "Max Tokens",
        "step_input": "Resolved Input",
        "step_output": "Model Output",
        "edited_output": "Edited Output (handoff to next step)",
        "view_mode": "View Mode",
        "text": "Text",
        "markdown": "Markdown",
        "note_input": "Raw Note (Text / Markdown)",
        "organize_note": "Organize into Markdown",
        "keep_prompt": "Keep Prompt on Note (custom instruction)",
        "apply_prompt": "Apply Prompt",
        "ai_magics": "AI Magics",
        "ai_formatting": "AI Formatting (Polish Markdown)",
        "ai_keywords": "AI Keywords Highlighter",
        "keywords": "Keywords (comma-separated)",
        "keyword_color": "Keyword color",
        "apply_keywords": "Highlight Keywords",
        "history": "History",
        "restore": "Restore",
        "batch_upload": "Upload multiple files (simulation)",
        "batch_actions": "Batch Actions (simulation)",
        "trim": "Trim",
        "summarize": "Summarize",
        "build_toc": "Build TOC",
        "skill_md": "SKILL.md",
        "agents_yaml": "agents.yaml",
        "security_note": "Privacy: Keys are stored only in Streamlit session memory (not persisted).",
        "provider_keys": "Provider API Keys",
        "gemini_key": "Gemini API Key",
        "openai_key": "OpenAI API Key",
        "anthropic_key": "Anthropic API Key",
        "grok_key": "Grok (xAI) API Key",
        "save_in_session": "Save in session",
    },
    "zh-TW": {
        "app_title": "WOW 代理生態系",
        "sidebar_controls": "控制面板",
        "theme_mode": "主題模式",
        "light": "亮色",
        "dark": "暗色",
        "language": "語言",
        "painter_style": "畫家風格",
        "jackpot": "Jackpot（隨機風格）",
        "nav": "導覽",
        "workspace": "工作區",
        "notes": "AI 筆記管家",
        "batch": "批次輸送帶",
        "settings": "設定",
        "about": "關於",
        "api_status": "API Key 狀態",
        "env_detected": "已從環境變數取得",
        "needs_key": "需要輸入",
        "running": "執行中",
        "complete": "完成",
        "idle": "待命",
        "error": "錯誤",
        "dashboard": "WOW 儀表板",
        "doc_ingest": "資料匯入",
        "agent_chain": "代理鏈",
        "run_all": "依序執行所有步驟",
        "run_step": "執行此步驟",
        "reset_chain": "重置代理輸出",
        "input_doc": "文件輸入",
        "upload_files": "上傳檔案",
        "paste_text": "貼上文字",
        "coral_format": "Coral 格式化",
        "apply_coral": "套用 Coral 格式化",
        "step_config": "步驟設定",
        "system_prompt": "System Prompt",
        "user_prompt": "User Prompt",
        "model": "模型",
        "temperature": "溫度",
        "max_tokens": "Max Tokens",
        "step_input": "解析後輸入",
        "step_output": "模型輸出",
        "edited_output": "編輯後輸出（交接給下一步）",
        "view_mode": "檢視模式",
        "text": "文字",
        "markdown": "Markdown",
        "note_input": "原始筆記（文字 / Markdown）",
        "organize_note": "整理為 Markdown",
        "keep_prompt": "對筆記套用自訂指令（Keep Prompt）",
        "apply_prompt": "套用指令",
        "ai_magics": "AI 魔法",
        "ai_formatting": "AI 排版（潤飾 Markdown）",
        "ai_keywords": "AI 關鍵字高亮",
        "keywords": "關鍵字（以逗號分隔）",
        "keyword_color": "關鍵字顏色",
        "apply_keywords": "套用關鍵字高亮",
        "history": "歷史紀錄",
        "restore": "還原",
        "batch_upload": "上傳多個檔案（模擬）",
        "batch_actions": "批次操作（模擬）",
        "trim": "裁切",
        "summarize": "摘要",
        "build_toc": "建立目錄",
        "skill_md": "SKILL.md",
        "agents_yaml": "agents.yaml",
        "security_note": "隱私：API Key 僅儲存在 Streamlit session 記憶體，不會持久化。",
        "provider_keys": "各供應商 API Keys",
        "gemini_key": "Gemini API Key",
        "openai_key": "OpenAI API Key",
        "anthropic_key": "Anthropic API Key",
        "grok_key": "Grok（xAI）API Key",
        "save_in_session": "儲存到 session",
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("lang", "en")
    return I18N.get(lang, I18N["en"]).get(key, key)


# =========================
# Painter Styles (20)
# =========================
PAINTER_STYLES = [
    {
        "id": "vangogh",
        "label": "Van Gogh — Impasto Night",
        "accent": "#FFD166",
        "accent2": "#06D6A0",
        "bg": """radial-gradient(1200px 800px at 15% 20%, rgba(255,209,102,0.35), transparent 55%),
                 radial-gradient(900px 600px at 85% 30%, rgba(6,214,160,0.22), transparent 60%),
                 radial-gradient(900px 900px at 55% 90%, rgba(17,138,178,0.22), transparent 55%),
                 linear-gradient(135deg, rgba(10,14,35,0.95), rgba(14,32,70,0.92))""",
    },
    {
        "id": "monet",
        "label": "Monet — Water Lilies",
        "accent": "#7BDFF2",
        "accent2": "#B2F7EF",
        "bg": """radial-gradient(1000px 800px at 20% 30%, rgba(123,223,242,0.35), transparent 60%),
                 radial-gradient(900px 700px at 80% 35%, rgba(178,247,239,0.28), transparent 60%),
                 radial-gradient(900px 700px at 40% 80%, rgba(239,255,245,0.18), transparent 55%),
                 linear-gradient(135deg, rgba(8,20,18,0.92), rgba(12,30,36,0.90))""",
    },
    {
        "id": "picasso",
        "label": "Picasso — Cubist Studio",
        "accent": "#F94144",
        "accent2": "#F9C74F",
        "bg": """linear-gradient(120deg, rgba(249,65,68,0.22), transparent 55%),
                 linear-gradient(240deg, rgba(249,199,79,0.22), transparent 55%),
                 radial-gradient(900px 600px at 55% 45%, rgba(144,190,109,0.18), transparent 60%),
                 linear-gradient(135deg, rgba(10,10,12,0.94), rgba(22,22,28,0.92))""",
    },
    {
        "id": "mondrian",
        "label": "Mondrian — De Stijl Grid",
        "accent": "#2D6CDF",
        "accent2": "#F3D34A",
        "bg": """linear-gradient(90deg, rgba(255,255,255,0.06) 0 6%, transparent 6% 30%, rgba(255,255,255,0.05) 30% 31%, transparent 31% 55%, rgba(255,255,255,0.05) 55% 56%, transparent 56% 100%),
                 linear-gradient(180deg, rgba(255,255,255,0.06) 0 10%, transparent 10% 42%, rgba(255,255,255,0.05) 42% 43%, transparent 43% 73%, rgba(255,255,255,0.05) 73% 74%, transparent 74% 100%),
                 radial-gradient(900px 600px at 20% 20%, rgba(45,108,223,0.22), transparent 65%),
                 radial-gradient(900px 600px at 80% 70%, rgba(243,211,74,0.20), transparent 65%),
                 linear-gradient(135deg, rgba(8,10,14,0.95), rgba(12,16,22,0.93))""",
    },
    {
        "id": "rothko",
        "label": "Rothko — Color Field",
        "accent": "#E07A5F",
        "accent2": "#3D405B",
        "bg": """radial-gradient(1000px 700px at 50% 25%, rgba(224,122,95,0.32), transparent 62%),
                 radial-gradient(1000px 700px at 50% 75%, rgba(61,64,91,0.26), transparent 62%),
                 linear-gradient(135deg, rgba(10,8,8,0.96), rgba(18,10,12,0.92))""",
    },
    {
        "id": "hokusai",
        "label": "Hokusai — Great Wave",
        "accent": "#3A86FF",
        "accent2": "#FFBE0B",
        "bg": """radial-gradient(1000px 700px at 25% 40%, rgba(58,134,255,0.35), transparent 60%),
                 radial-gradient(900px 700px at 80% 70%, rgba(255,190,11,0.20), transparent 62%),
                 linear-gradient(135deg, rgba(6,10,24,0.96), rgba(7,18,40,0.92))""",
    },
    {
        "id": "kahlo",
        "label": "Frida Kahlo — Botanical Surreal",
        "accent": "#43AA8B",
        "accent2": "#F94144",
        "bg": """radial-gradient(900px 700px at 30% 35%, rgba(67,170,139,0.30), transparent 60%),
                 radial-gradient(900px 700px at 75% 60%, rgba(249,65,68,0.22), transparent 62%),
                 radial-gradient(1000px 800px at 55% 90%, rgba(249,199,79,0.16), transparent 65%),
                 linear-gradient(135deg, rgba(9,14,10,0.96), rgba(16,18,12,0.92))""",
    },
    {
        "id": "dali",
        "label": "Dalí — Dream Melt",
        "accent": "#F8961E",
        "accent2": "#577590",
        "bg": """radial-gradient(1100px 800px at 20% 25%, rgba(248,150,30,0.30), transparent 62%),
                 radial-gradient(1000px 700px at 85% 50%, rgba(87,117,144,0.24), transparent 62%),
                 linear-gradient(135deg, rgba(12,10,8,0.96), rgba(18,16,14,0.92))""",
    },
    {
        "id": "pollock",
        "label": "Pollock — Drip Energy",
        "accent": "#00F5D4",
        "accent2": "#F15BB5",
        "bg": """repeating-radial-gradient(circle at 20% 30%, rgba(241,91,181,0.12) 0 8px, transparent 8px 18px),
                 repeating-radial-gradient(circle at 75% 60%, rgba(0,245,212,0.12) 0 9px, transparent 9px 19px),
                 radial-gradient(900px 700px at 50% 50%, rgba(254,228,64,0.10), transparent 65%),
                 linear-gradient(135deg, rgba(8,8,10,0.96), rgba(14,14,18,0.92))""",
    },
    {
        "id": "klimt",
        "label": "Klimt — Gilded Mosaic",
        "accent": "#D4AF37",
        "accent2": "#8E44AD",
        "bg": """repeating-linear-gradient(45deg, rgba(212,175,55,0.12) 0 8px, transparent 8px 20px),
                 radial-gradient(1100px 800px at 30% 25%, rgba(212,175,55,0.28), transparent 62%),
                 radial-gradient(1000px 700px at 80% 70%, rgba(142,68,173,0.18), transparent 62%),
                 linear-gradient(135deg, rgba(10,8,6,0.96), rgba(18,12,10,0.92))""",
    },
    {"id": "turner", "label": "Turner — Luminous Storm", "accent": "#F9C74F", "accent2": "#90BE6D",
     "bg": """radial-gradient(1100px 800px at 35% 30%, rgba(249,199,79,0.32), transparent 62%),
              radial-gradient(1000px 700px at 75% 55%, rgba(144,190,109,0.20), transparent 64%),
              linear-gradient(135deg, rgba(8,10,18,0.96), rgba(14,20,30,0.92))"""},
    {"id": "matisse", "label": "Matisse — Cutout Joy", "accent": "#FF4D6D", "accent2": "#4D96FF",
     "bg": """linear-gradient(120deg, rgba(255,77,109,0.18), transparent 55%),
              linear-gradient(240deg, rgba(77,150,255,0.18), transparent 55%),
              radial-gradient(900px 700px at 50% 60%, rgba(255,209,102,0.14), transparent 60%),
              linear-gradient(135deg, rgba(10,10,12,0.95), rgba(18,18,22,0.92))"""},
    {"id": "cezanne", "label": "Cézanne — Structured Nature", "accent": "#52B788", "accent2": "#F4A261",
     "bg": """radial-gradient(1100px 800px at 25% 35%, rgba(82,183,136,0.26), transparent 62%),
              radial-gradient(1000px 700px at 80% 65%, rgba(244,162,97,0.22), transparent 62%),
              linear-gradient(135deg, rgba(8,12,10,0.96), rgba(14,18,14,0.92))"""},
    {"id": "vermeer", "label": "Vermeer — Quiet Light", "accent": "#A8DADC", "accent2": "#457B9D",
     "bg": """radial-gradient(1100px 800px at 20% 30%, rgba(168,218,220,0.26), transparent 62%),
              radial-gradient(1000px 700px at 70% 50%, rgba(69,123,157,0.20), transparent 62%),
              linear-gradient(135deg, rgba(8,10,14,0.96), rgba(12,16,22,0.92))"""},
    {"id": "caravaggio", "label": "Caravaggio — Chiaroscuro", "accent": "#E63946", "accent2": "#F1FAEE",
     "bg": """radial-gradient(900px 600px at 30% 35%, rgba(230,57,70,0.22), transparent 62%),
              radial-gradient(1100px 800px at 65% 55%, rgba(241,250,238,0.10), transparent 66%),
              linear-gradient(135deg, rgba(6,6,7,0.98), rgba(18,10,10,0.92))"""},
    {"id": "warhol", "label": "Warhol — Pop Neon", "accent": "#00BBF9", "accent2": "#FEE440",
     "bg": """linear-gradient(120deg, rgba(0,187,249,0.18), transparent 55%),
              linear-gradient(240deg, rgba(254,228,64,0.18), transparent 55%),
              radial-gradient(900px 700px at 50% 50%, rgba(247,37,133,0.14), transparent 62%),
              linear-gradient(135deg, rgba(8,8,12,0.96), rgba(14,14,20,0.92))"""},
    {"id": "magritte", "label": "Magritte — Crisp Surreal", "accent": "#48CAE4", "accent2": "#FFB703",
     "bg": """radial-gradient(1100px 800px at 25% 30%, rgba(72,202,228,0.26), transparent 62%),
              radial-gradient(900px 700px at 80% 60%, rgba(255,183,3,0.20), transparent 62%),
              linear-gradient(135deg, rgba(6,10,18,0.96), rgba(12,18,28,0.92))"""},
    {"id": "seurat", "label": "Seurat — Pointillist Calm", "accent": "#06D6A0", "accent2": "#118AB2",
     "bg": """repeating-radial-gradient(circle at 25% 35%, rgba(6,214,160,0.10) 0 3px, transparent 3px 11px),
              repeating-radial-gradient(circle at 75% 60%, rgba(17,138,178,0.10) 0 3px, transparent 3px 11px),
              linear-gradient(135deg, rgba(8,10,12,0.96), rgba(14,18,20,0.92))"""},
    {"id": "gauguin", "label": "Gauguin — Tropical Flat Color", "accent": "#F3722C", "accent2": "#43AA8B",
     "bg": """radial-gradient(1100px 800px at 20% 35%, rgba(243,114,44,0.26), transparent 62%),
              radial-gradient(1000px 700px at 80% 65%, rgba(67,170,139,0.22), transparent 62%),
              linear-gradient(135deg, rgba(10,10,12,0.96), rgba(18,16,14,0.92))"""},
    {"id": "chagall", "label": "Chagall — Floating Fables", "accent": "#9B5DE5", "accent2": "#00BBF9",
     "bg": """radial-gradient(1000px 800px at 30% 30%, rgba(155,93,229,0.26), transparent 62%),
              radial-gradient(1000px 700px at 75% 60%, rgba(0,187,249,0.20), transparent 62%),
              radial-gradient(900px 700px at 55% 85%, rgba(254,228,64,0.14), transparent 65%),
              linear-gradient(135deg, rgba(8,8,14,0.96), rgba(14,12,22,0.92))"""},
]


def get_style(style_id: str) -> Dict[str, Any]:
    for s in PAINTER_STYLES:
        if s["id"] == style_id:
            return s
    return PAINTER_STYLES[0]


def inject_css(theme_mode: str, painter_id: str) -> None:
    s = get_style(painter_id)
    if theme_mode.lower() == "light":
        base_bg = "rgba(248, 250, 252, 0.85)"
        fg = "#0b1220"
        card = "rgba(255,255,255,0.60)"
        border = "rgba(2, 6, 23, 0.12)"
        muted = "rgba(2, 6, 23, 0.60)"
        shadow = "0 10px 30px rgba(2, 6, 23, 0.10)"
    else:
        base_bg = "rgba(2, 6, 23, 0.70)"
        fg = "#E8EEF9"
        card = "rgba(255,255,255,0.06)"
        border = "rgba(255,255,255,0.12)"
        muted = "rgba(232, 238, 249, 0.70)"
        shadow = "0 12px 35px rgba(0,0,0,0.35)"

    css = f"""
    <style>
      :root {{
        --wow-fg: {fg};
        --wow-muted: {muted};
        --wow-card: {card};
        --wow-border: {border};
        --wow-accent: {s['accent']};
        --wow-accent2: {s['accent2']};
        --wow-shadow: {shadow};
      }}

      .stApp {{ color: var(--wow-fg); }}

      .wow-bg {{
        position: fixed;
        z-index: 0;
        inset: 0;
        background: {s['bg']};
        filter: saturate(1.10) contrast(1.05);
      }}
      .wow-base {{
        position: fixed;
        z-index: 0;
        inset: 0;
        background: {base_bg};
        backdrop-filter: blur(10px);
      }}

      section.main > div {{ position: relative; z-index: 1; }}
      [data-testid="stSidebar"] > div {{ position: relative; z-index: 2; }}

      .wow-card {{
        background: var(--wow-card);
        border: 1px solid var(--wow-border);
        border-radius: 16px;
        padding: 16px;
        box-shadow: var(--wow-shadow);
        backdrop-filter: blur(10px);
      }}

      .wow-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid var(--wow-border);
        background: rgba(255,255,255,0.04);
        font-size: 12px;
      }}

      .wow-dot {{
        width: 10px; height: 10px; border-radius: 999px;
        background: var(--wow-muted);
        box-shadow: 0 0 0 3px rgba(255,255,255,0.04);
      }}
      .wow-dot.running {{ background: var(--wow-accent); }}
      .wow-dot.complete {{ background: var(--wow-accent2); }}
      .wow-dot.error {{ background: #EF4444; }}

      .wow-hr {{ height: 1px; background: var(--wow-border); margin: 10px 0; }}

      .stButton button {{
        border-radius: 12px !important;
        border: 1px solid var(--wow-border) !important;
        background: rgba(255,255,255,0.06) !important;
        color: var(--wow-fg) !important;
      }}
      .stButton button:hover {{
        border-color: rgba(255,255,255,0.22) !important;
        transform: translateY(-1px);
      }}

      input, textarea {{ border-radius: 12px !important; }}
      a {{ color: var(--wow-accent); }}
    </style>

    <div class="wow-bg"></div>
    <div class="wow-base"></div>
    """
    st.markdown(css, unsafe_allow_html=True)


# =========================
# Data Models
# =========================
@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0


# =========================
# Session State Init + Key Migration
# =========================
def ensure_api_keys_dict() -> Dict[str, str]:
    """
    Ensure we have a safe dict at st.session_state['api_keys'].
    Also migrate legacy st.session_state['keys'] if present.
    """
    # migrate legacy
    legacy = st.session_state.get("keys", None)
    if isinstance(legacy, dict) and "api_keys" not in st.session_state:
        st.session_state["api_keys"] = legacy

    # normalize
    api_keys = st.session_state.get("api_keys", None)
    if not isinstance(api_keys, dict):
        st.session_state["api_keys"] = {"gemini": "", "openai": "", "anthropic": "", "grok": ""}

    # ensure providers exist
    for p in ["gemini", "openai", "anthropic", "grok"]:
        if p not in st.session_state["api_keys"]:
            st.session_state["api_keys"][p] = ""

    return st.session_state["api_keys"]


def init_state() -> None:
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "Dark"
    if "painter" not in st.session_state:
        st.session_state["painter"] = PAINTER_STYLES[0]["id"]
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "workspace"

    ensure_api_keys_dict()

    if "doc_text" not in st.session_state:
        st.session_state["doc_text"] = ""
    if "coral_md" not in st.session_state:
        st.session_state["coral_md"] = ""

    if "chain_steps" not in st.session_state:
        st.session_state["chain_steps"] = []

    if "note_input" not in st.session_state:
        st.session_state["note_input"] = ""
    if "note_md" not in st.session_state:
        st.session_state["note_md"] = ""
    if "note_history" not in st.session_state:
        st.session_state["note_history"] = []

    if "batch_files" not in st.session_state:
        st.session_state["batch_files"] = []
    if "batch_toc" not in st.session_state:
        st.session_state["batch_toc"] = ""


init_state()
inject_css(st.session_state["theme_mode"], st.session_state["painter"])


# =========================
# Helpers: Load agents.yaml & SKILL.md
# =========================
def load_agents_yaml(path: str = "agents.yaml") -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if isinstance(data, dict) and "agents" in data:
        agents = data["agents"] or []
    elif isinstance(data, list):
        agents = data
    else:
        agents = []

    steps = []
    for a in agents:
        steps.append({
            "id": str(uuid.uuid4()),
            "name": a.get("name", "Agent"),
            "description": a.get("description", ""),
            "system_prompt": a.get("systemPrompt", a.get("system_prompt", "")),
            "user_prompt": a.get("userPrompt", a.get("user_prompt", "")),
            "model": a.get("model", "gemini-2.5-flash"),
            "temperature": float(a.get("temperature", 0.2)),
            "max_tokens": int(a.get("maxTokens", a.get("max_tokens", DEFAULT_MAX_TOKENS))),
            "input_override": a.get("input", ""),
            "output": "",
            "edited_output": "",
            "status": "idle",
            "usage": {"inputTokens": 0, "outputTokens": 0},
            "latency_s": 0.0,
            "error": "",
        })
    return steps


def ensure_chain_loaded() -> None:
    if st.session_state.get("chain_steps"):
        return
    steps = load_agents_yaml("agents.yaml")
    if not steps:
        steps = [{
            "id": str(uuid.uuid4()),
            "name": "CoralFormatter",
            "description": "Restructure raw text into clean Markdown.",
            "system_prompt": "You are an expert technical editor. Output clean, organized Markdown.",
            "user_prompt": "Format the input into structured Markdown with headings, bullets, and short sections.",
            "model": "gemini-2.5-flash",
            "temperature": 0.2,
            "max_tokens": DEFAULT_MAX_TOKENS,
            "input_override": "",
            "output": "",
            "edited_output": "",
            "status": "idle",
            "usage": {"inputTokens": 0, "outputTokens": 0},
            "latency_s": 0.0,
            "error": "",
        }]
    st.session_state["chain_steps"] = steps


def read_text_file(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


ensure_chain_loaded()


# =========================
# Provider Key Resolution (env first, else session)
# =========================
def env_key(provider: str) -> str:
    mapping = {
        "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "openai": ["OPENAI_API_KEY"],
        "anthropic": ["ANTHROPIC_API_KEY"],
        "grok": ["XAI_API_KEY", "GROK_API_KEY"],
    }
    for k in mapping.get(provider, []):
        v = os.getenv(k, "")
        if v:
            return v
    return ""


def get_api_key(provider: str) -> str:
    e = env_key(provider)
    if e:
        return e
    api_keys = ensure_api_keys_dict()
    return (api_keys.get(provider) or "").strip()


# =========================
# LLM Calls (HTTP)
# =========================
def call_gemini(api_key: str, model: str, system_prompt: str, prompt: str,
               temperature: float, max_tokens: int) -> Tuple[str, Usage]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": f"SYSTEM:\n{system_prompt}\n\nUSER:\n{prompt}"}]
        }],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
    }
    r = requests.post(url, json=payload, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"Gemini API error {r.status_code}: {r.text[:2000]}")
    data = r.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        text = json.dumps(data, ensure_ascii=False)[:4000]
    usage = Usage()
    um = data.get("usageMetadata") or {}
    usage.input_tokens = int(um.get("promptTokenCount") or 0)
    usage.output_tokens = int(um.get("candidatesTokenCount") or 0)
    return text, usage


def call_openai(api_key: str, model: str, system_prompt: str, prompt: str,
                temperature: float, max_tokens: int) -> Tuple[str, Usage]:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    }
    r = requests.post(url, headers=headers, json=payload, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"OpenAI API error {r.status_code}: {r.text[:2000]}")
    data = r.json()
    text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
    usage = Usage()
    u = data.get("usage") or {}
    usage.input_tokens = int(u.get("prompt_tokens") or 0)
    usage.output_tokens = int(u.get("completion_tokens") or 0)
    return text, usage


def call_anthropic(api_key: str, model: str, system_prompt: str, prompt: str,
                   temperature: float, max_tokens: int) -> Tuple[str, Usage]:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(url, headers=headers, json=payload, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"Anthropic API error {r.status_code}: {r.text[:2000]}")
    data = r.json()
    parts = data.get("content") or []
    text = "".join([p.get("text", "") for p in parts if isinstance(p, dict)]) if isinstance(parts, list) else ""
    usage = Usage()
    u = data.get("usage") or {}
    usage.input_tokens = int(u.get("input_tokens") or 0)
    usage.output_tokens = int(u.get("output_tokens") or 0)
    return text, usage


def call_grok(api_key: str, model: str, system_prompt: str, prompt: str,
              temperature: float, max_tokens: int) -> Tuple[str, Usage]:
    url = "https://api.x.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    }
    r = requests.post(url, headers=headers, json=payload, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"Grok (xAI) API error {r.status_code}: {r.text[:2000]}")
    data = r.json()
    text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
    usage = Usage()
    u = data.get("usage") or {}
    usage.input_tokens = int(u.get("prompt_tokens") or 0)
    usage.output_tokens = int(u.get("completion_tokens") or 0)
    return text, usage


def detect_provider(model: str) -> str:
    m = model.lower()
    if m.startswith("gemini"):
        return "gemini"
    if m.startswith("gpt-"):
        return "openai"
    if m.startswith("claude"):
        return "anthropic"
    if m.startswith("grok"):
        return "grok"
    return "gemini"


def call_llm(model: str, system_prompt: str, prompt: str,
             temperature: float, max_tokens: int) -> Tuple[str, Usage]:
    provider = detect_provider(model)
    key = get_api_key(provider)
    if not key:
        raise RuntimeError(f"Missing API key for provider: {provider} (model={model})")

    if provider == "gemini":
        return call_gemini(key, model, system_prompt, prompt, temperature, max_tokens)
    if provider == "openai":
        return call_openai(key, model, system_prompt, prompt, temperature, max_tokens)
    if provider == "anthropic":
        return call_anthropic(key, model, system_prompt, prompt, temperature, max_tokens)
    if provider == "grok":
        return call_grok(key, model, system_prompt, prompt, temperature, max_tokens)
    raise RuntimeError(f"Unknown provider for model: {model}")


# =========================
# UI Helpers
# =========================
def wow_badge(label: str, status: str) -> None:
    status = (status or "idle").lower()
    dot_class = "wow-dot"
    if status == "running":
        dot_class += " running"
    elif status == "complete":
        dot_class += " complete"
    elif status == "error":
        dot_class += " error"
    html = f"""
      <div class="wow-badge">
        <span class="{dot_class}"></span>
        <span>{label}</span>
      </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def divider():
    st.markdown('<div class="wow-hr"></div>', unsafe_allow_html=True)


def card_open(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="wow-card">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
        <div>
          <div style="font-weight:700; font-size:16px;">{title}</div>
          <div style="color: var(--wow-muted); font-size:12px;">{subtitle}</div>
        </div>
      </div>
    """, unsafe_allow_html=True)


def card_close():
    st.markdown("</div>", unsafe_allow_html=True)


def render_markdown_preview(md_text: str) -> None:
    st.markdown(md_text or "", unsafe_allow_html=True)


# =========================
# Agent Chain Logic
# =========================
def resolved_step_input(step_idx: int) -> str:
    steps = st.session_state["chain_steps"]
    cur = steps[step_idx]
    if cur.get("input_override"):
        return cur["input_override"]
    if step_idx == 0:
        return (st.session_state.get("coral_md") or st.session_state.get("doc_text") or "").strip()
    prev = steps[step_idx - 1]
    return (prev.get("edited_output") or prev.get("output") or "").strip()


def run_step(step_idx: int) -> None:
    steps = st.session_state["chain_steps"]
    step = steps[step_idx]
    step["status"] = "running"
    step["error"] = ""
    st.session_state["chain_steps"] = steps

    inp = resolved_step_input(step_idx)
    composed = f"INPUT:\n{inp}\n\nUSER INSTRUCTION:\n{step.get('user_prompt','')}".strip()

    t0 = time.time()
    try:
        text, usage = call_llm(
            model=step.get("model", "gemini-2.5-flash"),
            system_prompt=step.get("system_prompt", ""),
            prompt=composed,
            temperature=float(step.get("temperature", 0.2)),
            max_tokens=int(step.get("max_tokens", DEFAULT_MAX_TOKENS)),
        )
        latency = time.time() - t0
        step["output"] = text
        if not step.get("edited_output"):
            step["edited_output"] = text
        step["usage"] = {"inputTokens": usage.input_tokens, "outputTokens": usage.output_tokens}
        step["latency_s"] = latency
        step["status"] = "complete"
    except Exception as e:
        step["status"] = "error"
        step["error"] = str(e)
        step["latency_s"] = time.time() - t0

    st.session_state["chain_steps"] = steps


def run_all_steps() -> None:
    for i in range(len(st.session_state["chain_steps"])):
        run_step(i)


def reset_chain_outputs() -> None:
    for s in st.session_state["chain_steps"]:
        s["output"] = ""
        s["edited_output"] = ""
        s["status"] = "idle"
        s["usage"] = {"inputTokens": 0, "outputTokens": 0}
        s["latency_s"] = 0.0
        s["error"] = ""
    st.session_state["chain_steps"] = st.session_state["chain_steps"]


# =========================
# Notes Logic
# =========================
def push_note_history(label: str) -> None:
    st.session_state["note_history"].insert(0, {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "label": label,
        "note_input": st.session_state.get("note_input", ""),
        "note_md": st.session_state.get("note_md", ""),
    })
    st.session_state["note_history"] = st.session_state["note_history"][:50]


def ai_transform_note(instruction: str, model: str, temperature: float = 0.2, max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
    src = (st.session_state.get("note_md") or "").strip() or (st.session_state.get("note_input") or "").strip()
    prompt = f"""Transform the following note into well-organized Markdown.

Rules:
- Preserve meaning. Do not invent facts.
- Use headings, bullets, and short sections.
- If the note is messy, normalize structure.
- If there are code blocks, keep them as fenced code blocks.
- If there are tasks, format them as checklists.

INSTRUCTION:
{instruction}

NOTE:
{src}
"""
    text, _usage = call_llm(
        model=model,
        system_prompt="You are a senior technical writer and information architect.",
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return text


def highlight_keywords(md_text: str, keywords: List[str], color_hex: str) -> str:
    if not md_text or not keywords:
        return md_text
    parts = re.split(r"(```.*?```)", md_text, flags=re.DOTALL)
    out_parts = []
    for p in parts:
        if p.startswith("```") and p.endswith("```"):
            out_parts.append(p)
            continue
        for kw in keywords:
            if not kw:
                continue
            pattern = re.compile(rf"(?i)\b({re.escape(kw)})\b")
            p = pattern.sub(
                rf"<mark style='background:{color_hex}; padding:0 3px; border-radius:6px;'>\1</mark>",
                p
            )
        out_parts.append(p)
    return "".join(out_parts)


# =========================
# Sidebar
# =========================
with st.sidebar:
    st.markdown(f"### {t('app_title')}")
    st.caption(f"v{APP_VERSION}")

    card_open(t("sidebar_controls"), "Aesthetic Intelligence + Agentic Chains")

    theme_mode = st.radio(
        t("theme_mode"),
        options=[t("light"), t("dark")],
        index=0 if st.session_state["theme_mode"] == "Light" else 1,
        horizontal=True,
    )
    st.session_state["theme_mode"] = "Light" if theme_mode == t("light") else "Dark"

    lang = st.selectbox(
        t("language"),
        options=["en", "zh-TW"],
        index=0 if st.session_state["lang"] == "en" else 1,
        format_func=lambda x: "English" if x == "en" else "繁體中文",
    )
    st.session_state["lang"] = lang

    style_labels = {s["id"]: s["label"] for s in PAINTER_STYLES}
    painter = st.selectbox(
        t("painter_style"),
        options=[s["id"] for s in PAINTER_STYLES],
        index=[s["id"] for s in PAINTER_STYLES].index(st.session_state["painter"]),
        format_func=lambda x: style_labels.get(x, x),
    )
    st.session_state["painter"] = painter

    colA, colB = st.columns([1, 1])
    with colA:
        if st.button(t("jackpot"), use_container_width=True):
            st.session_state["painter"] = random.choice(PAINTER_STYLES)["id"]
            st.rerun()
    with colB:
        if st.button("Repaint UI", use_container_width=True):
            st.rerun()
    card_close()

    divider()

    card_open(t("nav"), "Tabs")
    tab = st.radio(
        "",
        options=TAB_KEYS,
        index=TAB_KEYS.index(st.session_state["active_tab"]),
        format_func=lambda k: t(k),
        label_visibility="collapsed",
    )
    st.session_state["active_tab"] = tab
    card_close()

    divider()

    card_open(t("api_status"), "Environment-first, then session input")
    for provider in ["gemini", "openai", "anthropic", "grok"]:
        has_env = bool(env_key(provider))
        has_key = bool(get_api_key(provider))
        if has_env:
            wow_badge(f"{provider.upper()}: {t('env_detected')}", "complete")
        elif has_key:
            wow_badge(f"{provider.upper()}: OK (session)", "complete")
        else:
            wow_badge(f"{provider.upper()}: {t('needs_key')}", "idle")
    st.caption(t("security_note"))
    card_close()

inject_css(st.session_state["theme_mode"], st.session_state["painter"])


# =========================
# Header WOW Status Strip
# =========================
style = get_style(st.session_state["painter"])
st.markdown(
    f"""
    <div class="wow-card" style="padding:14px 16px; display:flex; align-items:center; justify-content:space-between; gap:14px;">
      <div>
        <div style="font-weight:800; font-size:18px;">{t('app_title')}</div>
        <div style="color: var(--wow-muted); font-size:12px;">
          A painter-themed agentic workspace • Models: Gemini / OpenAI / Anthropic / Grok
        </div>
      </div>
      <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; justify-content:flex-end;">
        <span class="wow-badge"><span class="wow-dot complete"></span>Accent <span style="color:var(--wow-accent); font-weight:700;">{style['accent']}</span></span>
        <span class="wow-badge"><span class="wow-dot complete"></span>Style <b>{style['label']}</b></span>
        <span class="wow-badge"><span class="wow-dot complete"></span>Mode <b>{st.session_state["theme_mode"]}</b></span>
        <span class="wow-badge"><span class="wow-dot complete"></span>Lang <b>{st.session_state["lang"]}</b></span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")


# =========================
# Dashboard
# =========================
def render_dashboard():
    steps = st.session_state["chain_steps"]
    if not steps:
        return
    df = pd.DataFrame([{
        "step": f"{i+1}. {s.get('name','')}",
        "status": s.get("status", "idle"),
        "latency_s": float(s.get("latency_s") or 0.0),
        "input_tokens": int((s.get("usage") or {}).get("inputTokens") or 0),
        "output_tokens": int((s.get("usage") or {}).get("outputTokens") or 0),
        "model": s.get("model", ""),
    } for i, s in enumerate(steps)])

    total_in = int(df["input_tokens"].sum())
    total_out = int(df["output_tokens"].sum())
    total_latency = float(df["latency_s"].sum())
    completed = int((df["status"] == "complete").sum())
    errors = int((df["status"] == "error").sum())

    card_open(t("dashboard"), "Latency & Token Usage by Step")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Steps", len(df))
    c2.metric("Completed", completed)
    c3.metric("Errors", errors)
    c4.metric("Input Tokens", total_in)
    c5.metric("Output Tokens", total_out)

    st.caption(f"Total latency: {total_latency:.2f}s")

    lat_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("step:N", sort=None, title="Step"),
        y=alt.Y("latency_s:Q", title="Latency (s)"),
        color=alt.Color("status:N", legend=alt.Legend(title="Status")),
        tooltip=["step", "model", "status", "latency_s"]
    ).properties(height=220)

    tokens_long = df.melt(
        id_vars=["step", "status", "model"],
        value_vars=["input_tokens", "output_tokens"],
        var_name="token_type",
        value_name="tokens",
    )
    tok_chart = alt.Chart(tokens_long).mark_bar().encode(
        x=alt.X("step:N", sort=None, title="Step"),
        y=alt.Y("tokens:Q", stack=True, title="Tokens"),
        color=alt.Color("token_type:N", legend=alt.Legend(title="Token Type")),
        tooltip=["step", "model", "token_type", "tokens"]
    ).properties(height=220)

    st.altair_chart(lat_chart, use_container_width=True)
    st.altair_chart(tok_chart, use_container_width=True)
    card_close()


render_dashboard()
st.write("")


# =========================
# Tabs
# =========================
active = st.session_state["active_tab"]

if active == "workspace":
    left, right = st.columns([1.05, 1.35], gap="large")

    with left:
        card_open(t("doc_ingest"), "Text ingestion + Coral formatting")
        st.subheader(t("input_doc"))

        up = st.file_uploader(t("upload_files"), accept_multiple_files=True, type=None)
        if up:
            texts = []
            for f in up:
                try:
                    data = f.read()
                    texts.append(data.decode("utf-8", errors="ignore"))
                except Exception:
                    texts.append("")
            st.session_state["doc_text"] = "\n\n".join([x for x in texts if x]).strip()

        st.session_state["doc_text"] = st.text_area(
            t("paste_text"),
            value=st.session_state.get("doc_text", ""),
            height=220,
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(t("apply_coral"), use_container_width=True):
                try:
                    coral_model = "gemini-2.5-flash"
                    coral_prompt = """Format the input into clean Markdown.
- Use short headings.
- Use bullet lists.
- Highlight key terms by wrapping them in **bold**.
- Add a concise TL;DR at top.
"""
                    text, _usage = call_llm(
                        model=coral_model,
                        system_prompt="You are CoralFormatter, a meticulous Markdown formatter.",
                        prompt=f"INPUT:\n{st.session_state.get('doc_text','')}\n\nINSTRUCTION:\n{coral_prompt}",
                        temperature=0.2,
                        max_tokens=DEFAULT_MAX_TOKENS,
                    )
                    st.session_state["coral_md"] = text
                except Exception as e:
                    st.warning(f"Coral formatter unavailable: {e}")
                    st.session_state["coral_md"] = st.session_state.get("doc_text", "")
        with col2:
            if st.button(t("reset_chain"), use_container_width=True):
                reset_chain_outputs()

        divider()
        st.caption(t("coral_format"))
        coral_view = st.radio(t("view_mode"), [t("text"), t("markdown")], horizontal=True, key="coral_view_mode")
        if coral_view == t("text"):
            st.text_area("Coral Output", value=st.session_state.get("coral_md", ""), height=240, key="coral_out_text")
        else:
            render_markdown_preview(st.session_state.get("coral_md", ""))
        card_close()

    with right:
        card_open(t("agent_chain"), "Edit → Run step-by-step → Human-in-the-loop handoff")
        steps = st.session_state["chain_steps"]

        topc1, topc2 = st.columns([1, 1])
        with topc1:
            if st.button(t("run_all"), use_container_width=True):
                run_all_steps()
                st.rerun()
        with topc2:
            st.write("")

        divider()

        for idx, step in enumerate(steps):
            cols = st.columns([1.2, 0.9, 0.9])
            with cols[0]:
                st.markdown(f"#### {idx+1}. {step.get('name','Agent')}")
                if step.get("description"):
                    st.caption(step["description"])
            with cols[1]:
                wow_badge(
                    t(step.get("status", "idle")) if step.get("status") in ["running", "complete", "idle", "error"] else step.get("status", "idle"),
                    step.get("status", "idle")
                )
            with cols[2]:
                st.caption(f"Model: `{step.get('model','')}`")
                st.caption(
                    f"Latency: {float(step.get('latency_s') or 0):.2f}s • "
                    f"Tok In/Out: {int(step.get('usage',{}).get('inputTokens',0))}/{int(step.get('usage',{}).get('outputTokens',0))}"
                )

            with st.expander(t("step_config"), expanded=(idx == 0)):
                cA, cB = st.columns([1, 1])
                with cA:
                    step["model"] = st.selectbox(
                        t("model"),
                        options=MODEL_OPTIONS,
                        index=MODEL_OPTIONS.index(step["model"]) if step["model"] in MODEL_OPTIONS else 0,
                        key=f"model_{step['id']}",
                    )
                    step["temperature"] = st.slider(
                        t("temperature"),
                        min_value=0.0, max_value=1.0, value=float(step.get("temperature", 0.2)), step=0.05,
                        key=f"temp_{step['id']}",
                    )
                    step["max_tokens"] = st.number_input(
                        t("max_tokens"),
                        min_value=256, max_value=200000, value=int(step.get("max_tokens", DEFAULT_MAX_TOKENS)),
                        step=256,
                        key=f"maxt_{step['id']}",
                    )

                with cB:
                    step["input_override"] = st.text_area(
                        "Input override (optional)",
                        value=step.get("input_override", ""),
                        height=90,
                        key=f"in_over_{step['id']}",
                        help="If set, this step will use this input instead of previous step output.",
                    )

                step["system_prompt"] = st.text_area(
                    t("system_prompt"),
                    value=step.get("system_prompt", ""),
                    height=120,
                    key=f"sys_{step['id']}",
                )
                step["user_prompt"] = st.text_area(
                    t("user_prompt"),
                    value=step.get("user_prompt", ""),
                    height=120,
                    key=f"user_{step['id']}",
                )

                divider()
                st.caption(t("step_input"))
                st.text_area(
                    "Resolved Input (read-only)",
                    value=resolved_step_input(idx),
                    height=140,
                    key=f"resolved_{step['id']}",
                    disabled=True,
                )

                run_col, _ = st.columns([1, 4])
                with run_col:
                    if st.button(f"{t('run_step')} #{idx+1}", use_container_width=True, key=f"run_{step['id']}"):
                        run_step(idx)
                        st.rerun()

                if step.get("error"):
                    st.error(step["error"])

                divider()
                view_mode = st.radio(
                    t("view_mode"),
                    [t("text"), t("markdown")],
                    horizontal=True,
                    key=f"out_view_{step['id']}",
                )

                st.caption(t("step_output"))
                if view_mode == t("text"):
                    st.text_area("Output", value=step.get("output", ""), height=180, key=f"out_text_{step['id']}", disabled=True)
                else:
                    render_markdown_preview(step.get("output", ""))

                st.caption(t("edited_output"))
                edited_view = st.radio(
                    "Edited output view",
                    [t("text"), t("markdown")],
                    horizontal=True,
                    key=f"edit_view_{step['id']}",
                )
                if edited_view == t("text"):
                    step["edited_output"] = st.text_area("Edited Output", value=step.get("edited_output", ""), height=220, key=f"edited_{step['id']}")
                else:
                    step["edited_output"] = st.text_area("Edited Markdown (editable)", value=step.get("edited_output", ""), height=220, key=f"edited_md_{step['id']}")
                    st.caption("Preview")
                    render_markdown_preview(step.get("edited_output", ""))

            divider()

        st.session_state["chain_steps"] = steps
        card_close()

elif active == "notes":
    left, right = st.columns([1.05, 1.35], gap="large")

    with left:
        card_open(t("notes"), "Paste → Organize → Polish → Highlight keywords → History restore")
        st.session_state["note_input"] = st.text_area(
            t("note_input"),
            value=st.session_state.get("note_input", ""),
            height=260,
        )

        colA, colB = st.columns([1, 1])
        with colA:
            note_model = st.selectbox(
                "Model",
                MODEL_OPTIONS,
                index=MODEL_OPTIONS.index("gemini-2.5-flash") if "gemini-2.5-flash" in MODEL_OPTIONS else 0
            )
        with colB:
            note_temp = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05)

        if st.button(t("organize_note"), use_container_width=True):
            push_note_history("Before Organize")
            st.session_state["note_md"] = st.session_state["note_input"]
            try:
                st.session_state["note_md"] = ai_transform_note(
                    instruction="Organize into a clean, professional Markdown note with clear headings.",
                    model=note_model,
                    temperature=note_temp,
                    max_tokens=DEFAULT_MAX_TOKENS,
                )
                push_note_history("Organized")
            except Exception as e:
                st.error(str(e))

        divider()

        st.subheader(t("keep_prompt"))
        keep_prompt_text = st.text_area(
            "Prompt",
            value="Improve clarity and structure. Keep it factual. Output Markdown only.",
            height=90,
        )
        if st.button(t("apply_prompt"), use_container_width=True):
            push_note_history("Before Keep Prompt")
            st.session_state["note_md"] = (st.session_state.get("note_md") or "").strip() or st.session_state.get("note_input", "")
            try:
                st.session_state["note_md"] = ai_transform_note(
                    instruction=keep_prompt_text,
                    model=note_model,
                    temperature=note_temp,
                    max_tokens=DEFAULT_MAX_TOKENS,
                )
                push_note_history("Applied Keep Prompt")
            except Exception as e:
                st.error(str(e))

        divider()

        st.subheader(t("ai_magics"))
        mag_cols = st.columns(2)

        if mag_cols[0].button(t("ai_formatting"), use_container_width=True):
            push_note_history("Before AI Formatting")
            try:
                st.session_state["note_md"] = ai_transform_note(
                    instruction="Polish Markdown formatting: consistent headings, bullets, spacing; add a short TL;DR.",
                    model=note_model,
                    temperature=0.15,
                    max_tokens=DEFAULT_MAX_TOKENS,
                )
                push_note_history("AI Formatting")
            except Exception as e:
                st.error(str(e))

        kw = st.text_input(t("keywords"), value="")
        kw_color = st.color_picker(t("keyword_color"), value=style["accent"])
        if mag_cols[1].button(t("apply_keywords"), use_container_width=True):
            push_note_history("Before Keyword Highlight")
            kws = [x.strip() for x in kw.split(",") if x.strip()]
            st.session_state["note_md"] = highlight_keywords(st.session_state.get("note_md", "") or st.session_state.get("note_input", ""), kws, kw_color)
            push_note_history("Keyword Highlight")

        card_close()

    with right:
        card_open("Note Editor", "Edit note_md in text/markdown and preview")
        view = st.radio(t("view_mode"), [t("text"), t("markdown")], horizontal=True, key="note_view_mode")

        if view == t("text"):
            st.session_state["note_md"] = st.text_area("note_md", value=st.session_state.get("note_md", ""), height=420)
            st.caption("Preview")
            render_markdown_preview(st.session_state.get("note_md", ""))
        else:
            st.session_state["note_md"] = st.text_area("Markdown (editable)", value=st.session_state.get("note_md", ""), height=280)
            st.caption("Preview")
            render_markdown_preview(st.session_state.get("note_md", ""))

        divider()
        st.subheader(t("history"))
        if not st.session_state.get("note_history"):
            st.caption("No history yet.")
        else:
            for i, h in enumerate(st.session_state["note_history"][:12]):
                cols = st.columns([1.6, 1.2, 0.6])
                cols[0].markdown(f"**{h['label']}**")
                cols[1].caption(h["ts"])
                if cols[2].button(t("restore"), key=f"restore_{i}", use_container_width=True):
                    st.session_state["note_input"] = h["note_input"]
                    st.session_state["note_md"] = h["note_md"]
                    st.rerun()

        card_close()

elif active == "batch":
    card_open(t("batch"), "Conveyor belt UI (simulation)")
    st.subheader(t("batch_upload"))
    ups = st.file_uploader(t("upload_files"), accept_multiple_files=True, key="batch_upload")
    if ups:
        new_files = []
        for f in ups:
            new_files.append({
                "id": str(uuid.uuid4()),
                "name": f.name,
                "size": getattr(f, "size", 0),
                "status": "queued",
                "note": "",
            })
        st.session_state["batch_files"].extend(new_files)

    st.subheader("Queue")
    if st.session_state.get("batch_files"):
        df = pd.DataFrame(st.session_state["batch_files"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("No files in queue.")

    card_close()

elif active == "settings":
    card_open(t("settings"), "Environment-first keys + in-page input when missing")
    st.subheader(t("provider_keys"))

    def key_block(provider: str, label: str):
        has_env = bool(env_key(provider))
        st.markdown(f"#### {label}")
        if has_env:
            wow_badge(f"{provider.upper()}: {t('env_detected')}", "complete")
            st.caption("Key input disabled because environment key is present.")
        else:
            has_session = bool(get_api_key(provider))
            wow_badge(
                f"{provider.upper()}: {t('needs_key') if not has_session else 'OK (session)'}",
                "idle" if not has_session else "complete"
            )
            k = st.text_input(
                label,
                type="password",
                value="",
                placeholder="Paste API key here (stored only in session)",
                key=f"key_input_{provider}",
            )
            if st.button(f"{t('save_in_session')} — {provider.upper()}", use_container_width=True, key=f"save_{provider}"):
                api_keys = ensure_api_keys_dict()
                api_keys[provider] = (k or "").strip()
                st.session_state["api_keys"] = api_keys
                st.rerun()
        divider()

    key_block("gemini", t("gemini_key"))
    key_block("openai", t("openai_key"))
    key_block("anthropic", t("anthropic_key"))
    key_block("grok", t("grok_key"))

    st.caption(t("security_note"))
    card_close()

elif active == "about":
    card_open(t("about"), "Spec-driven implementation • agents.yaml • SKILL.md")
    st.markdown("### " + t("skill_md"))
    skill = read_text_file("SKILL.md")
    if skill.strip():
        st.markdown(skill)
    else:
        st.caption("SKILL.md not found (optional but recommended).")

    divider()

    st.markdown("### " + t("agents_yaml"))
    agents_raw = read_text_file("agents.yaml")
    if agents_raw.strip():
        st.code(agents_raw, language="yaml")
    else:
        st.caption("agents.yaml not found. App is running with fallback default steps.")

    divider()
    st.markdown("### Runtime")
    st.write({
        "version": APP_VERSION,
        "lang": st.session_state["lang"],
        "theme_mode": st.session_state["theme_mode"],
        "painter": st.session_state["painter"],
        "steps": len(st.session_state["chain_steps"]),
    })
    card_close()
