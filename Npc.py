from enum import Enum


class Game_Role(Enum):
    ASSASSINO = "Assassino"
    CIVILE = "Civile"
    AGENTE = "Agente"
    VITTIMA = "Vittima"
    TESTIMONE = "Testimone"

class Npc:

    def __init__(self, name, job, interest="", game_role= Game_Role.CIVILE, attitude = "Rilassato"):
        self.name = name
        self.job = job
        self.game_role = game_role
        self.attitude = attitude
        self.interest = interest
        self.relations = []
    
    def get_relations(self):
        pippo = ""
        for relation in self.relations:
            pippo += str(relation) + "\n"
        return pippo

    def __str__(self):
        return self.name + " - " + self.job + " - " + self.interest