import cv2
import numpy as np
import os

def aplicar_mascara_oval(imagem_200x200):
    # Aplico o exato formato da montagem nas fotos do dataset pro LBPH não ler o fundo da foto
    mascara = np.zeros((200, 200), dtype=np.uint8)
    cv2.ellipse(mascara, (100, 100), (70, 90), 0, 0, 360, 255, -1)
    mascara = cv2.GaussianBlur(mascara, (5, 5), 0)
    return cv2.bitwise_and(imagem_200x200, imagem_200x200, mask=mascara)

def detectar_e_recortar_igual_extrator(imagem_gray):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(imagem_gray, scaleFactor=1.2, minNeighbors=5)
    
    # Escolhi usar CLAHE em vez de EqualizeHist porque ele realça texturas locais (poros, rugas) sem estourar o contraste global
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        y_exp = max(0, y - int(h * 0.2))
        h_exp = h + int(h * 0.3)
        
        y_exp_end = min(imagem_gray.shape[0], y_exp + h_exp)
        x_end = min(imagem_gray.shape[1], x + w)
        
        rosto = imagem_gray[y_exp:y_exp_end, x:x_end]
        if rosto.size > 0:
            rosto = cv2.resize(rosto, (200, 200)) # Ajusta pra escala comum
            rosto = clahe.apply(rosto)
            return aplicar_mascara_oval(rosto)
            
    img_resized = cv2.resize(imagem_gray, (200, 200))
    img_resized = clahe.apply(img_resized)
    return aplicar_mascara_oval(img_resized)

def carregar_base_dados(caminho_dataset):
    faces = []
    labels = []
    label_id = 0
    label_dict = {}

    for pasta_suspeito in os.listdir(caminho_dataset):
        caminho_pasta = os.path.join(caminho_dataset, pasta_suspeito)
        if not os.path.isdir(caminho_pasta): continue
            
        label_dict[label_id] = pasta_suspeito
        for nome_imagem in os.listdir(caminho_pasta):
            caminho_imagem = os.path.join(caminho_pasta, nome_imagem)
            imagem = cv2.imread(caminho_imagem, cv2.IMREAD_GRAYSCALE)
            if imagem is not None:
                rosto_alinhado = detectar_e_recortar_igual_extrator(imagem)
                faces.append(rosto_alinhado)
                labels.append(label_id)
        label_id += 1
        
    return faces, np.array(labels), label_dict

def treinar_e_reconhecer_top5(caminho_dataset, caminho_suspeito):
    faces, labels, label_dict = carregar_base_dados(caminho_dataset)
    if len(faces) == 0: return []

    imagem_suspeito = cv2.imread(caminho_suspeito, cv2.IMREAD_GRAYSCALE)
    if imagem_suspeito is None: return []
    
    rosto_teste = cv2.resize(imagem_suspeito, (200, 200))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    rosto_teste = clahe.apply(rosto_teste)
    rosto_teste = aplicar_mascara_oval(rosto_teste)
    
    # ENSEMBLE LEARNING: Fatiei o rosto em 3 partes para a IA não dar peso excessivo aos olhos (que são maiores fisicamente)
    teste_olhos = rosto_teste[0:100, :]
    teste_nariz = rosto_teste[100:150, :]
    teste_boca  = rosto_teste[150:200, :]
    
    resultados = []
    for id_suspeito, nome_pasta in label_dict.items():
        faces_individuo = [faces[i] for i in range(len(faces)) if labels[i] == id_suspeito]
        labels_individuo = [id_suspeito] * len(faces_individuo)
        
        if len(faces_individuo) > 0:
            treino_olhos = [f[0:100, :] for f in faces_individuo]
            treino_nariz = [f[100:150, :] for f in faces_individuo]
            treino_boca  = [f[150:200, :] for f in faces_individuo]
            
            # Treino 3 modelos independentes (um especialista pra cada região)
            rec_olhos = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
            rec_olhos.train(treino_olhos, np.array(labels_individuo))
            _, dist_olhos = rec_olhos.predict(teste_olhos)
            
            rec_nariz = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
            rec_nariz.train(treino_nariz, np.array(labels_individuo))
            _, dist_nariz = rec_nariz.predict(teste_nariz)
            
            rec_boca = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
            rec_boca.train(treino_boca, np.array(labels_individuo))
            _, dist_boca = rec_boca.predict(teste_boca)
            
            # Calibrei uma média ponderada para fechar a nota final de distância
            dist_final = (dist_olhos * 0.45) + (dist_nariz * 0.30) + (dist_boca * 0.25)
            
            resultados.append((nome_pasta, dist_final))
            
    resultados.sort(key=lambda x: x[1])
    return resultados[:5]