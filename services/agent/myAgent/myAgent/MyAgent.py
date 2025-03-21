from .Agent import Agent
import json
import re

class MyAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process(self):

        pokemon_related, pokemon_mentionned = self.is_about_pokemon(self.last_message)

        if pokemon_related:

            rag = self.client.query_points(
                collection_name="pokemons",
                query = self.embed(self.last_message),
                limit=5
            )
            rag = str([rag.points[i].payload for i in range(len(rag.points))])
            instructions = self.format(rag)

        else :
            instructions = self.sorry()

        self.set_instructions(instructions)
        return self.body

    def is_about_pokemon(
        self,
        text,
    ):
        prompt = f"""
### INSTRUCTIONS

You are an assistant specialized in detecting
Pokémon topics. You receive an input text.
If the input text is likely about Pokémons, you
detect it and return the result in a json.

Also, if you identify that some pokemons have
been namely quoted, you mention them in the json
as a list.

```json
{{{{
    "pokemon_related": true,
    "pokemon_mentionned": [
        "Pikachu",
    ],
}}}}
```

if the topic is likely not about Pokémons,
or if you are note sure, also return the
result in a json:

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

{text}

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
        prompt = f"""
### INSTRUCTIONS

You are a Pokédex strictly designed to adress Pokémon questions.
You have are involved in a conversation with a user, and you must
adress the latest message.

Some information has been retrieved to help you build the most
appropriate answer.

### INFORMATION

{rag}

"""
        return prompt
    
    def sorry(
        self,
    ):
        prompt = f"""
### INSTRUCTIONS

You are a Pokédex strictly designed to adress Pokémon questions.
You have are involved in a conversation with a user, and you must
adress the latest message.

However, you have received an input question which is not related to
Pokémons. Explain the user you can't help them for this reasons.

"""
        return prompt