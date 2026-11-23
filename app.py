import io
import os
import tempfile

import streamlit as st
from basic_pitch.inference import predict

st.title("Audio to MIDI")

uploaded = st.file_uploader("Upload an MP3 or WAV file", type=["mp3", "wav"])

if uploaded is not None:
    st.audio(uploaded)

    if st.button("Convert to MIDI"):
        # basic-pitch needs a file path, so save the upload temporarily
        suffix = os.path.splitext(uploaded.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.getbuffer())
            tmp_path = tmp.name

        try:
            with st.spinner("Converting... this can take a minute."):
                _, midi_data, _ = predict(tmp_path)

            buffer = io.BytesIO()
            midi_data.write(buffer)
            st.session_state["midi_bytes"] = buffer.getvalue()
            st.session_state["midi_name"] = (
                os.path.splitext(uploaded.name)[0] + ".mid"
            )
        except Exception as e:
            st.error(f"Conversion failed: {e}")
        finally:
            os.remove(tmp_path)

# Stored in session_state so the download button survives Streamlit's reruns
if "midi_bytes" in st.session_state:
    st.success("Done!")
    st.download_button(
        label="Download MIDI",
        data=st.session_state["midi_bytes"],
        file_name=st.session_state["midi_name"],
        mime="audio/midi",
    )
