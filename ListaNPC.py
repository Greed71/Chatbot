from Npc import Npc, Game_Role
import random


class ListaNPC:
    def __init__(self):
        self.npcs = [
            Npc("Francesco", "Agente FBI", "Ama fare sci nautico",Game_Role.AGENTE),
            Npc("Giuseppe", "Meccanico", "Gareggia spesso clandestinamente"),
            Npc("Giorgio", "Prete", "Ama benedire luoghi, soprattutto la scuola elementare"),
            Npc("Mattia", "Benzinaio", "è appassionato di robot giganti"),
            Npc("Marta", "Commessa negozio di liquori", "ama uscire con le amiche e divertirsi"),
            Npc("Alessandro", "Venditore di armi", "Va spesso a caccia con gli amici"),
            Npc("Michele", "Venditore di licenze", "è uno scommettitore incallito, soprattutto nelle corse di cavalli"),
            Npc("Fabio", "Fruttivendolo", "Ama i percorsi naturalistici e campeggiare"),
            Npc("Luna", "Commessa banco dei pegni", "è una ethical hacker professionista"),
            Npc("Elena", "Commessa in banca", "Gioca spesso e volentieri a padel"),
            Npc("Salvo", "Sceriffo", "Ama studiare i misteri dell'analisi matematica"),
            Npc("Daniele", "Receptionist", "Suona la batteria per un gruppo metal"),
            Npc("Mariano", "Agente FBI", "Colleziona coltelli d'epoca", Game_Role.AGENTE),
            Npc("Jessica", "Commessa dolceria", "Ama gatti e cani"),
            Npc("Tano", "Commesso 24H", "Va spesso a fare volontariato")
        ]
        self.victims = [
            Npc("Mattia", "Usuraio"),
            Npc("Giuseppe", "Assicuratore"),
            Npc("Giorgio", "Influencer"),
            Npc("Salvo", "Professore di analisi all'universita'"),
            Npc("Daniele", "Streamer"),
            Npc("Michele", "Giocatore d'azzardo"),
            Npc("Fabio", "Osteopata"),
            Npc("Mariano", "Spacciatore"),
        ]
        self.attitude = [
            "Rilassato",
            "Attento",
            "Sorpreso",
            "Evasivo",
            "Paranoico",
            "Tranquillo"
        ]
        self.witnesses: list[Npc] = []
        self.set_attitude()
        self.set_assassin()
        self.set_victim()
        self.populate_relations()
        self.show_relations()
        self.populate_witnesses(4)
        print("LISTA NPC: Sono stata creata")

    def get_witnesses(self):
        return self.witnesses

    def populate_relations(self):
        for npc in self.npcs:
            if npc.game_role == Game_Role.AGENTE:
                continue
            while len(npc.relations) < 3:
                friend = random.choice(self.npcs)
                while friend == npc or friend in npc.relations or friend.game_role == Game_Role.AGENTE:
                    friend = random.choice(self.npcs)
                npc.relations.append(friend)
                friend.relations.append(npc)

    def show_relations(self):
        for npc in self.npcs:
            relations = " ".join([relation.name for relation in npc.relations])
            print(npc.name + " - " + relations)

    def populate_witnesses(self, n):
        print("I testimoni sono: \n")
        for i in range(n):
            npc = random.choice(self.npcs)
            while npc.game_role == Game_Role.AGENTE or npc in self.witnesses or npc.game_role == Game_Role.ASSASSINO or npc.name == self.get_victim().name:
                npc = random.choice(self.npcs)
            npc.game_role = Game_Role.TESTIMONE
            self.witnesses.append(npc)
            print(self.witnesses[i].name)
            
    def get_agents(self):
        return [npc for npc in self.npcs if npc.game_role == Game_Role.AGENTE]

    def set_attitude(self):
        for npc in self.npcs:
            attitude = random.choice(self.attitude)
            while npc.game_role == Game_Role.AGENTE and attitude == "Evasivo":
                attitude = random.choice(self.attitude)
            npc.attitude = attitude
        print("LISTA NPC: Le attitudini sono state impostate")

    def set_assassin(self):
        npc = random.choice(self.npcs)
        while npc.game_role == Game_Role.AGENTE:
            npc = random.choice(self.npcs)
        npc.game_role = Game_Role.ASSASSINO
        print("LISTA NPC: L'assassino è " + str(npc))
        return npc

    def get_assassin(self):
        for npc in self.npcs:
            if npc.game_role == Game_Role.ASSASSINO:
                return npc
    
    def is_assassin(self, name):
        for npc in self.npcs:
            if npc.name == name and npc.game_role == Game_Role.ASSASSINO:
                return True
        return False

    def set_victim(self):
        npc = random.choice(self.victims)
        npc.game_role = Game_Role.VITTIMA
        print("LISTA NPC: La vittima è " + str(npc))
        return npc
    
    def get_victim(self):
        for npc in self.victims:
            if npc.game_role == Game_Role.VITTIMA:
                return npc
            
    def get_npc(self, name):
        for npc in self.npcs:
            if npc.name == name:
                return npc