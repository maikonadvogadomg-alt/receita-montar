# 🍰 Receita: juntar ferramentas HTML dentro de um app (Mini SK, Caça-Bug, Laboratório, Jurídico)

Guia para a IA do Mini SK (versão de computador) seguir **passo a passo**.
Quem pede: Maikon. Ele não programa: explique em português simples e faça você mesmo.

## 1. Os dois jeitos que o Claude usou

### Jeito A — "pasta de HTMLs" (Laboratório, Jurídico 🧰 Ferramentas)
- Cada ferramenta continua sendo **um arquivo .html**, do jeito que veio, dentro da pasta `ferramentas/`.
- O app tem uma lista (nome, ícone, arquivo) e abre a ferramenta numa janelinha: `<iframe src="ferramentas/montador.html">`.
- **Bom:** não mexe em nada da ferramenta; trocar uma ferramenta = trocar o arquivo.
- **Cuidado:** o app precisa estar **publicado** (GitHub Pages / Netlify) ou aberto pelo Mini SK. Abrindo só o index.html solto, o navegador pode não carregar as outras pastas.
- **Conversar com a ferramenta:** por mensagem (`postMessage`). Ex.: o Laboratório manda o plano do projeto para o Meu Chat, que tem um "ouvido" (`js/95-ponte-lab.js`) e coloca o texto na caixa do chat.

### Jeito B — "montar" (Caça-Bug)
- Um programinha em **Python (`montar.py`)** lê cada HTML original e cria um arquivo **.js** que **guarda o HTML inteiro dentro dele** (como texto). Ex.: `ferramentas/limpador.js`:
  ```js
  (window.CB_FERRAMENTAS = window.CB_FERRAMENTAS || []).push({ id, nome, icone, desc, alimenta, html: "<!doctype html>…" });
  ```
- O `index.html` do app carrega esses .js com `<script src="ferramentas/limpador.js">`.
- O app (`js/40-ferramentas.js`) mostra os cartões e abre cada uma numa janelinha com `iframe.srcdoc = html`.
- **Bom:** funciona abrindo o **index.html direto**, no **APK** e **sem internet**. Tudo vira "parte do app".
- **A "tomada" (`window.__hub`):** no fim de cada HTML o montar.py acrescenta:
  ```html
  <script>window.__hub = { abrir: function (arquivo) { … }, relatorio: function () { … } };</script>
  ```
  - `abrir(arquivo)`: o app **entrega o projeto** (um .zip) para a ferramenta, chamando a função de importar QUE A FERRAMENTA JÁ TEM (ex.: `carregarFiles([f])`, `importZip(f)`).
  - `relatorio()`: o app **pega o resultado** em texto (botão 📌 Guardar relatório).
- **O "kit de baixar":** o app coloca no começo de cada ferramenta um pedacinho que faz o "⬇ baixar" dela passar pelo app (senão, dentro da janelinha, no celular/APK, o download não acontece).
- **Atualizar:** nunca edite os .js gerados. Troque o HTML original em `fontes/` e rode `python montar.py` de novo.

## 2. Qual usar?
| Situação | Jeito |
|---|---|
| Só quero um botão que abre a ferramenta | **A** (pasta de HTMLs) |
| Quero que o app **entregue o projeto** para a ferramenta e **guarde o relatório** | **B** (montar + `__hub`) |
| Vai virar APK / abrir sem internet / abrir pelo index.html solto | **B** |
| Ferramenta grande com várias pastas (ex.: Meu Chat, Mini Jurídico) | **A** (copia a pasta inteira) |

## 3. Receita do Jeito B (passo a passo para a IA)
1. Na pasta do app crie: `fontes/` (os HTML originais), `ferramentas/`, `lib/` (cópias locais de bibliotecas, ex.: jszip.min.js).
2. Copie o `montar.py` e o `receita.json` para a pasta do app.
3. Para **cada ferramenta**, ache dentro do HTML dela **qual função importa um arquivo** (procure `input type="file"` e veja qual função o `onchange` chama; ex.: `carregarFiles(files)`, `importZip(file)`, `loadInto('A', files)`).
   - Se achar: em `receita.json`, `"abrir": "nomeDaFuncao([f])"` (ou como ela espera o arquivo).
   - Se ela gera texto de resultado: `"relatorio": "nomeDaFuncaoQueDevolveTexto()"`. Se não tiver, deixe sem.
   - Se não precisa receber projeto (ex.: Limpador de Processos), não ponha `abrir`.
4. Rode no Terminal do Mini SK (computador): `python montar.py`.
5. Cole no `index.html` as linhas `<script src="ferramentas/....js"></script>` que ele mostrou, **antes** do `js/40-ferramentas.js`.
6. Se o app ainda não tem a parte que mostra os cartões e abre as ferramentas, copie o `js/40-ferramentas.js` do Caça-Bug (ele já tem o "kit de baixar", o `abrir`, o "entregar o projeto" e o "guardar relatório"). Ele precisa de: `SK.$`, `SK.toast`, `SK.download`, `SK.projeto.ativo`, `SK.projeto.arquivoZip(id)`, `SK.relatorios.guardar(...)` e uma tela `#ferr-host` — os mesmos do Caça-Bug (`js/00-core.js`).
7. **Teste:** abra o index.html, abra cada ferramenta, toque em importar dentro dela e veja se carrega; com um projeto escolhido, veja se ela recebe sozinha.

## 4. Receita do Jeito A (mais simples)
1. Copie os HTML para `ferramentas/` (ou a pasta inteira, se a ferramenta tiver várias pastas).
2. Na lista do app, acrescente uma linha: `{ id, icone, nome, descricao, arquivo: "ferramentas/x.html" }`.
3. A tela abre com `<iframe src="..." allow="microphone; camera; clipboard-read; clipboard-write; fullscreen">`.
4. Para mandar texto de um lado para o outro: `iframe.contentWindow.postMessage({ ... }, location.origin)` e, dentro da ferramenta, `window.addEventListener('message', ...)` conferindo `e.origin === location.origin`.

## 5. Regras de ouro
- **Nunca** mude o HTML original: trabalhe numa cópia (`fontes/`), e o montar gera o resto.
- **Nunca** ponha chave de IA, senha ou token dentro dos arquivos. As chaves ficam no app (⚙️ / 🔐 Cofre).
- Um arquivo por ferramenta. Nome curto, sem espaço (`limpador.js`, `perito.js`).
- Depois de juntar, **teste uma por uma** e anote no 📒 Memória/diário do projeto o que funcionou.
- Se travar 2 vezes no mesmo erro: escreva o erro e mande para o Claude ("levar para o Claude").

## 6. Para achar os códigos perdidos
- No Mini SK: **📚 Inventário** (joga vários .html/.zip → diz o que cada um faz, quais são versões repetidas e qual é a mais completa).
- No Laboratório: **⚖️ Comparar A × B** para ver a diferença entre duas versões.
- No computador: **🧹 Faxina de Repetidos** (no 🧰 Ferramentas do Laboratório) para separar repetidos.
