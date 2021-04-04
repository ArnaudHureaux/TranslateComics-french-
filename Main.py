#Ici il faut mettre les inputs de son code :
#La langue du texte à traduire
LANGUE_DEPART='EN'
#La langue dans laquelle vous voulez le traduire
LANGUE_ARRIVEE='FR'
#Votre clé Deepl (obtenable en vous abonnant à l'API Deepl payante)
KEY_DEEPL='**********-****-****-****-**********'
#Le chemin de votre Clé json Google Vision (obtenable avec un compte Google Cloud, gratuit si vous faites peu d'utilisation)
GOOGLE_JSON_PATH='Keys/Vision_Key.json'

#Ici on définit le répértoire où on veut traduire toutes les images
direct='/home/arnaud/Téléchargements/BD_MEDIUM'
#Ici on crée un répertoire voisin du premier répertoire où on mettra toutes nos images traduites
os.mkdir(direct+'_TRANSLATE')

#Ici on parcoure les images de notre répertoire et on les traduit + sauvegarde dans le répertoire voisin
os.listdir(direct)
for image_path in os.listdir(direct):
    SaveTraductImage(image_path=direct+'/'+image_path, save_path=direct+'_TRANSLATE/'+image_path)
    print(image_path,' Translated')