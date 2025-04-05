# ✅ Final Streamlit Version of Chhanda001 (with All Original Functionality)
# ----------------------------------------------------------------------------
# Features:
# - Multiline input
# - Metadata auto-extraction
# - Ghoṣā marker detection
# - Line-wise editable Ghoṣā and Antarā
# - Editable preview of all fields
# - CSV append with download
# - Batch mode rerun

import csv
import os
import json
import re
import pandas as pd
import streamlit as st

# Paths and Constants
OUTPUT_DIR = "ChhandaCollection"
CSV_FILE = os.path.join(OUTPUT_DIR, "odia_song_corpus_text.csv")
FIELDNAMES = [
    "title", "poet", "raga", "tala",
    "ghosa_total", "ghosa_lines", "ghosa_pattern", "ghosa_text",
    "antara_total", "antara_lines", "antara_pattern", "antara_text",
    "structure_notation", "structure_json"
]
GHOSHA_MARKERS = ["ଘୋଷା", "ଘୋଷା ।", "ଘୋଷା।", "॥ ଘୋଷା ॥", "॥ପଦ॥", "॥0॥", "॥"]
ANTARA_END_RE = r"[।॥] ?[୧୨୩123]+ ?[।॥]"

# Ensure output dir exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_existing_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=FIELDNAMES)

def save_and_get_csv(data, df):
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    csv_bytes = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    return csv_bytes

def extract_metadata(lines):
    title = poet = raga = tala = ""
    for line in lines[:4]:
        if "—" in line:
            parts = line.replace("(", "").replace(")", "").split("—")
            if len(parts) == 2:
                poet = parts[0].strip()
                raga_tala = parts[1].strip()
                match = re.search(r"ରାଗ[: ]?([^,]+),? ?ତାଳ[: ]?([^)]+)", raga_tala)
                if match:
                    raga, tala = match.group(1).strip(), match.group(2).strip()
        elif not title and not line.startswith("("):
            title = line.strip()
    return title, poet, raga, tala

def app():
    st.title("🎶 Odia Song Structure Collector (chhanda001)")
    st.markdown("Paste the full **Odia Song** below including Ghoṣā and one Antarā:")

    song_text = st.text_area("Odia Song (with Ghoṣā + Antarā)", height=300)

    if st.button("🔍 Parse Song"):
        if not song_text.strip():
            st.warning("Please paste the full song text.")
            return

        lines = song_text.strip().splitlines()
        title, poet, raga, tala = extract_metadata(lines)

        # Ghoṣā detection
        ghosha_end = -1
        for i, line in enumerate(lines):
            if any(marker in line for marker in GHOSHA_MARKERS):
                ghosha_end = i
                break

        if ghosha_end == -1:
            st.error("❌ Ghoṣā marker not found.")
            return

        st.subheader("✅ Select Ghoṣā lines")
        ghosha_candidate_lines = lines[:ghosha_end + 1]
        selected_ghosha = st.multiselect(
            "Select valid Ghoṣā lines (hold Ctrl to select multiple)",
            ghosha_candidate_lines,
            default=ghosha_candidate_lines[-2:] if len(ghosha_candidate_lines) >= 2 else ghosha_candidate_lines
        )

        antara_lines = []
        for line in lines[ghosha_end+1:]:
            if not line.strip() or line.startswith("("):
                continue
            antara_lines.append(line.strip())
            if re.search(ANTARA_END_RE, line.strip()):
                break

        st.subheader("✍️ Edit Metadata")
        title = st.text_input("Title", title)
        poet = st.text_input("Poet", poet)
        raga = st.text_input("Raga", raga)
        tala = st.text_input("Tala", tala)

        st.subheader("📝 Ghoṣā Lines with Akṣara Count")
        edited_ghosha = []
        ghosha_pattern = []
        for i, line in enumerate(selected_ghosha):
            col1, col2 = st.columns([4, 1])
            with col1:
                line_edit = st.text_input(f"Ghoṣā {i+1}", line, key=f"gh_{i}")
            with col2:
                count = st.number_input("Akṣaras", min_value=1, value=len(line_edit), key=f"ghc_{i}")
            edited_ghosha.append(line_edit)
            ghosha_pattern.append(count)

        st.subheader("📝 Antarā Lines with Akṣara Count")
        edited_antara = []
        antara_pattern = []
        for i, line in enumerate(antara_lines):
            col1, col2 = st.columns([4, 1])
            with col1:
                line_edit = st.text_input(f"Antarā {i+1}", line, key=f"an_{i}")
            with col2:
                count = st.number_input("Akṣaras", min_value=1, value=len(line_edit), key=f"anc_{i}")
            edited_antara.append(line_edit)
            antara_pattern.append(count)

        g_total, g_lines = sum(ghosha_pattern), len(ghosha_pattern)
        a_total, a_lines = sum(antara_pattern), len(antara_pattern)
        g_pattern = "*".join(map(str, ghosha_pattern))
        a_pattern = "*".join(map(str, antara_pattern))

        structure_notation = f"G:[{g_total}|{g_lines}|{g_pattern}], A:[{a_total}|{a_lines}|{a_pattern}]"
        structure_json = json.dumps({
            "ghosa_total": g_total,
            "ghosa_lines": g_lines,
            "ghosa_pattern": ghosha_pattern,
            "antara_total": a_total,
            "antara_lines": a_lines,
            "antara_pattern": antara_pattern
        }, ensure_ascii=False)

        st.subheader("📦 Preview & Final Edits Before Save")
        row = {
            "title": title, "poet": poet, "raga": raga, "tala": tala,
            "ghosa_total": g_total, "ghosa_lines": g_lines, "ghosa_pattern": g_pattern, "ghosa_text": "\n".join(edited_ghosha),
            "antara_total": a_total, "antara_lines": a_lines, "antara_pattern": a_pattern, "antara_text": "\n".join(edited_antara),
            "structure_notation": structure_notation,
            "structure_json": structure_json
        }

        st.json(row)

        if st.button("✅ Confirm & Save"):
            df = load_existing_data()
            csv_bytes = save_and_get_csv(row, df)
            st.success("✅ Song saved to odia_song_corpus_text.csv")
            st.download_button("⬇️ Download CSV", data=csv_bytes, file_name="odia_song_corpus_text.csv", mime="text/csv")
            st.markdown("---")
            st.info("You may now enter another song.")
            st.experimental_rerun()

if __name__ == "__main__":
    app()




