# 📘 chhanda001 Web Version (Streamlit-based)
# Lightweight front-end for entering Odia song metrical structures

import streamlit as st
import pandas as pd
import json
import os

CSV_FILE = "odia_song_corpus_text.csv"

# Ensure CSV exists
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=[
        "title", "poet", "raga", "tala",
        "ghosa_total", "ghosa_lines", "ghosa_pattern", "ghosa_text",
        "antara_total", "antara_lines", "antara_pattern", "antara_text",
        "structure_notation", "structure_json"
    ]).to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

st.title("🎵 Odia Song Chhanda Entry Tool")
st.markdown("Upload metrical details of Odia songs (Chhanda based)")

# --- Metadata Inputs ---
st.subheader("1️⃣ Song Metadata")
title = st.text_input("Title")
poet = st.text_input("Poet")
raga = st.text_input("Raga")
tala = st.text_input("Tala")

# --- Ghosha Section ---
st.subheader("2️⃣ Ghoṣā")
ghosa_text = st.text_area("Paste Ghoṣā Text (one line per row)")
if ghosa_text:
    g_lines = ghosa_text.strip().splitlines()
    st.markdown("#### Enter akṣara counts for Ghoṣā lines:")
    g_counts = [st.number_input(f"Ghoṣā {i+1}", min_value=1, max_value=100, value=8) for i in range(len(g_lines))]
else:
    g_lines = []
    g_counts = []

# --- Antara Section ---
st.subheader("3️⃣ Antarā")
antara_text = st.text_area("Paste Antarā Text (one line per row)")
if antara_text:
    a_lines = antara_text.strip().splitlines()
    st.markdown("#### Enter akṣara counts for Antarā lines:")
    a_counts = [st.number_input(f"Antarā {i+1}", min_value=1, max_value=100, value=8) for i in range(len(a_lines))]
else:
    a_lines = []
    a_counts = []

# --- Preview ---
if st.button("📋 Preview Entry"):
    if not title or not g_lines or not a_lines:
        st.error("Please fill in title, Ghoṣā, and Antarā.")
    else:
        g_total, a_total = sum(g_counts), sum(a_counts)
        g_pattern = "*".join(map(str, g_counts))
        a_pattern = "*".join(map(str, a_counts))

        structure_notation = f"G:[{g_total}|{len(g_lines)}|{g_pattern}], A:[{a_total}|{len(a_lines)}|{a_pattern}]"
        structure_json = json.dumps({
            "ghosa_total": g_total,
            "ghosa_lines": len(g_lines),
            "ghosa_pattern": g_counts,
            "antara_total": a_total,
            "antara_lines": len(a_lines),
            "antara_pattern": a_counts
        }, ensure_ascii=False)

        preview_data = {
            "title": title,
            "poet": poet,
            "raga": raga,
            "tala": tala,
            "ghosa_total": g_total,
            "ghosa_lines": len(g_lines),
            "ghosa_pattern": g_pattern,
            "ghosa_text": "\n".join(g_lines),
            "antara_total": a_total,
            "antara_lines": len(a_lines),
            "antara_pattern": a_pattern,
            "antara_text": "\n".join(a_lines),
            "structure_notation": structure_notation,
            "structure_json": structure_json
        }

        st.subheader("🔍 Preview")
        st.json(preview_data)

        if st.button("✅ Confirm and Save"):
            df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
            df = pd.concat([df, pd.DataFrame([preview_data])], ignore_index=True)
            df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
            st.success("✅ Song saved successfully!")

            # Download link
            with open(CSV_FILE, "rb") as f:
                st.download_button("⬇ Download CSV", f, file_name="odia_song_corpus_text.csv")
