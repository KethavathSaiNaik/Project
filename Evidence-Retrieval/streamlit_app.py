import streamlit as st
import requests

# ---------------- CONFIG ----------------
API_URL = "http://127.0.0.1:8000/api/verify"

st.set_page_config(
    page_title="Claim Verification System",
    layout="centered"
)

# ---------------- LABEL NORMALIZATION ----------------
LABEL_MAP = {
    "SUPPORTS": "Supported",
    "REFUTES": "Refuted",
    "NOT_ENOUGH_INFO": "Not Enough Information"
}

# ---------------- HEADER ----------------
st.title("🧠 Claim Verification System")
st.caption(
    "Fact-checking using multi-source evidence retrieval and DeBERTa-based NLI"
)

st.write(
    "Enter a factual claim below. The system retrieves evidence from trusted sources "
    "and classifies the claim as **Supported**, **Refuted**, or **Not Enough Information**."
)

# ---------------- INPUT ----------------
claim = st.text_area(
    "📝 Enter Claim",
    placeholder="Example: Smoking reduces the risk of lung cancer.",
    height=120
)

verify_btn = st.button("🔍 Verify Claim")

# ---------------- API CALL ----------------
if verify_btn:
    if not claim.strip():
        st.warning("⚠️ Please enter a claim before verifying.")
        st.stop()

    with st.spinner("Running verification pipeline (retrieval → ranking → NLI)..."):
        try:
            response = requests.post(
                API_URL,
                json={"claim": claim},
                timeout=300
            )

            if response.status_code != 200:
                st.error(f"❌ Backend error: {response.status_code}")
                st.stop()

            result = response.json()

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to connect to backend: {e}")
            st.stop()

    # ---------------- RESULT HEADER ----------------
    st.success("✅ Verification completed")

    raw_label = result.get("label", "")
    label = LABEL_MAP.get(raw_label, raw_label)
    confidence = result.get("confidence", 0.0)

    # ---------------- LABEL STYLING ----------------
    if label == "Supported":
        st.markdown("### 🟢 **SUPPORTED**")
    elif label == "Refuted":
        st.markdown("### 🔴 **REFUTED**")
    else:
        st.markdown("### 🟡 **NOT ENOUGH INFORMATION**")

    # ---------------- CONFIDENCE ----------------
    st.write("**Confidence Score**")
    st.progress(min(float(confidence), 1.0))
    st.caption(f"{confidence:.4f}")

    st.divider()

    # ---------------- EVIDENCE ----------------
    st.subheader("📄 Top Evidence")

    if not result.get("evidence"):
        st.info("No evidence sentences were returned.")
    else:
        for idx, ev in enumerate(result["evidence"], start=1):
            with st.container():
                st.markdown(f"#### Evidence {idx}")

                st.markdown(
                    f"""
                    **Sentence:**  
                    {ev['sentence_text']}
                    """
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Source:** `{ev['source']}`")
                    st.markdown(f"**Document ID:** `{ev['document_id']}`")

                with col2:
                    st.markdown(f"**Title:** {ev['title']}")
                    st.markdown(
                        f"**URL:** [Open Source]({ev['url']})"
                    )

                st.divider()

    # ---------------- RAW JSON ----------------
    with st.expander("🔎 View Raw API Response"):
        st.json(result)
