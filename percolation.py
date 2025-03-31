"""
Attention à l'ordre des i,j. Du à la nature des coordonnées du module PIL, la première coordonnée représente bien les x
et la deuxième les y. Cela est différent de beaucoup de programmes utilisant des matrice, qui préfère utiliser la première
coordonnée pour y (le numéro de la liste) et la deuxième pour le x (le numéro dans la liste).
"""

"""
Color1 = Couleur pour les fermés
Color2 = Couleur pour les ouverts
Color3 = Couleur pour le chemin
"""

#Imports nécessaires pour le programme
from PIL import Image, ImageDraw
import random as r
import time
import numpy as np

#Je ne vais commenter que la première classe en détail, le reste suit du même raisonnement

class SquareSite:
    def __init__(self, im, number, proba, width, color1, color2, color3):
        #Paramètres généraux d'une instance : l'image de fond, la taille, la probabilité, la largeur du trait, les 3 couleurs
        self.im = im
        self.number = number
        self.proba = proba
        self.width = width
        self.color1 = color1
        self.color2 = color2
        self.color3 = color3

        #Calcul de la taille en pixel d'un carré
        self.m = max(im.size[0], im.size[1])
        self.pix = int(self.m / self.number)
        self.largeur = int(im.size[0] // self.pix)  # nombre de carrés en largeur
        self.hauteur = int(im.size[1] // self.pix)  # nombre de carrés en hauteur

        #Génération via une binomiale de la matrice représentant l'ouverture/fermeture des cases
        self.open_list = np.random.binomial(1, proba, (self.hauteur +1, self.largeur))

        #Mise en place des variables nécessaires pour la recherche de chemin
        self.current = (0, 0)
        self.path = []
        self.already_tested = np.zeros((self.hauteur +1, self.largeur))
        self.to_follow = dict()

    def display(self):
        pix = self.pix
        draw = ImageDraw.Draw(self.im)
        for i in range(0, self.hauteur + 1):  # impression des carrés de couleur en fonction de l'ouverture
            for j in range(0, self.largeur):
                draw.rectangle([(j * pix, i * pix), ((j + 1) * pix - 1, (i + 1) * pix - 1)],[self.color1, self.color2][self.open_list[i, j]])
        #self.im.show() // à activer pour afficher l'image directement sans passer par l'application
        return self.im

    def sol_display(self):
        draw = ImageDraw.Draw(self.im)
        pix = self.pix
        for coo in self.path:
            draw.rectangle([(coo[1] * pix, coo[0] * pix), ((coo[1] + 1) * pix - 1, (coo[0] + 1) * pix - 1)],
                           self.color3) #dessin de la solution
        #self.im.show()  # COO reprend des elements de matrice !!! donc si (1,2) est dans path ca veut dire que (x=2, y=1)*pix est ouvert dans le quadrillage
        if self.path == []: #si la solution est vide on dessine une croix
            draw.line((0, 0, self.im.size[0], self.im.size[1]), fill=(255,0,0), width=10)
            draw.line((0, self.im.size[1], self.im.size[0], 0), fill=(255, 0, 0), width=10)
        return self.im

    def full_solve(self):
        path = []
        if self.solve(): #construction de la solution via le dictionnaire to_follow
            elem = self.current
            path.append(elem)
            while elem[0] != 0:
                elem = self.to_follow[elem] #on revient en arrière depuis la dernière case, en regardant qui l'a mise dans le chemin, en boucle
                path.append(elem)
            path.reverse() #on inverse la liste pour avoir le chemin dans le bon ordre
            self.path = path
        return path

    def solve(self):
        stack = []
        for i in range(self.largeur): #on place toutes les cases de la première ligne dans notre stack
            if self.open_list[0][i]:
                stack.append((0,i))
        stack.reverse() #on veut démarrer en haut à gauche

        #la résolution utilise un parcours en profondeur (DFS) et donc une pile qui stocke tous les éléments qu'il faut encore visiter (LIFO)
        while len(stack) > 0:
            start = self.current = stack.pop() #on récupère l'élément en haut du stack/de la pile
            self.already_tested[start[0]][start[1]] = 1 #on dit qu'on l'a déjà visité, pour éviter de le reprendre plus tard

            #fin
            if start[0] == self.hauteur:  #je regarde si je suis déjà tout en bas, si oui je m'arête, mon chemin est fini
                return True

            #vu que c'est une pile je démarre par les éléments que je veux visiter en dernier, notamment le haut vu que je ne veux remonter qu'en derniers recours
            #haut
            if start[0] > 0 and self.open_list[start[0] - 1][start[1]] == 1 and self.already_tested[start[0]-1][start[1]] == 0:
                #à chaque fois je vérifie que mon voisin est bien dans la grille, qu'il est bien ouvert et qu'il n'a pas encore été testé
                new_candidate = (start[0]-1, start[1])
                self.to_follow[new_candidate] = start
                stack.append(new_candidate)

            # droite
            if start[1] < self.largeur-1 and self.open_list[start[0]][start[1] + 1] == 1 and \
                    self.already_tested[start[0]][start[1] + 1] == 0:
                new_candidate = (start[0], start[1] + 1)
                self.to_follow[new_candidate] = start
                stack.append(new_candidate)

            # gauche
            if start[1] > 0 and self.open_list[start[0]][start[1] - 1] == 1 and self.already_tested[start[0]][start[1] - 1] == 0:
                new_candidate = (start[0], start[1] - 1)
                self.to_follow[new_candidate] = start
                stack.append(new_candidate)

            #je veux prioriser le fait d'aller vers le bas
            # bas
            if start[0] < self.hauteur and self.open_list[start[0] + 1][start[1]] == 1 and \
                    self.already_tested[start[0] + 1][start[1]] == 0:
                new_candidate = (start[0] + 1, start[1])
                self.to_follow[new_candidate] = start
                stack.append(new_candidate)

        return False

    def comp_con(self):
        #méthode utilisée uniquement dans cette classe, qui m'a permis de vérifier qu'on a bien une seule méga composante connexe après la probabilité critique
        final_dict = dict()
        for i in range(self.largeur):
            for j in range(self.hauteur):
                current_root = (j,i)
                stack = [current_root]
                if self.already_tested[current_root[0]][current_root[1]] == 0 and self.open_list[current_root[0]][current_root[1]] == 1:
                    while len(stack) > 0:
                        start = self.current = stack.pop()
                        self.already_tested[start[0]][start[1]] = 1

                        # haut
                        if start[0] > 0 and self.open_list[start[0] - 1][start[1]] == 1 and self.already_tested[start[0] - 1][
                            start[1]] == 0:
                            new_candidate = (start[0] - 1, start[1])
                            final_dict[new_candidate] = current_root
                            stack.append(new_candidate)

                        # droite
                        if start[1] < self.largeur - 1 and self.open_list[start[0]][start[1] + 1] == 1 and \
                                self.already_tested[start[0]][start[1] + 1] == 0:
                            new_candidate = (start[0], start[1] + 1)
                            final_dict[new_candidate] = current_root
                            stack.append(new_candidate)

                        # gauche
                        if start[1] > 0 and self.open_list[start[0]][start[1] - 1] == 1 and self.already_tested[start[0]][
                            start[1] - 1] == 0:
                            new_candidate = (start[0], start[1] - 1)
                            final_dict[new_candidate] = current_root
                            stack.append(new_candidate)

                        # bas
                        if start[0] < self.hauteur and self.open_list[start[0] + 1][start[1]] == 1 and \
                                self.already_tested[start[0] + 1][start[1]] == 0:
                            new_candidate = (start[0] + 1, start[1])
                            final_dict[new_candidate] = current_root
                            stack.append(new_candidate)
        return final_dict

class SquareEdge:
    def __init__(self,im,number, proba, width, color1, color2,color3):
        self.im = im
        self.number = number
        self.proba = proba
        self.width = width
        self.color1 = color1
        self.color2 = color2
        self.color3 = color3

        self.current = (0,0)
        self.path = []
        self.m = max(im.size[0], im.size[1])
        self.pix = self.m / self.number

        self.largeur = int(im.size[0] // self.pix) #nombre de carrés en largeur
        self.hauteur = int(im.size[1] // self.pix) #nombre de carrés en hauteur

        self.to_follow = dict()

        self.already_tested = np.zeros((self.hauteur+1, self.largeur+1))

        #Pour les arêtes des carrés, on génère notre grille avec ce principe : chaque point a une arête qui va vers sa droite et vers le bas
        open_list_num_1 = np.random.binomial(1,proba,(self.hauteur+1,self.largeur+1))
        open_list_num_2 = np.random.binomial(1,proba,(self.hauteur+1,self.largeur+1))
        self.open_list =np.stack([open_list_num_1, open_list_num_2],axis=2)


    def full_solve(self):
        path = []
        if self.solve():
            elem = self.current
            path.append(elem)
            while elem[0] != 0:
                elem = self.to_follow[elem]
                path.append(elem)
            path.reverse()
            self.path = path
        return path


    def solve(self):
        stack = []
        for i in range(self.largeur + 1):
            stack.append((0,i))
        stack.reverse()


        while len(stack) > 0:
            start = self.current = stack.pop()
            self.already_tested[start[0]][start[1]] = 1

            if start[0] == self.hauteur and self.open_list[start[0]][start[1]][0] == 1:
                self.to_follow[(start[0]+1,start[1])] = start
                self.current = (start[0]+1,start[1])
                return True

            #haut
            if start[0] > 0 and self.open_list[start[0]-1][start[1]][0] == 1 and self.already_tested[start[0]-1][start[1]] == 0:
                self.to_follow[(start[0]-1,start[1])] = start
                stack.append((start[0]-1,start[1]))

            #gauche
            if start[1] > 0 and self.open_list[start[0]][start[1]-1][1] == 1 and self.already_tested[start[0]][start[1]-1] == 0:
                self.to_follow[(start[0],start[1]-1)] = start
                stack.append((start[0],start[1]-1))

            #droite
            if start[1] < self.largeur and self.open_list[start[0]][start[1]][1] == 1 and self.already_tested[start[0]][start[1]+1] == 0:
                self.to_follow[(start[0],start[1]+1)] = start
                stack.append((start[0],start[1]+1))

            #bas
            if start[0] < self.hauteur  and self.open_list[start[0]][start[1]][0] == 1 and self.already_tested[start[0]+1][start[1]] == 0:
                self.to_follow[(start[0]+1,start[1])] = start
                stack.append((start[0]+1,start[1]))

        return False

    def display(self):
        draw = ImageDraw.Draw(self.im)
        for j in range(self.largeur +1):
            for i in range(self.hauteur+1):
                draw.line((j * self.pix, i * self.pix, (j + 1) * self.pix, i * self.pix), fill=[self.color1,self.color2][self.open_list[i][j][1]], width=self.width)

        for j in range(self.largeur + 1):
            for i in range(self.hauteur + 1):
                draw.line((j * self.pix, i * self.pix, j * self.pix, (i+1) * self.pix), fill=[self.color1,self.color2][self.open_list[i][j][0]], width=self.width)

        #self.im.show()
        return self.im

    def sol_display(self):
        draw = ImageDraw.Draw(self.im)
        sol = self.path
        i = 0
        while i < len(sol)-1:
            draw.line((sol[i][1] * self.pix, sol[i][0] * self.pix, sol[i+1][1] * self.pix, sol[i+1][0] * self.pix), fill=self.color3, width=self.width)
            i+=1
        if self.path == []:
            draw.line((0, 0, self.im.size[0], self.im.size[1]), fill=(255,0,0), width=10)
            draw.line((0, self.im.size[1], self.im.size[0], 0), fill=(255, 0, 0), width=10)
        # self.im.show()
        return self.im


class TriangleSite:
    def __init__(self, im, number, proba, width, color1, color2, color3):
        self.im = im
        self.number = number
        self.proba = proba
        self.width = width
        self.color1 = color1
        self.color2 = color2
        self.color3 = color3
        self.path = []

        self.current = (0, 0)
        self.m = max(im.size[0], im.size[1])
        self.pix = self.m / self.number

        self.to_follow = dict()

        self.largeur = int(im.size[0] // self.pix) + 1
        self.hauteur = int(im.size[1] // self.pix)

        self.already_tested = np.zeros((self.hauteur + 1, 2 * self.largeur + 1))

        self.open_list = np.random.binomial(1, self.proba, (self.hauteur + 1, 2 * self.largeur + 1))


    def full_solve(self):
        path = []
        if self.solve():
            elem = self.current
            path.append(elem)
            while not (elem[0] == 0 and elem[1] % 2 == 1):
                elem = self.to_follow[elem]
                path.append(elem)
            path.reverse()
            self.path = path
        return path

    def solve(self):
        stack = []
        for i in range(self.largeur):
            if self.open_list[0][2 * i + 1]:
                stack.append((0, 2 * i + 1))
        stack.reverse()

        while len(stack) > 0:
            start = self.current = stack.pop()
            self.already_tested[start[0]][start[1]] = 1

            # fin
            if start[0] == self.hauteur and (start[0] + start[1]) % 2 == 0:
                return True

            # cas où le triangle pointe vers le bas, on vérifie le voisin du haut
            if start[0] + start[1] % 2 == 1:
                if start[0] > 0 and self.open_list[start[0] - 1][start[1]] and self.already_tested[start[0] - 1][
                    start[1]] == 0:
                    new_candidate = (start[0] - 1, start[1])
                    self.to_follow[new_candidate] = start
                    stack.append(new_candidate)


            # droite
            if start[1] < 2 * self.largeur and self.open_list[start[0]][start[1] + 1] == 1 and \
                    self.already_tested[start[0]][start[1] + 1] == 0:
                new_candidate = (start[0], start[1] + 1)
                self.to_follow[new_candidate] = start
                stack.append(new_candidate)

            # gauche
            if start[1] > 0 and self.open_list[start[0]][start[1] - 1] == 1 and self.already_tested[start[0]][
                start[1] - 1] == 0:
                new_candidate = (start[0], start[1] - 1)
                self.to_follow[new_candidate] = start
                stack.append(new_candidate)

            # cas où le triangle pointe vers le haut, on vérifie le voisin du bas
            if (start[0] + start[1]) % 2 == 0:
                if self.open_list[start[0] + 1][start[1]] == 1 and self.already_tested[start[0] + 1][start[1]] == 0:
                    new_candidate = (start[0] + 1, start[1])
                    self.to_follow[new_candidate] = start
                    stack.append(new_candidate)

        return False

    def triangle_to_right(self, a, b, col, draw):
        #fonction pour dessiner un triangle qui pointe vers le bas, en partant de son sommet supérieur gauche
        draw.polygon([(a * self.pix, b * self.pix), ((a + 1) * self.pix, b * self.pix),
                      ((a + 0.5) * self.pix, (b + 1) * self.pix)],
                     fill=col, width=2, outline=(256, 256, 256))

    def triangle_to_down(self, a, b, col, draw):
        #fonction pour dessiner un triangle qui pointe vers le bas, en partant de sa pointe
        draw.polygon([(a * self.pix, b * self.pix), ((a + 0.5) * self.pix, (b + 1) * self.pix),
                      ((a - 0.5) * self.pix, (b + 1) * self.pix)], fill=col, width=2, outline=(256, 256, 256))

    def display(self):
        draw = ImageDraw.Draw(self.im)
        for j in range(2 * self.largeur + 1):
            print(j)
            for i in range(self.hauteur + 1):
                if self.open_list[i][j] == 1:
                    col = self.color2
                else:
                    col = self.color1
                #le dessin des triangles dépend de la parité de notre case, pour savoir comment décaler les triangles
                if i % 2 == 0 and j % 2 == 0:
                    self.triangle_to_down(j / 2, i, col, draw)
                elif i % 2 == 0 and j % 2 == 1:
                    self.triangle_to_right((j - 1) / 2, i, col, draw)
                elif i % 2 == 1 and j % 2 == 0:
                    self.triangle_to_right((j / 2) - 1 / 2, i, col, draw)
                elif i % 2 == 1 and j % 2 == 1:
                    self.triangle_to_down(j / 2, i, col, draw)

        #self.im.show()
        return self.im

    def sol_display(self):
        draw = ImageDraw.Draw(self.im)
        sol = self.path
        k = 0
        col = self.color3
        while k < len(sol):
            (i, j) = sol[k]
            if i % 2 == 0 and j % 2 == 0:
                self.triangle_to_down(j / 2, i, col, draw)
            elif i % 2 == 0 and j % 2 == 1:
                self.triangle_to_right((j - 1) / 2, i, col, draw)
            elif i % 2 == 1 and j % 2 == 0:
                self.triangle_to_right((j / 2) - 1 / 2, i, col, draw)
            elif i % 2 == 1 and j % 2 == 1:
                self.triangle_to_down(j / 2, i, col, draw)
            k += 1
        if self.path == []:
            draw.line((0, 0, self.im.size[0], self.im.size[1]), fill=(255, 0, 0), width=10)
            draw.line((0, self.im.size[1], self.im.size[0], 0), fill=(255, 0, 0), width=10)
        #self.im.show()
        return self.im

class TriangleEdge:
    def __init__(self, im, number, proba, width, color1, color2, color3):
        self.im = im
        self.number = number
        self.proba = proba
        self.width = width
        self.color1 = color1
        self.color2 = color2
        self.color3 = color3

        self.current = (0, 0)
        self.m = max(im.size[0], im.size[1])
        self.pix = self.m / self.number

        self.to_follow = dict()
        self.path = []

        self.largeur = int(im.size[0] // self.pix)
        self.hauteur = int(im.size[1] // self.pix)

        if (self.largeur - 0.5) * self.pix < im.size[0]:
            self.largeur += 1

        self.already_tested = np.zeros((self.hauteur + 1, self.largeur + 1))

        #Pour dessiner les arêtes du modèle triangulaire on part du principe : chaque sommet a une arête vers le sud-ouest, vers le sud-est, et vers l'est
        open_list_num1 = np.random.binomial(1, self.proba, (self.hauteur + 1, self.largeur + 1))
        open_list_num2 = np.random.binomial(1, self.proba, (self.hauteur + 1, self.largeur + 1))
        open_list_num3 = np.random.binomial(1, self.proba, (self.hauteur + 1, self.largeur + 1))
        self.open_list = np.stack([open_list_num1, open_list_num2, open_list_num3], axis=2)

    def full_solve(self):
        path = []
        if self.solve():
            elem = self.current
            path.append(elem)
            while elem[0] != 0:
                elem = self.to_follow[elem]
                path.append(elem)
            path.reverse()
            self.path = path
        return path

    def solve(self):
        # (0,1,2) : 0 = bas gauche, 1 = bas droite, 2 = horizontal droit

        stack = []
        for i in range(self.largeur + 1):
            stack.append((0, i))
        stack.reverse()

        while len(stack) > 0:
            start = self.current = stack.pop()
            self.already_tested[start[0]][start[1]] = 1

            # fin à bas gauche
            if start[1] > 0 and start[0] == self.hauteur and self.open_list[start[0]][start[1]][0] == 1:
                if start[0] % 2 == 0:
                    new_candidate = (start[0] + 1, start[1])
                else:
                    new_candidate = (start[0] + 1, start[1] - 1)
                self.to_follow[new_candidate] = start
                self.current = new_candidate
                return True

            # fin à bas droite
            if start[1] < self.largeur and start[0] == self.hauteur and self.open_list[start[0]][start[1]][1] == 1:
                if start[0] % 2 == 0:
                    new_candidate = (start[0] + 1, start[1] + 1)
                else:
                    new_candidate = (start[0] + 1, start[1])
                self.to_follow[new_candidate] = start
                self.current = new_candidate
                return True

            # haut gauche / haut droite
            if start[0] > 0:
                if start[0] % 2 == 0:
                    if start[1] > 0 and self.open_list[start[0] - 1][start[1]][1] == 1 and \
                            self.already_tested[start[0] - 1][start[1]] == 0:
                        new_candidate = (start[0] - 1, start[1])
                        self.to_follow[new_candidate] = start
                        stack.append(new_candidate)
                    if start[1] < self.largeur and self.open_list[start[0] - 1][start[1] + 1][0] == 1 and \
                            self.already_tested[start[0] - 1][start[1] + 1] == 0:
                        new_candidate = (start[0] - 1, start[1] + 1)
                        self.to_follow[new_candidate] = start
                        stack.append(new_candidate)
                else:
                    if start[1] > 0 and self.open_list[start[0] - 1][start[1] - 1][1] == 1 and \
                            self.already_tested[start[0] - 1][start[1] - 1] == 0:
                        new_candidate = (start[0] - 1, start[1] - 1)
                        self.to_follow[new_candidate] = start
                        stack.append(new_candidate)
                    if start[1] < self.largeur and self.open_list[start[0] - 1][start[1]][0] == 1 and \
                            self.already_tested[start[0] - 1][start[1]] == 0:
                        new_candidate = (start[0] - 1, start[1])
                        self.to_follow[new_candidate] = start
                        stack.append(new_candidate)

            # droite
            if start[1] < self.largeur and self.open_list[start[0]][start[1]][2] == 1 and self.already_tested[start[0]][
                start[1] + 1] == 0:
                new_candidate = (start[0], start[1] + 1)
                self.to_follow[new_candidate] = start
                stack.append(new_candidate)

            # gauche
            if (start[1] > 1 or (start[1] == 1 and start[0] % 2 == 0)) and self.open_list[start[0]][start[1] - 1][
                2] == 1 and self.already_tested[start[0]][start[1] - 1] == 0:
                new_candidate = (start[0], start[1] - 1)
                self.to_follow[new_candidate] = start
                stack.append(new_candidate)

            # bas à droite
            if start[1] < self.largeur and self.open_list[start[0]][start[1]][1] == 1:
                if start[0] % 2 == 0 and self.already_tested[start[0] + 1][start[1] + 1] == 0:
                    new_candidate = (start[0] + 1, start[1] + 1)
                    self.to_follow[new_candidate] = start
                    stack.append(new_candidate)
                elif start[0] % 2 == 1 and self.already_tested[start[0] + 1][start[1]] == 0:
                    new_candidate = (start[0] + 1, start[1])
                    self.to_follow[new_candidate] = start
                    stack.append(new_candidate)

            # bas gauche
            if start[1] > 0 and self.open_list[start[0]][start[1]][0] == 1:
                if start[0] % 2 == 0 and self.already_tested[start[0] + 1][start[1]] == 0:
                    new_candidate = (start[0] + 1, start[1])
                    self.to_follow[new_candidate] = start
                    stack.append(new_candidate)
                elif start[0] % 2 == 1 and self.already_tested[start[0] + 1][start[1] - 1] == 0:
                    new_candidate = (start[0] + 1, start[1] - 1)
                    self.to_follow[new_candidate] = start
                    stack.append(new_candidate)

        return False

    def display(self):
        # (0,1,2) : 0 = bas gauche, 1 = bas droite, 2 = horizontal droit
        draw = ImageDraw.Draw(self.im)
        for j in range(self.largeur + 1):
            for i in range(self.hauteur + 1):
                if self.open_list[i][j][2] == 1:
                    col = self.color2
                else:
                    col = self.color1
                new_j = j
                if i % 2:
                    new_j -= 1 / 2
                draw.line((new_j * self.pix, i * self.pix, (new_j + 1) * self.pix, i * self.pix), fill=col,
                          width=self.width)

        for j in range(self.largeur + 1):
            for i in range(self.hauteur + 1):
                if self.open_list[i][j][1] == 1:
                    col = self.color2
                else:
                    col = self.color1
                new_j = j
                if i % 2:
                    new_j -= 1 / 2
                draw.line((new_j * self.pix, i * self.pix, (new_j + 1 / 2) * self.pix, (i + 1) * self.pix), fill=col,
                          width=self.width)

        for j in range(self.largeur + 1):
            for i in range(self.hauteur + 1):
                if self.open_list[i][j][0] == 1:
                    col = self.color2
                else:
                    col = self.color1
                new_j = j
                if i % 2:
                    new_j -= 1 / 2
                draw.line((new_j * self.pix, i * self.pix, (new_j - 1 / 2) * self.pix, (i + 1) * self.pix), fill=col,
                          width=self.width)

        #self.im.show()
        return self.im

    def sol_display(self):
        draw = ImageDraw.Draw(self.im)
        sol = self.path
        i = 0
        while i < len(sol) - 1:
            new_j1 = sol[i][1]
            new_j2 = sol[i + 1][1]
            if sol[i][0] % 2:
                new_j1 -= 1 / 2
            if sol[i + 1][0] % 2:
                new_j2 -= 1 / 2
            draw.line((new_j1 * self.pix, sol[i][0] * self.pix, new_j2 * self.pix, sol[i + 1][0] * self.pix),
                      fill=self.color3, width=self.width)
            i += 1
        if self.path == []:
            draw.line((0, 0, self.im.size[0], self.im.size[1]), fill=(255, 0, 0), width=10)
            draw.line((0, self.im.size[1], self.im.size[0], 0), fill=(255, 0, 0), width=10)
        #self.im.show()
        return self.im


class HexagonSite:
    def __init__(self, im, number, proba, width, color1, color2, color3):
        self.im = im
        self.number = number
        self.proba = proba
        self.width = width
        self.color1 = color1
        self.color2 = color2
        self.color3 = color3

        self.current = (0, 0)
        print(im.size[0], im.size[1])
        self.pix = self.im.size[0] / (self.number * 1.5)

        self.to_follow = dict()
        self.path = []

        self.largeur = int(im.size[0] // (self.pix * 1.5))
        self.hauteur = int(im.size[1] // (2* self.pix)) + 1
        self.height_changed = False
        if (self.hauteur-0.5)*2*self.pix > im.size[1]:
            self.hauteur -= 1
            self.height_changed = True

        self.already_tested = np.zeros((self.hauteur +1,self.largeur +1))

        self.open_list = np.random.binomial(1, self.proba, (self.hauteur +1, self.largeur +1))

    def full_solve(self):
        path = []
        if self.solve():
            elem = self.current
            path.append(elem)
            while not elem[0] == 0:
                elem = self.to_follow[elem]
                path.append(elem)
            path.reverse()
            self.path = path
        return path

    def solve(self):
        stack = []
        for i in range(self.largeur):
            if self.open_list[0][i]:
                stack.append((0,i))
        stack.reverse()
        changed = self.height_changed

        while len(stack) > 0:
            start = self.current = stack.pop()
            self.already_tested[start[0]][start[1]] = 1

            # fin
            if changed:
                if start[0] == self.hauteur:
                    return True
            else:
                if start[0] == self.hauteur or (start[0] == self.hauteur-1 and start[1]%2 == 0):
                    return True

            # haut strict
            if start[0] > 0 and self.open_list[start[0]-1][start[1]] and self.already_tested[start[0]-1][start[1]] == 0:
                new_candidate = (start[0]-1, start[1])
                self.to_follow[new_candidate] = start
                stack.append(new_candidate)

            #haut gauche/droite
            if start[0] > 0 or (start[0] ==0 and start[1]%2 ==0):
                if start[1] > 0: #haut gauche
                    if (start[1]%2 == 0) and self.open_list[start[0]][start[1]-1] == 1 and self.already_tested[start[0]][start[1]-1] == 0:
                        new_candidate = (start[0], start[1]-1)
                        self.to_follow[new_candidate] = start
                        stack.append(new_candidate)
                    elif (start[1]%2 == 1) and self.open_list[start[0]-1][start[1]-1] == 1 and self.already_tested[start[0]-1][start[1]-1] == 0:
                        new_candidate = (start[0]-1, start[1] - 1)
                        self.to_follow[new_candidate] = start
                        stack.append(new_candidate)
                if start[1] < self.largeur: # haut droite
                    if (start[1]%2 == 0) and self.open_list[start[0]][start[1]+1] == 1 and self.already_tested[start[0]][start[1]+1] == 0:
                        new_candidate = (start[0], start[1]+1)
                        self.to_follow[new_candidate] = start
                        stack.append(new_candidate)
                    elif (start[1]%2 == 1) and self.open_list[start[0]-1][start[1]+1] == 1 and self.already_tested[start[0]-1][start[1]+1] == 0:
                        new_candidate = (start[0]-1, start[1] + 1)
                        self.to_follow[new_candidate] = start
                        stack.append(new_candidate)

            # bas gauche/droite
            if start[0] < self.hauteur:
                if start[1] < self.largeur:  # bas à droite
                    if (start[1] % 2 == 0) and self.open_list[start[0]+1][start[1] + 1] == 1 and self.already_tested[start[0]+1][start[1] + 1] == 0:
                        new_candidate = (start[0]+1, start[1] + 1)
                        self.to_follow[new_candidate] = start
                        stack.append(new_candidate)
                    elif (start[1] % 2 == 1) and self.open_list[start[0]][start[1] + 1] == 1 and self.already_tested[start[0]][start[1] + 1] == 0:
                        new_candidate = (start[0], start[1] + 1)
                        self.to_follow[new_candidate] = start
                        stack.append(new_candidate)
                if start[1] > 0:  # bas gauche
                    if (start[1] % 2 == 0) and self.open_list[start[0]+1][start[1] - 1] == 1 and self.already_tested[start[0]+1][start[1] - 1] == 0:
                        new_candidate = (start[0]+1, start[1] - 1)
                        self.to_follow[new_candidate] = start
                        stack.append(new_candidate)
                    elif (start[1] % 2 == 1) and self.open_list[start[0]][start[1] - 1] == 1 and self.already_tested[start[0]][start[1] - 1] == 0:
                        new_candidate = (start[0], start[1] - 1)
                        self.to_follow[new_candidate] = start
                        stack.append(new_candidate)

            # haut strict
            if self.open_list[start[0]+1][start[1]] and self.already_tested[start[0]+1][start[1]] == 0:
                new_candidate = (start[0] + 1, start[1])
                self.to_follow[new_candidate] = start
                stack.append(new_candidate)

        return False

    def hexa(self,i, j, col,draw):
        #dessin d'un hexagone à partir du sommet supérieur gauche
        draw.polygon([(j * self.pix, i * self.pix), ((j + 1) * self.pix, i * self.pix),
                      ((j + 1.5) * self.pix, (i + 1) * self.pix),
                      ((j + 1) * self.pix, (i + 2) * self.pix), (j * self.pix, (i + 2) * self.pix),
                      ((j - 0.5) * self.pix, (i + 1) * self.pix)],
                     fill=col, width=2, outline=(256, 256, 256))

    def display(self):
        draw = ImageDraw.Draw(self.im)
        for j in range(self.largeur+1):
            print(j)
            for i in range(self.hauteur+1):
                if self.open_list[i][j] == 1:
                    col = self.color2
                else:
                    col = self.color1
                if j %2 == 0:
                    self.hexa(2*i,j*1.5,col,draw)
                else:
                    self.hexa(2*i-1,j*1.5,col,draw)

        #self.im.show()
        return self.im

    def sol_display(self):
        draw = ImageDraw.Draw(self.im)
        sol = self.path
        k = 0
        col = self.color3
        while k < len(sol):
            (i,j) = sol[k]
            if j % 2 == 0:
                self.hexa(2 * i, j * 1.5, col,draw)
            else:
                self.hexa(2 * i - 1, j * 1.5, col,draw)
            k+=1
        if self.path == []:
            draw.line((0, 0, self.im.size[0], self.im.size[1]), fill=(255, 0, 0), width=10)
            draw.line((0, self.im.size[1], self.im.size[0], 0), fill=(255, 0, 0), width=10)
        #self.im.show()
        return self.im

class HexagonEdge:
    def __init__(self, im, number, proba, width, color1, color2, color3):
        self.im = im
        self.number = number
        self.proba = proba
        self.width = width
        self.color1 = color1
        self.color2 = color2
        self.color3 = color3

        self.current = (0,0)
        print(im.size[0],im.size[1])
        self.pix = self.im.size[0] / (self.number*1.5)

        self.to_follow = dict()
        self.path = []

        self.largeur = int(im.size[0] // (self.pix*1.5))
        self.hauteur = int(im.size[1] // self.pix) +1

        self.already_tested = np.zeros((self.hauteur +1,self.largeur +1))

        #Pour dessiner les arêtes hexagonales, on part du principe : un sommet sur deux a une arête vers le sud-ouest, est et nord-ouest
        open_list_num1 = np.random.binomial(1,self.proba,(self.hauteur +1,self.largeur +1))
        open_list_num2 = np.random.binomial(1,self.proba,(self.hauteur +1,self.largeur +1))
        open_list_num3 = np.random.binomial(1,self.proba,(self.hauteur +1,self.largeur +1))
        self.open_list = np.stack((open_list_num1, open_list_num2,open_list_num3), axis=2)
        index_sums = sum(np.meshgrid(np.arange(self.largeur +1),np.arange(self.hauteur +1))) #on somme les indices i et j
        odd_mask = (index_sums % 2) == 1 #récupération sommes indices impaires
        self.open_list[odd_mask] = -1 #valeur interdite


    def full_solve(self):
        path = []
        if self.solve():
            elem = self.current
            path.append(elem)
            while elem[0] != 0:
                elem = self.to_follow[elem]
                path.append(elem)
            path.reverse()
            self.path = path
        return path

    def solve(self):
        # (0,1,2) : 0 = bas gauche, 1 = droite, 2 = haut gauche

        stack = []
        for i in range(self.largeur + 1):
            stack.append((0, i))
        stack.reverse()

        while len(stack) > 0:
            start = self.current = stack.pop()
            self.already_tested[start[0]][start[1]] = 1

            if start[0] == self.hauteur:
                return True

            if (start[0]+start[1]) % 2 == 0:

                #haut gauche
                if start[1] > 0 and start[0] > 0 and self.open_list[start[0]][start[1]][2] == 1 and self.already_tested[start[0]-1][start[1]] == 0:
                    new_candidate = (start[0] - 1, start[1])
                    self.to_follow[new_candidate] = start
                    stack.append(new_candidate)

                #droite
                if start[1] < self.largeur and self.open_list[start[0]][start[1]][1] == 1 and self.already_tested[start[0]][start[1]+1] == 0:
                    new_candidate = (start[0], start[1]+1)
                    self.to_follow[new_candidate] = start
                    stack.append(new_candidate)

                #bas gauche
                if start[1] > 0 and self.open_list[start[0]][start[1]][0] == 1 and self.already_tested[start[0]+1][start[1]] == 0:
                    new_candidate = (start[0]+1, start[1])
                    self.to_follow[new_candidate] = start
                    stack.append(new_candidate)


            else:
                # haut droite
                if start[1] < self.largeur and start[0] > 0 and self.open_list[start[0]-1][start[1]][0] == 1 and self.already_tested[start[0] - 1][start[1]] == 0:
                    new_candidate = (start[0] - 1, start[1])
                    self.to_follow[new_candidate] = start
                    stack.append(new_candidate)

                # gauche
                if start[1] > 0 and self.open_list[start[0]][start[1]-1][1] == 1 and self.already_tested[start[0]][start[1]-1] == 0:
                    new_candidate = (start[0], start[1] - 1)
                    self.to_follow[new_candidate] = start
                    stack.append(new_candidate)

                #bas à droite
                if start[0] < self.hauteur and self.open_list[start[0]+1][start[1]][2] == 1 and self.already_tested[start[0] + 1][start[1]] == 0:
                    new_candidate = (start[0] + 1, start[1])
                    self.to_follow[new_candidate] = start
                    stack.append(new_candidate)


    def display(self):
        #(0,1,2) : 0 = bas gauche, 1 = droite, 2 = haut gauche
        draw = ImageDraw.Draw(self.im)
        for j in range(self.largeur+1):
            for i in range(self.hauteur+1):
                if (i+j) % 2 == 0:
                    new_j = j * 1.5
                    if self.open_list[i][j][1] == 1:
                        col = self.color2
                    else:
                        col = self.color1
                    draw.line((new_j * self.pix, i * self.pix, (new_j + 1) * self.pix, i * self.pix), fill=col, width=self.width)

                    if self.open_list[i][j][0] == 1:
                        col = self.color2
                    else:
                        col = self.color1
                    draw.line((new_j * self.pix, i * self.pix, (new_j-0.5) * self.pix, (i+1) * self.pix), fill=col, width=self.width)

                    if self.open_list[i][j][2] == 1:
                        col = self.color2
                    else:
                        col = self.color1
                    draw.line((new_j * self.pix, i * self.pix, (new_j-0.5) * self.pix, (i-1) * self.pix), fill=col, width=self.width)
        #self.im.show()
        return self.im

    def sol_display(self):
        draw = ImageDraw.Draw(self.im)
        sol = self.path
        i = 0
        while i < len(sol)-1:
            if (sol[i][0]+sol[i][1]) % 2 == 0:
                new_j1 = sol[i][1]*1.5
            else:
                new_j1 = ((sol[i][1]-1)*1.5)+1
            if (sol[i+1][0]+sol[i+1][1]) % 2 == 0:
                new_j2 = sol[i+1][1]*1.5
            else:
                new_j2 = ((sol[i+1][1]-1)*1.5)+1
            draw.line((new_j1* self.pix,  sol[i][0] * self.pix, new_j2  * self.pix,  sol[i+1][0] * self.pix), fill=self.color3, width=self.width)
            i+=1
        if self.path == []:
            draw.line((0, 0, self.im.size[0], self.im.size[1]), fill=(255, 0, 0), width=10)
            draw.line((0, self.im.size[1], self.im.size[0], 0), fill=(255, 0, 0), width=10)
        #self.im.show()
        return self.im

""" Permet d'étudier les composantes connexes, leur nombre et leur taille maximale
number = 100
proba = 0.65
width = 5
color2 = (20, 70, 120)
color1 = (230, 230, 230)
color3 = (256,20,100)
with Image.open("imgcarre.jpg") as img:
    for proba in [0.1,0.2,0.3,0.4,0.5,0.55,0.59,0.65,0.7,0.8,0.9,1]:
        print(proba)
        test = SquareSite(img,number, proba, width, color1, color2,color3)
        dictio = test.comp_con()
        test.display()
        new_dict = dict()
        for value in set(dictio.values()):
            new_dict[value] = []
        for key in dictio.keys():
            new_dict[dictio[key]].append(key)
        print(new_dict)
        number_comp = dict()
        for key in new_dict.keys():
            number_comp[key] = len(new_dict[key])
        print(number_comp)
        print(len(number_comp))
        m = max(list(set(number_comp.values())))
        print(m)
        print("fin")
"""
""" Permet de tester le programme et sa solution, avec le temps d'éxécution
if __name__ == "__main__":
    with Image.open("hopper_test.jpg") as img:
        t0 = time.time()
        my_test = HexagonSite(img,number,proba,width,color1,color2)
        my_test.display()
        t1 = time.time()
        print(t1-t0)
        my_test.full_solve()
        print(my_test.path)

        my_test.sol_display()
        #res.save("res.png")

"""
""" Permet de générer le graphique du tableau, avec le %age de case qui percolent
        list_numbers = []
        j = 0
        for number in [10,50,80]:
            list_prob = []
            for prob in [0.25,0.4,0.45,0.49,0.5,0.51,0.55,0.6,0.75]:
                nb_elem = 0
                for i in range(100):
                    a = TriangleEdge(img, number, prob, width, color1, color2)
                    a.full_solve()
                    if a.path != []:
                        nb_elem += 1
                list_prob.append(nb_elem)
            list_numbers.append(list_prob)
            print("ok " + str(j))
            j += 1
        print(list_numbers)
        """