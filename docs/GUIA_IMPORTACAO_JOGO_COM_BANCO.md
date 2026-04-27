# Guia prático para cadastrar o proximo jogo do Vasco (com padronizacao no banco)

Este documento serve para repetir o processo sem retrabalho: pegar o jogo, normalizar nomes com base no banco, montar o payload e cadastrar no projeto.

## 1) Objetivo
Inserir um jogo novo no sistema garantindo:

- Conjunto de campos completo do cadastro do jogo.
- Nomes padronizados para tecnico, jogadores e arbitragem conforme banco.
- Nenhum nome "novo" desnecessariamente criado quando existe equivalente no banco.
- Sem criar duplicata de competencia/tecnico/jogo.

## 2) Onde o app grava e consulta

- Banco ativo: `stats_vasco.sqlite3` (via `storage_sqlite.py`).
- Método de escrita: `save_matches(DB_PATH, jogos)` em `storage_sqlite.py`.
- Método de leitura: `load_matches(DB_PATH)`.
- Dicionario de listas auxiliares: `list_entries(list_type, value)`.
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

1. Coletar os dados brutos da fonte (noticia, relato tecnico, ficha de jogo).
2. Resolver nomes contra o banco antes de salvar.
3. Montar payload no formato aceito pelo app.
4. Conferir duplicata.
5. Inserir.
6. Atualizar lista de arbitros, auxiliares ou VAR, se houver nome novo faltante no cadastro.

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
- Titulares devem somar 11 e ter 1 goleiro.
- Reservas deve ter pelo menos 4.
- Periodo aceito no sistema para gols: `1T`, `2T`, `1P`, `2P`.
- Periodo aceito para substituicao: `1T`, `INT`, `2T`, `1P`, `INTP`, `2P`.
- Em substituicao no intervalo (`INT` ou `INTP`) pode usar minuto `0`.

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
   - `data`, `local`, `placar`
   - `adversario`, `competicao`, `estadio`, `tecnico`
   - nomes de arbitragem e cartoes/gols/escalacao
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
- Se novo nome adversario/jogador realmente for desconhecido:
  - manter consistencia do time no `adversario`.
  - inserir no `jogadores_vasco` ou `jogadores_contra` apenas se o nome for realmente novo.

## 12) Checklist rapido (usar antes de fechar)

- [ ] data no formato `dd/mm/aaaa`
- [ ] `local` e `estadio` corretos
- [ ] `competicao` valida e existente
- [ ] nome de `tecnico` padronizado
- [ ] arbitragem padronizada
- [ ] escalação com 11 titulares e 1 goleiro
- [ ] reservas >= 4
- [ ] cartões, gols e substituicoes revisados
- [ ] conferencia de duplicidade no mesmo dia vs mesmo adversario
- [ ] salvar

## 13) Fonte padrão: NetVasco (prioritária)

Sempre usar a matéria da NetVasco da rodada como fonte principal do jogo, porque ela costuma trazer:

- data/hora do texto
- placar e contexto do confronto
- bloco de ficha técnica completo (adversário, competição, local, árbitro/auxiliares/VAR)
- escalações e mudanças
- cartões e gols com detalhes por minuto

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

Regra de controle:

- Sempre validar e padronizar nomes extraídos contra o banco antes de inserir (o que está no Guia das Regras de Padronizacao já cobre).
- Se faltar algum campo na matéria, completar depois via fonte secundária, sem inventar nomes.

---

Gerado para o fluxo pratico de importacao com padronizacao contra o banco local.
