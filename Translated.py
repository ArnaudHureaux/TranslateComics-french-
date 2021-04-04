#Cette fonction va traduire un texte donné
#Entrée : du texte (text), la langue du texte (source), la langue dans laquelle il faut traduire le texte (target)
#Sortie : le texte traduit dans la langue indiquée
def Translate(text):
    r =  requests.post(url='https://api.deepl.com/v2/translate',
                          data = {
                            'target_lang' : LANGUE_ARRIVEE,  
                            'source_lang' : LANGUE_DEPART,
                            'auth_key' : KEY_DEEPL,
                            'text': text
                          })
    return r.json()['translations'][0]['text']