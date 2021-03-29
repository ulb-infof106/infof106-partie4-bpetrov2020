from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QComboBox,
    QSlider,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QSizePolicy,
    QAbstractItemView,
    QHeaderView
    )
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QColor, QBrush

from amazons import Amazons
from const import *
from players import *
import copy


class NewGame(QDialog):
    """Fenêtre de configuration d'une nouvelle partie.
    """

    def __init__(self):
        super().__init__()

        self.resize(565, 796)
        self.setWindowTitle("Configuration de la partie")
        # self.setStyleSheet("QTableWidget::item::selected{border:2px solid blue}")
        self.layout = QVBoxLayout()

        self.players = PlayersType()
        self.layout.addLayout(self.players)
        self.board = CustomBoard()
        self.layout.addLayout(self.board)

        beg_game_button = QPushButton("Commencer la partie")
        beg_game_button.clicked.connect(self.begin_func)
        self.layout.addWidget(beg_game_button)

        self.setLayout(self.layout)
        # self.exec_()

    def begin_func(self):
        self.board.to_amazon()
        # self.board.amazons.
        print(self.players.white.type_.currentText())
        if self.players.white.type_.currentText() == "Humain":
            player1 = (HumanPlayer(self.board.amazons.board, PLAYER_1))
        else:
            player1 = (AIPlayer(self.board.amazons.board, PLAYER_1))

        if self.players.black.type_.currentText() == "Humain":
            player2 = (HumanPlayer(self.board.amazons.board, PLAYER_2))
        else:
            player2 = (AIPlayer(self.board.amazons.board, PLAYER_2))

        self.board.amazons.players = (player1, player2)
        self.game = self.board.amazons
        self.close()


class PlayersType(QHBoxLayout):
    """Représente le formulaire de choix des types des joueurs."""

    def __init__(self):
        super().__init__()

        self.white = Player("blanc")
        self.addLayout(self.white)
        self.black = Player("noir")
        self.addLayout(self.black)
        self.insertSpacing(1, 8)


class Player(QFormLayout):
    """Représente le formulaire de choix d'un joueur.

    Args:
        couleur (str): couleur du joueur de ce formulaire
    """

    def __init__(self, couleur):
        super().__init__()

        self.setFormAlignment(Qt.AlignCenter)

        self.addRow(f"Joueur {couleur} :", self.type_())
        self.addRow("Délais IA :", self.slider())

    def enable_slider(self, ia):
        """Activer et désactiver le slider selon le choix du joueur.
        Le slider n'est actif que si le joueur est une IA.

        Args:
            ia (int): index élément sélectionné -> 1 si IA 0 si humain
        """
        if ia:
            self.slider.setEnabled(True)  # slider est en deuxième pos
        else:
            self.slider.setEnabled(False)

    def type_(self):
        """Création de la combobox qui choisit le type d'un joueur."""
        self.type_ = QComboBox()
        self.type_.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.type_.addItems(["Humain", "Ordinateur"])
        self.type_.activated.connect(self.enable_slider)
        return self.type_

    def slider(self):
        """Création du slider de délais de l'IA. Plus élevé = plus dur."""
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.setTickPosition(QSlider.TicksBelow)

        self.slider.setRange(1, 10)
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(1)
        return self.slider


class CustomBoard(QVBoxLayout):
    """Initialise la configuration du plateau de jeu."""

    def __init__(self):
        super().__init__()

        self.amazons = Amazons(10, [], [], [])

        self.addLayout(self.top_buttons())
        self.board = BoardUI()
        self.addWidget(self.board)
        self.addLayout(self.bottom_buttons())

    def to_amazon(self, file_=None):
        # TODO
        if file_ is not None:
            self.amazons.read_new_file(file_)
        else:
            pos_arrows = []
            pos_black = []
            pos_white = []
            size = self.spinner.value()
            letters = "abcdefghijklmnopqrstuvwxyz"
            for j in range(size):
                for i in range(size):
                    cell = self.board.cellWidget(i, j)
                    # print(self.board.itemAt(i, j))
                    # print(cell)
                    if cell is not None:
                        # print(cell.type_)
                        if cell.type_ == 0:
                            pos_white.append(f'{letters[j]}{-(i-size)}')
                        elif cell.type_ == 1:
                            pos_black.append(f'{letters[j]}{-(i-size)}')
                        elif cell.type_ == 2:
                            pos_arrows.append(f'{letters[j]}{-(i-size)}')

            print(pos_arrows, pos_white, pos_black)
            self.amazons.from_config(size,
                                     pos_black,
                                     pos_white,
                                     pos_arrows)
        
        pass

    def from_amazon(self):
        # TODO
        self.board.clear()

        size = self.amazons.board.N
        self.spinner.setValue(size)

        # chars = [WHITE, BLACK, CHARS[3]]
        chars = self.board.tokens
        pions = self.amazons.board.queens
        pions.append(self.amazons.board.arrows[0])
        size
        for positions, char in zip(pions, chars):
            for pos in positions:
                # print(pos)
                # print(pos.x, pos.y, colors[n])
                fill = QTableWidgetItem(char)
                fill.setTextAlignment(Qt.AlignCenter)
                self.board.setItem(-(pos.y-size+1), pos.x, fill)
        pass

    def load_file(self):
        filename = QFileDialog.getOpenFileName(None,
                                               "Ouvrir un fichier",
                                               "",
                                               "Fichier amazones (.txt)")
        # print(self.board.itemAt(0,0).text())
        # self.to_amazon(filename[0])
        self.to_amazon(filename[0])
        self.from_amazon()
        # size, pos_black, pos_white, pos_arrows = read_file(filename[0])

        # self.spinner.setValue(size)
        # print(pos_black, pos_white, pos_arrows)

    def load_file_button(self):
        button = QPushButton("Charger un fichier")
        button.clicked.connect(self.load_file)
        return button

    def reset_button(self):
        button = QPushButton("Réinitialiser le plateau")
        button.clicked.connect(self.board.clear)
        return button

    def bottom_buttons(self):
        buttons = QHBoxLayout()
        buttons.addWidget(self.reset_button())
        buttons.addWidget(self.load_file_button())
        return buttons

    def fill_selection(self):
        """Remplit la sélection du plateau du pion choisit."""
        token = None
        # tokens = ('\u25CB', '\u25CF', "✕")
        tokens = self.board.tokens
        for i in range(1, 4):
            if self.top_bar.itemAt(i).widget().isDown():
                token = tokens[i-1]
                break
        selection = self.board.selectedIndexes()
        for i in selection:
            # fill = QTableWidgetItem(token)
            # fill.setTextAlignment(Qt.AlignCenter)
            # self.board.setItem(i.row(), i.column(), fill)
            self.board.setCellWidget(i.row(), i.column(), copy.copy(token))

    def change_board_size(self, new_size):
        """Change la taille du plateau selon la valeur du spinner."""
        self.board.setRowCount(new_size)
        self.board.setColumnCount(new_size)
        self.board.size_changed(new_size)

        # change également la hauteur des cellules pour qu'elles soient carrées
        width = self.board.horizontalHeader().sectionSize(0)
        self.board.verticalHeader().setDefaultSectionSize(width)

    def size_spinner(self):
        self.spinner = QSpinBox()
        self.spinner.setRange(1, 26)
        self.spinner.valueChanged.connect(self.change_board_size)
        self.spinner.setToolTip("Taille du plateau de jeu")
        self.spinner.setToolTipDuration(5000)
        return self.spinner

    def config_button(self, label):
        """Initialise un bouton de la barre d'outils supérieure du plateau."""
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

    def top_buttons(self):
        """Crée les bouttons au-dessus du plateau."""
        self.top_bar = QHBoxLayout()
        self.top_bar.addWidget(self.size_spinner())
        self.top_bar.addWidget(self.config_button("Blancs"))
        self.top_bar.addWidget(self.config_button("Noirs"))
        self.top_bar.addWidget(self.config_button("Flèches"))
        self.top_bar.addWidget(self.config_button("Vide"))
        return self.top_bar

    def board_widget(self):
        """Crée le plateau de jeu configurable."""
        self.board = QTableWidget(3, 3)
        self.board.horizontalHeader().hide()
        self.board.verticalHeader().hide()

        self.board.horizontalHeader().setMinimumSectionSize(20)
        self.board.verticalHeader().setMinimumSectionSize(20)

        item = QTableWidgetItem()
        # icon = QIcon("ocean3.0@1x.png")
        resource = "crown_white.svg"
        icon = QWidget()
        label = QLabel()
        label.setScaledContents(True)
        label.setPixmap(QPixmap(resource))
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignCenter)
        margin = 6
        layout.setContentsMargins(margin, margin, margin, margin)
        icon.setLayout(layout)
        color = QColor('#6d5e3c')
        
#     int row = 0;
# int column = 0;
# QSize sizeIcon(32, 32);
# QString iconSrc = ":/Actions/myicon.png";
# 
# QWidget *pWidget = new QWidget();
# QLabel *label = new QLabel;
# label->setMaximumSize(sizeIcon);
# label->setScaledContents(true);
# label->setPixmap(QPixmap(iconSrc));
# QHBoxLayout *pLayout = new QHBoxLayout(pWidget);
# pLayout->addWidget(label);
# pLayout->setAlignment(Qt::AlignCenter);
# pLayout->setContentsMargins(0,0,0,0);
# pWidget->setLayout(pLayout);
# 
# this->ui->myTableWidget->setCellWidget(row, column, pWidget);
#     
#     
#     
        # item.setData(Qt.DecorationRole, QPixmap("crown.svg"))
        item = QTableWidgetItem()
        item.setBackground(QBrush(color))
        self.board.setItem(0,0,item)
        self.board.setCellWidget(0, 0, icon)
        self.board.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.board.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return self.board

class BoardUI(QTableWidget):
    """Représente l'interface graphique d'un plateau de jeu.
    """

    def __init__(self):
        super().__init__(10, 10)
        self.size = 10
        # self.setStyleSheet("QTableWidget.item{ selection-background-color: red}")
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        self.horizontalHeader().setMinimumSectionSize(20)
        self.verticalHeader().setMinimumSectionSize(20)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.tokens = []
        self.tokens.append(Token("crown_white.svg", 0))
        self.tokens.append(Token("crown_black.svg", 1))
        self.tokens.append(Token("arrow.svg", 2))

        self.board_colors = []
        self.board_colors.append(QBrush(QColor("#463c26")))
        self.board_colors.append(QBrush(QColor("#d2cba8")))

        self.size_changed()

    def size_changed(self, new_size=10):
        self.size = new_size
        for i in range(self.size):
            for j in range(self.size):
                back = QTableWidgetItem()
                back.setBackground(self.board_colors[(i+j)%2])
                self.setItem(i, j, back)


class Token(QWidget):

    def __init__(self, image, type_):
        super().__init__()
        self.image_file = image
        self.type_ = type_

        label = QLabel()
        label.setScaledContents(True)
        label.setPixmap(QPixmap(self.image_file))

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignCenter)
        self.margin = 6
        layout.setContentsMargins(self.margin, self.margin, self.margin, self.margin)

        self.setLayout(layout)

    def __copy__(self):
        res = Token(self.image_file, self.type_)
        return res
