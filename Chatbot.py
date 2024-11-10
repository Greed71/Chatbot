from quart import Quart,request,jsonify
import uvicorn
import json
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from DialogueManager import DialogueManager
from Chains import CatenonaDiDio, create_witnesses_chain, create_intro_chain
from Narratore import Narratore
from ListaNPC import ListaNPC
from ContextManager import ContextManager
from langchain_core.runnables import Runnable


app = Quart(__name__)
LLM: Runnable = None
LLM_NO_LIMIT: Runnable = None
CHAIN: CatenonaDiDio = None
DIALOGUE_MANAGER: DialogueManager = None
CONTEXT_MANAGER: ContextManager = None
LISTA_NPC: ListaNPC = None

async def AI(user_input):
    response = await CHAIN.ainvoke(user_input)
    print(response)
    last_message = response['npc_message']
    return last_message

@app.route("/chat", methods = ['POST'])
async def chat():
    try:
        data = await request.get_json()
        print(data)
        response = await AI(data)
        return app.response_class(
            response=json.dumps({"response": response}, ensure_ascii=False),
            status=200,
            mimetype='application/json')
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "Nope"})

@app.route("/begin", methods = ['GET'])
async def begin():
    try:
        response = start()
        print("RESPONSE: ", response)
        print("La lunghezza è: ",len(response))
        return app.response_class(
            response=json.dumps({"response": response}, ensure_ascii=False),
            status=200,
            mimetype='application/json')
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "Nope"})

@app.route("/get_assassin", methods = ['GET'])
async def get_assassin():
    try:
        assassin = LISTA_NPC.get_assassin().name
        return app.response_class(
            response=json.dumps({"response": assassin}, ensure_ascii=False),
            status=200,
            mimetype='application/json')
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "Nope"})

def main():
    uvicorn.run(app,host="0.0.0.0", port=9669)

def start():
    print("it's starting time!")
    global LLM, LLM_NO_LIMIT, DIALOGUE_MANAGER, CONTEXT_MANAGER, NARRATOR, LISTA_NPC, CHAIN
    load_dotenv(find_dotenv())
    LLM = ChatOpenAI(model = 'gpt-4o-mini', temperature = 0.2, max_tokens= 60)
    LLM_NO_LIMIT = ChatOpenAI(model = 'gpt-4o-mini', temperature = 1)
    LLM_2 = ChatOpenAI(model = 'gpt-4o-mini', temperature = 0, max_tokens= 200)
    DIALOGUE_MANAGER = DialogueManager(12)
    NARRATOR = Narratore(LLM_NO_LIMIT)
    LISTA_NPC = ListaNPC()
    assassino = LISTA_NPC.get_assassin()
    vittima = LISTA_NPC.get_victim()
    general_context = NARRATOR.generate_context(assassino, vittima)
    CONTEXT_MANAGER = ContextManager(general_context, LISTA_NPC)
    witness_chain = create_witnesses_chain(LLM_NO_LIMIT)
    CONTEXT_MANAGER.witness_context(witness_chain)
    CONTEXT_MANAGER.assassin_context()
    CONTEXT_MANAGER.agent_context()
    CHAIN = CatenonaDiDio(LLM, "CatenonaDiDio", DIALOGUE_MANAGER, CONTEXT_MANAGER)
    return intro(general_context, LLM_2, assassino.name)
    
def intro(general_context, llm, assassin_name):
    st = ""
    st += str(general_context.get("Vittima", "")) + " " + str(general_context.get("Modalita", ""))
    print("INTRO: " + st)
    chain = create_intro_chain(llm)
    general_context = st.replace(assassin_name, "il Killer")
    return chain.invoke(general_context)

main()