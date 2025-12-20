# import streamlit as st
# import requests

# # ---------------- CONFIG ----------------
# API_URL = "http://127.0.0.1:8000/api/verify"

# st.set_page_config(
#     page_title="Claim Verification System",
#     layout="centered"
# )

# # ---------------- LABEL NORMALIZATION ----------------
# LABEL_MAP = {
#     "SUPPORTS": "Supported",
#     "REFUTES": "Refuted",
#     "NOT_ENOUGH_INFO": "Not Enough Information"
# }

# # ---------------- HEADER ----------------
# st.title("🧠 Claim Verification System")
# st.caption(
#     "Fact-checking using multi-source evidence retrieval and DeBERTa-based NLI"
# )

# st.write(
#     "Enter a factual claim below. The system retrieves evidence from trusted sources "
#     "and classifies the claim as **Supported**, **Refuted**, or **Not Enough Information**."
# )

# # ---------------- INPUT ----------------
# claim = st.text_area(
#     "📝 Enter Claim",
#     placeholder="Example: Smoking reduces the risk of lung cancer.",
#     height=120
# )

# verify_btn = st.button("🔍 Verify Claim")

# # ---------------- API CALL ----------------
# if verify_btn:
#     if not claim.strip():
#         st.warning("⚠️ Please enter a claim before verifying.")
#         st.stop()

#     with st.spinner("Running verification pipeline (retrieval → ranking → NLI)..."):
#         try:
#             response = requests.post(
#                 API_URL,
#                 json={"claim": claim},
#                 timeout=300
#             )

#             if response.status_code != 200:
#                 st.error(f"❌ Backend error: {response.status_code}")
#                 st.stop()

#             result = response.json()

#         except requests.exceptions.RequestException as e:
#             st.error(f"❌ Failed to connect to backend: {e}")
#             st.stop()

#     # ---------------- RESULT HEADER ----------------
#     st.success("✅ Verification completed")

#     raw_label = result.get("label", "")
#     label = LABEL_MAP.get(raw_label, raw_label)
#     confidence = result.get("confidence", 0.0)

#     # ---------------- LABEL STYLING ----------------
#     if label == "Supported":
#         st.markdown("### 🟢 **SUPPORTED**")
#     elif label == "Refuted":
#         st.markdown("### 🔴 **REFUTED**")
#     else:
#         st.markdown("### 🟡 **NOT ENOUGH INFORMATION**")

#     # ---------------- CONFIDENCE ----------------
#     st.write("**Confidence Score**")
#     st.progress(min(float(confidence), 1.0))
#     st.caption(f"{confidence:.4f}")

#     st.divider()

#     # ---------------- EVIDENCE ----------------
#     st.subheader("📄 Top Evidence")

#     if not result.get("evidence"):
#         st.info("No evidence sentences were returned.")
#     else:
#         for idx, ev in enumerate(result["evidence"], start=1):
#             with st.container():
#                 st.markdown(f"### 📄 Evidence {idx}")

#                 st.markdown(
#                     f"""
#                     > *{ev['sentence_text']}*
#                     """
#                 )

#                 st.markdown(
#                     f"""
#                     **Title:** {ev['title']}  
#                     🔗 [Read Source]({ev['url']})
#                     """
#                 )

#                 st.divider()
import streamlit as st
import requests

# ---------------- CONFIG ----------------
VERIFY_API_URL = "http://127.0.0.1:8000/api/verify"
CHAT_API_URL = "http://127.0.0.1:8000/api/chat"

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

# ---------------- SESSION STATE INIT ----------------
if "verified" not in st.session_state:
    st.session_state.verified = False
if "result" not in st.session_state:
    st.session_state.result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- HEADER ----------------
st.title("Claim Verification System")
st.caption(
    "Fact-checking using multi-source evidence retrieval and DeBERTa-based NLI"
)

st.write(
    "Enter a factual claim below. The system retrieves evidence from trusted sources "
    "and classifies the claim as Supported, Refuted, or Not Enough Information."
)

# ---------------- INPUT ----------------
claim = st.text_area(
    "Enter Claim",
    placeholder="Example: Smoking reduces the risk of lung cancer.",
    height=120
)

verify_btn = st.button("Verify Claim")

# ---------------- VERIFY API CALL ----------------
if verify_btn:
    if not claim.strip():
        st.warning("Please enter a claim before verifying.")
        st.stop()

    st.session_state.verified = False
    st.session_state.chat_history = []

    with st.spinner("Running verification pipeline..."):
        try:
            response = requests.post(
                VERIFY_API_URL,
                json={"claim": claim},
                timeout=300
            )

            if response.status_code != 200:
                st.error(f"Backend error: {response.status_code}")
                st.stop()

            result = response.json()
            st.session_state.result = result
            st.session_state.verified = True

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to backend: {e}")
            st.stop()

# ---------------- SHOW VERIFICATION RESULT ----------------
if st.session_state.verified and st.session_state.result:
    result = st.session_state.result

    st.success("Verification completed")

    raw_label = result.get("label", "")
    label = LABEL_MAP.get(raw_label, raw_label)
    confidence = result.get("confidence", 0.0)

    if label == "Supported":
        st.markdown("### SUPPORTED")
    elif label == "Refuted":
        st.markdown("### REFUTED")
    else:
        st.markdown("### NOT ENOUGH INFORMATION")

    st.write("Confidence Score")
    st.progress(min(float(confidence), 1.0))
    st.caption(f"{confidence:.4f}")

    st.divider()

    st.subheader("Top Evidence")

    if not result.get("evidence"):
        st.info("No evidence sentences were returned.")
    else:
        for idx, ev in enumerate(result["evidence"], start=1):
            with st.container():
                st.markdown(f"Evidence {idx}")
                st.markdown(f"> {ev['sentence_text']}")
                st.markdown(
                    f"Title: {ev['title']}  \n"
                    f"Source: {ev['source']}  \n"
                    f"[Open Link]({ev['url']})"
                )
                st.divider()

# ---------------- CHAT SECTION ----------------
st.divider()
st.subheader("Explainability Chat")

if not st.session_state.verified:
    st.info("Verify a claim first to enable the chat.")
else:
    user_question = st.text_input(
        "Ask a question about the evidence or decision",
        placeholder="Why was this claim supported?"
    )

    ask_btn = st.button("Ask")

    if ask_btn and user_question.strip():
        with st.spinner("Retrieving explanation..."):
            try:
                chat_payload = {
                    "query_id": st.session_state.result["query_id"],
                    "question": user_question,
                    "label": st.session_state.result["label"],
                    "confidence": st.session_state.result["confidence"]
                }

                chat_response = requests.post(
                    CHAT_API_URL,
                    json=chat_payload,
                    timeout=300
                )

                if chat_response.status_code != 200:
                    st.error("Chat backend error")
                else:
                    answer = chat_response.json().get("answer", "")
                    st.session_state.chat_history.append(
                        (user_question, answer)
                    )

            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to chat backend: {e}")

    # ---------------- CHAT HISTORY ----------------
    if st.session_state.chat_history:
        st.markdown("### Conversation")
        for q, a in st.session_state.chat_history:
            st.markdown(f"User: {q}")
            st.markdown(f"Assistant: {a}")
            st.divider()
