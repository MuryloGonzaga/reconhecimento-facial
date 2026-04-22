import customtkinter as ctk
from PIL import Image
import os
import random # Adicionado o import do random
from gerador_retrato import gerar_retrato
from pre_processamento import pre_processar_imagem
from reconhecimento import treinar_e_reconhecer_top5

class AppRetratoFalado(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1000x650")
        self.title("Sistema de Perícia Forense - Projeto A3")
        
        self.dir_atual = os.path.dirname(os.path.abspath(__file__))
        self.pasta_assets = os.path.join(self.dir_atual, '..', 'assets')
        self.caminho_saida = os.path.join(self.dir_atual, '..', 'retrato_falado_suspeito.png')
        self.caminho_dataset = os.path.join(self.dir_atual, '..', 'dataset')
        self.manequim_universal = os.path.join(self.pasta_assets, 'faces', 'rosto_base_universal.png')

        self.grid_columnconfigure(1, weight=1)
        
        self.frame_menu = ctk.CTkFrame(self, width=300)
        self.frame_menu.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.frame_view = ctk.CTkFrame(self)
        self.frame_view.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)

        ctk.CTkLabel(self.frame_menu, text="Composição do Rosto", font=("Arial", 18, "bold")).pack(pady=10)

        self.valores = {}
        self.opcoes_disponiveis = {} # Dicionário pra guardar as listas pra eu poder sortear depois
        
        partes = ['olhos', 'nariz', 'boca']
        
        for p in partes:
            ctk.CTkLabel(self.frame_menu, text=f"{p.capitalize()}:").pack(anchor="w", padx=20)
            caminho = os.path.join(self.pasta_assets, p)
            
            opcoes = [f for f in os.listdir(caminho) if f.endswith('.png')] if os.path.exists(caminho) else []
            self.opcoes_disponiveis[p] = opcoes.copy() # Salvo a lista original sem o "Nenhum"
            
            opcoes.insert(0, "Nenhum")
            
            var = ctk.StringVar(value="Nenhum")
            self.valores[p] = var
            ctk.CTkOptionMenu(self.frame_menu, variable=var, values=opcoes, command=self.atualizar).pack(fill="x", padx=20, pady=5)

        # Botão novo de Sorteio
        self.btn_aleatorio = ctk.CTkButton(self.frame_menu, text="GERAR ALEATÓRIO", command=self.gerar_aleatorio)
        self.btn_aleatorio.pack(pady=(20, 5), padx=20, fill="x")

        self.btn_reconhecer = ctk.CTkButton(self.frame_menu, text="IDENTIFICAR SUSPEITO", fg_color="red", hover_color="darkred", command=self.identificar)
        self.btn_reconhecer.pack(pady=(5, 30), padx=20, fill="x")

        self.label_img = ctk.CTkLabel(self.frame_view, text="")
        self.label_img.pack(expand=True)
        
        self.txt_ranking = ctk.CTkTextbox(self.frame_view, height=150)
        self.txt_ranking.pack(fill="x", padx=20, pady=20)
        
        self.atualizar()

    def gerar_aleatorio(self):
        # Varre as partes e escolhe uma imagem aleatória pra cada
        for p in self.valores:
            if self.opcoes_disponiveis[p]:
                escolha_random = random.choice(self.opcoes_disponiveis[p])
                self.valores[p].set(escolha_random)
        
        # Chama a atualização pra refletir na tela
        self.atualizar()

    def atualizar(self, _=None):
        comp_final = {'face': self.manequim_universal}
        mapeamento = {'olhos': 'olhos', 'nariz': 'nariz', 'boca': 'boca'}
        
        for pasta, chave in mapeamento.items():
            escolha = self.valores[pasta].get()
            if escolha != "Nenhum":
                comp_final[chave] = os.path.join(self.pasta_assets, pasta, escolha)
        
        gerar_retrato(comp_final, self.caminho_saida)
        
        if os.path.exists(self.caminho_saida):
            img = ctk.CTkImage(Image.open(self.caminho_saida), size=(350, 350))
            self.label_img.configure(image=img, text="")

    def identificar(self):
        # Removi a dependência do pre_processar_imagem. O reconhecimento agora faz o corte matemático direto.
        ranking = treinar_e_reconhecer_top5(self.caminho_dataset, self.caminho_saida)
        
        self.txt_ranking.delete("1.0", "end")
        self.txt_ranking.insert("end", "--- RANKING DE SIMILARIDADE (TOP 5) ---\n")
        for i, (nome, dist) in enumerate(ranking, 1):
            self.txt_ranking.insert("end", f"{i}º: {nome} (Distância: {dist:.2f})\n")

if __name__ == "__main__":
    AppRetratoFalado().mainloop()