# Projeto A3 - Modelagem de Retrato Falado e Reconhecimento Facial

## Descrição do Projeto
Este projeto integra técnicas de Computação Gráfica e Processamento de Imagens para simular sistemas de investigação forense. O objetivo principal é desenvolver uma ferramenta capaz de compor retratos falados digitais e realizar a identificação de indivíduos por meio de algoritmos de reconhecimento facial em bases de dados criminais.

Trabalho desenvolvido para a UC de Computação Gráfica e Realidade Virtual do curso de Ciência da Computação (Una Uberlândia).

## Status do Projeto: Etapa 2 Concluída
Atualmente, o sistema é capaz de realizar a modelagem gráfica completa e a geração da imagem final do suspeito.

### Funcionalidades Implementadas
1. **Modelagem de Retrato Falado (Etapa 1):** Sistema de composição de face a partir de componentes gráficos como formato do rosto, olhos, nariz, boca e cabelo.
2. **Manipulação de Camadas:** Uso de imagens em formato PNG com fundo transparente para sobreposição gráfica.
3. **Geração da Imagem (Etapa 2):** Processamento de fusão de camadas e exportação do arquivo final (retrato_falado_suspeito.png).

## Tecnologias Utilizadas
* Linguagem: Python
* Bibliotecas: OpenCV, Pillow (PIL), NumPy, Matplotlib 
* Base de Dados: AT&T Face Database (Kaggle) 

## Estrutura do Repositório
* /assets: Biblioteca de componentes faciais organizados por categorias (faces, olhos, nariz, etc.).
* /dataset: Banco de dados simulado de indivíduos cadastrados para futura comparação.
* /src: Scripts Python responsáveis pela lógica de composição e testes.
* requirements.txt: Lista de dependências do projeto.
* retrato_falado_suspeito.png: Imagem final gerada pelo sistema de modelagem.

## Próximos Passos
* Implementação do pré-processamento de imagem (conversão para cinza e normalização).
* Detecção facial via Haar Cascade.
* Extração de características e cálculo de similaridade (LBPH).

-----------------------------------------------------------------
Autores: Murylo e João Pablo
