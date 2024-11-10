from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnableSequence,
    RunnablePassthrough,
)
from abc import ABC, abstractmethod
from DialogueManager import DialogueManager, Role
from ContextManager import ContextManager
from Npc import Game_Role


class Chain(ABC):
    def __init__(self, llm: ChatOpenAI, name: str):
        self.llm = llm
        self.name = name
    
    @abstractmethod
    def run(self):
        pass

    def invoke(self, user_input):
        response = self.run().invoke(user_input)
        return response
    
    async def ainvoke(self, user_input):
        response = await self.run().ainvoke(user_input)
        return response

class FirstChainBase(Chain):
    def __init__(self, llm: ChatOpenAI, name: str, prompt: str):
        super().__init__(llm, name)
        self.prompt = prompt
    
    def fill_prompt(self):
        return PromptTemplate.from_template(self.prompt).with_config(run_name="FirstPrompt")

STD = '''
Rispondi solo come farebbe l'npc appena descritto. Non aggiungere apici o virgolette nelle risposte e nemmeno ulteriori descrizioni. \
Scrivi solo la prossima battuta del tuo personaggio. Scrivi al massimo 30 parole.
'''

class NotFirstChainBase(Chain):
    def __init__(self, llm: ChatOpenAI, name: str, prompt: str):
        super().__init__(llm, name)
        self.prompt = prompt
    
    def fill_prompt(self):
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.prompt),
                MessagesPlaceholder("messages"),
                ("system", STD)
            ]
        )

FIRST_TEMPLATE = '''
Sei in un videogioco investigativo, devi impersonare {name}, "{job}" è il tuo lavoro.\
Al momento sei {attitude}. Non hai mai parlato con il giocatore. Il giocatore è il detective che deve risolvere un caso di omicidio.\
Accogli il detective e presentati. esempio:\
"Salve detective, come posso aiutarla?"\
Aggiungi anche informazioni su te stesso, ma solo se pertinente al dialogo.\
Rispondi solo come farebbe l'npc appena descritto. Non aggiungere apici o virgolette nelle risposte e nemmeno ulteriori descrizioni.\
Scrivi solo le battute del personaggio. Scrivi al massimo 30 parole.\
'''

class FirstChain(FirstChainBase):
    def __init__(self, llm: ChatOpenAI, name: str, prompt: str):
        super().__init__(llm, name, prompt)
        print(f"\33[1;34m[{self.name}]\33[0m: Chain inizializzata")
    
    def sequence(self):
        return RunnableSequence(
            self.fill_prompt(),
            self.llm,
            StrOutputParser()
        ).with_config(run_name="FirstSequence")
    
    def get_npc_messagge(self):
        return RunnablePassthrough.assign(
            npc_message = RunnableLambda(lambda x: self.sequence())
        ).with_config(run_name="GetNPCMessage")
    
    def run(self):
        return (
            self.get_npc_messagge()
        ).with_config(run_name=self.name)

NOT_FIRST_TEMPLATE = '''
Sei in un videogioco investigativo, devi impersonare {name}, "{job}" è il tuo lavoro. I tuoi interessi sono {interest}.\
Sei amico di: {relations}. Nomina i tuoi amici o ciò che li riguardo solo se lo ritieni necessario.\
Al momento sei {attitude}. Il giocatore è un detective che deve risolvere un caso di omicidio.\
Dai informazioni pertinenti con la discussione in corso.\
Hai già parlato col giocatore e vi siete detti:\
'''

class NotFirstChain(NotFirstChainBase):
    def __init__(self, llm: ChatOpenAI, name: str, prompt: str):
        super().__init__(llm, name, prompt)
        print(f"\33[1;34m[{self.name}]\33[0m: Chain inizializzata")
    
    def sequence(self):
        return RunnableSequence(
            self.fill_prompt(),
            self.llm,
            StrOutputParser()
        ).with_config(run_name="NotFirstSequence")
    
    def get_npc_messagge(self):
        return RunnablePassthrough.assign(
            npc_message = RunnableLambda(lambda x: self.sequence())
        ).with_config(run_name="GetNPCMessage")
    
    def run(self):
        return (
            self.get_npc_messagge()
        ).with_config(run_name=self.name)

FIRST_TESTIMONE_TEMPLATE = '''
Sei in un videogioco investigativo, devi impersonare {name}, "{job}" è il tuo lavoro.\
Al momento sei {attitude}. Non hai mai parlato con il giocatore. Il giocatore è un detective che deve risolvere un caso di omicidio.\
Accogli il detective. esempio:\
"Salve detective, come posso aiutarla?"\
Aggiungi anche informazioni su te stesso, ma solo se pertinente al dialogo.\
Rispondi solo come farebbe l'npc appena descritto. Non aggiungere apici o virgolette nelle risposte e nemmeno ulteriori descrizioni.\
Scrivi solo le battute del personaggio. Scrivi al massimo 30 parole.
'''

FIRST_ASSASSIN_TEMPLATE = '''
Sei in un videogioco investigativo, devi impersonare {name}, "{job}" è il tuo lavoro.\
Al momento sei {attitude}. Non hai mai parlato con il giocatore. Il giocatore è un detective che deve risolvere un caso di omicidio.\
Tu sei l'assassino. Devi cercare di non farti scoprire. Il contesto è questo {context}.\
Rispondi solo come farebbe l'npc appena descritto. Non aggiungere apici o virgolette nelle risposte e nemmeno ulteriori descrizioni.\
Scrivi solo le battute del personaggio. Scrivi al massimo 30 parole.
'''

FIRST_FBI_TEMPLATE = '''
Sei in un videogioco investigativo e interpreti un agente dell'fbi, devi impersonare {name}. Al momento sei {attitude}.\
Non hai mai parlato con il giocatore. Il giocatore è un tuo collega e deve risolvere un caso di omicidio.\
Accogli il detective. esempio:\
"Salve detective, abbiamo un caso di omicidio" ed aggiungi qualche dettaglio.\
Tu hai informazioni riguardanti l'omicidio. Tu sai questo {context}\
Le informazioni che hai sul contesto non rivelarle se non esplicitamente richiesto.\
Rispondi solo come farebbe un agente dell'fbi. Non aggiungere apici o virgolette nelle risposte e nemmeno ulteriori descrizioni.\
Scrivi solo le battute del personaggio. Scrivi al massimo 30 parole.\
'''

NOT_FIRST_TESTIMONE_TEMPLATE = '''
Sei in un videogioco investigativo, devi impersonare {name}, "{job}" è il tuo lavoro. Al momento sei {attitude}.\
I tuoi interessi sono {interest}. Il giocatore è un detective che deve risolvere un caso di omicidio.\
Sei amico di: {relations}. Nomina i tuoi amici o ciò che li riguardo solo se lo ritieni necessario.\
Tu hai informazioni riguardanti l'omicidio. Tu sai questo {context}\
Le informazioni che hai sul contesto non rivelarle se non esplicitamente richiesto.\
Non nominare l'assassino direttamente nel caso in cui tu sappia chi è, ma se richiesto aiuta il giocatore.\
Se ti vengono chieste informazioni che non possiedi non inventare fatti, limitati a dire che non ne sai niente o che non sai altro\
es: user: "Sai le abitudini dell'assassino?", npc: "Purtroppo non so come aiutarla".\
Le informazioni che hai sul contesto non rivelarle se non esplicitamente richiesto.\
Hai già parlato col giocatore e vi siete detti:\
'''

NOT_FIRST_FBI_TEMPLATE = '''
Sei in un videogioco e interpreti un agente dell'fbi, devi impersonare {name}. Al momento sei {attitude}.\
I tuoi interessi sono {interest}. Il giocatore è un tuo collega e deve risolvere un caso di omicidio.\
Tu hai informazioni riguardanti l'omicidio. Tu sai questo {context}\
Se ti vengono chieste informazioni che non possiedi non inventare fatti, limitati a dire che non ne sai niente o che non sai altro\
es: user: "Mi sai dire il nome dell'assassino?", npc: "Non siamo ancora riusciti a trovarlo, è per questo che sei qui".\
Le informazioni che hai sul contesto non rivelarle se non esplicitamente richiesto.\
Hai già parlato col giocatore e vi siete detti:\
'''

NOT_FIRST_ASSASSIN_TEMPLATE = '''
Sei in un videogioco investigativo, devi impersonare {name}, "{job}" è il tuo lavoro. Al momento sei {attitude}.\
I tuoi interessi sono {interest}. Il giocatore è un detective che deve risolvere un caso di omicidio.\
Sei amico di: {relations}. Nomina i tuoi amici o ciò che li riguardo solo se lo ritieni necessario.\
Tu sei l'assassino. Devi cercare di non farti scoprire. Il contesto è questo {context}.\
Se le accuse che ti vengono fatte sono pertinenti col contesto, puoi negarle se vuoi, ma se diventano insistenti o sono inequivocabili confessa.\
Hai già parlato col giocatore e vi siete detti:\
'''

ATTITUDE_TEMPLATE = '''
In base a quello che ti ha appena detto l'utente valuta se cambiare il tuo umore attuale in uno di questi:\
- Arrabbiato: Se il giocatore ti insulta diventa Arrabbiato\
- Sorpreso: Se il giocatore ti dice qualcosa di assurdo diventa Sorpreso\
- Evasivo: Se il giocatore ti accusa di qualcosa diventa Evasivo\
- Paranoico: Se ti fanno domande che ti fanno pensare che si stia indagando su di te, o pensi di essere in pericolo diventa Paranoico\
- Tranquillo: Se il giocatore ti tranquillizza diventa Traqnuillo\
Se non ritieni opportuno cambiarlo restituisci l'attitude iniziale.\
Restituiscimi un json impostato in questa maniera:\
{{"attitude": "Arrabbiato"}}, {{"attitude": "Paranoico"}}, {{"attitude": "Evasivo"}},...
'''

class AttitudeModifier(Chain):
    def __init__(self, llm: ChatOpenAI, name: str):
        super().__init__(llm, name)
        print("\33[1;34m[AttitudeModifier]\33[0m: Attitude inizializzata")
    
    def fill_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", "Stai interpretando un npc in un gioco investigativo, il giocatore è un detective. Al momento sei {attitude}."),
            ("user", "{message}"),
            ("system", ATTITUDE_TEMPLATE)
        ])

    def sequence(self, user_input):
        sequence = RunnableSequence(
            self.fill_prompt(),
            self.llm,
            JsonOutputParser()
        ).with_config(run_name="FirstSequence")
        return sequence.invoke(user_input)

    def update_attitude(self, initial_d : dict, new_field : dict):
        initial_d["attitude"] = new_field.get("attitude", "Tranquillo")
        return initial_d

    def run(self):
        return (
            RunnableLambda(lambda x:self.update_attitude(x, self.sequence(x)))
        ).with_config(run_name=self.name)

class FirstBigChain(Chain):
    def __init__(self, llm: ChatOpenAI, name: str, dialogue: DialogueManager, context: ContextManager):
        super().__init__(llm, name)
        self.dialogue = dialogue
        self.context = context
        self.std_chain = FirstChain(llm, "FirstChain", FIRST_TEMPLATE)
        self.testimone_chain = FirstChain(llm, "TestimoneChain", FIRST_TESTIMONE_TEMPLATE)
        self.assassin_chain = FirstChain(llm, "AssassinChain", FIRST_ASSASSIN_TEMPLATE)
        self.agents_chain = FirstChain(llm, "AgentsChain", FIRST_FBI_TEMPLATE)
        print("\33[1;34m[FirstBigChain]\33[0m: Chain inizializzata")
    
    def std(self):
        return self.std_chain.run()
    
    def get_context(self):
        return RunnablePassthrough.assign(
            context = RunnableLambda(lambda x: self.context.get(x.get("name")).info),
        )
    
    def fbi(self):
        return self.agents_chain.run()

    def testimone(self):
        return self.testimone_chain.run()
    
    def assassino(self):
        return self.assassin_chain.run()
    
    def super_branch(self):
        return (RunnableLambda(lambda x: self.get_context())
            |RunnableBranch(
            (
                RunnableLambda(lambda x: self.context.npcs.get_npc(x.get("name")).game_role == Game_Role.ASSASSINO),
                self.assassino()
            ),
            (
                RunnableLambda(lambda x: self.context.npcs.get_npc(x.get("name")).game_role == Game_Role.AGENTE),
                self.fbi()
            ),
            self.testimone()
        )).with_config(run_name="Super branch")

    def ctx_branch(self):
        return RunnableBranch(
            (RunnableLambda(lambda x: self.context.get(x.get("name")) != None),
             self.super_branch()
            ),
            self.std()
        ).with_config(run_name="Context branch")
    
    def run(self):
        return (
            self.ctx_branch()
            | RunnableLambda(lambda x: (self.dialogue.add(x.get("name"), Role.NPC, x.get("npc_message")), x)[1])
        ).with_config(run_name=self.name)

class NotFirstBigChain(Chain):
    def __init__(self, llm: ChatOpenAI, name: str, dialogue: DialogueManager, context: ContextManager):
        super().__init__(llm, name)
        self.dialogue = dialogue
        self.context = context
        self.std_chain = NotFirstChain(llm, "NotFirstChain", NOT_FIRST_TEMPLATE)
        self.testimone_chain = NotFirstChain(llm, "TestimoneChain", NOT_FIRST_TESTIMONE_TEMPLATE)
        self.assassin_chain = NotFirstChain(llm, "AssassinChain", NOT_FIRST_ASSASSIN_TEMPLATE)
        self.agents_chain = NotFirstChain(llm, "AgentsChain", NOT_FIRST_FBI_TEMPLATE)
        self.attitude_modifier = AttitudeModifier(llm, "AttitudeModifier")
        print("\33[1;34m[FirstBigChain]\33[0m: Chain inizializzata")
    
    def std(self):
        return self.std_chain.run()
    
    def get_context(self):
        return RunnablePassthrough.assign(
            context = RunnableLambda(lambda x: self.context.get(x.get("name")).info),
        )
    
    def get_messages(self):
        return RunnablePassthrough.assign(
            messages = RunnableLambda(lambda x: self.dialogue.get_chat_history(x.get("name"))),
        )

    def fbi(self):
        return self.agents_chain.run()

    def testimone(self):
        return self.testimone_chain.run()
    
    def assassino(self):
        return self.assassin_chain.run()
    
    def super_branch(self):
        return (RunnableLambda(lambda x: self.get_context())
            |RunnableBranch(
            (
                RunnableLambda(lambda x: self.context.npcs.get_npc(x.get("name")).game_role == Game_Role.ASSASSINO),
                self.assassino()
            ),(
                RunnableLambda(lambda x: self.context.npcs.get_npc(x.get("name")).game_role == Game_Role.AGENTE),
                self.fbi()
            ),
            self.testimone()
        )).with_config(run_name="Super branch")

    def ctx_branch(self):
        return RunnableBranch(
            (RunnableLambda(lambda x: self.context.get(x.get("name")) != None),
             self.super_branch()
            ),
            self.std()
        ).with_config(run_name="Context branch")
    
    def attitude(self):
        return self.attitude_modifier.run()

    
    def run(self):
        return (
            RunnableLambda(lambda x: (self.dialogue.add(x.get("name"), Role.USER, x.get("message")) if x.get("message") else None, x)[1])
            | RunnableLambda(lambda x: self.attitude().invoke(x) if x.get("message") else x)
            | RunnableLambda(lambda x: self.get_messages())
            | self.ctx_branch()
            | RunnableLambda(lambda x: (self.dialogue.add(x.get("name"), Role.NPC, x.get("npc_message")), x)[1])
        ).with_config(run_name=self.name)

class CatenonaDiDio(Chain):
    def __init__(self, llm: ChatOpenAI, name: str, dialogue: DialogueManager, context: ContextManager):
        super().__init__(llm, name)
        self.dialogue = dialogue
        self.context = context
        self.first = FirstBigChain(llm, "FirstBigChain", dialogue, context)
        self.not_first = NotFirstBigChain(llm, "NotFirstBigChain", dialogue, context)
        print("\33[1;34m[CatenonaDiDio]\33[0m: Chain inizializzata")

    def FirstBig(self):
        return self.first.run()
    
    def get_data(self):
        return RunnablePassthrough.assign(
            job = RunnableLambda(lambda x: self.context.npcs.get_npc(x.get("name")).job),
            attitude = RunnableLambda(lambda x: self.context.npcs.get_npc(x.get("name")).attitude),
            interest = RunnableLambda(lambda x: self.context.npcs.get_npc(x.get("name")).interest),
            relations = RunnableLambda(lambda x: self.context.npcs.get_npc(x.get("name")).get_relations()),
        )

    def NotFirstBig(self):
        return self.not_first.run()

    def branch(self):
        return RunnableBranch(
            (RunnableLambda(lambda x: self.dialogue.get_chat_history(x.get("name")) != []),
             self.NotFirstBig()
            ),
            self.FirstBig()
        ).with_config(run_name="Branch")
        
    def run(self):
        return (
            RunnableLambda(lambda x: self.get_data())
            | self.branch()
        ).with_config(run_name=self.name)

NARRATOR_TEMPLATE = '''
Sei un narratore per un videogioco investigativo. Il gioco è ambientato nella città collinare di Montagna, dove un detective sta indagando su un omicidio. Il tuo compito è creare un contesto coinvolgente e realistico\
per il caso di omicidio, includendo una descrizione dettagliata della vittima e dell’assassino, il movente e la modalità dell’omicidio.\
1. L’assassino è {nome_assassino}, il suo lavoro è {lavoro_assassino} e i suoi interessi sono {interest_assassino}. Descrivi la sua personalità, le sue abitudini e i suoi interessi, fornendo qualche dettaglio sulla sua reputazione in città.
2. La vittima è {nome_vittima}, il suo lavoro è {lavoro_vittima} e i suoi interessi sono {interest_vittima}. Descrivi il suo carattere, il modo in cui interagiva con gli altri e i suoi hobby,\
spiegando perché era conosciuta e apprezzata (o non apprezzata) dagli abitanti di Montagna.\
3. Crea un movente convincente per cui l’assassino ha ucciso la vittima, descrivendo il rapporto preesistente tra i due e le tensioni che hanno portato al crimine.\
4. Fornisci una descrizione del modo in cui è avvenuto l’omicidio. Assicurati che sia coerente con il contesto, ma senza specificare il nome dell’assassino, in modo che sembri che il colpevole possa essere chiunque.\
Genera il risultato in formato JSON seguendo questo esempio:\
{{
    "Vittima": "Descrizione dettagliata della vittima, il suo lavoro, hobby, personalità e il ruolo nella comunità.",
    "Assassino": "Descrizione dettagliata dell’assassino, il suo lavoro, interessi, carattere e la sua reputazione a Montagna.",
    "Movente": "Descrizione del movente, del rapporto tra vittima e assassino e delle tensioni che hanno portato all'omicidio.",
    "Modalita": "Descrizione del modo in cui è avvenuto l'omicidio, senza specificare il nome dell'assassino."
}}
'''

TESTIMONI_TEMPLATE = '''
Sei un'intelligenza artificiale per un videogioco investigativo. Dato questo contesto di un crimine:\
{contesto}\
Devi creare una testimonianza per ogni persona inclusa nella lista di testimoni: {testimoni}. Ogni testimone ha assistito a un momento diverso della scena o a dettagli specifici collegati al crimine, come persone coinvolte, rumori, oggetti o eventi sospetti.\
Linee guida:\
1. Ogni testimone deve dare informazioni realistiche basate sul contesto, senza dichiarare esplicitamente il nome dell’assassino.\
2. Invece del nome, inserisci dettagli sulla professione, interessi o tratti distintivi dell’assassino, così che il giocatore possa fare collegamenti indiretti.\
3. Le dichiarazioni devono sembrare coerenti con ciò che ogni testimone avrebbe potuto percepire e dovrebbero essere utili per un detective che cerca di risolvere il caso.\
Fornisci l'output in formato JSON, con ogni chiave come nome del testimone e ogni valore come una dichiarazione:\
Esempio:\
{{
"testimone1": "Ho visto qualcuno con in mano qualcosa di metallico, sembrava un attrezzo da giardinaggio.",
"testimone2": "Ho notato delle mele cadute a terra, mi sono chiesto se appartenessero al negozio di frutta.",
"testimone3": "Ho sentito qualcuno parlare di vecchi rancori e eredità."
}}
'''

INTRO_TEMPLATE = '''
Siamo in un videogioco investigativo. Devi scrivere un'introduzione che ha il fine di spiegare al giocatore il contesto della partita e il suo compito.\
il contesto è: {context}.\
Fammi una report a mo di documento d'indagine.Es:\
"Luogo: Città di Montagna\n
Quando: Sera tardi\n
Dove: In un vicolo vicino il negozio di dolci\n
Obiettivo: Consegna l'assassino di <nome vittima>"\
Evita apici, virgolette, asterischi, usa solo testo semplice.
Sii conciso e non dilungarti in cose inutili e non inventare ne aggiungere roba.\
Sii più coinciso e breve nella descrizione.\
'''

def create_narrator_chain(llm):
    narrator_prompt = PromptTemplate.from_template(NARRATOR_TEMPLATE)
    narrator_chain = (narrator_prompt | llm | JsonOutputParser()).with_config(run_name="Narrator")
    return narrator_chain

def create_witnesses_chain(llm):
    witnesses_prompt = PromptTemplate.from_template(TESTIMONI_TEMPLATE)
    witnesses_chain = (witnesses_prompt | llm | JsonOutputParser()).with_config(run_name="Witnesses")
    return witnesses_chain

def create_intro_chain(llm):
    intro_prompt = PromptTemplate.from_template(INTRO_TEMPLATE)
    intro_chain = (intro_prompt | llm | StrOutputParser()).with_config(run_name="Intro")
    return intro_chain
