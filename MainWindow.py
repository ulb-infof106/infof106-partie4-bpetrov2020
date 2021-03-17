import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QMessageBox,\
QLineEdit, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout, QFormLayout, QGroupBox,\
QLabel, QComboBox, QSlider, QHBoxLayout, QSizePolicy, QRadioButton, QSpinBox, QGridLayout, QHeaderView, QButtonGroup, QShortcut, QAbstractItemView,\
QFileDialog
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import pyqtSlot, Qt


class LoadConfigFile(QPushButton):

    def __init__(self):
        super().__init__()
        self.setText("Charger un fichier")
        self.filename = None
        self.setFlat(True)
        self.clicked.connect(self.load_file_dialog)

    def load_file_dialog(self):
        self.filename = QFileDialog.getOpenFileName(self,
                                                    "Ouvrir un fichier",
                                                    "/home",
                                                    "Fichier amazones (.amzn)")
        print(self.filename)


class PlayersType(QHBoxLayout):
    """Représente le formulaire de choix des types des joueurs."""

    def __init__(self):
        super().__init__()
        self.addLayout(Player("blanc"))
        self.addLayout(Player("noir"))
        self.insertSpacing(1, 10)


class Player(QFormLayout):
    """Représente le formulaire de choix d'un joueur.

    Args:
        couleur (str): couleur du joueur de ce formulaire
    """

    def __init__(self, couleur):
        super().__init__()
        self.setFormAlignment(Qt.AlignCenter)
        self.player_init()
        self.slider_init()
        self.addRow(f"Joueur {couleur} :", self.players)
        self.addRow("Délais IA :", self.slider)

    def enable_slider(self, ia):
        """Activer et désactiver le slider selon le choix du joueur.
        Le slider n'est actif que si le joueur est une IA.

        Args:
            ia (int): index élément sélectionné -> 1 si IA 0 si humain
        """
        if ia:
            self.slider.setEnabled(True)
        else:
            self.slider.setEnabled(False)

    def player_init(self):
        """Création de la combobox qui choisit le type d'un joueur."""
        self.players = QComboBox()
        self.players.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.players.addItems(["Humain", "Ordinateur"])
        self.players.activated.connect(self.enable_slider)

    def slider_init(self):
        """Création du slider de délais de l'IA. Plus élevé = plus dur."""
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.setRange(1, 10)
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)


class CustomBoard(QVBoxLayout):
    """Initialise la configuration du plateau de jeu."""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.board_init()
        self.top_bar_init()
        self.layout = QHBoxLayout()
        self.addLayout(self.top_bar)
        self.addWidget(self.board)
        self.addWidget(self.reset_button())
        self.spinner.setValue(10)

    def reset_button(self):
        reset_button = QPushButton("Réinitialiser le plateau")
        reset_button.clicked.connect(self.board.clear)
        return reset_button

    def top_bar_button(self, label):
        """Initialise une bouton de la barre d'outils du plateau."""
        button = QPushButton(label)
        button.pressed.connect(self.fill_selection)
        if label == "Flèches":
            button.setToolTip("Appuyez pour remplir la sélection de flèches")
            button.setShortcut(QKeySequence("X"))
        elif label == "Vide":
            button.setToolTip("Appuyez pour supprimer la sélection")
            button.setShortcut(QKeySequence("Del"))
        else:
            button.setToolTip(f"Appuyez pour remplir la "
                              f"sélection de pions {label.lower()}")
            if label == "Blancs":
                button.setShortcut("B")
            else:
                button.setShortcut("N")
        button.setToolTipDuration(5000)
        return button

    def fill_selection(self):
        """Remplit la sélection du plateau du pion choisit."""
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

    def spinner_init(self):
        self.spinner = QSpinBox()
        self.spinner.setRange(1, 26)
        self.spinner.valueChanged.connect(self.change_size)
        self.spinner.setValue(11)
        self.spinner.setToolTip("Taille du plateau de jeu")
        self.spinner.setToolTipDuration(5000)

    def top_bar_init(self):
        self.top_bar = QHBoxLayout()
        self.spinner_init()
        self.top_bar.addWidget(self.spinner)
        self.top_bar.addWidget(self.top_bar_button("Blancs"))
        self.top_bar.addWidget(self.top_bar_button("Noirs"))
        self.top_bar.addWidget(self.top_bar_button("Flèches"))
        self.top_bar.addWidget(self.top_bar_button("Vide"))

    def board_init(self):
        self.board = QTableWidget()
        # self.lettres = [chr(i) for i in range(97, 97+26)]

        self.board.horizontalHeader().setMinimumSectionSize(20)
        self.board.verticalHeader().setMinimumSectionSize(20)
        # self.board.resize(self.board.width(), 800)

        # self.board.setViewportMargins(20, 20, 20, 20)
        self.board.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.board.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.board.horizontalHeader().hide()
        self.board.verticalHeader().hide()
        # print(self.board.viewportSizeHint())


class NewGame(QWidget):

    def __init__(self):
        super().__init__()
        self.title = "Configuration de la partie"
        self.initUI()

    def initUI(self):
        glob = QVBoxLayout()  # layout principal

        glob.addLayout(PlayersType())
        # value = 20
        # players.setContentsMargins(value, value, value, value)

        but = QPushButton("Charger un fichier")
        but.setFlat(True)
        glob.addWidget(but)
        glob.addLayout(CustomBoard())

        # glob.addWidget(QPushButton("Commencer la partie"))

        self.setLayout(glob)
        self.setWindowTitle(self.title)  # titre

        # self.show()  # affiche la fenêtre


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = "Jeu des amazones"
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.widget = QWidget()
        self.buttons = QHBoxLayout()
        self.new = NewGame()

        newgame_button = QPushButton("Nouvelle partie")
        newgame_button.pressed.connect(self.new.show)
        loadgame_button = QPushButton("Charger une partie")

        self.buttons.addWidget(newgame_button)
        self.buttons.addWidget(loadgame_button)
        self.widget.setLayout(self.buttons)

        self.setCentralWidget(self.widget)
        self.setWindowTitle(self.title)

        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
