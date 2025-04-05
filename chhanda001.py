import csv
import os
import json
import re
import pandas as pd
import streamlit as st

# 🔁 Ensure output directory exists
OUTPUT_DIR = "ChhandaCollection"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 📁 CSV path inside folder
CSV_FILE = os.path.join(OUTPUT_DIR, "odia_song_corpus_text.csv")

FIELDNAMES = [
    "title", "poet", "raga", "tala",
    "ghosa_total", "ghosa_lines", "ghosa_pattern", "ghosa_text",
    "antara_total", "antara_lines", "antara_pattern", "antara_text",
    "structure_notation", "structure_json"
]

GHOSHA_MARKERS = ["ଘୋଷା", "ଘୋଷା ।", "ଘୋଷା।", "॥ ଘୋଷା ॥", "॥ପଦ॥", "॥0॥", "॥"]
ANTARA_END_RE = r"[।॥] ?[୧୨୩123]+ ?[।॥]"

def load_existing_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=FIELDNAMES)

def save_and_get_csv(data, df):
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

# --- Streamlit App Starts ---
st.title("🎶 Odia Song Structure Collector (Chhanda001)")
st.markdown("Paste your **Odia song** below (include Ghoṣā & one Antarā).")
song_text = st.text_area("Odia Song (Ghoṣā + Antarā)", height=300)

if st.button("Submit Song"):
    if not song_text.strip():
        st.warning("Please paste the full song text.")
    else:
        lines = song_text.strip().splitlines()

        # Parse metadata
        title = poet = raga = tala = ""
        for line in lines[:4]:
            if "—" in line:
                parts = line.replace("(", "").replace(")", "").split("—")
                if len(parts) == 2:
                    poet_candidate = parts[0].strip()
                    raga_tala = parts[1].strip()
                    poet = poet or poet_candidate
                    match = re.search(r"ରାଗ[: ]?([^,]+),? ?ତାଳ[: ]?([^)]+)", raga_tala)
                    if match:
                        raga = match.group(1).strip()
                        tala = match.group(2).strip()
            elif not title and not line.startswith("("):
                title = line.strip()

        ghosha_index = -1
        for i, line in enumerate(lines):
            if any(marker in line for marker in GHOSHA_MARKERS):
                ghosha_index = i
                break

        if ghosha_index == -1:
            st.error("❌ Ghoṣā marker not found.")
        else:
            ghosha_lines = lines[:ghosha_index + 1]
            antara_lines = []
            for line in lines[ghosha_index+1:]:
                if not line.strip() or line.startswith("("):
                    continue
                antara_lines.append(line.strip())
                if re.search(ANTARA_END_RE, line.strip()):
                    break

            st.subheader("✏️ Edit Metadata")
            title = st.text_input("Title", title)
            poet = st.text_input("Poet", poet)
            raga = st.text_input("Raga", raga)
            tala = st.text_input("Tala", tala)

            st.subheader("📌 Ghoṣā Lines")
            edited_ghosha = []
            ghosha_pattern = []
            for i, line in enumerate(ghosha_lines):
                col1, col2 = st.columns([4, 1])
                with col1:
                    edited = st.text_input(f"Ghoṣā Line {i+1}", line)
                with col2:
                    count = st.number_input(f"Akṣaras", value=len(edited), min_value=1, key=f"ghosha_{i}")
                edited_ghosha.append(edited)
                ghosha_pattern.append(count)

            st.subheader("📌 Antarā Lines")
            edited_antara = []
            antara_pattern = []
            for i, line in enumerate(antara_lines):
                col1, col2 = st.columns([4, 1])
                with col1:
                    edited = st.text_input(f"Antarā Line {i+1}", line)
                with col2:
                    count = st.number_input(f"Akṣaras", value=len(edited), min_value=1, key=f"antara_{i}")
                edited_antara.append(edited)
                antara_pattern.append(count)

            g_total, g_lines = sum(ghosha_pattern), len(ghosha_pattern)
            a_total, a_lines = sum(antara_pattern), len(antara_pattern)
            g_pattern = "*".join(map(str, ghosha_pattern))
            a_pattern = "*".join(map(str, antara_pattern))

            notation = f"G:[{g_total}|{g_lines}|{g_pattern}], A:[{a_total}|{a_lines}|{a_pattern}]"

            row = {
                "title": title, "poet": poet, "raga": raga, "tala": tala,
                "ghosa_total": g_total, "ghosa_lines": g_lines, "ghosa_pattern": g_pattern,
                "ghosa_text": "\n".join(edited_ghosha),
                "antara_total": a_total, "antara_lines": a_lines, "antara_pattern": a_pattern,
                "antara_text": "\n".join(edited_antara),
                "structure_notation": notation,
                "structure_json": json.dumps({
                    "ghosa_total": g_total, "ghosa_lines": g_lines, "ghosa_pattern": ghosha_pattern,
                    "antara_total": a_total, "antara_lines": a_lines, "antara_pattern": antara_pattern
                }, ensure_ascii=False)
            }

            df = load_existing_data()
            csv_data = save_and_get_csv(row, df)

            st.success("✅ Entry saved to CSV!")
            st.download_button("⬇️ Download Full CSV", data=csv_data, file_name="odia_song_corpus_text.csv", mime="text/csv")

            st.markdown("---")
            if st.button("➕ Add Another Song"):
                st.experimental_rerun()

