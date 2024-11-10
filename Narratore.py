from Npc import Npc
from Chains import create_narrator_chain


class Narratore:

    def __init__(self,llm):
        self.chain = create_narrator_chain(llm)
        print("NARRATORE: Sono stato creato")

    def generate_context(self, assassin: Npc, victim: Npc):
        input = {
            "nome_assassino":assassin.name,
            "lavoro_assassino":assassin.job,
            "nome_vittima":victim.name,
            "lavoro_vittima":victim.job,
            "interest_assassino":assassin.interest,
            "interest_vittima":victim.interest
        }
        print("NARRATORE: Sto creando il contesto")
        resolve = self.chain.invoke(input)
        print(resolve)
        return resolve

