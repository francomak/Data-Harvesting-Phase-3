#!/usr/bin/env python3

import wave
import sys
import json

from vosk import Model, KaldiRecognizer, SetLogLevel


def print_if_full_result(jsontext):
    jsondict = json.loads(jsontext)
    if "text" in jsondict:
        print(jsondict['text'])

# You can set log level to -1 to disable debug messages
SetLogLevel(0)

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <model> <wave file>", file=sys.stderr)
    sys.exit(1)

wf = wave.open(sys.argv[2], "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    print("Audio file must be WAV format mono PCM.")
    sys.exit(1)

model = Model(sys.argv[1])

# You can also init model by name or with a folder path
# model = Model(model_name="vosk-model-en-us-0.21")
# model = Model("models/en")

rec = KaldiRecognizer(model, wf.getframerate())
#rec.SetWords(True)
#rec.SetPartialWords(True)

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        jsontext = rec.Result()
        print_if_full_result(jsontext)

jsontext = rec.FinalResult()
print_if_full_result(jsontext)

