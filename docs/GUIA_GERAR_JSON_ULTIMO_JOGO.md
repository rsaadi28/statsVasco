# Guia para pesquisar o ultimo jogo do Vasco e gerar JSON de importacao

Este documento e a instrucao para o "Codex do futuro" quando o objetivo for pesquisar o ultimo jogo ja realizado do Vasco e entregar um JSON pronto para o importador do app, sem salvar diretamente em DEV ou PRD.

## Objetivo

Pesquisar o ultimo jogo ja realizado do Vasco, montar um payload completo no formato aceito pelo importador JSON do app e entregar ao usuario:

- um arquivo `.json` ou um bloco JSON valido;
- com nomes padronizados contra o banco local;
- sem escrever diretamente em `stats_vasco.sqlite3`;
- sem repetir a operacao em banco de DEV/PRD;
- com todos os dados pesquisaveis da partida preenchidos;
- com estatisticas avancadas apenas do Vasco e dos jogadores do Vasco, quando houver fonte confiavel;
- sem gerar o JSON final se faltar algum dado relevante sem confirmacao do usuario.

## Diferenca para o guia com banco

Use o mesmo criterio de pesquisa do `docs/GUIA_IMPORTACAO_JOGO_COM_BANCO.md`, mas pare antes de salvar:

1. Pesquisar fontes.
2. Conferir nomes no banco local.
3. Montar o JSON.
4. Validar o JSON como texto.
5. Entregar o JSON ao usuario.

Nao executar `save_matches`, nao alterar `list_entries`, nao rodar SQL de insert/update e nao importar pela UI no lugar do usuario.

## Fonte principal

Priorize a materia da NetVasco da rodada do jogo realizado:

- pagina do resultado/ficha tecnica do jogo;
- bloco `FICHA TECNICA`;
- bloco das escalacoes;
- gols, cartoes e substituicoes;
- arbitragem;
- publico pagante, publico presente e renda em qualquer jogo, inclusive fora de casa.

Tambem pesquisar a materia pre-jogo de desfalques da mesma rodada, quando existir, para preencher:

- `suspensos`;
- `lesionados`;
- retornos de suspensao, para nao marcar indevidamente como suspenso.
- ignorar pendurados e nao tentar prever suspensoes por acumulacao de cartoes.

Se a NetVasco nao tiver dado suficiente, use fonte secundaria confiavel apenas para completar o campo faltante. Se ainda assim qualquer dado relevante ficar sem confirmacao, pare e pergunte ao usuario antes de gerar o JSON final.

Para estatisticas avancadas, use fontes confiaveis que tenham scout da partida. Priorize fontes que separem os numeros por equipe e por jogador, como SofaScore, FotMob, Footstats, 365Scores, ESPN Gamecast, Flashscore, AiScore, WhoScored, FBref/Opta quando disponivel, CBF/CONMEBOL ou equivalente. Extraia somente o lado do Vasco; nao coloque estatisticas do adversario no JSON.

Quando a NetVasco nao trouxer estatisticas detalhadas, pesquise no Google e em buscadores com termos como:

- `"Vasco x Adversario estatisticas SofaScore dd/mm/aaaa"`;
- `"Adversario x Vasco player stats FotMob"`;
- `"Vasco Adversario match stats 365Scores"`;
- `"Vasco Adversario estatisticas Footstats"`;
- `"Vasco Adversario CONMEBOL stats"` ou `"CBF Vasco Adversario estatisticas"`, conforme a competicao.

Se a fonte for dinamica e os numeros aparecerem apenas em interface, use os dados visiveis da pagina, print ou transcricao manual, mas registre no texto de entrega qual fonte foi usada. Estatisticas avancadas sao desejaveis, mas nao devem ser inventadas: se nenhum scout confiavel for encontrado, omita os campos ou deixe arrays/objetos vazios e informe a pendencia fora do JSON.

## Dados a pesquisar antes de gerar o JSON

Pesquisar e tentar preencher tudo que houver sobre a partida:

- data, horario, adversario, competicao, fase/rodada quando a fonte trouxer;
- mando (`local`), estadio, cidade e contexto do mando se houver;
- placar final;
- tecnico do Vasco;
- capitao do Vasco;
- posicao do Vasco na tabela, quando a competicao usar classificacao;
- arbitragem completa: arbitro, auxiliares e VAR;
- titulares do Vasco por posicao;
- reservas completos do Vasco;
- substituicoes do Vasco, com jogador que saiu, jogador que entrou, minuto e periodo;
- gols do Vasco e do adversario, com autor, minuto e periodo;
- cartoes amarelos e vermelhos do Vasco;
- lesionados/desfalques medicos daquela partida;
- suspensos daquela partida;
- jogadores servindo selecao, se houver;
- jogadores nao relacionados, quando a comparacao com o elenco atual permitir;
- estado do elenco atual depois da partida, para que o app fique salvo como o Vasco comecou/foi relacionado nesse ultimo jogo: titulares como `Titular`, banco como `Reserva`, lesionados como `Lesionado`, suspensos como `Suspenso`, servindo selecao como `Servindo a selecao` e ausentes sem motivo especifico como `Nao Relacionado`;
- publico pagante, publico presente e renda, inclusive em jogos fora de casa;
- estatisticas coletivas do Vasco: posse de bola, passes certos, passes errados, passes tentados/totais, precisao de passes, finalizacoes, finalizacoes no gol, finalizacoes fora, finalizacoes bloqueadas, escanteios, impedimentos, faltas cometidas, faltas recebidas, desarmes, interceptacoes, cruzamentos e lancamentos quando a fonte trouxer;
- estatisticas individuais dos jogadores do Vasco: minutos, nota da fonte, passes certos, passes errados, passes tentados/totais, precisao de passes, finalizacoes, finalizacoes no gol, assistencias, chances criadas, desarmes, interceptacoes, duelos ganhos, duelos aereos ganhos, faltas cometidas/recebidas, defesas do goleiro e outros numeros do scout disponiveis;
- gols anulados, penaltis perdidos/defendidos, expulsao de membro da comissao ou outra ocorrencia relevante, registrando em `observacao` quando o importador nao tiver campo especifico.

Nao considere "fora de casa" como motivo para deixar `publico_pagante`, `publico_presente` ou `renda` sem pesquisar. Se o dado nao aparecer em fonte confiavel, pergunte ao usuario antes de gerar o JSON final.

## Consultas locais antes de montar o JSON

Consultar o banco local apenas para normalizar nomes e evitar divergencia. Exemplos:

```sql
SELECT value FROM list_entries WHERE list_type='tecnicos' ORDER BY lower(value);
SELECT value FROM list_entries WHERE list_type='arbitros' ORDER BY lower(value);
SELECT value FROM list_entries WHERE list_type='auxiliares' ORDER BY lower(value);
SELECT value FROM list_entries WHERE list_type='vars' ORDER BY lower(value);
SELECT value FROM list_entries WHERE list_type='estadios' ORDER BY lower(value);
SELECT value FROM list_entries WHERE list_type='jogadores_vasco' ORDER BY lower(value);
SELECT value FROM list_entries WHERE list_type='jogadores_contra' ORDER BY lower(value);
SELECT name FROM competitions ORDER BY lower(name);
SELECT name FROM teams WHERE team_type='adversario' OR team_type='vasco' ORDER BY lower(name);
```

Para verificar duplicidade antes de entregar:

```sql
SELECT m.id, m.date_text, t.name AS adversario, c.name AS competicao,
       m.vasco_goals, m.opponent_goals
FROM matches m
LEFT JOIN teams t ON t.id = m.opponent_team_id
LEFT JOIN competitions c ON c.id = m.competition_id
WHERE m.date_text = 'dd/mm/aaaa'
  AND lower(t.name) = lower('Adversario');
```

Se existir jogo igual, avisar o usuario junto com o JSON. Nao sobrescrever nada.

## Formato aceito pelo importador

O importador da UI em `main.py` aceita um objeto de jogo ou uma lista de jogos. Para este fluxo, entregue preferencialmente um objeto unico.

Campos principais:

```json
{
  "data": "dd/mm/aaaa",
  "adversario": "Nome do clube",
  "competicao": "Nome da competicao",
  "local": "casa",
  "estadio": "Nome do estadio",
  "horario": "HH:MM",
  "tecnico": "Nome do tecnico",
  "capitao": "",
  "posicao_tabela": null,
  "placar": {
    "vasco": 0,
    "adversario": 0
  },
  "gols_vasco": [],
  "gols_adversario": [],
  "cartoes_amarelos_vasco": [],
  "cartoes_vermelhos_vasco": [],
  "estatisticas_vasco": {
    "posse_bola": null,
    "passes_certos": null,
    "passes_errados": null,
    "passes_tentados": null,
    "precisao_passes": null,
    "finalizacoes": null,
    "finalizacoes_no_gol": null,
    "finalizacoes_fora": null,
    "finalizacoes_bloqueadas": null,
    "escanteios": null,
    "impedimentos": null,
    "faltas_cometidas": null,
    "faltas_recebidas": null,
    "desarmes": null,
    "interceptacoes": null,
    "cruzamentos_certos": null,
    "cruzamentos_errados": null,
    "cruzamentos_tentados": null,
    "lancamentos_certos": null,
    "lancamentos_errados": null,
    "lancamentos_tentados": null
  },
  "estatisticas_jogadores_vasco": [
    {
      "nome": "Nome do jogador do Vasco",
      "minutos": null,
      "nota_sofascore": null,
      "passes_certos": null,
      "passes_errados": null,
      "passes_tentados": null,
      "precisao_passes": null,
      "finalizacoes": null,
      "finalizacoes_no_gol": null,
      "assistencias": null,
      "chances_criadas": null,
      "desarmes": null,
      "interceptacoes": null,
      "duelos_ganhos": null,
      "duelos_aereos_ganhos": null,
      "faltas_cometidas": null,
      "faltas_recebidas": null,
      "defesas": null
    }
  ],
  "publico_pagante": null,
  "publico_presente": null,
  "renda": null,
  "arbitragem": {
    "arbitro": "",
    "auxiliares": [],
    "var": ""
  },
  "escalacao_partida": {
    "titulares_por_posicao": {
      "Goleiro": [],
      "Lateral-Direito": [],
      "Zagueiro": [],
      "Lateral-Esquerdo": [],
      "Volante": [],
      "Meio-Campista": [],
      "Atacante": []
    },
    "reservas": [],
    "substituicoes": [],
    "nao_relacionados": [],
    "lesionados": [],
    "suspensos": [],
    "servindo_selecao": []
  },
  "observacao": ""
}
```

Observacoes do formato:

- `data` e `adversario` sao obrigatorios.
- `placar.vasco` e `placar.adversario` sao obrigatorios e inteiros.
- `local` aceita apenas `casa` ou `fora`.
- `horario` deve ser `HH:MM`; use `""` se a fonte nao confirmar.
- `publico_pagante`, `publico_presente` e `renda` podem ser `null` tecnicamente, mas so use `null` depois de perguntar ao usuario ou quando ele autorizar seguir sem o dado.
- Pesquise publico pagante, publico presente e renda em jogos em casa e fora de casa.
- `posicao_tabela` so importa para competicoes em que o app usa posicao; use `null` se nao souber.
- O importador completa automaticamente alguns nomes de `nao_relacionados`, `lesionados`, `suspensos` e `servindo_selecao` com base no elenco atual, mas o JSON deve trazer tudo que a pesquisa confirmar.

## Estatisticas avancadas

Use `estatisticas_vasco` somente para numeros coletivos do Vasco. Nao inclua campos equivalentes do adversario, mesmo que a fonte mostre comparativo lado a lado. Se a fonte mostrar "Vasco 423 passes / adversario 510 passes", coloque apenas o numero do Vasco.

Use `estatisticas_jogadores_vasco` somente para jogadores do Vasco. Cada item precisa ter `nome`; o importador normaliza o nome contra elenco/listas locais. Nao inclua jogadores do adversario.

Campos aceitos podem ser ampliados por chave, mas prefira os nomes abaixo:

```json
{
  "posse_bola": 48.5,
  "passes_certos": 312,
  "passes_errados": 80,
  "passes_tentados": 392,
  "precisao_passes": 79.6,
  "finalizacoes": 11,
  "finalizacoes_no_gol": 4,
  "escanteios": 5,
  "desarmes": 18
}
```

Regras:

- Percentuais devem ser numeros de 0 a 100. Use `48.5`, nao `0.485`.
- `passes_tentados` pode ser omitido se houver `passes_certos` e `passes_errados`; o importador calcula a soma.
- `passes_errados` pode ser omitido se houver `passes_tentados` e `passes_certos`; o importador calcula a diferenca.
- `precisao_passes` pode ser omitido se houver `passes_certos` e `passes_tentados`; o importador calcula o percentual.
- Para valores nao encontrados, use `null` apenas quando o campo for importante no modelo e a ausencia ja foi aceita; caso contrario, omita o campo.
- Pode usar chaves equivalentes comuns (`passes`, `passes_totais`, `chutes`, `chutes_no_gol`, `posse`, `xg`, `nota`) porque o importador normaliza aliases, mas prefira as chaves canonicas do exemplo.
- Para estatisticas individuais, preencha somente jogadores do Vasco que tenham scout confiavel. Se a fonte tiver apenas titulares ou apenas jogadores com nota, nao complete os demais com zeros.
- Nao misture fonte/link dentro de `estatisticas_vasco` ou `estatisticas_jogadores_vasco`; registre ressalvas no texto de entrega ao usuario, e nao dentro de `observacao` se for apenas nota de pesquisa.

## Eventos de gol

Formato preferido:

```json
{
  "nome": "Nome do jogador",
  "gols": 1,
  "minutos": [37],
  "periodos": ["1T"],
  "assistencias": ["Nome de quem assistiu"],
  "clube": "Nome do clube"
}
```

Regras:

- Para `gols_vasco`, `clube` e opcional; o app resolve como Vasco.
- Para `gols_adversario`, informe `clube` com o nome do adversario quando possivel.
- Assistencia e opcional. Para um gol, pode usar `"assistencia": "Nome do jogador"`. Para varios gols do mesmo jogador no mesmo item, use `assistencias` na mesma ordem de `minutos` e `periodos`.
- O importador valida que a assistencia nao seja do proprio autor do gol.
- Periodos aceitos: `1T`, `2T`, `1P`, `2P`.
- O numero de eventos expandidos nao pode passar o placar.
- Se houver gol contra a favor do Vasco, use `"nome": "Gol contra"` somente se essa for a convencao ja usada no banco; caso contrario, explique a duvida fora do JSON.

## Cartoes

O importador JSON atual registra apenas cartoes do Vasco:

```json
{ "nome": "Nome do jogador", "cartoes": 1 }
```

Campos:

- `cartoes_amarelos_vasco`
- `cartoes_vermelhos_vasco`

Nao ha campo de importacao para cartoes do adversario neste fluxo.

## Escalacao

`titulares_por_posicao` deve somar 11 jogadores e ter exatamente 1 goleiro.

Posicoes validas:

- `Goleiro`
- `Lateral-Direito`
- `Zagueiro`
- `Lateral-Esquerdo`
- `Volante`
- `Meio-Campista`
- `Atacante`

`reservas` deve conter pelo menos 4 jogadores e deve listar os jogadores efetivamente relacionados no banco. Nao invente reservas ausentes.

Substituicoes:

```json
{
  "jogador_saiu": "Nome do titular",
  "jogador_entrou": "Nome do reserva",
  "minuto": 0,
  "periodo": "INT"
}
```

Periodos aceitos para substituicao:

- `1T`
- `INT`
- `2T`
- `1P`
- `INTP`
- `2P`

No intervalo (`INT` ou `INTP`), use `minuto: 0`.

Regras importantes:

- `jogador_entrou` precisa estar em `reservas`.
- `jogador_saiu` precisa estar nos titulares.
- Nao repetir jogador que saiu nem jogador que entrou.
- Se a fonte nao trouxer todos os reservas, pedir a foto da escalacao completa ao usuario antes de fechar o JSON.
- Jogador do elenco atual que nao foi relacionado e nao esta lesionado/suspenso/servindo selecao deve ir em `nao_relacionados`.
- Jogador emprestado nao deve ser incluido na escalacao do jogo.
- O JSON deve deixar claro o estado do elenco atual para depois da importacao: quem comecou jogando fica em `titulares_por_posicao`, quem foi banco fica em `reservas`, lesionados ficam em `lesionados`, suspensos em `suspensos`, jogadores servindo selecao em `servindo_selecao` e ausentes sem justificativa em `nao_relacionados`.
- Ao entregar, peca explicitamente para o usuario importar esse JSON para que o app salve o elenco atual no estado em que o Vasco iniciou/foi relacionado para a ultima partida.

## Gols anulados

Na versao atual do importador JSON da UI, gols anulados nao sao normalizados por `_normalizar_jogo_importado`. Portanto, nao dependa de campos como `anulados_vasco`, `anulados_adversario` ou `gols_anulados` para importar pela UI.

Se a partida tiver gol anulado:

- registre a informacao em `observacao`;
- avise o usuario fora do JSON que esse dado pode precisar de ajuste manual depois da importacao.

## Regras de parada

Nao entregar JSON como "pronto" se faltar algum destes pontos:

- resultado final;
- data;
- adversario;
- competicao;
- local;
- estadio;
- tecnico;
- escalacao titular completa;
- pelo menos 4 reservas confirmados;
- substituicoes confirmadas quando houver;
- lesionados/desfalques medicos da partida;
- suspensos da partida;
- publico pagante, publico presente ou renda, inclusive em jogo fora de casa, se a informacao nao aparecer em fonte confiavel;
- duvida forte de grafia sem equivalente claro no banco.

Nesses casos, nao gere a lista/JSON final. Entregue no maximo um rascunho parcial separado e pergunte ao usuario exatamente o que falta. Nao preencha inventando.

## Como entregar ao usuario

Entregar:

1. O JSON puro em bloco `json`, sem comentarios dentro do JSON.
2. Uma lista curta de fontes usadas.
3. Uma lista curta de pendencias, se houver.
4. Um aviso de duplicidade, se a consulta local encontrar jogo igual.
5. Uma frase dizendo que, ao importar, o app deve deixar o elenco atual salvo conforme o Vasco comecou/foi relacionado nessa ultima partida.

Nao dizer que importou. A acao do usuario sera abrir o app, clicar em `Importar JSON`, colar o conteudo e confirmar.

## Prompt pronto para usar com o Codex do futuro

```text
Pesquise o ultimo jogo ja realizado do Vasco e gere um JSON pronto para o importador de jogo do app StatsVasco.

Use docs/GUIA_GERAR_JSON_ULTIMO_JOGO.md e docs/GUIA_IMPORTACAO_JOGO_COM_BANCO.md como referencia. Siga o mesmo metodo de pesquisa do guia com banco, mas nao salve diretamente em DEV nem PRD.

Tarefas:
1. Identifique o ultimo jogo ja realizado do Vasco.
2. Use a NetVasco como fonte principal da ficha do jogo e procure tambem a materia pre-jogo de desfalques da rodada.
3. Pesquise todos os dados da partida: escalacao completa, banco, substituicoes, gols, cartoes, lesionados, suspensos, nao relacionados, arbitragem, publico pagante, publico presente e renda, inclusive se o Vasco jogou fora de casa.
4. Pesquise tambem estatisticas avancadas em Google/sites especializados quando a NetVasco nao trouxer: SofaScore, FotMob, Footstats, 365Scores, ESPN Gamecast, Flashscore, AiScore, WhoScored, FBref/Opta, CBF/CONMEBOL ou fontes equivalentes. Traga estatisticas coletivas do Vasco e estatisticas individuais dos jogadores do Vasco quando houver scout confiavel.
5. Consulte o banco local apenas para padronizar nomes de adversario, competicao, estadio, tecnico, jogadores e arbitragem.
6. Monte o JSON para que, quando eu importar, o app deixe o elenco atual salvo do jeito que o Vasco comecou/foi relacionado nessa ultima partida: titulares, reservas, lesionados, suspensos, servindo selecao e nao relacionados corretamente preenchidos.
7. Monte um objeto JSON unico aceito pelo importador da UI.
8. Nao execute insert/update/delete, nao chame save_matches e nao importe pela UI.
9. Se faltar reserva completo, lesionados, suspensos, publico pagante, publico presente, renda ou qualquer dado relevante da partida, pare antes de gerar o JSON final e me pergunte exatamente o que falta. Se faltarem apenas scouts avancados depois de pesquisa real, entregue o JSON e informe a pendencia fora dele.
10. Entregue o JSON puro em bloco json, mais fontes e pendencias fora do JSON, e diga que ao importar o app deve salvar o elenco atual conforme essa ultima partida.
```
