import cv2
import numpy as np
import os

def detectar_e_recortar_igual_extrator(imagem_gray):
    # Usamos EXATAMENTE a mesma métrica de corte que usamos pra fatiar os recortes
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(imagem_gray, scaleFactor=1.2, minNeighbors=5)
    
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        y_exp = max(0, y - int(h * 0.2))
        h_exp = h + int(h * 0.3)
        
        # Proteção pra não cortar fora do limite da imagem
        y_exp_end = min(imagem_gray.shape[0], y_exp + h_exp)
        x_end = min(imagem_gray.shape[1], x + w)
        
        rosto = imagem_gray[y_exp:y_exp_end, x:x_end]
        if rosto.size > 0:
            # Redimensiona pro nosso tamanho de análise e aplica a equalização de luz
            rosto = cv2.resize(rosto, (200, 200))
            return cv2.equalizeHist(rosto)
            
    # Se der erro (raro na AT&T), retorna a imagem padronizada
    img_resized = cv2.resize(imagem_gray, (200, 200))
    return cv2.equalizeHist(img_resized)

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
                # O banco de dados agora passa pelo MESMO recorte das nossas peças
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
    
    # O Pulo do Gato: A nossa montagem já é o rosto esticado em 400x400.
    # Então se eu simplesmente encolher ela pra 200x200, ela fica IDÊNTICA
    # ao zoom da base de dados! E aplicamos a equalização de luz nela também.
    rosto_teste = cv2.resize(imagem_suspeito, (200, 200))
    rosto_teste = cv2.equalizeHist(rosto_teste)
    
    resultados = []
    for id_suspeito, nome_pasta in label_dict.items():
        faces_individuo = [faces[i] for i in range(len(faces)) if labels[i] == id_suspeito]
        labels_individuo = [id_suspeito] * len(faces_individuo)
        
        if len(faces_individuo) > 0:
            # LBPH padrão é excelente lidando com texturas após a equalização de histograma
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train(faces_individuo, np.array(labels_individuo))
            
            _, confianca = recognizer.predict(rosto_teste)
            resultados.append((nome_pasta, confianca))
            
    resultados.sort(key=lambda x: x[1])
    return resultados[:5]