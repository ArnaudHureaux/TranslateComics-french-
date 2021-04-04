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