from google.cloud import vision
from google.cloud import vision_v1

import requests
import ast

import io
from PIL import Image, ImageDraw
from enum import Enum
import os
import pandas as pd
from googletrans import Translator

from PIL import Image, ImageDraw, ImageFont
import textwrap
import time

#Cette fonction va nettoyer tous les textes identifiés dans une image en mettant des carrés blanc d'une taille adapté par dessus ces textes
#Entrées :
# (image) chemin de l'image à traduire
# (precision) seuil de précision, tous les carrés dont la précision est supérieur à cette valeur seront blanchit et traduit
# (df) table contenant les positions, contenus, précision des textes identifiés par l'api de Google
def Blanchiment(image,precision,df):
    df=df[df.Len>3]
    df=df[df.Ratio<800]
    df_prec=df[df.Confidence>precision]
    draw = ImageDraw.Draw(image)
    for k in range(len(df_prec)):
        draw.rectangle([df_prec.iloc[k].xrange[0],
                        df_prec.iloc[k].yrange[0],
                        df_prec.iloc[k].xrange[1],
                        df_prec.iloc[k].yrange[1]], fill='white')
    return image

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

#Cette fonction va analyser une image avec l'api de Google pour obtenir la table df 
#Entrée : chemin du fichier d'image à traduire (image_file), langue source(src), langue de destination(dest)
#Sortie : 
#    (df) Un tableau généré par l'api de Google indiquant :
#        Text : le texte détecté
#        Confidence : l'indice de confiance que ce texte soit bel et bien du texte (d'expérience, c'est quasi toujours du vrai texte au delà de 0.85)
#        X et Y : les 4 points délimitant le texte identifié
#        xrange et yrange : les 2 points délimitant un rectangle aligné au bord supérieur de l'image
#        Len : nombre de caractère du texte
#        Ratio : le rapport entre le volume de la bulle (largeur*hauteur) et le nombre de caractère
#        Lower Text : le text en minuscule
#        French_trad : le texte traduit en français
#
#    (df_symb) Le même tableau que df mais cette fois ci cela envoit la liste des caractères identifiés (avec leurs positions)
#    au lieu de la liste des textes identifiés, df_symb m'est utile pour déduire quelle police utilisé pour le texte de remplacement
    
def GetTables(image_file):
    image = Image.open(image_file)

    #Ici on fait une requête Google Vision
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_JSON_PATH

    client = vision.ImageAnnotatorClient()
    with io.open(image_file, 'rb') as image_file1:
            content = image_file1.read()
    content_image = vision_v1.Image(content=content)
    response = client.document_text_detection(image=content_image)
    document = response.full_text_annotation
    
    #Ici on remplit la table df contenant le texte, la traduction, la position, et la confiance
    bounds=[]
    for i,page in enumerate(document.pages):
        for block in page.blocks:
            bounds.append(block.bounding_box)
            
    all_text=[]
    all_confidence=[]
    for block in document.pages[0].blocks:
        full_text=''
        for paragraph in block.paragraphs:
            for word in paragraph.words:
                for symbol in word.symbols:
                    full_text+=symbol.text
                full_text+=' '
        all_text.append(full_text)
        all_confidence.append(block.confidence)
    
    all_x=[]
    all_y=[]
    for i in bounds:
        x=[]
        y=[]
        for k in i.vertices:
            x.append(k.x)
            y.append(k.y)
        all_x.append(x)
        all_y.append(y)
        
    df=pd.DataFrame()
    df['Text']=all_text
    df['Confidence']=all_confidence
    df['X']=all_x
    df['Y']=all_y
    df['xrange']=df['X'].apply(lambda x:[min(x),max(x)])
    df['yrange']=df['Y'].apply(lambda x:[min(x),max(x)])
    df['Len']=df['Text'].apply(lambda x:len(x))
    temp=df
    temp['xmin']=temp['xrange'].apply(lambda x:min(x))
    temp['xmax']=temp['xrange'].apply(lambda x:max(x))
    temp['ymin']=temp['yrange'].apply(lambda x:min(x))
    temp['ymax']=temp['yrange'].apply(lambda x:max(x))
    df['Ratio']=(temp['xmax']-temp['xmin'])*(temp['ymax']-temp['ymin'])/temp['Len']
    for k in range(20):
        try:
            df['Lower Text']=df['Text'].apply(lambda x:x.lower())
            df['French_trad'] = df['Lower Text'].apply(lambda x: Translate(x))
            break
        except AttributeError:
            print("Oops!  Google Trad fail to translate.  Try again...")
            time.sleep(2)   
    #Ici on remplit la table df_symb, donnant les caractères, leurs positions, leurs confiances
    #et la largeur/longueur des caractères
    bounds_symb=[]
    confidence_symb=[]
    text_symb=[]
    for i,page in enumerate(document.pages):
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                            bounds_symb.append(symbol.bounding_box)
                            confidence_symb.append(symbol.confidence)
                            text_symb.append(symbol.text)

    all_x=[]
    all_y=[]
    for bound in bounds_symb:
        x=[]
        y=[]
        for vertice in bound.vertices:
            x.append(vertice.x)
            y.append(vertice.y)
        all_x.append(x)
        all_y.append(y)

    df_symb=pd.DataFrame()
    df_symb['X']=all_x
    df_symb['Y']=all_y
    df_symb['xrange']=df_symb['X'].apply(lambda x:[min(x),max(x)])
    df_symb['yrange']=df_symb['Y'].apply(lambda x:[min(x),max(x)])
    df_symb['Confidence']=confidence_symb
    df_symb['Text']=text_symb
    df_symb['Largeur_w']=df_symb['xrange'].apply(lambda x:abs(x[1]-x[0]))
    df_symb['Longueur_v']=df_symb['yrange'].apply(lambda x:abs(x[1]-x[0]))
    return df, df_symb
#Google me donne le nombre de pixel occupé par un texte, or pour remplacer ce texte il me faut déduire une police adaptée
#J'utilise une table de conversion Pixel->Police
conversion=pd.read_csv('ConversionPXP.csv')

#Cette fonction va ajouter le texte traduit à une image blanchit par la fonction Blanchiment 
#Entrées:
# (image) chemin de l'image à traduire
# (v) et (w) constante pour déduire une largeur et longueur de texte à partir du nombre de caractères à écrire et sa police
# (conversion) table pour convertir le nombre de pixel utilisé et le nombre de caractère d'un texte identifié pour déduire une police adpaté
# (df) table avec tous les textes identifiés incluant leurs contenus, leur position etc
#Sortie :
# (image) image traduite en objet PIL (il ne manque plus qu'un .save pour la sauvegarder)
def GetTranslateImage(image,v,w,df,conversion):
    df_conf=df[df.Len>3] #je ne traduis que les textes avec plus de 3 caractères
    df_conf=df_conf[df_conf.Ratio<800] # je ne traduit que les bulles dont le ratio volume(longueur*largeur)/nombre de charactères est inférieur à 800
    df_conf=df_conf[df_conf.Confidence>0.85].reset_index(drop=True)# je ne traduit que les textes que Google m'indique fiable à plus de 0.85

    for k in range(len(df_conf)):
        x=df_conf['xrange'][k]
        y=df_conf['yrange'][k]
        text=df_conf['French_trad'][k]

        larg=round(abs(x[1]-x[0])*1.3)
        long=round(abs(y[1]-y[0])*1.6)

        text_largeur=len(text)*w*1.2
        nb_ligne=round(text_largeur/(larg*0.9))+1
        for k in range(10):
            if (v*nb_ligne>long)&(nb_ligne>1):
                #print('trop de ligne')
                nb_ligne-=1
        saut_naif=int(round(len(text)/nb_ligne))


        font_size=2+int(conversion[conversion['PX']==min(conversion['PX'], key=lambda x:abs(x-v))]['PT'].values[0])

        astr = text
        para = textwrap.wrap(astr, width=saut_naif)



        MAX_W, MAX_H = larg, long
        im = Image.new('RGB', (MAX_W, MAX_H), (255, 255, 255))
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype('/home/arnaud/Téléchargements/Comfortaa-VariableFont_wght.ttf',font_size)

        current_h, pad = 0, 0
        for line in para:
            ww, h = draw.textsize(line, font=font)
            draw.text(((MAX_W - ww) / 2, current_h), line, fill=(0,0,0),font=font)
            current_h += h + pad

        image.paste(im, (min(x),min(y)))
    return image

#Cette fonction va traduire une image et sauvegarder l'image traduire dans un répertoire approprié
#Entrée :
# (image_path) chemin de l'image à traduire 
# (save_path) chemin où on va sauvegarder l'image traduite
#Sortie :
# pas de sortie, l'image est sauvegarder dans la fonction dans un répertoire approprié
def SaveTraductImage(image_path,save_path):
    image  = Image.open(image_path)
    df,df_symb=GetTables(image_path)

    v=df_symb[df_symb.Confidence>0.98]['Longueur_v'].median()
    w=df_symb[df_symb.Confidence>0.95]['Largeur_w'].median()

    image=Blanchiment(image,0.95,df)

    output=GetTranslateImage(image,v,w,df,conversion)
    output.save(save_path)

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