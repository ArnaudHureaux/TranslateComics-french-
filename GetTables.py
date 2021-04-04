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