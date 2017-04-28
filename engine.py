import subprocess


class Engine:

    def __init__(self):

        self.process = subprocess.Popen("stockfish_8_x64.exe",
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        universal_newlines=True)
        self._readline()
        self._setuci()

    def _write(self, command):
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

    def _readline(self):
        return self.process.stdout.readline()

    def _isready(self):
        self._write("uci")

        while True:
            response = self._readline()
            if response == "uciok\n":
                return True

    def _setuci(self):
        self._write("isready")

        while True:
            response = self._readline()
            if response == "readyok\n":
                return True
    def _parse_info_string(string):

        splitted = string.split()
        result = {}

        for ind, word in enumerate(splitted[1::2]):
            result[word] = splitted[2*ind + 2]

    def new_game(self):
        self._write("ucinewgame")

    def next_position(self, moves):
        self._write("position startpos moves " + " ".join(moves))

    def get_best_move(self, depth):
        self._write("go "+ str(depth))
        
        while True:
            response = self._readline()
            if response.startswith("bestmove"):
                return response.split()[1]

    def search_best_move(self):
        self._write("position ")

    def stop_searching_best_move(self):
        self._write("stop")
        
    def print_board(self):
        self._write("d")
        
        while True:
            response = self._readline()
            print response.rstrip()
            if response.startswith("Checkers:"):
                break

if __name__ == "__main__":
    eng = Engine()
    print eng._isready()
    eng._write("position startpos moves e2e4")
    eng._write("position startpos moves e7e6")
    eng.print_board()
