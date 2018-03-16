import subprocess
import threading
import queue
import time
import os

class Engine:

    def __init__(self):

        self.process = subprocess.Popen("octochess-windows-generic-r5190.exe",
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        universal_newlines=True)

        self.reader = StreamReader(self.process.stdout)
        
        self._readline()
        #self._isready()
        self._setuci()
        self._write("setoption name Threads value {}".format(os.cpu_count()))
        self._write("setoption name Hash value 4096")
        self._isready()

    def _write(self, command):
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

    def _readline(self):
        return self.reader.readline()

    def _isready(self):
        self._write("isready")

        while True:
            response = self._readline()
            if response == "readyok\n":
                return True

    def _setuci(self):
        self._write("uci")

        while True:
            response = self._readline()
            if response == "uciok\n":
                return True

    def new_game(self):
        self._write("ucinewgame")

    def set_position(self, moves):
        self._write("position startpos moves " + " ".join(moves))

    def get_best_move(self, depth=""):
        self._write("go "+ str(depth))

        while True:
            response = self._readline()
            if response and response.startswith("bestmove"):
                return response.split()[1]

    def _parse_info_string(self, string):

        splitted = string.split()[1:]
        parsed = {}

        for ind, word in enumerate(splitted):
            if word.isalpha():
                if word == "score":
                    parsed[word] = {}
                elif word == "cp":
                    parsed["score"][word] = int(splitted[ind + 1])
                elif word == "lowerbound" or word == "upperbound":
                    parsed["score"]["bound"] = word
                elif word == "mate":
                    parsed["score"][word] = int(splitted[ind + 1])
                elif word == "pv":
                    parsed[word] = splitted[ind + 1:]
                elif word == "currmove":
                    parsed[word] = splitted[ind + 1]
                else:
                    parsed[word] = int(splitted[ind + 1])
        #print (parsed)
        return parsed

    def start_infinite_search(self):
        self._write("go infinite")

        while True:
            response = self._readline()
            if response:
                if response.startswith("info"):
                    yield self._parse_info_string(response)
                elif response.startswith("bestmove"):
                    # Read and discard
                    self.reader.readline()
                    break
                else:
                    print("Unexpected output from engine.")
            #time.sleep(0.2)
            
    def stop_infinite_search(self):
        self._write("stop")

    def stop_process(self):
        self.process.terminate()

    def print_board(self):
        self._write("d")

        while True:
            response = self._readline()
            print((response.rstrip()))
            if response.startswith("Checkers:"):
                break

class StreamReader:
    """
    A class that reads a stream. This is implemented because of the need
    of a non-blocking stream reader, which does not exist in subprocess
    module and hard to achieve using other Python modules with Windows.
    """

    def __init__(self, stream):

        self._stream = stream
        self._queue = queue.Queue()

        self._thread = threading.Thread(target=self._fill_queue)
        self._thread.daemon = True
        self._thread.start()

    def _fill_queue(self):

        while True:
            line = self._stream.readline()
            if line.strip():
                self._queue.put(line)

    def readline(self, timeout = None):

        try:
            a = self._queue.get(block = timeout is not None, timeout = timeout)
            if a:
                pass
                print(a.strip())
            return a
        except queue.Empty:
            return None


if __name__ == "__main__":
    eng = Engine()
    for i in eng.start_infinite_search():
        print(i)
    #eng._write("position startpos moves e2e4")
    #eng._write("position startpos moves e7e6")
    
    #eng.print_board()
