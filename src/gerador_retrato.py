from PIL import Image
import os

def gerar_retrato(componentes, output_path="../retrato_falado_suspeito.png"):
    base_img = None
    
    # Ordem das camadas simplificada (sem sobrancelhas)
    ordem_camadas = ['face', 'olhos', 'nariz', 'boca']
    
    for camada in ordem_camadas:
        if camada in componentes and os.path.exists(componentes[camada]):
            img_camada = Image.open(componentes[camada]).convert("RGBA")
            
            if base_img is None:
                base_img = img_camada
            else:
                base_img = Image.alpha_composite(base_img, img_camada)
    
    if base_img:
        base_img.save(output_path)

if __name__ == "__main__":
    pass