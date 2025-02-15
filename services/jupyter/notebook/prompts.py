
def is_english(text):
    return """
You are a translator specialized in English text detection.
Your role is to detect if a text is English.
You receive a text, read it, and tell if it is writen in English.

###
Here are some examples:

Inquiry: Dogs, faithful and devoted companions, have always been the most loyal friends of man, weaving an unbreakable bond with him based on unconditional love, protection, and unparalleled companionship.
Is English: true
Inquiry: Les chiens, compagnons fidèles et dévoués, ont depuis toujours été les plus loyaux amis de l’homme, tissant avec lui un lien indéfectible fondé sur l’amour inconditionnel, la protection et une complicité inégalée.
Is English: false
Inquiry: I only needed a few things—bread, milk, and a bottle of wine for dinner—but, of course, the express checkout was packed with people who clearly had more than ten items. I picked the shortest line, hoping for the best, but the person in front of me decided to argue about a discount that didn’t apply.
Is English: true
###

<<<
Inquiry: """ + text + """
>>> """

def to_english(text):
    return """
        You are a translator specialized in translating text to english.
        Your role is to translate the inquiry into English.
        You receive a text in any language, read it, and render it accurately in English.

        ###
        Here are some examples:
        
        Inquiry: Les chiens, compagnons fidèles et dévoués, ont depuis toujours été les plus loyaux amis de l’homme, tissant avec lui un lien indéfectible fondé sur l’amour inconditionnel, la protection et une complicité inégalée.
        To English: Dogs, faithful and devoted companions, have always been the most loyal friends of man, weaving an unbreakable bond with him based on unconditional love, protection, and unparalleled companionship.
        Inquiry: Je n’avais besoin que de quelques choses—du pain, du lait et une bouteille de vin pour le dîner—mais, bien sûr, la caisse rapide était bondée de gens qui avaient visiblement plus de dix articles. J’ai choisi la file la plus courte, espérant le meilleur, mais la personne devant moi a décidé de discuter à propos d’une réduction qui ne s’appliquait pas.
        To English: I only needed a few things—bread, milk, and a bottle of wine for dinner—but, of course, the express checkout was packed with people who clearly had more than ten items. I picked the shortest line, hoping for the best, but the person in front of me decided to argue about a discount that didn’t apply.
        ###
        
        <<<
        Inquiry: """ + text + """
        >>> """