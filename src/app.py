import os
import datetime
import shutil

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from gerador_retrato import gerar_retrato
from reconhecimento import treinar_e_reconhecer_top5
from PIL import Image

dir_atual       = os.path.dirname(os.path.abspath(__file__))
pasta_assets    = os.path.join(dir_atual, '..', 'assets')
pasta_dataset   = os.path.join(dir_atual, '..', 'dataset')
pasta_suspeitos = os.path.join(dir_atual, '..', 'suspeitos_encontrados')
caminho_retrato = os.path.join(dir_atual, '..', 'retrato_falado_suspeito.png')
manequim        = os.path.join(pasta_assets, 'faces', 'rosto_base_universal.png')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'forense_key_2024'

# Inicializa o SocketIO — async_mode='threading' funciona bem com Flask simples
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins='*')


# ── Serve arquivos da pasta assets ──────────────────────────────
@app.route('/assets/<path:caminho>')
def assets_estaticos(caminho):
    return send_from_directory(pasta_assets, caminho)


# ── Serve o retrato gerado ───────────────────────────────────────
@app.route('/retrato')
def retrato_estatico():
    pasta = os.path.dirname(caminho_retrato)
    nome  = os.path.basename(caminho_retrato)
    resp  = send_from_directory(pasta, nome)
    resp.headers['Cache-Control'] = 'no-store'
    return resp


# ── Serve fotos dos suspeitos ────────────────────────────────────
@app.route('/suspeitos/<nome_arquivo>')
def suspeito_estatico(nome_arquivo):
    return send_from_directory(pasta_suspeitos, nome_arquivo)


# ── Rota principal (testemunha) ──────────────────────────────────
@app.route('/')
def index():
    def listar(pasta):
        caminho = os.path.join(pasta_assets, pasta)
        if not os.path.exists(caminho):
            return []
        return sorted([f for f in os.listdir(caminho) if f.endswith('.png')])

    olhos = listar('olhos')
    nariz = listar('nariz')
    boca  = listar('boca')

    return render_template('index.html', olhos=olhos, nariz=nariz, boca=boca)


# ── Rota do investigador (segundo PC) ───────────────────────────
@app.route('/investigador')
def investigador():
    return render_template('investigador.html')


# ── Gera o retrato ───────────────────────────────────────────────
@app.route('/gerar-retrato', methods=['POST'])
def rota_gerar_retrato():
    dados = request.json
    componentes = {'face': manequim}

    for parte in ['olhos', 'nariz', 'boca']:
        arquivo = dados.get(parte)
        if arquivo and arquivo != 'Nenhum':
            caminho = os.path.join(pasta_assets, parte, arquivo)
            if os.path.exists(caminho):
                componentes[parte] = caminho

    gerar_retrato(componentes, caminho_retrato)
    ts = datetime.datetime.now().timestamp()
    return jsonify({'retrato_url': f'/retrato?t={ts}'})


# ── Reconhecimento com emissão via WebSocket ─────────────────────
@app.route('/reconhecer', methods=['POST'])
def rota_reconhecer():
    dados = request.json
    componentes = {'face': manequim}

    for parte in ['olhos', 'nariz', 'boca']:
        arquivo = dados.get(parte)
        if arquivo and arquivo != 'Nenhum':
            caminho = os.path.join(pasta_assets, parte, arquivo)
            if os.path.exists(caminho):
                componentes[parte] = caminho

    gerar_retrato(componentes, caminho_retrato)

    # Avisa o investigador que começou o processo
    socketio.emit('investigacao_iniciada', {
        'olhos': dados.get('olhos', 'Nenhum'),
        'nariz': dados.get('nariz', 'Nenhum'),
        'boca':  dados.get('boca',  'Nenhum'),
        'hora':  datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    })

    ranking = treinar_e_reconhecer_top5(pasta_dataset, caminho_retrato)

    if os.path.exists(pasta_suspeitos):
        shutil.rmtree(pasta_suspeitos)
    os.makedirs(pasta_suspeitos)

    suspeitos_resultado = []

    for i, (nome_pasta, dist) in enumerate(ranking, 1):
        caminho_origem = os.path.join(pasta_dataset, nome_pasta, '1.pgm')
        url_foto = None

        if os.path.exists(caminho_origem):
            img = Image.open(caminho_origem)
            nome_final = f"{i}_lugar_suspeito_{nome_pasta.replace('s','')}.png"
            img.save(os.path.join(pasta_suspeitos, nome_final))
            url_foto = f'/suspeitos/{nome_final}'

        suspeito = {
            'posicao':   i,
            'suspeito':  nome_pasta.replace('s', ''),
            'distancia': round(dist, 2),
            'foto_url':  url_foto
        }
        suspeitos_resultado.append(suspeito)

        # Emite cada suspeito separado — efeito de "revelação" no investigador
        socketio.emit('novo_suspeito', suspeito)

    # Sinaliza que terminou
    socketio.emit('investigacao_concluida', {'total': len(suspeitos_resultado)})

    # Gera o relatório
    caminho_relatorio = os.path.join(dir_atual, '..', 'relatorio_forense.txt')
    with open(caminho_relatorio, 'w', encoding='utf-8') as f:
        f.write(f"RELATORIO FORENSE - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write("-" * 50 + "\n")
        f.write(f"Olhos: {dados.get('olhos', 'Nenhum')}\n")
        f.write(f"Nariz: {dados.get('nariz', 'Nenhum')}\n")
        f.write(f"Boca:  {dados.get('boca',  'Nenhum')}\n\n")
        f.write("RANKING DE SIMILARIDADE:\n")
        for s in suspeitos_resultado:
            f.write(f" {s['posicao']}o Lugar: Suspeito {s['suspeito']} (Dist: {s['distancia']})\n")

    return jsonify({'ranking': suspeitos_resultado})


if __name__ == '__main__':

  socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)