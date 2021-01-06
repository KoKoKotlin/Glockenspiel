from Glockenspiel import Glockenspiel
import sys
import mido

import RPi.GPIO as GPIO

def main():
    

    if len(sys.argv) == 1:
        gl = Glockenspiel()
        gl.init()
        gl.start_worker()
        gl.manuel_mode()
    else:
        fileName = sys.argv[1]
        
        channel = None
        if len(sys.argv) == 3:
            channel = int(sys.argv[2])

        midi = mido.MidiFile(fileName)
        gl = Glockenspiel(midi, channel)
        gl.init()
        gl.start_worker()
        gl.playSong()
        gl.stop_worker()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    GPIO.cleanup()
