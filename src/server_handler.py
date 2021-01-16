from pymidi import server
from pprint import pprint

import threading

class MidiServerHandler(server.Handler):
    NOTE_ON = 144
    
    def __init__(self, glockenspiel):
        self.msgs = []
        self.server_thread = None
        self.glockenspiel = glockenspiel

        self.serving = False

    def start_server(self):

        def task():
            self.glockenspiel.init()
            s = server.Server([("0.0.0.0", 5051)])
            s.add_handler(self)
            s.serve_forever()
        
        self.serving = True
        self.server_thread = threading.Thread(target=task)
        self.server_thread.start()

    def on_peer_connected(self, peer):
        self.debug_print(f"Peer connected {peer}!")
    
    def on_peer_disconnected(self, peer):
        self.debug_print(f"Peer disconnected {peer}!")

    def on_midi_commands(self, peer, command_list):
        for command in command_list:
            if int(command.command) == self.NOTE_ON:
                if self.glockenspiel.channel == None or self.glockenspiel.channel == command.channel:
                    self.glockenspiel._queue_note(int(command.params.key))

    def debug_print(self, msg):
        pprint(f"[SERVER] {msg}")