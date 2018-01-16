"""Jeu de 421 en Pyhton

Le joueur affronte l'ordinateur avec un pot de départ de 21 jetons

Le but est de se débarrasser le plus vite possible de ses jetons.

La partie se déroule en 2 phases : la charge et la décharge.

Lors de la charge, la machine puis le joueur, alternativement,
tirent un coup sec de 3 dés tant que le pot n'est pas vide.

Le joueur ayant la combinaison la plus faible reçoit du pot le nombre de jetons correspondant à celui de la meilleure
combinaison.
La combinaison la plus faible est appelé 'Nénette', le joueur reçoit alors 2 jetons du pot immédiatement, en plus des
jetons de la meilleure combinaison.


Lors de la décharge, le joueur puis la machine tirent 3 dés,
puis peuvent choisir de changer 1, 2 ou 3 dés, jusqu'à 2 fois.

La machine doit faire au plus le même nombre de lancers que le joueur.

Celui qui a obtenu la meilleure combinaison donne alors à son adversaire le nombre de jetons correspondant
à sa combinaison.

En cas de Nénette, le joueur reçoit immédiatement 2 jetons de son adversaire en plus des jetons que l'adversaire doit
lui donner.

S'il y a égalité à la décharge, les joueurs sont départagés par un coup sec, qui définira le nombre de jetons à donner
au perdant.

La phase de décharge recommence tant que les deux joueurs ont des jetons.

Le premier à se débarraser entièrement de ses jetons gagne.
"""

"""This code requires Python 3.6 (absolute requirement because of f-strings and class variables annotations) AND
(if you want to understand a majority of variable names) knowing a bit of French to understand both the code and the
console output (Sorry, would need a translator for that as I don't have the time to do it).
It opens a browser window with the report created on the fly with the results of your game."""

"""I added (will add) English comments to help non-French speakers to help understand (a bit) the code."""

"""Further note: the code was made hastily, in about a week, so it might not be completely Pythonic and I don't feel
like going through it again for now"""

from collections import defaultdict
import os.path
from random import randint
import webbrowser

# Note: yes, I did that by hand
combinaisons = {'421': (1, 8), '111': (2, 7), '611': (3, 6), '666': (4, 6), '511': (5, 5), '555': (6, 5), '411': (7, 4),
                '444': (8, 4), '311': (9, 3), '333': (10, 3), '211': (11, 2), '222': (12, 2), '654': (13, 2),
                '543': (14, 2), '432': (15, 2), '321': (16, 2), '665': (17, 1), '664': (18, 1), '663': (19, 1),
                '662': (20, 1), '661': (21, 1), '655': (22, 1), '653': (23, 1), '652': (24, 1), '651': (25, 1),
                '644': (26, 1), '643': (27, 1), '642': (28, 1), '641': (29, 1), '633': (30, 1), '632': (31, 1),
                '631': (32, 1), '622': (33, 1), '621': (34, 1), '554': (35, 1), '553': (36, 1), '552': (37, 1),
                '551': (38, 1), '544': (39, 1), '542': (40, 1), '541': (41, 1), '533': (42, 1), '532': (43, 1),
                '531': (44, 1), '522': (45, 1), '521': (46, 1), '443': (47, 1), '442': (48, 1), '441': (49, 1),
                '433': (50, 1), '431': (51, 1), '422': (52, 1), '332': (53, 1), '331': (54, 1), '322': (55, 1),
                '221': (56, 0)}


def input_user(input_phrase=''):
    # makes sure the user typed exactly 3 characters
    user = ''
    while len(user) != 3:
        user = input(input_phrase)
    return user


# This represents the common behaviour of combinations
class Combinaison:
    """Repésentation ds différentes combinaisons"""
    
    def __init__(self, combo: str):
        self.combo = combo
        self.place, self.jetons = combinaisons[self.combo]
    
    # Overriding this function and __lt__ is necessary: I rely on the order of combinations
    def __eq__(self, other):
        return self.place == other.place
    
    def __lt__(self, other):
        # A combination is lower (worse) if it has a higher rating
        return self.place > other.place
    
    # Used to shorten the combination representation and make it possible to loop over its str representation
    # I could have used the iterator protocol, but didn't feel like it.
    def __str__(self):
        return self.combo
    
    # If you ever need to see it. Used it for the debug, not necessary, but nice nontheless
    def __repr__(self):
        return ', '.join((str(self.combo), 'place : ' + str(self.place), 'jetons : ' + str(self.jetons)))


# This is the worse possible combination, it has special rules if one of the opponents gets it.
nenette = Combinaison('221')


# The computer and its behaviour
class IA:
    """Comportement de l'IA"""
    
    def __init__(self, jetons=0):
        self.jetons: int = jetons  # Stores the number of chips the computer has
        self.combinaison: Combinaison = None  # Stores the combination of the computer (of type Combinaison)
    
    # Console representation
    def __str__(self):
        return "La machine"
    
    # Debug representation (see note for Combination.__repr__)
    def __repr__(self):
        return ' : '.join((str(self), str(self.jetons) + ' jetons'))
    
    # Usage:
    # computer = IA()
    # new_combination = computer(first_combination, number_of_tries)
    def __call__(self, combinaison, nb_essais):
        # It tries to throw a better combination in the number of remaining times (number_of_tries - 1)
        for _ in range(nb_essais - 1):
            self.combinaison = self.garde_ou_pas(combinaison)
        return self.combinaison
    
    @staticmethod
    def garde_ou_pas(combinaison):
        """
        Vérifie si la combinaison de la machine est avantageuse ou non:
        Tout chiffre au dessus de 5 ou combinaison au moins 12è est gardé à chaque tour.
        """
        # This function is used in the unloading part of the game (you need French for that, sorry)
        
        # If the combination is '222' or better
        # I might have underestimated the strategy of the computer, as I seem to win pretty much all of my games...
        if combinaison.place >= 12:
            return combinaison
        nouvelle_combinaison = ''
        for chiffre in str(combinaison):  # That's why wee need Combinaison.__str__
            # Every digit over five in the combination is kept
            if int(chiffre) >= 5:
                nouvelle_combinaison += chiffre
            else:
                # otherwise, get another throw.
                nouvelle_combinaison += str(randint(1, 6))
        # The combination is always in the decreasing order (long live the ASCII encoding comparison order)
        return Combinaison(''.join(sorted(nouvelle_combinaison, reverse=True)))
    
    # This is used as a shortcut.
    # computer = IA()
    # Usage:
    # computer += chips (instead of computer.jetons += chips)
    def __iadd__(self, jetons: int):
        self.jetons += jetons
        return self
    
    # As for __iadd__, used as a shortcut:
    # computer -= chips instead of computer.jetons -= chips
    def __isub__(self, jetons: int):
        self.jetons -= jetons
        return self
    
    # Ordering between the player and the computer, relies on combination order
    def __lt__(self, other):
        return self.combinaison < other.combinaison
    
    def __eq__(self, other):
        return self.combinaison == other.combinaison


class Joueur:
    """Caractéristiques du Joueur"""
    
    def __init__(self, nom, jetons=0):
        self.nom: str = nom  # Here is your name"
        self.jetons = jetons
        self.nb_lancers = 0  # As you go first in the unloading part, the computer can't do more throws than you did
        self.combinaison = None
    
    # Console representation, just your name
    def __str__(self):
        return self.nom
    
    # Name : jetons
    def __repr__(self):
        return ' : '.join((str(self), str(self.jetons) + ' jetons'))
    
    # Shortcut (see IA.__iadd__ and IA.__isub__)
    def __iadd__(self, jetons: int):
        self.jetons += jetons
        return self
    
    def __isub__(self, jetons: int):
        self.jetons -= jetons
        return self
    
    # Ordering between player and Computer
    def __lt__(self, other: IA):
        return self.combinaison < other.combinaison
    
    def __eq__(self, other):
        return self.combinaison == other.combinaison


# The loading part of the game:
# The computer goes first
# All throws are "dry" (no rethrows)
# The game needs confirmation before throwing you dice
class Charge:
    """Comportement du jeu lors de la charge"""
    
    def __init__(self, joueur, machine, pot=21):
        self.joueur = joueur
        self.machine = machine
        self.pot = pot
        self.evenements = {'phase': 'Charge',
                           'repartition': []}  # repartition is a list of dicts
        self.transferts = []
        self.combinaisons = defaultdict(list)
    
    # A dry throw
    @staticmethod
    def _coup():
        """Tire un coup sec"""
        return Combinaison(''.join(sorted([str(randint(1, 6)) for _ in range(3)], reverse=True)))
    
    # If one of the players gets a "nénette" (221) (*receveur* got it):
    # *receveur* gets 2 chips from the pot in addition to the ones he gets because of the throw of the other player
    def _fait_nenette(self, receveur) -> None:
        """Comportement si *receveur* fait Nénette"""
        # You only give 2 if there is enough in the pot
        mini = min(2, self.pot)
        print(receveur, "a fait Nénette, il/elle reçoit", mini, "jetons du pot.")
        
        # Change the states of *receveur* and of the pot
        receveur += mini
        self.pot -= mini
    
    def _recoit_jetons(self, receveur, jetons) -> None:
        mini = min(self.pot, jetons)  # Le joueur reçoit *jetons* s'il y a assez de jetons dans le pot
        print(receveur, "reçoit", mini, "jetons du pot")
        receveur += mini
        self.pot -= mini
        if receveur.combinaison == nenette:
            mini = min(self.pot, mini + 2)
            self.transferts.append("Pot -> " + str(receveur) + " : " + str(mini) + ' (Nénette)')
            return None
        self.transferts.append("Pot -> " + str(receveur) + " : " + str(mini))
    
    def __call__(self):
        if self.pot == 0:
            return self.joueur, self.machine, self.evenements
        print("Phase de charge")
        print("Il y a", self.pot, "jetons dans le pot")
        repartition = {str(self.joueur): self.joueur.jetons, str(self.machine): self.machine.jetons, 'pot': self.pot}
        self.evenements['repartition'].append(repartition)
        self.machine.combinaison = combo_m = self._coup()
        print(self.machine, "a fait", combo_m)
        self.combinaisons[str(self.machine)].append(str(combo_m))
        
        # On attend la validation du joueur pour lancer les dés pour "ajouter" du hasard
        input("Appuyez sur entrée pour lancer les dés")
        self.joueur.combinaison = combo_j = self._coup()
        print(self.joueur, "a fait", combo_j)
        self.combinaisons[str(self.joueur)].append(str(combo_j))
        
        if combo_j == combo_m:
            print("Egalité, on rejoue le tour")
            self.transferts.append('Egalité : aucun transfert')
            self()
        elif combo_j < combo_m:
            if combo_j == nenette:
                self._fait_nenette(self.joueur)
            jetons = combo_m.jetons
            
            self._recoit_jetons(self.joueur, jetons)
        
        else:
            if combo_m == nenette:
                self._fait_nenette(self.machine)
            jetons = combo_j.jetons
            
            self._recoit_jetons(self.machine, jetons)
        print()
        self.evenements['transferts'] = self.transferts
        self.evenements['combinaisons'] = dict(self.combinaisons)
        
        yield self.pot, self.joueur, self.machine


class Decharge:
    """Code de la décharge"""
    
    def __init__(self, joueur, machine):
        self.joueur = joueur
        self.machine = machine
        
        self.evenements = {'phase': 'Décharge', 'repartition': []}
        self.tranferts = []
        self.combinaisons = defaultdict(list)
    
    @staticmethod
    def _coup():
        """Tire un coup sec"""
        return Combinaison(''.join(sorted([str(randint(1, 6)) for _ in range(3)], reverse=True)))
    
    @staticmethod
    def relancer(combinaison, user_input):
        """Relance les dés en fonction de l'indication de l'utilisateur"""
        nouveau = ''
        for chiffre, usr in zip(str(combinaison), user_input):
            if chiffre == usr:
                nouveau += chiffre
            else:
                nouveau += str(randint(1, 6))
        return Combinaison(''.join(sorted(nouveau, reverse=True)))
    
    def _decharge_utilisateur(self):
        i, user_input = 1, None
        
        combo = self._coup()
        
        while not (user_input == str(combo) or i >= 3):
            print("Vous avez fait ", combo)
            print("Il vous reste", 3 - i, "lancers pour faire mieux")
            user_input = input_user("Entrez les changements à faire (0 change relance le dé, le chiffre garde le dé)")
            combo = self.relancer(combo, user_input)
            
            i += 1
        
        print("Vous avez fait", combo)
        self.joueur.nb_lancers = i
        self.joueur.combinaison = combo
        self.combinaisons[str(self.joueur)].append(str(self.joueur.combinaison))
    
    def _decharge_machine(self):
        combo = self._coup()
        self.machine(combo, self.joueur.nb_lancers)
        print(self.machine, "a fait", self.machine.combinaison)
        self.combinaisons[str(self.machine)].append(str(self.machine.combinaison))
    
    def _fait_nenette(self, receveur, donneur):
        mini = min(2, donneur.jetons)
        print(receveur, "a fait Nénette. Il/elle reçoit", mini, "jetons de", donneur)
        
        donneur -= mini
        receveur += mini
    
    def _donne_jetons(self, receveur, donneur, jetons):
        mini = min(jetons, donneur.jetons)
        print(receveur, "reçoit", mini, "jetons de", donneur)
        donneur -= mini
        receveur += mini
        if receveur.combinaison == nenette:
            mini = min(donneur.jetons, mini + 2)
            self.tranferts.append(str(donneur) + " -> " + str(receveur) + " : " + str(mini) + ' (Nénette)')
            return
        self.tranferts.append(str(donneur) + " -> " + str(receveur) + " : " + str(mini))
    
    def _trouver_max(self):
        if self.joueur == self.machine:
            self.egalite()
        elif self.joueur < self.machine:
            if self.joueur.combinaison == nenette:
                self._fait_nenette(self.joueur, self.machine)
            jetons = self.machine.combinaison.jetons
            self._donne_jetons(self.joueur, self.machine, jetons)
        else:
            if self.machine.combinaison == nenette:
                self._fait_nenette(self.machine, self.joueur)
            jetons = self.joueur.combinaison.jetons
            self._donne_jetons(self.machine, self.joueur, jetons)
    
    def egalite(self):
        """S'il y a égalité, les joueurs sont départagés par un coup sec"""
        print("Rampo !")
        
        self.tranferts.append("Egalité, pas de tranfert")
        
        self.machine.combinaison, self.joueur.combinaison = self._coup(), self._coup()
        
        print(self.machine, "a fait", self.machine.combinaison)
        
        print(self.joueur, "a fait", self.joueur.combinaison)
        
        self.combinaisons[str(self.joueur)].append(str(self.joueur.combinaison))
        
        self.combinaisons[str(self.machine)].append(str(self.machine.combinaison))
        
        self._trouver_max()
    
    def __call__(self):
        if self.joueur.jetons == 0:
            self.evenements['gagnant'] = str(self.joueur)
            return self.evenements
        elif self.machine.jetons == 0:
            self.evenements['gagnant'] = str(self.machine)
            return self.evenements
        print("Phase de décharge")
        self.evenements['repartition'].append({str(self.joueur): self.joueur.jetons,
                                               str(self.machine): self.machine.jetons})
        self._decharge_utilisateur()
        
        self._decharge_machine()
        
        self._trouver_max()
        
        print()
        
        self.evenements['combinaisons'] = dict(self.combinaisons)
        self.evenements['transferts'] = self.tranferts
        yield self.joueur, self.machine


class Manche:
    """Une manche complète de 421 à 2 joueurs : humain contre machine"""
    
    def __init__(self, joueur=Joueur('Exemple'), machine=IA(), pot=21):
        self.joueur = joueur
        self.machine = machine
        self.pot = pot
        self.evenements = {}
        self.i = 0
    
    def __call__(self):
        charge = Charge(self.joueur, self.machine, self.pot)
        while True:
            try:
                self.pot, self.joueur, self.machine = next(charge())
            except StopIteration as e:
                self.joueur, self.machine, self.evenements['charge'] = e.value
                break
        decharge = Decharge(self.joueur, self.machine)
        
        while True:
            try:
                self.joueur, self.machine = next(decharge())
            except StopIteration as e:
                self.evenements['decharge'] = e.value
                break
        
        return self.evenements


def evenements_html(joueurs, evenements, fichier):
    """Met les événements de *evenements* dans le fichier *fichier* au format HTML et l'ouvre dans le navigateur."""
    charge = evenements['charge']
    decharge = evenements['decharge']
    joueur, machine = joueurs
    
    table = ["""<table>
    <tr>
    <th>N° tour</th>
    <th>Phase</th>
    <th>Répartition avant le tour</th>
    <th>Combinaison joueur</th>
    <th>Combinaison machine</th>
    <th>Transfert</th>
    </tr>
    """]
    
    longueur_charge = len(charge['combinaisons'][str(joueur)])
    
    for i in range(longueur_charge):
        ligne = ['<tr>\n<td>', str(i + 1), '</td>\n<td>']
        ligne.extend([charge['phase'], '</td>\n<td>', str(charge['repartition'][i]), '</td>\n <td>',
                      str(charge['combinaisons'][str(joueur)][i]), '</td>\n<td>',
                      str(charge['combinaisons'][str(machine)][i]), '</td>\n<td>', charge['transferts'][i],
                      '</td>\n</tr>'])
        table.append(''.join(ligne))
    
    longueur_decharge = len(decharge['combinaisons'][str(joueur)])
    
    for k in range(longueur_decharge):
        ligne = ['<tr>\n<td>', str(k + longueur_charge + 1), '</td>\n<td>']
        ligne.extend([decharge['phase'], '</td>\n<td>', str(decharge['repartition'][k]), '</td>\n<td>',
                      str(decharge['combinaisons'][str(joueur)][k]), '</td>\n<td>',
                      str(decharge['combinaisons'][str(machine)][k]), '</td>\n<td>',
                      decharge['transferts'][k], '</td>\n<tr>'])
        table.append(''.join(ligne))
    
    table = ''.join(table)
    html = f"""<!doctype html>
    <html>
    <head>
        <meta charset="Windows-1252" />
        <meta charset="iso-8859-15" />
        <title>Partie {str(joueur)} contre {str(machine)}</title>
        <style>table, tr, td, th {{
            border: 1px solid black;
            border-collapse: collapse
        }}
        </style>
    </head>
    
    <body>
        <h1>Partie de {str(joueur)} contre {str(machine)}</h1>
        
        <h2>Compte rendu</h2>
        
        <h3>Gagnant : {decharge['gagnant']}</h3>
        
        {table}
    </body>
    </html>"""
    
    with open(fichier, 'w') as f:
        f.write(html)
    
    webbrowser.open(''.join(('file:///', os.path.abspath(fichier))))


def jouer_partie(joueur: Joueur, machine: IA, pot: int = 21):
    """Joue la partie *joueur* contre *machine* avec un pot initial de *pot*"""
    manche = Manche(joueur, machine, pot)
    
    evenements = manche()
    evenements_html((joueur, machine), evenements, 'partie.html')


if __name__ == '__main__':
    nom = input("Entrez votre nom")
    
    
    def _valider_int():
        entree = None
        while entree is None:
            try:
                entree = int(input("Entrez le nombre de jetons avec lequel vous jouez"))
            except ValueError:
                print("Ce nombre doit être un entier, entrée invalide")
                entree = None
        return entree
    
    
    jouer_partie(Joueur(nom), IA(), _valider_int())
