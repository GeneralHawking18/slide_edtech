import io
from gtts import gTTS
from flask import (
    request, 
)


def read_content(text):
    # text = request.form['text']
    #lang = request.form['lang']
    tts = gTTS(text=text, lang="en")

    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    data = buffer.read()
    return data