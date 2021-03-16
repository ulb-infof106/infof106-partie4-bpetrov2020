import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QMessageBox,\
QLineEdit, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout, QFormLayout, QGroupBox,\
QLabel, QComboBox, QSlider, QHBoxLayout, QSizePolicy, QRadioButton, QSpinBox, QGridLayout, QHeaderView, QButtonGroup
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt


class Player(QFormLayout):
    """"""

    def enable_slider(self, ia):
        """Activer et désactiver le slider selon le choix du joueur."""
        if ia:
            self.slider.setEnabled(True)
        else:
            self.slider.setEnabled(False)

    def __init__(self, couleur):
        super().__init__()
        self.setFormAlignment(Qt.AlignCenter)
        self.width = 200
        self.player_init()
        self.slider_init()
        self.addRow(f"Joueur {couleur} :", self.players)
        self.addRow(f"Délais IA :", self.slider)

    # création de la combobox
    def player_init(self):
        self.players = QComboBox()
        # self.players.setMinimumWidth(self.width)
        self.players.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.players.addItems(["Humain", "Ordinateur"])
        self.players.activated.connect(self.enable_slider)

    # création du slider
    def slider_init(self):
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.setRange(1, 10)
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(1)
        # self.slider.setMaximumWidth(self.width)
        self.slider.setTickPosition(QSlider.TicksBelow)


class CustomBoard(QVBoxLayout):
    """"""

    def __init__(self):
        super().__init__()
        self.board_init()
        self.top_bar_init()
        self.layout = QHBoxLayout()
        self.addLayout(self.top_bar)
        self.addWidget(self.board)
        print(type(self.top_bar))

    def top_bar_button(self, label):
        button = QPushButton(label)
        button.pressed.connect(self.fill_selection)
        if label == "Flèches":
            button.setToolTip("Appuyez pour remplir la sélection de flèches")
        else:
            button.setToolTip(f"Appuyez pour remplir la "
                              f"sélection de pions {label.lower()}")
        button.setToolTipDuration(5000)
        return button

    def fill_selection(self):
        token = None
        tokens = ('\u25CB', '\u25CF', "✕")
        for i in range(1, 4):
            if self.top_bar.itemAt(i).widget().isDown():
                token = tokens[i-1]
                break
        selection = self.board.selectedIndexes()
        for i in selection:
            fill = QTableWidgetItem(token)
            fill.setTextAlignment(Qt.AlignCenter)
            self.board.setItem(i.row(), i.column(), fill)

    def change_size(self, new_size):
        self.board.setRowCount(new_size)
        self.board.setColumnCount(new_size)
        width = self.board.horizontalHeader().sectionSize(0)
        self.board.verticalHeader().setDefaultSectionSize(width)

    def spinner(self):
        spinner = QSpinBox()
        spinner.setRange(1, 26)
        spinner.valueChanged.connect(self.change_size)
        spinner.setValue(10)
        spinner.setToolTip("Taille du plateau de jeu")
        spinner.setToolTipDuration(5000)
        return spinner

    def top_bar_init(self):
        self.top_bar = QHBoxLayout()
        self.top_bar.addWidget(self.spinner())
        self.top_bar.addWidget(self.top_bar_button("Blancs"))
        self.top_bar.addWidget(self.top_bar_button("Noirs"))
        self.top_bar.addWidget(self.top_bar_button("Flèches"))

    def board_init(self):
        self.board = QTableWidget(10, 10)
        # self.lettres = [chr(i) for i in range(97, 97+26)]

        self.board.horizontalHeader().setMinimumSectionSize(20)
        self.board.verticalHeader().setMinimumSectionSize(20)

        # self.board.setViewportMargins(20, 20, 20, 20)
        self.board.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.board.horizontalHeader().hide()
        self.board.verticalHeader().hide()
        # print(self.board.viewportSizeHint())

class NewGame(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = "Configuration de la partie"
        self.initUI()

    def enable_slider_w(self, ia):
        """Active et désactive le slider du joueur blanc."""
        if ia:
            self.white_slid.setEnabled(True)
        else:
            self.white_slid.setEnabled(False)

    def enable_slider_b(self, ia):
        """Active et désactive le slider du joueur noir."""
        if ia:
            self.black_slid.setEnabled(True)
        else:
            self.black_slid.setEnabled(False)

    def initUI(self):
        widget = QWidget()  # widget principal
        glob = QVBoxLayout()  # layout principal

        players = QHBoxLayout()
        value = 20
        # players.setContentsMargins(value, value, value, value)
        white = Player('blanc')
        black = Player('noir')
        players.addLayout(white)
        players.addLayout(black)
        
   #    # joueur blanc
   #    white = QFormLayout()
   #    white.setFormAlignment(Qt.AlignCenter)
   #    white_chose = self.players
   #    white_chose.activated.connect(self.enable_slider_w)
   #    white.addRow("Joueur blanc :", white_chose)
   #    self.white_slid = self.slider
   #    white.addRow("Délais IA :", self.white_slid)
   #    
   # #  white_chose = self.players
   # #  white_chose.activated.connect(self.enable_slider_w)
   # #  form.addRow("Joueur blanc :", white_chose)
   # #  self.white_slid = self.slider
   # #  form.addRow("Délais IA :", self.white_slid)

   #    # joueur noir
   #    black = QFormLayout()
   #    black.setFormAlignment(Qt.AlignCenter)
   #    black_chose = self.players
   #    black_chose.activated.connect(self.enable_slider_b)
   #    black.addRow("Joueur noir :", black_chose)
   #    self.black_slid = self.slider
   #    black.addRow("Délais IA :", self.black_slid)
   #    
   #    colors.addLayout(white)
   #    colors.addLayout(black)
        glob.addLayout(players)

     #  black_chose = self.players
     #  black_chose.activated.connect(self.enable_slider_b)
     #  form.addRow("Joueur noir :", black_chose)
     #  self.black_slid = self.slider
     #  form.addRow("Délais IA :", self.black_slid)

        # création de plateau
        # buttons = QHBoxLayout()
        # spinner = QSpinBox()
        # spinner.setRange(2, 26)
        # buttons_group = [spinner, QPushButton("Blanc"), QPushButton("Noir"), QPushButton("Flèches")]
        # for i in buttons_group:
        #     buttons.addWidget(i)
        # glob.addLayout(buttons)
        glob.addLayout(CustomBoard())

        widget.setLayout(glob)
        self.setCentralWidget(widget)
        self.setWindowTitle(self.title)  # titre
        self.setCentralWidget

        glob.addWidget(QPushButton("Commencer la partie"))

        self.show()  # affiche la fenêtre


def MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = "Jeu des amazones"
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.widget = QWidget()
        self.buttons = QHBoxLayout()

        newgame_button = QPushButton("Nouvelle partie")
        loadgame_button = QPushButton("Charger une partie")

        self.buttons.addItems([newgame_button, loadgame_button])

        self.setCentralWidget(self.widget)
        self.setWindowTitle(self.title)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = NewGame()
    sys.exit(app.exec_())
