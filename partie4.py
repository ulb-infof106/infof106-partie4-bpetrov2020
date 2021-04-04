from sys import argv
from os.path import isfile

from PyQt5.QtWidgets import QApplication

from amazons import Amazons
from mainwindow import MainWindow

def check_file():
    if len(argv) < 2:
        print('Usage: python3 partie3.py <path>')
        return False
    if not isfile(argv[1]):
        print(f'{argv[1]} n\'est pas un chemin valide vers un fichier')
        return False
    return True

def main():
    if len(argv) != 1:
        if not check_file():
            return
        game = Amazons(argv[1])
        game.play()
    else:
        app = QApplication(argv)
        main = MainWindow()
        app.exit(app.exec_())

if __name__ == '__main__':
    import random
    random.seed(0xCAFE)
    main()
