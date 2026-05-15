# Mapa de auditoria de temporadas historicas

Este guia deixa o fluxo pronto para repetir a auditoria do ano 2000 nos anos seguintes.

## Objetivo

Auditar e enriquecer todos os jogos de uma temporada sem editar PRD diretamente:

- comparar o banco de PRD em modo leitura;
- validar o nucleo do jogo: data, adversario, competicao, local, placar, gols e tecnico;
- mapear todos os campos ricos salvos pelo app: estadio, horario, capitao, publico, renda, arbitragem, escalação, relacionados, substituições, minutos, cartões, gols anulados e observações;
- cadastrar jogadores historicos que aparecerem nas fontes para que ex-jogadores também fiquem visiveis na aba de jogadores;
- gerar SQL revisavel para aplicar primeiro em copia/DEV e só depois em PRD.

## Fontes por prioridade

1. Fontes oficiais ou institucionais do jogo/clube/competição.
2. NetVasco, Vaskipédia e páginas históricas do Vasco.
3. Bases de ficha de jogo: oGol/Zerozero, PlaymakerStats, Soccerzz, Football-Lineups, Transfermarkt.
4. Sites oficiais dos adversários, especialmente quando têm almanaque ou memorial.
5. Hemerotecas e imprensa da época para público, renda, súmula, cartões e escalações.

Não usar uma única fonte quando houver conflito. Quando duas fontes discordarem, registrar no CSV e só gerar SQL para o dado confirmado.

## Artefatos por ano

Para cada ano, manter estes arquivos:

- `scripts/audit_temporada_<ano>.py`: matriz esperada, fontes e exportadores.
- `docs/auditoria_temporada_<ano>.md`: relatório humano.
- `docs/auditoria_temporada_<ano>_mapa.csv`: mapa jogo a jogo com todos os campos pesquisáveis.
- `docs/sql_corrigir_temporada_<ano>.sql`: correções de núcleo confirmadas.
- `docs/sql_enriquecer_temporada_<ano>_*.sql`: enriquecimentos por bloco de campo ou por jogo.

## Colunas mínimas do CSV

O mapa CSV deve ter uma linha por jogo e, no mínimo:

- `match_id`, `data`, `competicao`, `adversario`, `local_ref`;
- `placar_ref`, `placar_banco`, `gols_vasco_ref`, `gols_vasco_banco`;
- `tecnico_ref`, `tecnico_banco`, `tecnico_status`;
- `horario_ref`, `horario_banco`, `horario_status`;
- `estadio_ref`, `estadio_banco`, `estadio_status`;
- `arbitro_ref`, `arbitragem_banco`, `arbitragem_status`;
- `titulares_status`, `reservas_status`, `substituicoes_status`;
- `relacionados_status`, `minutos_status`, `cartoes_status`;
- `publico_presente_ref`, `publico_banco`, `renda_banco`;
- `fonte_rica`.

## Campos que o banco realmente guarda

Ao pesquisar uma temporada, cobrir todos estes campos do schema atual:

Partida (`matches`):

- `date_text` / `date_iso`: data do jogo.
- `opponent_team_id`: adversário padronizado.
- `competition_id`: competição padronizada.
- `location`: `casa` ou `fora`.
- `stadium`: estádio.
- `match_time`: horário.
- `vasco_goals` e `opponent_goals`: placar.
- `observation`: contexto/fase/observações relevantes.
- `coach_id`: técnico do Vasco.
- `table_position`: posição na tabela quando a competição usar isso.
- `captain_name`: capitão do Vasco.
- `paid_attendance`: público pagante.
- `total_attendance`: público presente/total.
- `match_revenue`: renda.
- `arbitration_json`: árbitro, auxiliares e VAR.
- `lineup_json`: escalação, reservas, substituições e status dos relacionados.

Gols (`match_goals`):

- `side`: `vasco` ou `adversario`.
- `player_name` / `player_id`: autor do gol quando conhecido.
- `goals`: quantidade de gols daquele jogador.
- `club_name`: clube do autor quando for adversário ou gol contra identificado.
- `is_disallowed`: `0` para gol válido, `1` para gol anulado.
- `goal_minutes_json`: minutos dos gols, quando encontrados.
- `goal_periods_json`: período dos gols (`1T`, `2T`, `1P`, `2P` etc.), quando encontrado.

Cartões (`match_cards`):

- `side`: no fluxo atual do app, preencher principalmente cartões do Vasco.
- `player_name` / `player_id`: jogador advertido/expulso.
- `card_type`: `amarelo` ou `vermelho`.
- `card_count`: quantidade.
- `club_name`: clube, quando necessário.

Escalação (`lineup_json`):

- `titulares_por_posicao`: posições do app (`Goleiro`, `Lateral-Direito`, `Zagueiro`, `Lateral-Esquerdo`, `Volante`, `Meio-Campista`, `Atacante`).
- `reservas`: banco completo quando houver fonte.
- `reservas_que_entraram`: reservas usados, quando houver fonte ou substituições.
- `substituicoes`: `jogador_saiu`, `jogador_entrou`, `minuto`, `periodo`.
- `nao_relacionados`: jogadores do grupo que ficaram fora sem outro motivo.
- `lesionados`: desfalques médicos.
- `suspensos`: desfalques por suspensão.
- `servindo_selecao`: jogadores fora por seleção.

Jogadores históricos (`players`, `historic_players`, `list_entries`):

- `players.name`: nome padronizado.
- `historic_players.position`: posição, quando confirmada.
- `registered_date_text`, `joined_date_text`, `left_date_text`: datas quando houver fonte.
- `passages_json`: passagens quando houver fonte confiável.
- `matches_played_for_vasco`: só preencher quando houver total confiável; caso contrário deixar em branco.
- `list_entries`: manter listas auxiliares para jogadores, clubes, competições, técnicos, estádios e arbitragem.

## Profundidade máxima por jogo

Para cada partida, pesquisar tudo que existir em fontes confiaveis e deixar em branco apenas o que realmente não for encontrado:

- Identificação: data, hora, competição, fase/rodada, adversário, mando, estádio, cidade e país.
- Resultado: placar, gols do Vasco, gols do adversário, minutos dos gols, períodos, gols contra, gols anulados e disputa por pênaltis quando houver.
- Comissão/jogo: técnico do Vasco, capitão, observação/contexto da partida.
- Arbitragem: árbitro, auxiliares, quarto árbitro e VAR quando existir. Para anos antigos, VAR normalmente fica em branco.
- Público e renda: público pagante, público presente e renda, tanto em casa quanto fora, se a fonte trouxer.
- Cartões: amarelos e vermelhos do Vasco, com quantidade por jogador; minutos se a fonte trouxer.
- Cartões adversários: pesquisar e registrar no CSV quando encontrados, mas só gerar SQL se o app/tela for usar esse lado; hoje o fluxo principal carrega cartões do Vasco.
- Escalação titular: 11 titulares do Vasco, com posição quando a fonte permitir.
- Banco/reservas: todos os reservas relacionados, quando a fonte trouxer.
- Substituições: jogador que saiu, jogador que entrou, minuto e período.
- Relacionados especiais: não relacionados, lesionados, suspensos e servindo seleção, quando houver matéria pré-jogo ou súmula.
- Minutagem de jogador: quando houver fonte com substituições/minutos, registrar o possível para calcular participação na aba de jogadores.
- Jogadores históricos: todo jogador que aparece em titular, reserva, substituição, gol, cartão, capitão, suspenso, lesionado ou não relacionado deve existir em `historic_players`/listas auxiliares conforme o padrão do app.

Regra de segurança: se a fonte só confirma parte da informação, preencher a parte confirmada e deixar o restante em branco. Não inferir banco, substituição, capitão, minutos ou relacionados por escalação provável.

## Status de completude por jogo

Cada jogo deve receber status por bloco no CSV:

- `confirmado`: fonte confiável trouxe o dado completo.
- `parcial`: fonte trouxe parte do dado, por exemplo titulares sem banco.
- `não encontrado`: pesquisado e não localizado.
- `conflito`: duas fontes confiáveis discordam; não gerar SQL até resolver.
- `não aplicável`: campo inexistente na época ou no contexto, como VAR em 2001.

Para escalação:

- Gerar SQL de `escalacao_partida` se os 11 titulares estiverem confirmados.
- Reservas podem ficar vazias se não houver fonte, mas `reservas_status` deve ficar `não encontrado`.
- Substituições podem ficar vazias se não houver fonte, mas `substituicoes_status` deve ficar `não encontrado`.
- Se houver banco ou substituições sem posição segura, ainda assim salvar nomes confirmados em `reservas` e `substituicoes`, sem inventar posições.

## Jogadores históricos

Antes de aplicar SQL de escalação ou eventos:

1. Extrair todos os nomes de jogadores citados nas fontes.
2. Comparar com `players`, `list_entries` e `historic_players`.
3. Normalizar grafias conhecidas, acentos e apelidos.
4. Criar SQL revisável para inserir jogadores ausentes no cadastro histórico.
5. Só depois aplicar escalações, gols, cartões e substituições.

Campos mínimos para novos jogadores históricos quando a fonte não trouxer mais dados:

- nome;
- posição, se confirmada;
- período/passagem, se confirmada;
- deixar em branco/null o que não foi encontrado.

Não usar ausência de fonte como motivo para bloquear a partida inteira: registra-se o jogo com o máximo confirmado e marca-se o restante como pendente.

## Execução em lotes pequenos

Depois da auditoria de núcleo da temporada inteira, os campos ricos devem ser pesquisados e aplicados em lotes pequenos de jogos consecutivos. A meta é avançar com segurança, não esperar que todos os campos de todos os jogos estejam completos.

Tamanho recomendado:

- Primeiro lote de um ano: 5 a 8 jogos consecutivos.
- Se o padrão das fontes estiver limpo e a validação passar, próximos lotes: até 10 jogos.
- Se houver HTML quebrado, ficha incompleta ou conflito de fonte, reduzir para 1 a 3 jogos.

Para cada lote:

1. Ler manualmente as fichas/fontes de cada jogo do lote.
2. Registrar no CSV todos os campos encontrados e o status por bloco.
3. Gerar SQL apenas para os dados confirmados.
4. Não inventar dado ausente: se a fonte não trouxer banco, renda, auxiliar, capitão, minuto ou substituição, deixar em branco e marcar `não encontrado` ou `parcial`.
5. Se uma ficha trouxer parte da escalação, salvar apenas o que for modelável sem distorcer o app. Exemplo: só gerar `lineup_json` completo quando houver 11 titulares confirmados; reservas e substituições podem ficar vazias se não encontrados.
6. Validar o SQL do lote em cópia temporária do banco.
7. Rodar novamente o script de auditoria para confirmar que o CSV e o relatório refletem o estado pós-lote.
8. Rodar `load_matches` na cópia.
9. Só depois aplicar o lote em DEV e PRD, com backup antes de cada aplicação.

Estados recomendados no CSV para lotes:

- `confirmado - aplicado`: dado confirmado e já aplicado no banco.
- `confirmado - sql gerado`: dado confirmado, mas ainda não aplicado.
- `parcial - aplicado`: parte confirmada foi aplicada e o restante ficou vazio.
- `parcial - pendente`: parte confirmada foi registrada no CSV, mas ainda não virou SQL.
- `não encontrado`: campo pesquisado e não localizado.
- `conflito`: fontes discordam; registrar as fontes e não gerar SQL para esse campo.
- `pendente - fonte indicada`: há link/fonte provável, mas o campo ainda não foi revisado.

O relatório Markdown do ano deve ter uma seção por lote aplicado, com:

- intervalo de jogos do lote;
- SQLs aplicados;
- cópia temporária validada;
- backups de DEV e PRD;
- resultado de `load_matches`;
- cobertura final do recorte depois do lote.

## Fluxo para qualquer ano

1. Copiar `scripts/audit_temporada_2000.py` para o novo ano.
2. Trocar `EXPECTED_MATCHES`, `EXPECTED_TIMES`, totais e fontes para o ano solicitado.
3. Criar também matrizes de enriquecimento:
   - `EXPECTED_LINEUPS`, quando houver escalação;
   - `EXPECTED_SUBSTITUTIONS`, quando houver substituições;
   - `EXPECTED_CARDS`, quando houver cartões;
   - `EXPECTED_ATTENDANCE_REVENUE`, quando houver público/renda;
   - `EXPECTED_PLAYER_REGISTRY`, quando houver jogadores ausentes no cadastro.
4. Rodar contra PRD em modo leitura:

```bash
ANO=2001
python3 "scripts/audit_temporada_${ANO}.py" \
  --output "docs/auditoria_temporada_${ANO}.md" \
  --map-output "docs/auditoria_temporada_${ANO}_mapa.csv" \
  --sql-output "docs/sql_enriquecer_temporada_${ANO}_horarios_tecnicos.sql"
```

5. Revisar o Markdown e o CSV.
6. Separar os SQLs em dois níveis:
   - núcleo/global da temporada: correções de data, adversário, competição, mando, placar, gols, técnico e horários;
   - lotes de campos ricos: estádio, arbitragem, público, renda, capitão, escalação, banco, substituições, cartões e minutos.
7. Aplicar SQL apenas em copia temporaria:

```bash
ANO=2001
cp "$HOME/Library/Application Support/StatsVasco/stats_vasco.sqlite3" "/tmp/stats_vasco_${ANO}_audit.sqlite3"
sqlite3 "/tmp/stats_vasco_${ANO}_audit.sqlite3" < "docs/sql_corrigir_temporada_${ANO}.sql"
sqlite3 "/tmp/stats_vasco_${ANO}_audit.sqlite3" < "docs/sql_enriquecer_temporada_${ANO}_horarios_tecnicos.sql"
sqlite3 "/tmp/stats_vasco_${ANO}_audit.sqlite3" < "docs/sql_enriquecer_temporada_${ANO}_lote_001.sql"
python3 "scripts/audit_temporada_${ANO}.py" --db "/tmp/stats_vasco_${ANO}_audit.sqlite3"
```

8. Validar leitura pelo app:

```bash
ANO=2001
python3 - <<'PY'
from storage_sqlite import load_matches
import os
ano = os.environ.get("ANO", "2001")
matches = load_matches(f'/tmp/stats_vasco_{ano}_audit.sqlite3')
print(len(matches))
PY
```

9. Conferir aba/relatórios de jogadores:
   - ex-jogadores aparecem no histórico;
   - contagem de jogos não diminuiu indevidamente;
   - gols/cartões/substituições aparecem nos detalhes.
10. Só depois repetir em DEV/PRD.

## Status da temporada 2000

Arquivos prontos:

- `docs/auditoria_temporada_2000.md`
- `docs/auditoria_temporada_2000_mapa.csv`
- `docs/sql_corrigir_temporada_2000.sql`
- `docs/sql_enriquecer_temporada_2000_horarios_tecnicos.sql`
- `docs/sql_enriquecer_temporada_2000_20000301.sql`

O ano 2000 já tem:

- auditoria de núcleo para os 89 jogos;
- mapa jogo a jogo para todos os campos ricos;
- SQL global para horários e técnicos;
- SQL específico de enriquecimento completo para Palmeiras-SP x Vasco em 01/03/2000.

## Prompt padrão para solicitar uma temporada

Quando quiser que a auditoria seja executada para outro ano, envie uma mensagem neste formato:

```text
Execute o MAPA_AUDITORIA_TEMPORADAS.md para a temporada <ANO>.
Pesquise o máximo de dados disponíveis na internet para todos os jogos do Vasco desse ano:
núcleo do jogo, estádio, horário, técnico, capitão, público, renda, arbitragem,
gols válidos/anulados com minutos e períodos, cartões amarelos/vermelhos,
escalação titular, reservas, reservas que entraram, substituições, lesionados,
suspensos, não relacionados, servindo seleção e jogadores históricos.
Não altere PRD antes de gerar relatório, mapa CSV e SQLs revisáveis.
Valide tudo em cópia temporária antes de pedir/aplicar em PRD.
```

Ao receber esse pedido, o executor deve:

1. Ler este documento primeiro.
2. Auditar PRD em modo leitura.
3. Pesquisar múltiplas fontes, não só NetVasco.
4. Gerar Markdown, CSV e SQLs revisáveis.
5. Validar em cópia temporária.
6. Só aplicar em PRD se o usuário pedir explicitamente.
