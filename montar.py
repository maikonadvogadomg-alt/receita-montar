# -*- coding: utf-8 -*-
"""
MONTAR — a "receita do bolo" do Caça-Bug, para qualquer app.

Pega ferramentas que são UM HTML cada (do jeito que vieram, sem mexer nelas)
e transforma cada uma num arquivo .js que guarda o HTML inteiro dentro dele.
O app (index.html) carrega esses .js e abre cada ferramenta numa "janelinha"
(iframe srcdoc). Assim:
  - funciona abrindo o index.html direto (sem servidor), no APK e sem internet;
  - o app pode ENTREGAR o projeto para a ferramenta e PEGAR o relatório dela
    (pela "tomada" window.__hub, que este script coloca no fim de cada HTML).

COMO USAR (no PC, na pasta do app):
  1. Ponha os HTML originais na pasta  fontes/
  2. Escreva a lista em  receita.json  (exemplo no guia)
  3. Rode:   python montar.py
  4. Ele cria  ferramentas/<nome>.js  e  ferramentas/ordem.txt
     e mostra as linhas <script> para colar no index.html.
Nada nos originais é mudado. Para atualizar uma ferramenta: troque o HTML em
fontes/ e rode de novo.
"""
import json, os, sys
# no Windows (terminal do Mini SK) o Python escreve em outra 'língua' de letras: força UTF-8 para os ✅ não quebrarem
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PASTA = os.path.dirname(os.path.abspath(__file__))
RECEITA = os.path.join(PASTA, 'receita.json')
FONTES = os.path.join(PASTA, 'fontes')
SAIDA = os.path.join(PASTA, 'ferramentas')
NOME_LISTA = 'CB_FERRAMENTAS'   # o nome da "lista" que o app lê (no Caça-Bug é este)

# bibliotecas da internet -> cópia local (para funcionar sem internet e no APK)
LIBS_LOCAIS = [
    ('https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js', 'lib/jszip.min.js'),
    ('https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js', 'lib/jszip.min.js'),
    ('https://cdnjs.cloudflare.com/ajax/libs/jsdiff/5.2.0/diff.min.js', 'lib/diff.min.js'),
]

def ler(caminho):
    with open(caminho, encoding='utf-8', errors='replace') as f:
        return f.read()

def no_fim_do_body(html, extra):
    i = html.lower().rfind('</body>')
    return html[:i] + extra + html[i:] if i >= 0 else html + extra

def main():
    if not os.path.exists(RECEITA):
        sys.exit('Falta o receita.json (veja o exemplo no guia).')
    receita = json.loads(ler(RECEITA))
    os.makedirs(SAIDA, exist_ok=True)
    ordem, scripts = [], []
    for item in receita:
        origem = os.path.join(FONTES, item['fonte'])
        if not os.path.exists(origem):
            print('⚠ não achei', origem, '— pulei'); continue
        html = ler(origem)
        for de, para in LIBS_LOCAIS:
            html = html.replace(de, para)
        # a "tomada": como o app conversa com a ferramenta
        #   abrir  = código JS que recebe o arquivo f (um .zip/.pdf...) e carrega na ferramenta
        #   relatorio = código JS que devolve o texto do resultado
        partes = []
        if item.get('abrir'):
            partes.append('abrir:function(f,slot){return (' + item['abrir'] + ');}')
        if item.get('relatorio'):
            partes.append('relatorio:function(){try{return (' + item['relatorio'] + ');}catch(e){return "";}}')
        if partes:
            html = no_fim_do_body(html, '<script>window.__hub={' + ','.join(partes) + '};</script>')
        ficha = {
            'id': item['id'], 'nome': item['nome'], 'icone': item.get('icone', '🧰'),
            'desc': item.get('desc', ''), 'alimenta': bool(item.get('abrir')), 'html': html,
        }
        js = ('/* Ferramenta gerada pelo montar.py a partir de fontes/' + item['fonte'] + ' (não edite aqui). */\n'
              '(window.' + NOME_LISTA + ' = window.' + NOME_LISTA + ' || []).push('
              + json.dumps(ficha, ensure_ascii=False).replace('</script', '<\\/script') + ');\n')
        nome_js = item['id'] + '.js'
        with open(os.path.join(SAIDA, nome_js), 'w', encoding='utf-8') as f:
            f.write(js)
        ordem.append(item['id'])
        scripts.append('<script src="ferramentas/' + nome_js + '"></script>')
        print('✅', item['nome'], '→ ferramentas/' + nome_js, '(' + str(len(js) // 1024) + ' KB)')
    with open(os.path.join(SAIDA, 'ordem.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(ordem) + '\n')
    print('\nCole estas linhas no index.html (antes do js/40-ferramentas.js):')
    print('\n'.join(scripts))

if __name__ == '__main__':
    main()
