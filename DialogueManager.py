from langchain_core.messages import HumanMessage,AIMessage
from enum import Enum


class Role(Enum):
    USER = "user"
    NPC = "npc"

class DialogueManager:
    def __init__(self, max_history) -> None:
        self.dialogues = {}
        self.max_history = max_history
        print("DIALOGUE MANAGER: Sono stato creato")

    def add(self, id: str, ruolo: Role, messagge: str):
        if id not in self.dialogues:
            self.dialogues[id] = Dialogue()
            self.dialogues[id].add(ruolo, messagge, self.max_history)
        else:
            self.dialogues[id].add(ruolo, messagge, self.max_history)
    
    def get_chat_history(self, id: str) -> str:
        i = self.dialogues.get(id)
        if i:
            return i.messages
        return []

class Dialogue:
    def __init__(self) -> None:
        self.messages = []
        
    def add(self, ruolo: Role, messaggio: str, max_history: int):
        if ruolo == Role.USER:
            self.messages.append(HumanMessage(content=messaggio))
        else:
            self.messages.append(AIMessage(content=messaggio))
        if len(self.messages) > max_history:
            self.messages = self.messages[-max_history:]

    def __str__(self) -> str:
        return str(self.messages)
    
    def to_string(self) -> str:
        stringa = ""
        for messaggio in self.messages:
            if isinstance(messaggio, HumanMessage):
                stringa += "USER: "
            else:
                stringa += "NPC: "
            stringa += messaggio.content
            stringa += "\n"
        return stringa