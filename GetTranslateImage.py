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