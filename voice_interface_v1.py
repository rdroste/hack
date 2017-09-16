from __future__ import print_function
import sounddevice as sd
import soundfile as sf
import requests
import httplib
import uuid
import json
import os

SAMPLERATE = 16000
NUMCHANNELS = 1
DURATION = 8


class Microsoft_ASR():
    def __init__(self):
        self.sub_key = os.environ['MICROSOFT_VOICE']
        self.token = None
        pass

    def get_speech_token(self):
        FetchTokenURI = "/sts/v1.0/issueToken"
        header = {'Ocp-Apim-Subscription-Key': self.sub_key}
        conn = httplib.HTTPSConnection('api.cognitive.microsoft.com')
        body = ""
        conn.request("POST", FetchTokenURI, body, header)
        response = conn.getresponse()
        str_data = response.read()
        conn.close()
        self.token = str_data
        print("Got Token: ", self.token)
        return True

    def transcribe(self,speech_file):

        # Grab the token if we need it
        if self.token is None:
            print("No Token... Getting one")
            self.get_speech_token()

        endpoint = 'https://speech.platform.bing.com/recognize'
        request_id = uuid.uuid4()
        # Params form Microsoft Example 
        params = {'scenarios': 'ulm',
                  'appid': 'D4D52672-91D7-4C74-8AD8-42B1D98141A5',
                  'locale': 'en-US',
                  'version': '3.0',
                  'format': 'json',
                  'instanceid': '565D69FF-E928-4B7E-87DA-9A750B96D9E3',
                  'requestid': uuid.uuid4(),
                  'device.os': 'linux'}
        content_type = "audio/wav; codec=""audio/pcm""; samplerate=16000"

        def stream_audio_file(speech_file, chunk_size=1024):
            with open(speech_file, 'rb') as f:
                while 1:
                    data = f.read(1024)
                    if not data:
                        break
                    yield data

        headers = {'Authorization': 'Bearer ' + self.token, 
                   'Content-Type': content_type}
        resp = requests.post(endpoint, 
                            params=params, 
                            data=stream_audio_file(speech_file), 
                            headers=headers)
        val = json.loads(resp.text)
        return val["results"][0]["name"], val["results"][0]["confidence"]


def speak_to_YuMi():

    try:
        print("Starting to record...")
        myrecording = sd.rec(DURATION*SAMPLERATE, blocking=True)
        print("Writing to WAV...")
        sf.write('test.wav', myrecording, SAMPLERATE)
    except:
        print("Recording failed :(")
        return

    try:
        text, confidence = ms_asr.transcribe('test.wav')
        print("Text: ", text)
        print("Confidence: ", confidence)
    except:
        print("Transcription failed :(")
        return

    # parse text
    if 'coin' in text:
        print("Doing the coin test...")
    elif 'block' in text:
        print("Doing the block test...")
    elif 'bye' in text:
        print("Waving to the audience...")
    else:
        print("I'm sorry, I didn't quite get that")


if __name__ == "__main__":

    # initialize Microsoft ASR
    ms_asr = Microsoft_ASR()
    ms_asr.get_speech_token()

    sd.default.samplerate = SAMPLERATE
    sd.default.channels = NUMCHANNELS

    # always listening
    while(1):
        # ideally trigger word for this
        print("\nWhat would you like to do?")
        print("[1] - Tell YuMi to do something")
        print("[2] - QUIT")
        print("Enter your choice [1-2]: ", end="")
        choice = int(input())

        if choice == 1:
            speak_to_YuMi()
        elif choice == 2:
            os.remove('test.wav')
            break
        else:
            print("Invalid choice!")



