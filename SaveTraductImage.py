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