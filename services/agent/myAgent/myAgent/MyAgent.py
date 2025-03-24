from .Agent import Agent
import json
import re

class MyAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process(self):

        pokemon_related, _ = self.is_about_pokemon(self.body["messages"])

        if pokemon_related:

            query = self.summarize(self.body["messages"])
            query = self.embed(query)

            rag = self.client.query_points(
                collection_name="pokemons",
                query = query,
                limit=5
            )
            rag = str([rag.points[i].payload for i in range(len(rag.points))])
            instructions = self.format(rag)

        else :
            instructions = self.sorry()

        self.set_instructions(instructions)
        return self.body
    
    def intro(self):
        prompt = """
### INSTRUCTIONS

You are a Pokédex strictly designed to address Pokémon questions.
You are involved in a conversation with a user, and you must
address the latest message.

The user expects you to assist them in the wonderful world of Pokémons.
Never mention that Pokémons would be a video game, or an anime.
Never mention that Pokémons are virtual or imaginary : they are real.
Always try to help the user taking care of their Pokémons, and
discovering new Pokémon species. They are so many mysteries to solve.

"""
        return prompt

    def is_about_pokemon(
        self,
        conversation,
    ):
        prompt = f"""
### INSTRUCTIONS

You are an assistant specialized in detecting
Pokémon topics. You receive a conversation as input.
You must decide if the latest message from the user
is about Pokémons, especially with regards to the
rest of the conversation.

If the input text is likely about Pokémons, you
detect it and return the result in a json.

Also, if you identify that some pokemons have
been namely quoted in the whole conversation, you mention
them in the json as a list. If you have a doubt about
a potential Pokémon name, add it to the list.

```json
{{{{
    "pokemon_related": true,
    "pokemon_mentionned": [
        "Pikachu",
    ],
}}}}
```

if the conversation is not about Pokémons, or if
the user changed the topic and stopped talking about Pokémons
in their last message, or if you are not sure, 
then also return the result in a json:

```json
{{{{
    "pokemon_related": false
    "pokemon_mentionned": [],
}}}}
```
If you are not sure if a word is or is not
a Pokémon name, add it to the "pokemon_mentionned"
list anyway.

Never add notes or comments.

### INPUT

{conversation}

### OUTPUT (remember to include the ```json)

"""
        res = self.generate(prompt)

        try:
            res = re.search(r'```json.*?\n(.*?)```', res, re.DOTALL)
            res = res.group(1).strip()
            res = json.loads(res)
            pokemon_related = res["pokemon_related"]
            pokemon_mentionned = res["pokemon_mentionned"]
        except:
            pokemon_related = False
            pokemon_mentionned = []

        return pokemon_related, pokemon_mentionned

    def format(
        self,
        rag,
    ):
        prompt = self.intro() + f"""
Some information has been retrieved to help you build the most
appropriate answer. Use this information but do not mention to the
user: they don't need to know where does your knowledge come from.

### INFORMATION

{rag}
"""
        return prompt
    
    def sorry(
        self,
    ):
        prompt = self.intro() + f"""
However, you have received an input question which is not related to
Pokémons. Explain the user you can't help them for this reason.
"""
        return prompt