import sys
from email.utils import collapse_rfc2231_value
from typing import final

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QTabWidget, QWidget, QLabel, QSlider, QRadioButton, QPushButton

from PIL import Image, ImageDraw
import numpy as np

from percolation import SquareEdge, SquareSite, TriangleEdge, TriangleSite, HexagonEdge, HexagonSite


class Tab(QDialog):
    def __init__(self):
        super().__init__()
        self.setGeometry(10, 25, 650, 1040)
        self.setWindowTitle("Perko")
        #self.setWindowIcon(QIcon("logo.png")) pour éventuellement mettre un logo
        layout = QVBoxLayout()
        tab_widget = QTabWidget()
        tab_widget.addTab(TabSimulateur(), "Simulateur de percolation")
        layout.addWidget(tab_widget)
        self.setLayout(layout)



class TabSimulateur(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QWidget.__init__(self)

        # Paramètres par défaut
        self.number = 10
        self.width = 5
        self.color_open = (20, 70, 120)
        self.color_close = (220, 220, 220)
        self.color_path = (255, 0, 0)
        self.proba = 0
        self.mode = 1
        self.probleme = None

        #Fonctions
        def mode_set(x): #Permet de changer le mode de percolation, et limite la taille de certains modes par site pour éviter de prendre trop de temps
            radio_button = self.sender()
            if radio_button.isChecked():
                if isinstance(x, int):
                    self.mode = x
                    print(self.mode)
                    if x == 3:
                        limit_number(15)
                    elif x ==5:
                        limit_number(25)
                    else:
                        limit_number(100)


        def proba_set(x): #Permet de changer la probabilité à la main et de modifier les thèmes de couleur avec un mot clé
            if x != "" and x[0] == 0 and x[-1] in {"0","1","2","3","4","5","6","7","8","9","."} and len(x) > 2: #la probabilité doit démarrer par un zéro et ne contenir que des chiffres ou un point
                x = float(x)
                self.proba = x
                print(x)
                self.slider_proba.setValue(int(x*100))
            elif x == "forest": #thème spécial forêt
                print('ok forest')
                col1 = (150,110,45)
                col2 = (170,255,0)
                col3 = (255,0,0)
                self.color_close = col1
                self.color_open = col2
                self.color_path = col3
                start_color(self.color_close_label,col1)
                start_color(self.color_open_label,col2)
                start_color(self.color_path_label,col3)
            elif x == "multi": #thème multicolore
                print('ok multi')
                col1 = (255,51,228)
                col2 = (255,218,32)
                col3 = (0,251,255)
                self.color_close = col1
                self.color_open = col2
                self.color_path = col3
                start_color(self.color_close_label,col1)
                start_color(self.color_open_label,col2)
                start_color(self.color_path_label,col3)
            elif x == "water": #thème eau qui coule
                print('ok water')
                col1 = (196,209,227)
                col2 = (37,94,177)
                col3 = (255,0,0)
                self.color_close = col1
                self.color_open = col2
                self.color_path = col3
                start_color(self.color_close_label,col1)
                start_color(self.color_open_label,col2)
                start_color(self.color_path_label,col3)

        def limit_number(x): #Permet de changer la taille
            print(x)
            self.slider_width.setMaximum(int(x/5)) #La taille est un multiple de 5 pour faciliter le tout

        def simu(type, proba, taille, largeur, col1, col2, col3): #Permet de générer une instance en fon ction du mode
            print(np.random.get_state())
            with Image.open("hopper_test.jpg") as im:
                if type == 1:
                    probleme = SquareSite(im, taille, proba, largeur, col1, col2, col3)
                elif type == 2:
                    probleme = SquareEdge(im, taille, proba, largeur, col1, col2, col3)
                elif type == 3:
                    probleme = TriangleSite(im, taille, proba, largeur, col1, col2, col3)
                elif type == 4:
                    probleme = TriangleEdge(im, taille, proba, largeur, col1, col2, col3)
                elif type == 5:
                    probleme = HexagonSite(im, taille, proba, largeur, col1, col2, col3)
                elif type == 6:
                    probleme = HexagonEdge(im, taille, proba, largeur, col1, col2, col3)
                self.probleme = probleme
                self.probleme.full_solve()
                res = self.probleme.display()
                res.save("res.jpg")
                display()
                res2 = self.probleme.sol_display()
                res2.save("res2.jpg")
                #On sauvegarde déjà les 2 images (avec et sans solution) pour pouvoir les afficher sans chargement

        def display(): #Génère une image et l'affiche dans le cadre de l'image
            self.pixmap = QPixmap("res.jpg")
            self.img_label.setPixmap(self.pixmap)
            self.show()

        def sol_display(): #Génère l'image de la solution et l'affiche dans le cadre
            self.pixmap = QPixmap("res2.jpg")
            self.img_label.setPixmap(self.pixmap)
            print(self.probleme.path)
            self.show()

        #Différentes fonctions pour changer uniformément les styles des boutons
        def change_radio_style(radio):
            radio.setStyleSheet("QRadioButton"
                                        "{"
                                        "font : 20px Arial;"
                                        "}")

        def change_button_style(button):
            button.setStyleSheet("QPushButton"
                          "{"
                          "font : 20px Arial;"
                          "}")

        def change_color_value(label,to_change):
            color = QColorDialog.getColor()
            label.setStyleSheet("QLabel"
                                "{"
                                "border : 20px solid black;"
                                "font : 2px Arial;"
                                "}")
            #Ici on change aussi les rectangles de couleurs à coté des boutons
            label.setText("")
            graphic = QGraphicsColorizeEffect(self)
            graphic.setColor(color)
            label.setGraphicsEffect(graphic)
            col = (color.red(), color.green(), color.blue())
            if to_change == 1:
                self.color_close = col
            elif to_change == 2:
                self.color_open = col
            elif to_change == 3:
                self.color_path = col


        def start_color(label, color): #Permet de changer les couleurs sans passer par le picker, au début et lors des changements de thème
            label.setStyleSheet("QLabel"
                                "{"
                                "border : 20px solid black;"
                                "font : 2px Arial;"
                                "}")

            label.setText("")
            graphic = QGraphicsColorizeEffect(self)
            color = QtGui.QColor(color[0],color[1],color[2])
            graphic.setColor(color)
            label.setGraphicsEffect(graphic)

        #Textes génériques utilisables plus tard
        self.vide_label = QLabel('    ')
        self.vide_label2 = QLabel('    ')
        #line_other = "___________________________________________________________________________"
        line = "▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂"
        self.line_label1 = QtWidgets.QLabel(line)
        self.line_label2 = QtWidgets.QLabel(line)
        self.line_label3 = QtWidgets.QLabel(line)
        self.line_label4 = QtWidgets.QLabel(line)


        #Partie présentation
        self.presentation_label = QLabel(
            "Veuillez choisir : \n- Une probabilité de percolation \n- Un mode de percolation \n- La taille du graphe")
        self.font2 = QtGui.QFont()
        self.font2.setPointSize(15)
        self.presentation_label.setFont(self.font2)

        #Partie Proba texte + slider
        self.proba_label = QtWidgets.QLabel("Probabilité = 0")

        self.slider_proba = QtWidgets.QSlider()
        self.slider_proba.setOrientation(Qt.Horizontal)

        self.slider_proba.valueChanged.connect(self.change_proba)

        self.slider_proba.setSingleStep(1)
        self.slider_proba.setMinimum(0)
        self.slider_proba.setMaximum(100)
        self.slider_proba.setGeometry(QtCore.QRect(19, 10, 16, 16))

        #Partie taille du graphe
        self.number_label = QtWidgets.QLabel("Largeur = 10")

        self.slider_width = QtWidgets.QSlider()
        self.slider_width.setOrientation(Qt.Horizontal)

        self.slider_width.valueChanged.connect(self.change_width)

        self.slider_width.setSingleStep(2)
        self.slider_width.setMinimum(1)
        self.slider_width.setMaximum(20)
        self.slider_width.setGeometry(QtCore.QRect(19, 10, 16, 16))


        #Taille de la police des textes proba et taille
        self.font = QtGui.QFont()
        self.font.setPointSize(20)
        self.proba_label.setFont(self.font)
        self.number_label.setFont(self.font)


        #Partie boutons "radio" pour choisir le modèle
        self.carre_site = QRadioButton("CARRÉ PAR SITE")
        self.carre_site.setChecked(True)
        self.carre_site.toggled.connect(lambda: mode_set(1))

        self.carre_arete = QRadioButton("CARRÉ PAR ARÊTE")
        self.carre_arete.toggled.connect(lambda: mode_set(2))

        self.triangle_site = QRadioButton("TRIANGLE PAR SITE")
        self.triangle_site.toggled.connect(lambda: mode_set(3))

        self.triangle_arete = QRadioButton("TRIANGLE PAR ARÊTE")
        self.triangle_arete.toggled.connect(lambda: mode_set(4))

        self.hexagone_site = QRadioButton("HEXAGONE PAR SITE")
        self.hexagone_site.toggled.connect(lambda: mode_set(5))

        self.hexagone_arete = QRadioButton("HEXAGONE PAR ARÊTE")
        self.hexagone_arete.toggled.connect(lambda: mode_set(6))

        change_radio_style(self.carre_site)
        change_radio_style(self.carre_arete)
        change_radio_style(self.triangle_site)
        change_radio_style(self.triangle_arete)
        change_radio_style(self.hexagone_site)
        change_radio_style(self.hexagone_arete)

        #Proba manuelle
        self.manual_input = QLineEdit()
        self.manual_input.setPlaceholderText("...")
        self.manual_input.textEdited.connect(lambda: proba_set(self.manual_input.text()))

        #Boutons de génération et affichage de grille et sa solution
        self.generate_button = QPushButton('Générer et afficher')
        self.display_button = QPushButton('Afficher la grille')
        self.sol_display_button = QPushButton('Afficher la solution')

        change_button_style(self.generate_button)
        change_button_style(self.display_button)
        change_button_style(self.sol_display_button)

        self.generate_button.clicked.connect(
            lambda: simu(self.mode, self.proba, self.number, self.width, self.color_close, self.color_open,
                         self.color_path))
        self.display_button.clicked.connect(lambda: display())
        self.sol_display_button.clicked.connect(lambda: sol_display())


        #Boutons et textes pour le choix de couleur
        self.color_open_button = QPushButton('Couleur "ouvert"')
        self.color_close_button = QPushButton('Couleur "fermé"')
        self.color_path_button = QPushButton('Couleur du chemin')

        self.color_open_label = QLabel(self)
        self.color_close_label = QLabel(self)
        self.color_path_label = QLabel(self)

        start_color(self.color_open_label, self.color_open)
        start_color(self.color_close_label, self.color_close)
        start_color(self.color_path_label, self.color_path)

        self.color_close_button.clicked.connect(lambda: change_color_value(self.color_close_label, 1))
        self.color_open_button.clicked.connect(lambda: change_color_value(self.color_open_label, 2))
        self.color_path_button.clicked.connect(lambda: change_color_value(self.color_path_label, 3))

        # Affichage du canevas
        self.img_label = QLabel(self)
        self.pixmap = QPixmap('hopper_test.jpg')
        self.img_label.setPixmap(self.pixmap)
        self.img_label.resize(self.pixmap.width(), self.pixmap.height())

        """
        --------------------- Partie construction de l'interface
        """

        self.tabMenu = QTabWidget


        param_widget = QWidget()
        param_widget.setLayout(QVBoxLayout())
        param_widget.layout().addWidget(self.proba_label)
        param_widget.layout().addWidget(self.slider_proba)

        param_widget.layout().addWidget(self.line_label1)

        param_widget.layout().addWidget(self.carre_site)
        param_widget.layout().addWidget(self.carre_arete)
        param_widget.layout().addWidget(self.triangle_site)
        param_widget.layout().addWidget(self.triangle_arete)
        param_widget.layout().addWidget(self.hexagone_site)
        param_widget.layout().addWidget(self.hexagone_arete)

        param_widget.layout().addWidget(self.line_label2)

        param_widget.layout().addWidget(self.number_label)
        param_widget.layout().addWidget(self.slider_width)

        param_widget.layout().addWidget(self.line_label3)


        button_widget = QWidget()
        button_widget.setLayout(QHBoxLayout())
        button_widget.layout().addWidget(self.generate_button)
        button_widget.layout().addWidget(self.display_button)
        button_widget.layout().addWidget(self.sol_display_button)
        button_widget.layout().addWidget(self.manual_input)


        open_color_widget = QWidget()
        open_color_widget.setLayout(QHBoxLayout())
        open_color_widget.layout().addWidget(self.color_open_button)
        open_color_widget.layout().addWidget(self.color_open_label)

        close_color_widget = QWidget()
        close_color_widget.setLayout(QHBoxLayout())
        close_color_widget.layout().addWidget(self.color_close_button)
        close_color_widget.layout().addWidget(self.color_close_label)

        path_color_widget = QWidget()
        path_color_widget.setLayout(QHBoxLayout())
        path_color_widget.layout().addWidget(self.color_path_button)
        path_color_widget.layout().addWidget(self.color_path_label)


        left_layout = QWidget()
        left_layout.setLayout(QVBoxLayout())

        left_layout.layout().addWidget(self.presentation_label)
        left_layout.layout().addWidget(param_widget)
        left_layout.layout().addWidget(button_widget)

        left_layout.layout().addWidget(self.line_label4)

        left_layout.layout().addWidget(open_color_widget)
        left_layout.layout().addWidget(close_color_widget)
        left_layout.layout().addWidget(path_color_widget)


        final_layout = QHBoxLayout()
        final_layout.addWidget(left_layout)
        final_layout.addWidget(self.img_label)

        self.setLayout(final_layout)
        self.show()

    #Fonctions externes
    def change_proba(self, value): #Change la probabilité, en la mettant bien avec une valeur à virgule entre 0 et 1
        self.proba_label.setText("Probabilité = " + str(value / 100))
        self.proba = value / 100
        print(self.proba)

    def change_width(self, value): #Change la taille du graphe et peut changer la taille du trait dans les grandes grilles
        self.number_label.setText("Taille du graphe = " + str(value * 5))
        self.number = value * 5
        print(self.number)
        if self.mode % 2 == 0 and self.number > 40:
            self.width = 3
        else:
            self.width = 5


"""
Inutilisé mais peut être implémenté

Bouton pour fermer la fenêtre : self.close_button.clicked.connect(sys.exit)

Onglet pour afficher beaucoup de texte
class TabText(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QVBoxLayout()
        self.textBrowser = QTextBrowser()
        self.textBrowser.setOpenExternalLinks(True)
        layout.addWidget(self.textBrowser)
        self.text = open('file.html', "r", encoding="utf-8").read()
        self.textBrowser.setHtml(self.text)
        self.setLayout(layout)
        
"""


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Tab()
    window.show()
    sys.exit(app.exec_())
