import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops

def criar_manequim_universal(pasta_assets):
    tamanho_canvas = (400, 400)
    canvas = Image.new('RGBA', tamanho_canvas, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    
    cor_pele_generica = (80, 80, 80, 255)
    draw.ellipse((80, 20, 320, 380), fill=cor_pele_generica)
    canvas = canvas.filter(ImageFilter.GaussianBlur(radius=5))
    
    caminho_salvar = os.path.join(pasta_assets, 'faces', 'rosto_base_universal.png')
    os.makedirs(os.path.dirname(caminho_salvar), exist_ok=True)
    canvas.save(caminho_salvar)

def extrair_e_salvar_componentes(caminho_imagem_origem, id_extracao):
    dir_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_assets = os.path.join(dir_atual, '..', 'assets')
    
    img_cv = cv2.imread(caminho_imagem_origem)
    if img_cv is None: return

    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

    if len(faces) == 0: return
    (x, y, w, h) = faces[0]
    
    y_exp = max(0, y - int(h * 0.2))
    h_exp = h + int(h * 0.3)
    rosto_recortado = img_cv[y_exp:y_exp+h_exp, x:x+w]
    
    img_pil = Image.fromarray(cv2.cvtColor(rosto_recortado, cv2.COLOR_BGR2RGB)).convert("RGBA")
    img_400 = img_pil.resize((400, 400))
    
    mask_oval = Image.new('L', (400, 400), 0)
    ImageDraw.Draw(mask_oval).ellipse((80, 20, 320, 380), fill=255)
    mask_oval = mask_oval.filter(ImageFilter.GaussianBlur(radius=5))
    
    def fatiar_suave(pasta_destino, nome_arquivo, poligono):
        mask_peca = Image.new('L', (400, 400), 0)
        ImageDraw.Draw(mask_peca).polygon(poligono, fill=255)
        
        # O SEGREDO ESTÁ AQUI: Desfoque pesado de 15 pixels na borda da peça
        mask_peca = mask_peca.filter(ImageFilter.GaussianBlur(radius=15))
        mask_final = ImageChops.multiply(mask_peca, mask_oval)
        
        img_final = img_400.copy()
        img_final.putalpha(mask_final)
        
        os.makedirs(os.path.join(pasta_assets, pasta_destino), exist_ok=True)
        img_final.save(os.path.join(pasta_assets, pasta_destino, nome_arquivo))

    # POLÍGONOS COM SOBREPOSIÇÃO (Eles se cruzam para o Blur funcionar sem deixar buracos transparentes)
    poly_cabelo = [(0, 0), (400, 0), (400, 160), (0, 160)]
    poly_olhos  = [(0, 100), (400, 100), (400, 280), (280, 280), (230, 160), (170, 160), (120, 280), (0, 280)]
    poly_nariz  = [(150, 150), (250, 150), (280, 280), (120, 280)]
    poly_boca   = [(0, 240), (400, 240), (400, 400), (0, 400)]

    fatiar_suave('cabelo', f'cabelo_{id_extracao}.png', poly_cabelo)
    fatiar_suave('olhos', f'olhos_{id_extracao}.png', poly_olhos)
    fatiar_suave('nariz', f'nariz_{id_extracao}.png', poly_nariz)
    fatiar_suave('boca', f'boca_{id_extracao}.png', poly_boca)

if __name__ == "__main__":
    dir_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_assets = os.path.join(dir_atual, '..', 'assets')
    criar_manequim_universal(pasta_assets)
    for i in range(1, 11):
        img_path = os.path.join(dir_atual, '..', 'dataset', f's{i}', '1.pgm')
        if os.path.exists(img_path):
            extrair_e_salvar_componentes(img_path, f"sujeito_{i:02d}")
    print("Peças extraídas com bordas suaves e sobreposição!")