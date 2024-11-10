from ListaNPC import ListaNPC


class ContextManager:
    def __init__(self, general_context: dict, npcs: ListaNPC) -> None:
        self.contexts = {}
        self.general_context = general_context
        self.npcs = npcs
        self.agents = npcs.get_agents()
        self.assassin = npcs.get_assassin()
        self.victim = npcs.get_victim()
        self.witnesses = npcs.get_witnesses()
        print("CONTEXT MANAGER: Sono stato creato")
    
    def add(self, id: str, info: str):
        print("ID: ", id, "\ninfo: ", info)
        if id not in self.contexts:
            self.contexts[id] = Context()
            self.contexts[id].add(info)
        else:
            self.contexts[id].add(info)
    
    def assassin_context(self):
        self.add(self.assassin.name, str(self.general_context))

    def witness_context(self, chain):
        testimoni = " ".join([w.name for w in self.witnesses])
        i_c = chain.invoke({"contesto": self.general_context, "testimoni": testimoni})
        for k, v in i_c.items():
            self.add(k, v)
    
    def agent_context(self):
        agents = [a.name for a in self.agents]
        vittima_data = str(self.general_context.get("Vittima", "")).replace(self.assassin.name, "il Killer")
        modalita_data = str(self.general_context.get("Modalita", "")).replace(self.assassin.name, "il Killer")
        fbi_data = vittima_data + " " + modalita_data
        testimoni = ", ".join([w.name for w in self.witnesses])
        testimoni = "Testimoni: " + testimoni
        fbi_data += " " + testimoni
        for agent in agents:
            self.add(agent, fbi_data)

    def get(self, id: str):
        return self.contexts.get(id, None)
    
class Context:
    def __init__(self) -> None:
        self.info = ""
    
    def add(self, new_info):
        self.info += new_info
