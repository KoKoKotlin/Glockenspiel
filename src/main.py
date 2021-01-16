from Glockenspiel import Glockenspiel
from server_handler import MidiServerHandler

import sys
import mido

import RPi.GPIO as GPIO
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file", help="The filepath of a midi file that should be played back.", type=str, nargs="?")
parser.add_argument("-m", "--manuel", help="Start the program in manuel mode.", action="store_true")
parser.add_argument("-s", "--server", help="Start a midi server at port 5051.", action="store_true")
parser.add_argument("-c", "--channel", help="Channel that should be played back [by default -> all channels].", type=int)
parser.add_argument("-o", "--offset", help="Base note offset.", type=int)

def main():
    
    args = parser.parse_args()
    
    if args.manuel:
        gl = Glockenspiel()
        gl.init()
        gl.start_worker()
        gl.manuel_mode()
    elif args.server:
        gl = Glockenspiel(offset=args.offset)
        gl.init()
        gl.start_worker()
        server_handler = MidiServerHandler(gl)
        server_handler.start_server()
    else:
        fileName = args.file
        
        channel = None
        if args.channel:
            channel = args.channel

        offset = None
        if args.offset:
            offset = args.offset

        midi = mido.MidiFile(fileName)
        gl = Glockenspiel(midi, channel, offset)
        gl.init()
        gl.start_worker()
        gl.playSong()
        gl.stop_worker()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
