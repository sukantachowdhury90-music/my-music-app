import io
import os
import tempfile
import pathlib

import streamlit as st
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

# Set the page title and icon
st.set_page_config(page_title="My AI Music App", page_icon="🎵")

st.title("Audio to MIDI")
st.write("Upload an audio file to convert it to a clean MIDI file.")

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
                # USE THE ONNX MODEL instead of TensorFlow
                onnx_model_path = pathlib.Path(ICASSP_2022_MODEL_PATH).parent / "nmp.onnx"
                _, midi_data, _ = predict(tmp_path, model_or_model_path=str(onnx_model_path))

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
    st.success("Done! Your MIDI file is ready.")
    st.download_button(
        label="Download MIDI",
        data=st.session_state["midi_bytes"],
        file_name=st.session_state["midi_name"],
        mime="audio/midi",
    )
    )
