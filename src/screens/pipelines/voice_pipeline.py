import librosa
import numpy as np
import io
import streamlit as st

# Safe top-level import for resemblyzer
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    RESEMBLYER_AVAILABLE = True
except Exception:
    RESEMBLYER_AVAILABLE = False
    VoiceEncoder = None
    preprocess_wav = None


@st.cache_resource
def load_voice_encoder():
    if not RESEMBLYER_AVAILABLE or VoiceEncoder is None:
        st.warning("Voice recognition is unavailable: resemblyzer module not loaded.")
        return None
    try:
        return VoiceEncoder()
    except Exception as e:
        st.warning(f"Voice recognition initialization error: {e}")
        return None


def get_voice_embedding(audio_bytes):
    try:
        if not audio_bytes:
            return None

        encoder = load_voice_encoder()
        if encoder is None or preprocess_wav is None:
            return None

        # Load audio into numpy array at 16kHz
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        if len(audio) == 0:
            st.error("Audio recording is empty.")
            return None

        wav = preprocess_wav(audio, source_sr=sr)
        if len(wav) == 0:
            st.error("Could not process audio wave.")
            return None

        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()
    except Exception as e:
        st.error(f"Voice recognition error: {e}")
        return None


def identify_speaker(new_embedding, candidates_dict, threshold=0.65):
    if new_embedding is None or not candidates_dict:
        return None, 0.0
    
    best_sid = None
    best_score = -1.0

    new_emb_arr = np.array(new_embedding)
    norm_new = np.linalg.norm(new_emb_arr)
    if norm_new == 0:
        return None, 0.0

    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding:
            stored_emb_arr = np.array(stored_embedding)
            norm_stored = np.linalg.norm(stored_emb_arr)
            if norm_stored > 0:
                similarity = float(np.dot(new_emb_arr, stored_emb_arr) / (norm_new * norm_stored))
                if similarity > best_score:
                    best_score = similarity
                    best_sid = sid

    if best_score >= threshold:
        return best_sid, best_score
    
    return None, max(best_score, 0.0)


def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.65):
    try:
        if not audio_bytes:
            return {}

        encoder = load_voice_encoder()
        if encoder is None or preprocess_wav is None:
            return {}

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        if len(audio) == 0:
            return {}

        # Split audio into voice segments
        segments = librosa.effects.split(audio, top_db=30)
        
        # If no silence-split segments detected (e.g. background noise or continuous speech), fall back to whole audio
        if len(segments) == 0:
            segments = np.array([[0, len(audio)]])

        identified_results = {}

        for start, end in segments:
            if (end - start) < int(sr * 0.1):  # Ignore tiny clips under 0.1s
                continue
            
            segment_audio = audio[start:end]
            try:
                wav = preprocess_wav(segment_audio, source_sr=sr)
                if len(wav) == 0:
                    continue
                embedding = encoder.embed_utterance(wav)

                sid, score = identify_speaker(embedding, candidates_dict, threshold)

                if sid:
                    if sid not in identified_results or score > identified_results[sid]:
                        identified_results[sid] = score
            except Exception:
                continue

        return identified_results
    except Exception as e:
        st.error(f"Bulk voice processing error: {e}")
        return {}



    
