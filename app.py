import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from matcher.pipeline import screen_resumes

st.set_page_config(page_title="Resume Screener", layout="wide")
st.title("Resume Screening System")

jd_text = st.text_area(
    "Paste the job description here",
    height=300,
)

uploaded_files = st.file_uploader(
    "Upload resume files:",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)

if st.button("Screen Resumes", type="primary"):
    if not jd_text.strip() or not uploaded_files:
        st.warning("Please paste a job description and upload at least one resume.")
    else:
        with st.spinner("Processing resumes..."):
            with tempfile.TemporaryDirectory() as tmp_dir:
                paths = []
                for uploaded in uploaded_files:
                    path = Path(tmp_dir) / uploaded.name
                    path.write_bytes(uploaded.getbuffer())
                    paths.append(path)
                # Streamlit re-runs the script, so worker processes are unreliable here
                results = screen_resumes(jd_text, paths, parallel=False)

        st.success(f"Screened {len(results)} resume(s)")

        rows = [
            {
                "Rank": rank,
                "Candidate": r["candidate"],
                "Score": r["score"],
                "Matched required": ", ".join(r.get("matched_required", [])),
                "Missing required": ", ".join(r.get("missing_required", [])),
                "Matched preferred": ", ".join(r.get("matched_preferred", [])),
                "Years": r.get("years_experience", ""),
                "Error": r["error"] or "",
            }
            for rank, r in enumerate(results, start=1)
        ]
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="screening_results.csv",
            mime="text/csv",
        )
