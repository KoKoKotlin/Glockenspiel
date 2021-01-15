from pymidi import server

import threading

class MidiServerHandler(server.Handler):

    def __init__(self, glockenspiel):
        self.msgs = []
        self.server_thread = None
        self.glockenspiel = glockenspiel

        self.serving = False

    def start_server(self):

        def task():
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
        self.glockenspiel.events += command_list

    def debug_print(self, msg):
        print(f"[SERVER] {msg}")