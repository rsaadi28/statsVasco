# Guia prático para importar o ultimo jogo do Vasco (com padronizacao no banco)

Este documento serve para repetir o processo sem retrabalho: buscar o ultimo jogo ja realizado do Vasco, coletar os dados da fonte principal, normalizar tudo com base no banco, montar o payload completo e aplicar no projeto.

## 1) Objetivo
Buscar e inserir o ultimo jogo ja realizado do Vasco no sistema garantindo:

- Conjunto de campos completo do cadastro do jogo.
- Nomes padronizados para tecnico, jogadores e arbitragem conforme banco.
- Nenhum nome "novo" desnecessariamente criado quando existe equivalente no banco.
- Sem criar duplicata de competencia/tecnico/jogo.
- Aplicacao correta primeiro em DEV e depois em PRD.
- Coleta da fonte principal com o maximo de dados possiveis: data, horario, estadio, tecnico, arbitragem, gols, cartoes, substituicoes, escalação, placar, renda e publico quando aplicavel.

## 2) Onde o app grava e consulta

- Banco ativo: `stats_vasco.sqlite3` (via `storage_sqlite.py`).
- Método de escrita: `save_matches(DB_PATH, jogos)` em `storage_sqlite.py`.
- Método de leitura: `load_matches(DB_PATH)`.
- Dicionario de listas auxiliares: `list_entries(list_type, value)`.
- Atualizações devem ser feitas **sempre em DEV e PRD**. Fluxo recomendado:
  - testar e validar no DEV primeiro,
  - depois repetir a operação no PRD quando estiver confirmado.
- Listas críticas para normalizacao:
  - `tecnicos`
  - `clubes_adversarios`
  - `competicoes`
  - `jogadores_vasco`
  - `jogadores_contra`
  - `arbitros`
  - `auxiliares`
  - `vars`
  - `estadios`

## 3) Ordem de trabalho (sempre seguir nesta ordem)

1. Identificar o ultimo jogo ja realizado do Vasco.
2. Abrir a materia da NetVasco da rodada e usar essa materia como fonte principal.
3. Abrir tambem a materia de `desfalques e pendurados` da NetVasco da mesma rodada, quando existir.
4. Coletar os dados brutos da fonte (noticia, relato tecnico, ficha de jogo).
5. Confirmar se a materia traz:
   - data
   - horario
   - adversario
   - competicao
   - local
   - estadio
   - tecnico
   - arbitragem
   - gols
   - cartoes
   - substituicoes
   - escalação
   - renda e publico, se o jogo for em casa
6. Coletar da materia de `desfalques e pendurados`:
   - jogadores suspensos para a partida
   - jogadores lesionados ou fora por motivo medico
   - retornos de suspensao, quando a materia indicar
7. Se a materia nao trouxer a lista completa de reservas, **nao inventar** os nomes que faltam:
   - pedir ao usuario a foto da escalação completa para anexar
   - usar a foto para completar banco e reservas
8. Se o jogo for em casa e a materia nao trouxer `publico_pagante`, `publico_presente` ou `renda`, pedir esses dados ao usuario antes de finalizar.
9. Resolver nomes contra o banco antes de salvar.
10. Montar payload no formato aceito pelo app.
11. Conferir duplicata.
12. Inserir em DEV.
13. Validar.
14. Repetir em PRD.
15. Atualizar lista de arbitros, auxiliares ou VAR, se houver nome novo faltante no cadastro.

## 4) Campos obrigatorios do payload de partida

Exemplo estrutural:

```json
{
  "data": "dd/mm/aaaa",
  "adversario": "Nome do clube",
  "competicao": "Nome da competicao",
  "local": "casa|fora",
  "estadio": "Nome do estadio",
  "tecnico": "Nome do tecnico",
  "horario": "HH:MM" ou "",
  "placar": { "vasco": 0, "adversario": 0 },
  "observacao": "...",
  "capitao": "",
  "publico_pagante": 0,
  "publico_presente": 0,
  "renda": 0,
  "arbitragem": {
    "arbitro": "",
    "auxiliares": [],
    "var": ""
  },
  "escalacao_partida": {
    "titulares_por_posicao": {...},
    "reservas": [...],
    "substituicoes": [
      {
        "jogador_saiu": "",
        "jogador_entrou": "",
        "minuto": 0,
        "periodo": "2T|INT|1T|..."
      }
    ],
    "nao_relacionados": [],
    "lesionados": [],
    "suspensos": [],
    "servindo_selecao": []
  },
  "gols_adversario": [],
  "gols_vasco": [],
  "anulados_vasco": [],
  "anulados_adversario": [],
  "cartoes_amarelos_vasco": [],
  "cartoes_vermelhos_vasco": []
}
```

Regras de normalizacao:
- `local`: apenas `casa` ou `fora`.
- `horario`: sempre preencher quando a materia trouxer a hora do jogo.
- Titulares devem somar 11 e ter 1 goleiro.
- Reservas deve ter pelo menos 4.
- Periodo aceito no sistema para gols: `1T`, `2T`, `1P`, `2P`.
- Periodo aceito para substituicao: `1T`, `INT`, `2T`, `1P`, `INTP`, `2P`.
- Em substituicao no intervalo (`INT` ou `INTP`) pode usar minuto `0`.
- Quando `local = "casa"`, preencher `publico_pagante`, `publico_presente` e `renda` com os valores informados pela noticia.
- Quando `local = "fora"`, nao exigir `publico_pagante`, `publico_presente` ou `renda`.
- `suspensos`: preencher com os jogadores suspensos para aquela partida com base na materia de `desfalques e pendurados`.
- `lesionados`: preencher com os desfalques por lesao quando a fonte pre-jogo trouxer essa informacao.
- Se a materia disser que um jogador `retorna de suspensao`, nao marcar esse jogador em `suspensos` para essa partida.
- `titulares` e `reservas` devem conter apenas jogadores que estejam efetivamente nos relacionados do jogo.
- Se um jogador estava antes em `titular` ou `reserva` e nao aparece mais nos relacionados do novo jogo, e tambem nao estiver como `suspenso`, `lesionado` ou `servindo_selecao`, mover para `nao_relacionados`.
- Em outras palavras: sobrou jogador do status anterior e ele nao esta nos relacionados atuais? Entao ele nao pode continuar em `titular` ou `reserva`.
- Se algum dado obrigatorio da fonte principal nao estiver disponivel, pedir ao usuario antes de concluir a importacao.

## 5) Consulta de nomes no banco antes de finalizar

Use estes comandos para validar o que ja existe e evitar divergencia:

1) Listar tecnicos, arbritros, auxiliares e VAR

```sql
SELECT value FROM list_entries WHERE list_type='tecnicos' ORDER BY lower(value);
SELECT value FROM list_entries WHERE list_type='arbitros' ORDER BY lower(value);
SELECT value FROM list_entries WHERE list_type='auxiliares' ORDER BY lower(value);
SELECT value FROM list_entries WHERE list_type='vars' ORDER BY lower(value);
```

2) Listar competicoes e clubes

```sql
SELECT name FROM competitions ORDER BY lower(name);
SELECT name FROM teams WHERE team_type='adversario' OR team_type='vasco' ORDER BY lower(name);
```

3) Conferir jogadores cadastrados (vasco e contra)

```sql
SELECT value FROM list_entries WHERE list_type='jogadores_vasco' ORDER BY lower(value);
SELECT value FROM list_entries WHERE list_type='jogadores_contra' ORDER BY lower(value);
```

4) Conferir players da base completa (quando nome vier de fora e nao existir na lista)

```sql
SELECT name FROM players ORDER BY lower(name);
```

## 6) Regras de padronizacao de nomes

Antes de salvar, transformar nome bruto da fonte para a forma padronizada do banco:

- `Renato Gaucho` -> `Renato Gaúcho` (tecnico)
- `Tchê Tchê` -> `Tche Tche` (jogador)
- `Barros` -> `Cauan Barros` (se o contexto for o jogador do Vasco)

Se houver empate de nome curto entre adversario e jogador, use contexto:
- Se aparecer no evento do Vasco, procurar em `jogadores_vasco`.
- Se aparecer no Vasco como técnico, procurar em `tecnicos`.
- Se estiver na ficha de jogo do adversario, procurar em `jogadores_contra`.
- Arbitros/auxiliares/VAR sempre procurar nas listas `arbitros`, `auxiliares`, `vars`.

## 7) Consulta de duplicidade (anti-fantasma)

Antes de inserir, confirme que nao existe partida com:

- mesma `data` e mesmo `adversario`, ou
- linha muito parecida com mesmo `data + placar + adversario`.

Consulta SQL:

```sql
SELECT m.id, m.date_text, t.name, m.vasco_goals, m.opponent_goals
FROM matches m
LEFT JOIN teams t ON t.id = m.opponent_team_id
WHERE m.date_text = 'dd/mm/aaaa' AND t.name = 'adversario';
```

## 8) Insercao no app pelo fluxo de UI (recomendado)

1. Abrir importador JSON.
2. Colar payload no formato do item 4.
3. Revisar:
   - `data`, `horario`, `local`, `placar`
   - `adversario`, `competicao`, `estadio`, `tecnico`
   - nomes de arbitragem e cartoes/gols/escalacao
   - `suspensos` e `lesionados`
   - `publico_pagante`, `publico_presente`, `renda` se jogo em casa
4. Confirmar.

## 9) Insercao direta via script (se for necessario)

Quando voce quiser inserir via script, manter ordem:

1) carregar jogos atuais:

```python
from storage_sqlite import load_matches, save_matches
jogos = load_matches(DB_PATH)
```

2) appendar o novo jogo normalizado e salvar:

```python
jogos.append(novo_jogo)
save_matches(DB_PATH, jogos)
```

3) depois atualizar listas extras caso apareçam nomes novos de arbitragem:

```sql
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('auxiliares', 'Nome');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('vars', 'Nome');
```

## 10) Padrao de normalizacao da partida (exemplo completo usado agora)

```json
{
  "data": "26/04/2026",
  "adversario": "Corinthians",
  "competicao": "Campeonato Brasileiro Serie A",
  "local": "fora",
  "estadio": "Neo Quimica Arena",
  "tecnico": "Renato Gaúcho",
  "placar": { "vasco": 0, "adversario": 1 },
  "arbitragem": {
    "arbitro": "Davi de Oliveira Lacerda",
    "auxiliares": ["Rafael da Silva Alves", "Douglas Pagung"],
    "var": "Rafael Traci"
  },
  "gols_adversario": [
    {
      "nome": "Matheus Bidu",
      "gols": 1,
      "minutos": [37],
      "periodo": "1T",
      "periodos": ["1T"],
      "clube": "Corinthians"
    }
  ],
  "cartoes_amarelos_vasco": [
    { "nome": "Tche Tche", "cartoes": 1, "clube": "Vasco" },
    { "nome": "Thiago Mendes", "cartoes": 1, "clube": "Vasco" },
    { "nome": "Cauan Barros", "cartoes": 1, "clube": "Vasco" },
    { "nome": "Johan Rojas", "cartoes": 1, "clube": "Vasco" }
  ]
}
```

## 11) Dica final para manter a base limpa

- Nao inventar nomes novos para tecnico, arbitro, auxiliares e VAR.
- Para nomes com acento, abreviacao ou grafia alternativa, sempre procurar equivalente existente no banco antes de inserir.
- Nao inventar reservas ausentes quando a materia trouxer apenas os jogadores que entraram.
- Se faltar banco completo, pedir ao usuario a foto da escalação antes de fechar.
- Se faltar renda ou publico em jogo em casa, pedir ao usuario antes de fechar.
- Sempre consultar a materia de `desfalques e pendurados` antes de fechar para registrar `suspensos` e `lesionados`.
- Se houver conflito entre a ficha do jogo e a materia pre-jogo sobre suspensao, priorizar a materia pre-jogo e registrar a duvida em `observacao`.
- Se um jogador sumir de `titulares` e `reservas` de uma partida para outra, nao deixar o status indefinido:
  - se a fonte indicar `lesionado`, `suspenso` ou `servindo_selecao`, usar esse status
  - se ele nao estiver nos relacionados atuais e nao houver outro motivo especifico, marcar como `nao_relacionado`
- Se novo nome adversario/jogador realmente for desconhecido:
  - manter consistencia do time no `adversario`.
  - inserir no `jogadores_vasco` ou `jogadores_contra` apenas se o nome for realmente novo.

## 12) Checklist rapido (usar antes de fechar)

- [ ] data no formato `dd/mm/aaaa`
- [ ] horario preenchido quando a fonte trouxer
- [ ] `local` e `estadio` corretos
- [ ] `competicao` valida e existente
- [ ] nome de `tecnico` padronizado
- [ ] arbitragem padronizada
- [ ] escalação com 11 titulares e 1 goleiro
- [ ] reservas >= 4
- [ ] suspensos pesquisados na materia de `desfalques e pendurados`
- [ ] lesionados/desfalques pesquisados na materia pre-jogo
- [ ] se a materia nao trouxer todos os reservas, pedir foto da escalação completa
- [ ] `titulares` e `reservas` contem apenas jogadores realmente relacionados para o jogo
- [ ] jogador que saiu dos relacionados e nao ganhou outro motivo especifico foi movido para `nao_relacionados`
- [ ] se `local = casa`, publico presente/pagante e renda coletados na materia e incluidos
- [ ] se `local = fora`, nao exigir publico/renda
- [ ] cartões, gols e substituicoes revisados
- [ ] conferencia de duplicidade no mesmo dia vs mesmo adversario
- [ ] salvar em DEV
- [ ] validar
- [ ] repetir em PRD

## 13) Fonte padrão: NetVasco (prioritária)

Sempre usar a matéria da NetVasco da rodada como fonte principal do jogo, porque ela costuma trazer:

- data/hora do texto
- horario do jogo
- placar e contexto do confronto
- bloco de ficha técnica completo (adversário, competição, local, árbitro/auxiliares/VAR)
- escalações e mudanças
- cartões e gols com detalhes por minuto
- renda e publico quando o jogo for em casa

Complemento recomendado:

- buscar tambem a materia `desfalques e pendurados` da mesma rodada para descobrir:
  - quem estava suspenso para a partida
  - quem estava fora por lesao
  - quem retornava de suspensao

## 14) Regras de parada obrigatoria

Antes de concluir a importacao, parar e pedir informacao ao usuario nestes casos:

- materia sem lista completa de reservas
- materia sem foto da escalação e sem banco completo
- jogo em casa sem `publico_pagante`
- jogo em casa sem `publico_presente`
- jogo em casa sem `renda`
- duvida de grafia de tecnico, estadio, arbitragem ou jogador sem equivalente claro no banco

Padrão de URL:

```
https://www.netvasco.com.br/n/<id>/<slug-da-materia>
```

Exemplos de matérias já usadas para validação:

- `https://www.netvasco.com.br/n/383669/vasco-perde-para-o-corinthians-no-itaquerao-1-a-0`

Como localizar no conteúdo da página:

- Bloco `FICHA TÉCNICA` para:
  - placar
  - campeonato
  - data
  - local
  - arbitragem
- Seção de escalação no bloco com:
  - `CORINTHIANS: ... Técnico: ...`
  - `VASCO: ... Técnico: ...`
- Lista de cartões:
  - `Cartões amarelos: ...`
  - `Cartão vermelho: ...`
- Linha de gols:
  - `Gols: Nome, minuto/periodo`
- Bloco de público (jogos em casa, quando existir):
  - `público pagante`
  - `público presente`

Observação crítica sobre reservas:

- No texto, a NetVasco normalmente não traz todos os reservas completos.
- Antes de finalizar, se a lista de reservas não estiver 100% (ou tiver ambiguidades), **peça a foto da escalação completa** para pegar substitutos e banco completo do jogo.
- Prioridade de preenchimento:
  - usar primeiro a informação textual (titulares + mudanças),
  - e completar reservas apenas com a foto da escalação.

Regra de controle:

- Sempre validar e padronizar nomes extraídos contra o banco antes de inserir (o que está no Guia das Regras de Padronizacao já cobre).
- Se faltar algum campo na matéria, completar depois via fonte secundária, sem inventar nomes.

---

Gerado para o fluxo pratico de importacao com padronizacao contra o banco local.
