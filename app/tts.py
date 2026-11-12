"""Text-to-speech with Google's Gemini API: listening episodes and "hear it" pronunciation."""
import base64
import hashlib
import io
import os
import wave

from google import genai
from google.genai import errors

import sys

from . import db, usage
from .ai import AIError

VOICES = ["Kore", "Puck", "Aoede", "Charon", "Leda", "Orus", "Zephyr", "Fenrir", "Callirrhoe", "Iapetus",
          "Despina", "Algieba", "Erinome", "Achird", "Sulafat", "Gacrux"]
TURNS_PER_REQUEST = 12  # long episodes are voiced in chunks and joined


def _client():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise AIError("No Google Gemini API key yet. Add one under Settings to use audio features.")
    return genai.Client(api_key=key)


def _call(client, model, content, speech_config):
    try:
        usage.log_gemini(sys._getframe(1).f_code.co_name, model)
    except Exception:
        pass
    try:
        resp = client.interactions.create(
            model=model,
            input=[{"type": "user_input", "content": content}],
            response_format={"type": "audio"},
            generation_config={"speech_config": speech_config},
        )
    except errors.ClientError as e:
        if getattr(e, "code", None) in (401, 403):
            raise AIError("Gemini rejected the API key. Check it under Settings.")
        if getattr(e, "code", None) == 429:
            raise AIError("Gemini rate limit reached. Wait a minute and try again.")
        raise AIError(f"Gemini rejected the request: {getattr(e, 'message', e)}")
    except errors.APIError as e:
        raise AIError(f"Gemini error: {getattr(e, 'message', e)}")
    except Exception as e:  # network problems etc.
        raise AIError(f"Couldn't reach Gemini: {e}")
    data = resp.output_audio.data
    if isinstance(data, str):
        data = base64.b64decode(data)
    elif not data.startswith(b"RIFF"):
        try:
            data = base64.b64decode(data, validate=True)
        except ValueError:
            pass
    return data


def _pcm(data):
    """Returns (params, frames) from WAV bytes, or treats headerless audio as 24 kHz mono 16-bit PCM."""
    if data.startswith(b"RIFF"):
        with wave.open(io.BytesIO(data)) as w:
            return (w.getnchannels(), w.getsampwidth(), w.getframerate()), w.readframes(w.getnframes())
    return (1, 2, 24000), data


def _wav(params, frames):
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(params[0])
        w.setsampwidth(params[1])
        w.setframerate(params[2])
        w.writeframes(frames)
    return out.getvalue(), len(frames) / (params[0] * params[1] * params[2])


def synthesize(turns, speakers):
    """turns: [{speaker, text, style}]; speakers: {name: voice}. Returns (wav_bytes, seconds)."""
    client = _client()
    model = db.get_settings()["tts_model"]
    if len(speakers) == 1:
        speech_config = [{"voice": next(iter(speakers.values()))}]
    else:
        speech_config = {"speakers": [{"speaker": n, "voice": v} for n, v in speakers.items()]}
    params, frames = None, []
    for i in range(0, len(turns), TURNS_PER_REQUEST):
        content = []
        for t in turns[i:i + TURNS_PER_REQUEST]:
            meta = {"type": "speech_metadata", "speaker": t["speaker"]} if len(speakers) > 1 else {"type": "speech_metadata"}
            if t.get("style"):
                meta["style"] = t["style"]
            content.append({"type": "text", "text": t["text"], "annotations": [meta]})
        p, f = _pcm(_call(client, model, content, speech_config))
        params = params or p
        frames.append(f)
        frames.append(b"\x00" * (params[1] * params[0] * params[2] // 2))  # half a second between chunks
    return _wav(params, b"".join(frames))


def speak(text):
    """Short clip of one voice reading text slowly and clearly. Cached so replaying is free."""
    s = db.get_settings()
    key = hashlib.sha1(f"{s['tts_model']}|{s['voice_a']}|{text}".encode()).hexdigest()
    path = db.MEDIA / "cache" / f"{key}.wav"
    if path.exists():
        return path
    content = [{"type": "text", "text": text,
                "annotations": [{"type": "speech_metadata", "style": "clear, slow and natural, like a German teacher"}]}]
    params, frames = _pcm(_call(_client(), s["tts_model"], content, [{"voice": s["voice_a"]}]))
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(_wav(params, frames)[0])
    return path
