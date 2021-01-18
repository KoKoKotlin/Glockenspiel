import RPi.GPIO as GPIO

import curses

from time import sleep
import time
from statistics import median

import threading

def find_note_minimum(track, channel):
    if not track: return 0

    return median(
        map(lambda x: x.note, 
            filter(lambda x: not x.is_meta and x.type == "note_on" and (channel == None or channel != None and x.channel == channel), 
            track)
        )
    )

def get_note_offset(track, channel):
    min_note = find_note_minimum(track, channel)
    multiple_of_twelve = int((min_note - 7) / 12)
    
    return multiple_of_twelve * 12 + 7

class Glockenspiel:
    
    # PIN out for differebt tones
    # 1st octave
    G1      = 13
    G1_S    = 6
    A1      = 19
    A1_S    = 3
    B1      = 26
    # 2nd octave
    C2      = 14
    C2_S    = 4
    D2      = 15
    D2_S    = 9
    E2      = 18
    F2      = 23
    F2_S    = 17
    G2      = 24
    G2_S    = 27
    A2      = 25
    A2_S    = 22
    B2      = 8
    # 3rd ocvtave
    C3      = 7
    C3_S    = 10
    D3      = 12
    D3_S    = 5
    E3      = 16
    F3      = 20
    F3_S    = 11
    G3      = 21
    # ------------

    note_array = [
        # 1st octave
        G1, G1_S, A1, A1_S, B1, 
        # 2nd octave
        C2, C2_S, D2, D2_S, E2, F2, F2_S, G2, G2_S, A2, A2_S, B2, 
        # 3rd ocvtave
        C3, C3_S, D3, D3_S, E3, F3, F3_S, G3
    ]
    
    durations = {
        # 1st octave
        G1: 0.04, G1_S: 0.04, A1: 0.04, A1_S: 0.04, B1: 0.04, 
        # 2nd octave
        C2: 0.04, C2_S: 0.04, D2: 0.04, D2_S: 0.04, E2: 0.04, F2: 0.04, F2_S: 0.04, G2: 0.04, G2_S: 0.04, A2: 0.04, A2_S: 0.04, B2: 0.04, 
        # 3rd ocvtave
        C3: 0.04, C3_S: 0.04, D3: 0.04, D3_S: 0.04, E3: 0.04, F3: 0.04, F3_S: 0.04, G3: 0.04
    }

    def __init__(self, midi=None, channel=None, offset=None):
        self.last_note = 0
        self.midi = midi
        self.channel = channel

        self.events = []
        
        if self.midi != None and offset == None:
            self.offset = get_note_offset(self.midi, self.channel)
            self.events = self.midi
        else:
            self.offset = offset

        self.note_queue = []
        self.working = False
        self.song_thread = None

        self.start_time = time.time()
        self.input_time = 0.0

    def init(self):
        # enable gpio pins
        GPIO.setmode(GPIO.BCM)

        for i in range(1, 28):
            GPIO.setup(i, GPIO.OUT)
            sleep(0.02)
            GPIO.output(i, GPIO.HIGH)

    def start_worker(self):
        def work_queue():
            while self.working:
                to_remove = []
                for i, event in enumerate(self.note_queue):
                    event_time, delay, pin = event

                    delta = time.time() - event_time
                    if delta >= delay:
                        GPIO.output(pin, GPIO.HIGH)
                        to_remove.append(i)

                for i in reversed(to_remove):
                    del self.note_queue[i]
        
        self.working = True
        self.song_thread = threading.Thread(target=work_queue)
        self.song_thread.start()

    def stop_worker(self):
        self.working = False

    def playSong(self):
        if not self.working:
            print("Not started yet!")
            return

        self.events = self.midi
        self.play_timed_events()

    def _queue_note(self, note_id):                
        # set pin low immediately
        pin = self.getPinFromNoteId(note_id)
        GPIO.output(pin, GPIO.LOW)
        
        # schedule setting the pin high again
        duration = self.durations[pin]
        self.note_queue.append((time.time(), duration, pin))

    def play_timed_events(self):
        for event in self.events:
            self.input_time += event.time

            playback_time = time.time() - self.start_time
            duration_to_next_event = self.input_time - playback_time

            if duration_to_next_event > 0.0:
                time.sleep(duration_to_next_event)

            if not event.is_meta:
                if event.type == "note_on":
                    if self.channel == None or \
                       self.channel != None and event.channel == self.channel:
                        _queue_note(event.note)

    def getPinFromNoteId(self, note_id):
        pin = note_id - self.offset

        while pin < 0:
            pin += 12
        
        while pin >= 25:
            pin -= 12

        return self.note_array[pin]

