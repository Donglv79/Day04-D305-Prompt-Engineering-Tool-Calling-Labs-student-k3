from __future__ import annotations

import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import (
    now_iso,
    safe_slug,
    trim_history,
    run_model_tool_loop,
    write_transcript,
)

# Root directory setup
ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
RUNS_DIR = ROOT / "runs"
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
load_lab_env(ROOT)

# Page configuration
st.set_page_config(
    page_title="Research Agent Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Safe styling for Header Badges & Tool Call Cards
st.markdown(
    """
    <style>
    .v-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.85rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .v-tag-v0 { background-color: #ef4444; color: #ffffff; }
    .v-tag-v1 { background-color: #f59e0b; color: #ffffff; }
    .v-tag-v2 { background-color: #3b82f6; color: #ffffff; }
    .v-tag-v3 { background-color: #10b981; color: #ffffff; }

    .h-tag {
        display: inline-block;
        background-color: #1e293b;
        color: #f8fafc;
        border: 1px solid #475569;
        padding: 4px 10px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 0.82rem;
    }

    .new-tool-badge {
        background-color: #8b5cf6;
        color: #ffffff;
        font-size: 0.7rem;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
        margin-left: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "turns_log" not in st.session_state:
    st.session_state.turns_log = []
if "transcript_id" not in st.session_state:
    st.session_state.transcript_id = None
if "turn_index" not in st.session_state:
    st.session_state.turn_index = 0

# Sidebar Configuration
with st.sidebar:
    st.title("⚡ Agent Studio")
    st.caption("Day 04 Research Agent Tool Calling Lab")
    st.divider()

    st.subheader("⚙️ Model & Version Config")
    provider_name = st.selectbox("LLM Provider", ["openrouter", "openai", "anthropic", "gemini"], index=0)
    version_label = st.selectbox("Artifact Version", ["v0", "v1", "v2", "v3"], index=3)
    custom_model = st.text_input("Custom Model (Optional)", placeholder="e.g. google/gemini-2.0-flash-001")

    st.divider()
    st.subheader("🎛️ Execution Parameters")
    max_tool_rounds = st.slider("Max Tool Rounds", min_value=1, max_value=8, value=4)
    history_window = st.slider("History Window (Turns)", min_value=1, max_value=10, value=5)

    st.divider()

    # Load Artifacts dynamically
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_yaml_path = ARTIFACTS_DIR / "tools.yaml"

    if system_prompt_path.exists():
        system_prompt = system_prompt_path.read_text(encoding="utf-8")
    else:
        system_prompt = "You are a helpful research assistant."

    tool_declarations = load_tool_declarations(tools_yaml_path) if tools_yaml_path.exists() else []
    openai_tools = to_openai_tools(tool_declarations)

    artifact_version = build_artifact_version(version_label, system_prompt_path, tools_yaml_path)

    # Transcript session initialization
    if not st.session_state.transcript_id:
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        st.session_state.transcript_id = f"{safe_slug(version_label)}_{safe_slug(provider_name)}_{timestamp}"

    transcript_path = TRANSCRIPTS_DIR / f"{st.session_state.transcript_id}.transcript.json"

    # Quick View Artifact Details
    with st.expander("📄 System Prompt Inspector", expanded=False):
        st.code(system_prompt, language="markdown")

    with st.expander(f"🛠️ Loaded Tools ({len(tool_declarations)})", expanded=False):
        for tool in tool_declarations:
            name = tool.get('name')
            is_new = "NEW" if name == "dedupe_sources" else ""
            badge_html = '<span class="new-tool-badge">NEW</span>' if is_new else ''
            st.markdown(f"**`{name}`** {badge_html}: {tool.get('description')}", unsafe_allow_html=True)

    if st.button("🗑️ Reset Chat Session", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.turns_log = []
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        st.session_state.transcript_id = f"{safe_slug(version_label)}_{safe_slug(provider_name)}_{timestamp}"
        st.session_state.turn_index = 0
        st.rerun()

# Main Header
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🔬 Research Agent Studio")
    st.caption("Evidence-driven Prompt & Tool Engineering Playground")
    st.markdown(
        f"""
        <div style="margin-bottom: 15px;">
            <span class="v-tag v-tag-{version_label}">VERSION: {version_label}</span> &nbsp;
            <span class="h-tag">Prompt Hash: <b>{artifact_version.prompt_hash[:8]}</b></span> &nbsp;
            <span class="h-tag">Tools Hash: <b>{artifact_version.tools_hash[:8]}</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_h2:
    st.info(f"**Active Session ID:**\n`{st.session_state.transcript_id[:20]}...`")

# Dashboard Metrics Row
m1, m2, m3, m4 = st.columns(4)
total_turns = len(st.session_state.turns_log)
total_tool_calls = sum(len(t.get("tool_events", [])) for t in st.session_state.turns_log)
active_provider = provider_name.upper()
declared_tools_count = len(tool_declarations)

m1.metric("Active Version", version_label, delta="v3 Accuracy: 100%" if version_label == "v3" else None)
m2.metric("User Turns", total_turns)
m3.metric("Tools Fired", total_tool_calls)
m4.metric("Active Provider", active_provider, delta=f"{declared_tools_count} Tools Loaded")

st.divider()

# Main Interface Tabs
tab_chat, tab_trace, tab_benchmark, tab_transcript = st.tabs([
    "💬 Agent Chat & Live Traces",
    "🔍 Deep Tool Inspector",
    "📊 Version Optimization Log",
    "📜 Saved Transcripts"
])

with tab_chat:
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Display tool traces if attached to assistant message
            if "tool_events" in message and message["tool_events"]:
                with st.expander(f"🔧 Execution Trace ({len(message['tool_events'])} tool calls)", expanded=False):
                    for idx, event in enumerate(message["tool_events"], 1):
                        tool_name = event.get("tool", "unknown")
                        args = event.get("args", {})
                        result = event.get("result", {})
                        st.markdown(f"**Call #{idx}: `{tool_name}`**")
                        st.json({"args": args, "result": result})

    # Chat Input Box
    if user_input := st.chat_input("Nhập câu hỏi hoặc yêu cầu nghiên cứu của bạn..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.turn_index += 1
        history_msgs = trim_history(st.session_state.chat_history, history_window)
        messages_payload = [
            {"role": "system", "content": system_prompt},
            *history_msgs,
            {"role": "user", "content": user_input},
        ]

        turn_record: dict[str, Any] = {
            "turn_index": st.session_state.turn_index,
            "started_at": now_iso(),
            "user": user_input,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }

        with st.chat_message("assistant"):
            with st.spinner("🤖 Agent đang xử lý và thực thi tools..."):
                try:
                    provider_obj = make_provider(provider_name)
                    selected_model = custom_model or getattr(provider_obj, "default_model", None)

                    loop_result = run_model_tool_loop(
                        provider=provider_obj,
                        messages=messages_payload,
                        tools=openai_tools,
                        model=selected_model,
                        max_tool_rounds=max_tool_rounds,
                    )

                    turn_record.update(loop_result)
                    assistant_response = loop_result.get("assistant_text", "")
                    tool_events = loop_result.get("tool_events", [])

                    st.markdown(assistant_response)

                    if tool_events:
                        with st.expander(f"🔧 Execution Trace ({len(tool_events)} tool calls)", expanded=True):
                            for idx, event in enumerate(tool_events, 1):
                                tool_name = event.get("tool", "unknown")
                                args = event.get("args", {})
                                result = event.get("result", {})
                                st.markdown(f"**Call #{idx}: `{tool_name}`**")
                                st.json({"args": args, "result": result})

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_response,
                        "tool_events": tool_events,
                    })
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

                except Exception as exc:
                    error_msg = f"❌ **Provider Error**: `{type(exc).__name__}: {str(exc)}`"
                    st.error(error_msg)
                    turn_record.update({"status": "provider_error", "error": str(exc)})
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

                turn_record["ended_at"] = now_iso()
                st.session_state.turns_log.append(turn_record)

                transcript_payload = {
                    "transcript_id": st.session_state.transcript_id,
                    **artifact_version_dict(artifact_version),
                    "provider": provider_name,
                    "model": custom_model or "default",
                    "system_prompt": str(system_prompt_path),
                    "tools": str(tools_yaml_path),
                    "history_window": history_window,
                    "max_tool_rounds": max_tool_rounds,
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                    "turns": st.session_state.turns_log,
                }
                write_transcript(transcript_path, transcript_payload)

with tab_trace:
    st.subheader("🔍 Chi Tiết Trace Từng Tool Fired Trong Session")
    if not st.session_state.turns_log:
        st.info("Chưa có tool call nào được thực thi trong phiên làm việc này.")
    else:
        for turn in st.session_state.turns_log:
            st.markdown(f"#### Turn #{turn.get('turn_index')} - User: *\"{turn.get('user')}\"*")
            events = turn.get("tool_events", [])
            if not events:
                st.caption("Không có tool nào được gọi trong lượt này.")
            else:
                for idx, ev in enumerate(events, 1):
                    col_t1, col_t2 = st.columns([1, 2])
                    with col_t1:
                        st.markdown(f"**Tool:** `{ev.get('tool')}`")
                        st.markdown("**Arguments:**")
                        st.json(ev.get("args", {}))
                    with col_t2:
                        st.markdown("**Result / Response Output:**")
                        st.json(ev.get("result", {}))
                    st.divider()

with tab_benchmark:
    st.subheader("📊 Lịch Sử Tối Ưu Phiên Bản (v0 ➔ v3)")
    version_csv_path = ARTIFACTS_DIR / "version_log.csv"

    if version_csv_path.exists():
        with open(version_csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        for row in rows:
            v = row.get("version")
            acc_after = row.get("metric_after", "N/A")
            try:
                acc_val = f"{float(acc_after)*100:.0f}%"
            except ValueError:
                acc_val = acc_after

            if v == "v0":
                col_b1.metric("v0 (Baseline)", acc_val, delta=None)
            elif v == "v1":
                col_b2.metric("v1 (Prompt Cleanup)", acc_val, delta="+15%")
            elif v == "v2":
                col_b3.metric("v2 (Clarify Rules)", acc_val, delta="+5%")
            elif v == "v3":
                col_b4.metric("v3 (Tool Declaration)", acc_val, delta="+10% (100% PASS)")

        st.divider()
        st.markdown("### 📝 Chi tiết Giả thuyết & Thay đổi qua các Version")
        for row in rows:
            with st.expander(f"📌 Version **{row.get('version')}** - Author: {row.get('author')}", expanded=(row.get('version') == "v3")):
                st.markdown(f"**Tệp thay đổi:** `{row.get('changed_artifact')}`")
                st.markdown(f"**Lý do sửa:** {row.get('reason')}")
                st.markdown(f"**Giả thuyết:** {row.get('hypothesis')}")
                st.markdown(f"**Chỉ số:** `{row.get('metric_name')}`: {row.get('metric_before')} ➔ **{row.get('metric_after')}**")
                st.caption(f"Run File: `{row.get('run_file')}`")
    else:
        st.warning("Chưa tìm thấy file version_log.csv")

    st.divider()
    st.markdown("### 📁 Evaluated Run Logs (JSON Files)")
    run_files = list(RUNS_DIR.glob("*.json")) if RUNS_DIR.exists() else []
    if run_files:
        selected_run = st.selectbox("Chọn Run File để xem chi tiết:", run_files, format_func=lambda p: p.name)
        if selected_run:
            try:
                run_data = json.loads(selected_run.read_text(encoding="utf-8"))
                st.json(run_data.get("summary", {}))
                with st.expander("Xem toàn bộ JSON Run Log", expanded=False):
                    st.json(run_data)
            except Exception as e:
                st.error(f"Không thể đọc run file: {e}")

with tab_transcript:
    st.subheader("📜 Quản Lý & Xem Log Transcript JSON")
    transcript_files = list(TRANSCRIPTS_DIR.glob("*.json"))

    if not transcript_files:
        st.warning("Chưa có file transcript nào được lưu.")
    else:
        selected_file = st.selectbox(
            "Chọn file Transcript để xem:",
            transcript_files,
            format_func=lambda p: p.name,
        )
        if selected_file:
            try:
                transcript_data = json.loads(selected_file.read_text(encoding="utf-8"))
                st.markdown(f"**Transcript ID:** `{transcript_data.get('transcript_id')}`")
                st.markdown(f"**Artifact Version:** `{transcript_data.get('artifact_version')}`")
                st.markdown(f"**Prompt Hash:** `{transcript_data.get('prompt_hash')}`")
                st.json(transcript_data)
            except Exception as e:
                st.error(f"Lỗi khi đọc file transcript: {e}")
