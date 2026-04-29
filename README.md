# Projeto A3 - Modelagem de Retrato Falado e Reconhecimento Facial

## Descrição do Projeto
Este sistema integra técnicas avançadas de Computação Gráfica, Processamento de Imagens e Visão Computacional aplicadas à perícia forense. O objetivo é permitir a construção de rostos no formato de mosaico a partir de componentes faciais reais e submeter a composição final a um algoritmo de Inteligência Artificial para cruzamento de dados com um banco criminal.

Trabalho acadêmico desenvolvido para a unidade curricular de Computação Gráfica e Realidade Virtual (Una Uberlândia).

## Funcionalidades e Soluções Técnicas
1. **Composição Gráfica Avançada (Puzzle Cut & Feathering):** Extração de feições (olhos, nariz e boca) utilizando recortes poligonais precisos e desfoque gaussiano no Canal Alpha. O algoritmo garante um encaixe sem sobreposições grosseiras, fundindo a pele de diferentes sujeitos de forma realista em um "manequim universal".
2. **Interface UI/UX Forense:** Dashboard imersivo e responsivo desenvolvido em `CustomTkinter`. Apresenta uma galeria com layout flexível, miniaturas contextualizadas no formato do rosto e embaralhamento dinâmico (anti-vício de seleção).
3. **Pré-Processamento com CLAHE:** Utilização de Equalização de Histograma Adaptativo Limitado por Contraste (`cv2.createCLAHE`) para normalizar a iluminação e realçar microtexturas da pele sem estourar o brilho.
4. **Reconhecimento Biométrico por Ensemble Learning:** Em vez de uma análise global falha, o rosto é fatiado horizontalmente. O sistema utiliza três redes neurais **LBPH** independentes, aplicando uma média ponderada para o ranking: Olhos (45%), Nariz (30%) e Boca (25%).
5. **Exportação Ética (Blind Test):** Para evitar viés de confirmação testemunhal, a interface não exibe os resultados da IA. O sistema gera um Laudo Técnico Automático (`relatorio_forense.txt`) e converte/exporta as fotos originais (`.pgm`) do Top 5 suspeitos para uma pasta segura em `.png`.
6. **Painel do Investigador em Tempo Real (WebSocket):** A interface web conta com dois terminais — o da testemunha (montagem do retrato) e o do investigador (recepção dos suspeitos). Ao enviar o laudo, os suspeitos são transmitidos em tempo real via WebSocket para o segundo PC, sem que a testemunha veja os resultados.

## Tecnologias Utilizadas
* **Linguagem:** Python 3.x
* **Visão Computacional e ML:** OpenCV (Haar Cascades, Filtros CLAHE/Gaussian, LBPHFaceRecognizer).
* **Computação Gráfica:** Pillow (Manipulação Avançada de Máscaras e Canal Alpha).
* **Interface Desktop:** CustomTkinter.
* **Interface Web:** Flask + Flask-SocketIO (WebSocket).
* **Base de Dados:** AT&T Face Database (ORL) - 40 indivíduos padronizados.

## Como Executar
1. Instale as dependências executando: `pip install -r requirements.txt`
2. Execute o extrator para fatiar toda a base de dados e popular a pasta assets (necessário apenas na primeira execução ou caso atualize o dataset): `python src/extrator_automatico.py`

### Interface Desktop
3. Inicie o painel desktop: `python src/interface.py`

### Interface Web (dois PCs em rede)
3. Inicie o servidor web: `python src/app.py`
4. **Testemunha:** acessa `http://IP_DO_SERVIDOR:5000` para montar o retrato falado.
5. **Investigador:** acessa `http://IP_DO_SERVIDOR:5000/investigador` em outro PC para receber os suspeitos em tempo real.