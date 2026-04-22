# Projeto A3 - Modelagem de Retrato Falado e Reconhecimento Facial

## Descrição do Projeto
Este sistema integra técnicas de Computação Gráfica e Visão Computacional aplicadas à perícia forense. O objetivo é permitir a construção de rostos no formato de mosaico a partir de componentes faciais reais e submeter a composição final a um algoritmo de Inteligência Artificial para cruzamento de dados com um banco criminal, gerando um ranking de similaridade.

Trabalho acadêmico desenvolvido para a unidade curricular de Computação Gráfica e Realidade Virtual (Una Uberlândia).

## Funcionalidades e Soluções Técnicas
1. **Manequim Universal e Puzzle Cut:** Utilização de uma "tela em branco" padronizada. As peças do rosto (olhos, nariz e boca) são extraídas e inseridas utilizando recortes poligonais precisos que se encaixam perfeitamente, sem sobreposições grosseiras.
2. **Feathering (Suavização de Bordas):** Aplicação de desfoque gaussiano no Canal Alpha das imagens. Isso permite uma fusão de pele em degradê, disfarçando as linhas de corte e criando uma composição realista.
3. **Interface Live Preview:** Interface gráfica desenvolvida em `CustomTkinter` que permite a montagem do rosto em tempo real. Inclui a funcionalidade de **Geração Aleatória** para testes rápidos.
4. **Equalização de Histograma:** Normalização da iluminação (`cv2.equalizeHist`) para nivelar o contraste entre as diferentes peças do rosto e as fotos originais do banco de dados.
5. **Reconhecimento Biométrico Avançado:** Motor de reconhecimento baseado em **LBPH** (Local Binary Patterns Histograms). O sistema utiliza alinhamento matemático rigoroso, garantindo que o algoritmo processe o rosto gerado sob a exata mesma escala de proporção e zoom das fotos do banco de dados, retornando um Top 5 de suspeitos.

## Tecnologias Utilizadas
* **Linguagem:** Python 3.14.4
* **Bibliotecas Principais:** OpenCV (Processamento e ML), Pillow (Manipulação Alpha/Camadas), CustomTkinter (GUI) e NumPy (Operações Matriciais).
* **Base de Dados:** AT&T Face Database (ORL) - 40 indivíduos padronizados. *(Nota: O processamento foca exclusivamente no núcleo facial, descartando características periféricas como cabelo por limitações de enquadramento da base de dados).*

## Como executar
* Instale as dependências executando: pip install -r requirements.txt
* Execute o extrator para popular a pasta assets com as feições recortadas (necessário apenas na primeira execução do projeto): python src/extrator_automatico.py
* Inicie o sistema forense: python src/interface.py