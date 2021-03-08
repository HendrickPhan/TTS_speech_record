from sys import byteorder
from array import array
from struct import pack

import tkinter as tk
from tkinter import *
import asyncio

import pyaudio
import wave
from ultilities import *

# UI
currentText = None
statusText = None
phrases = []
# record
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

TEXT_PATH = 'text.txt'

window = tk.Tk()
p = None
stream = None
recording = False
r = None
current_path = 0

def record():
    global r
    if recording:  # Only do this if the Stop button has not been clicked
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)
    # After 1 second, call scanning again (create a recursive loop)
    window.after(1, record)

# recording functions
def start_record():
    global recording
    recording = True

    global statusText
    statusText.set('Status: Recording')
    
    global p
    p = pyaudio.PyAudio()
    global stream
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)
    global r
    r = array('h')
    
def stop_record():
    global recording
    recording = False
    global p
    global stream
    global r

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()
    r = trim(r)
    data = pack('<' + ('h'*len(r)), *r)
    
    wf = wave.open('wavs/' + str(current_path) + '.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()
    stream = None
    p = None

    global statusText
    statusText.set('Status: Waiting')
    
def next_text():
    if(recording):
        stop_record()
    global currentText
    global current_path
    global phrases
    current_path += 1
    if(current_path >= len(phrases)):
        currentText.set('Hết')
    else:
        currentText.set(phrases[current_path])


def init_window():
    global currentText
    global statusText

    current_text_label = tk.Label(text='Current Text')
    current_text_label.pack()
    currentText = StringVar()
    current_text_label['textvariable'] = currentText
    currentText.set(phrases[current_path])

    status_label = tk.Label(text='Status: Waiting')
    status_label.pack()
    statusText = StringVar()
    status_label['textvariable'] = statusText
    statusText.set('Status: Waiting')

    recordButton = tk.Button(
        command = start_record,
        text='RECORD',
    )
    recordButton.pack()

    nextButton = tk.Button(
        text='NEXT',
        command = next_text,
    )
    nextButton.pack()

def main():
    global phrases
    phrases = get_phrases(TEXT_PATH)

    init_window()
    window.after(1, record)
    window.mainloop()

main()