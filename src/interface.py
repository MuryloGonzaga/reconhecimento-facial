import customtkinter as ctk
from PIL import Image
import os
import datetime
import random
import shutil
from gerador_retrato import gerar_retrato
from reconhecimento import treinar_e_reconhecer_top5

class AppRetratoFalado(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Perícia Forense - Projeto A3")
        # Forço o programa a abrir maximizado pra ter imersão de software de verdade
        self.after(0, lambda: self.state('zoomed')) 
        
        self.dir_atual = os.path.dirname(os.path.abspath(__file__))
        self.pasta_assets = os.path.join(self.dir_atual, '..', 'assets')
        self.caminho_saida = os.path.join(self.dir_atual, '..', 'retrato_falado_suspeito.png')
        self.caminho_dataset = os.path.join(self.dir_atual, '..', 'dataset')
        self.pasta_suspeitos = os.path.join(self.dir_atual, '..', 'suspeitos_encontrados')
        self.manequim_universal = os.path.join(self.pasta_assets, 'faces', 'rosto_base_universal.png')

        # Dividi a tela usando peso: 40% pra galeria de peças (esquerda), 60% pro rosto montado (direita)
        self.grid_columnconfigure(0, weight=4) 
        self.grid_columnconfigure(1, weight=6) 
        self.grid_rowconfigure(0, weight=1) 
        
        self.frame_menu = ctk.CTkFrame(self)
        self.frame_menu.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.frame_view = ctk.CTkFrame(self)
        self.frame_view.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)

        ctk.CTkLabel(self.frame_menu, text="Biblioteca de Componentes Faciais", font=("Arial", 24, "bold")).pack(pady=(20, 10))

        self.valores = {}
        partes = ['olhos', 'nariz', 'boca']
        
        self.tabview = ctk.CTkTabview(self.frame_menu)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Leio o manequim uma vez só pra usar de "fundo" em todas as miniaturas
        img_manequim_base = Image.open(self.manequim_universal).convert("RGBA")
        
        img_crop_vazio = img_manequim_base.crop((50, 20, 350, 380)) 
        img_res_vazio = img_crop_vazio.resize((90, 108), Image.Resampling.LANCZOS)
        img_ctk_vazio = ctk.CTkImage(light_image=img_res_vazio, size=(90, 108))
        
        for p in partes:
            aba = self.tabview.add(p.capitalize())
            self.valores[p] = ctk.StringVar(value="Nenhum")
            
            caminho = os.path.join(self.pasta_assets, p)
            opcoes = [f for f in os.listdir(caminho) if f.endswith('.png')] if os.path.exists(caminho) else []
            
            # Embaralho as opções no boot pra forçar a testemunha a olhar tudo, evitando viés cognitivo
            random.shuffle(opcoes)
            
            scroll = ctk.CTkScrollableFrame(aba)
            scroll.pack(fill="both", expand=True)
            # Crio 4 colunas com o mesmo peso pra imitar um "display: flex" do CSS
            scroll.grid_columnconfigure((0,1,2,3), weight=1)
            
            btn_vazio = ctk.CTkButton(
                scroll, image=img_ctk_vazio, text="X\nVazio", compound="center",
                text_color="#ff4444", font=("Arial", 16, "bold"),
                width=90, height=108, fg_color="#333333", command=lambda pt=p: self.selecionar_peca(pt, "Nenhum")
            )
            btn_vazio.grid(row=0, column=0, padx=10, pady=10)
            
            for i, arquivo in enumerate(opcoes, 1):
                # Carrego a peça, colo no manequim cinza e corto pra gerar o thumbnail vertical
                img_p = Image.open(os.path.join(caminho, arquivo)).convert("RGBA")
                img_c = Image.alpha_composite(img_manequim_base, img_p).crop((50, 20, 350, 380))
                img_tk = ctk.CTkImage(light_image=img_c.resize((90, 108)), size=(90, 108))
                
                btn = ctk.CTkButton(
                    scroll, image=img_tk, text="", width=90, height=108,
                    fg_color="#2b2b2b", command=lambda pt=p, arq=arquivo: self.selecionar_peca(pt, arq)
                )
                btn.grid(row=i//4, column=i%4, padx=10, pady=10)

        ctk.CTkLabel(self.frame_view, text="Composição Forense", font=("Arial", 24, "bold")).pack(pady=(20, 10))
        
        self.label_img = ctk.CTkLabel(self.frame_view, text="")
        self.label_img.pack(expand=True, pady=10)
        
        self.btn_reconhecer = ctk.CTkButton(
            self.frame_view, text="GERAR LAUDO E EXPORTAR FOTOS", 
            fg_color="#cc0000", hover_color="#990000", 
            font=("Arial", 16, "bold"), height=60, 
            command=self.identificar
        )
        self.btn_reconhecer.pack(pady=(10, 5), padx=40, fill="x")
        
        self.lbl_status = ctk.CTkLabel(self.frame_view, text="", font=("Arial", 14))
        self.lbl_status.pack(pady=(0, 30))
        
        self.atualizar()

    def selecionar_peca(self, parte, arquivo):
        self.valores[parte].set(arquivo)
        self.atualizar()
        self.lbl_status.configure(text="") 

    def atualizar(self, _=None):
        comp = {'face': self.manequim_universal}
        for p in ['olhos', 'nariz', 'boca']:
            escolha = self.valores[p].get()
            if escolha != "Nenhum":
                comp[p] = os.path.join(self.pasta_assets, p, escolha)
        gerar_retrato(comp, self.caminho_saida)
        if os.path.exists(self.caminho_saida):
            img = ctk.CTkImage(Image.open(self.caminho_saida), size=(450, 450)) 
            self.label_img.configure(image=img, text="")

    def identificar(self):
        self.lbl_status.configure(text="Processando Biometria...", text_color="orange")
        self.update()
        
        ranking = treinar_e_reconhecer_top5(self.caminho_dataset, self.caminho_saida)
        
        # Passo 1 (Exportação Ética): Limpo a pasta pra não misturar os suspeitos da investigação atual com os antigos
        if os.path.exists(self.pasta_suspeitos):
            shutil.rmtree(self.pasta_suspeitos)
        os.makedirs(self.pasta_suspeitos)

        # Passo 2: O Pillow converte direto de .pgm para .png e eu salvo com o nome do ranking
        for i, (nome_pasta, dist) in enumerate(ranking, 1):
            caminho_origem = os.path.join(self.caminho_dataset, nome_pasta, '1.pgm')
            if os.path.exists(caminho_origem):
                img_suspeito = Image.open(caminho_origem)
                nome_final = f"{i}_lugar_suspeito_{nome_pasta.replace('s','')}.png"
                img_suspeito.save(os.path.join(self.pasta_suspeitos, nome_final))

        # Passo 3: Geração do documento oficial TXT (Ocultando o resultado da UI pra não criar viés na testemunha)
        caminho_relatorio = os.path.join(self.dir_atual, '..', 'relatorio_forense.txt')
        with open(caminho_relatorio, 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO FORENSE - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Olhos: {self.valores['olhos'].get()}\nNariz: {self.valores['nariz'].get()}\nBoca:  {self.valores['boca'].get()}\n\n")
            f.write("RANKING DE SIMILARIDADE:\n")
            for i, (n, d) in enumerate(ranking, 1):
                f.write(f" {i}º Lugar: Suspeito {n.replace('s','')} (Dist: {d:.2f})\n")
            
        self.lbl_status.configure(text="✔ Relatório e fotos exportados com sucesso!", text_color="#00ff00")

if __name__ == "__main__":
    AppRetratoFalado().mainloop()