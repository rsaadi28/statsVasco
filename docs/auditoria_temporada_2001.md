# Auditoria Dos Jogos Do Vasco - Temporada 2001

- Banco auditado: `/Users/rodrigo/Library/Application Support/StatsVasco/stats_vasco.sqlite3`
- Modo de leitura: SQLite `mode=ro`
- Recorte: temporada NetVasco 2001, com 68 jogos, incluindo 2 amistosos no México.
- Nota de recorte: `18/01/2001 Vasco 3 x 1 São Caetano` é jogo válido pelo Brasileiro 2000 e fica como sobra no ano civil.

## Fontes
- indice_netvasco: https://www.netvasco.com.br/futebol/index2001.shtml
- estatisticas_netvasco: https://www.netvasco.com.br/futebol/estatisticas2001/
- rio_sao_paulo_netvasco: https://www.netvasco.com.br/futebol/riosaopaulo2001/
- estadual_netvasco: https://www.netvasco.com.br/futebol/estadual2001/
- libertadores_netvasco: https://www.netvasco.com.br/futebol/libertadores2001/
- mercosul_netvasco: https://www.netvasco.com.br/futebol/mercosul2001/
- brasileiro_netvasco: https://www.netvasco.com.br/futebol/brasileiro2001/index.html
- amistosos_netvasco: https://www.netvasco.com.br/futebol/amistosos2001/
- leon_supervasco: https://www.supervasco.com/noticias/ha-12-anos-vasco-vencia-amistoso-contra-o-leonmex-por-3-a-1-185670.html
- leon_blog_garone: https://blogdogarone.blogspot.com/2011/07/bau-do-portuga-ha-10-anos-vasco-vencia.html
- bahia_netvasco_ficha: https://www.netvasco.com.br/futebol/brasileiro2001/50vasbah.html
- corinthians_rsp_netvasco_ficha: https://www.netvasco.com.br/futebol/riosaopaulo2001/05vascor.html

## Totais

| Métrica | Banco atual ano civil 2001 | Referência NetVasco 2001 | Status |
| --- | ---: | ---: | --- |
| jogos | 67 | 68 | DIVERGE |
| vitorias | 35 | 35 | OK |
| empates | 15 | 16 | DIVERGE |
| derrotas | 17 | 17 | OK |
| gols_pro | 134 | 136 | DIVERGE |
| gols_contra | 81 | 83 | DIVERGE |

## Cobertura De Campos Ricos No Banco

| Campo salvo | Preenchidos em PRD | Observação |
| --- | ---: | --- |
| estadio | 0/67 | fichas NetVasco detalhadas cobrem parte relevante; PRD está vazio |
| horario | 1/67 | tabelas NetVasco por competição trazem horário para os 68 jogos |
| capitao | 0/67 | buscar em súmula/ficha detalhada; encontrado em algumas fichas |
| publico_pagante | 0/67 | NetVasco detalha público em fichas específicas; PRD está vazio |
| publico_presente | 0/67 | NetVasco detalha público em fichas específicas; PRD está vazio |
| renda | 0/67 | renda muitas vezes não divulgada |
| arbitragem | 0/67 | fichas NetVasco detalhadas trazem árbitros e auxiliares em parte dos jogos |
| escalacao | 0/67 | fichas NetVasco detalhadas trazem titulares e substituições em parte dos jogos |

## Totais Por Competição

| Competição | Banco atual ano civil 2001 | Referência NetVasco 2001 | Status |
| --- | --- | --- | --- |
| Amistoso | 0J 0V 0E 0D 0GP 0GC | 2J 1V 1E 0D 5GP 3GC | DIVERGE |
| Campeonato Brasileiro Serie A | 28J 11V 9E 8D 60GP 37GC | 27J 10V 9E 8D 57GP 36GC | DIVERGE |
| Campeonato Carioca | 19J 13V 3E 3D 42GP 18GC | 19J 13V 3E 3D 42GP 18GC | OK |
| Copa Libertadores | 10J 8V 0E 2D 20GP 10GC | 10J 8V 0E 2D 20GP 10GC | OK |
| Copa Mercosul | 6J 2V 2E 2D 11GP 11GC | 6J 2V 2E 2D 11GP 11GC | OK |
| Torneio Rio-São Paulo | 4J 1V 1E 2D 1GP 5GC | 4J 1V 1E 2D 1GP 5GC | OK |

## Fontes Complementares Mapeadas

| Jogo/Grupo | Campos aproveitáveis | Fonte | Status |
| --- | --- | --- | --- |
| 08/07/2001 León x Vasco | estádio, arbitragem, público, escalação, substituições, gols/minutos, cartões e observações | NetVasco Amistosos 2001 + SuperVasco + Blog do Garone | confirmado para SQL de correção/enriquecimento; ficha NetVasco traz ano 2000 por provável erro de template |
| 10/07/2001 Tigres x Vasco | estádio, arbitragem, público, escalação, substituições, gols/minutos, cartões e observações | NetVasco Amistosos 2001 | confirmado para SQL de correção/enriquecimento; ficha NetVasco traz ano 2000 por provável erro de template |
| 31/01/2001 Vasco x Corinthians | estádio, arbitragem, público, escalação, substituições, gols/minutos, cartões e observações | NetVasco Rio-São Paulo 2001, ficha 05vascor | fonte detalhada encontrada, pendente de SQL específico |
| 16/09/2001 Vasco x Bahia | estádio, arbitragem completa, público pagante, escalação, reservas, substituições, gols/minutos, cartões e observações | NetVasco Brasileiro 2001, ficha 50vasbah | fonte detalhada encontrada, pendente de SQL específico |
| Brasileiro 2001 | 24 fichas detalhadas linkadas pela página da competição, mais tabela completa de 27 jogos | NetVasco Brasileiro 2001 | fonte complementar mapeada |
| Estadual/Rio-SP/Libertadores/Mercosul 2001 | fichas detalhadas parciais e tabelas completas por competição | NetVasco por competição | fonte complementar mapeada |
| Jogos de Brasileiro e Libertadores | validação cruzada de placar, mando e ficha quando disponível | oGol/Zerozero/PlaymakerStats/Soccerzz/Football-Lineups e páginas de adversários | candidato para próximas levas de enriquecimento fino |

## Enriquecimento Global Preparado

- Horários: referência externa mapeada para os 68 jogos a partir das páginas NetVasco por competição.
- Técnicos: `Joel Santana` até os amistosos de julho; `Hélio dos Anjos` a partir da Copa Mercosul/Brasileiro.
- Correção de núcleo preparada: inclusão revisável dos amistosos `León 1 x 3 Vasco` e `Tigres 2 x 2 Vasco`.
- Campos ricos preparados em SQL específico para os dois amistosos mexicanos.
- Jogadores históricos ausentes detectados para revisar antes de aplicar escalações: `Valdo` e `William`.

## Validação Em Cópia Temporária

- Cópia validada: `/tmp/stats_vasco_2001_audit.sqlite3`.
- SQLs aplicados na cópia: jogadores históricos, correção de núcleo, horários/técnicos e enriquecimento dos amistosos do México.
- `load_matches('/tmp/stats_vasco_2001_audit.sqlite3')` carregou `1757` partidas sem erro.
- Recorte NetVasco 2001 após aplicação, excluindo `18/01/2001` por pertencer ao Brasileiro 2000: `68J 35V 16E 17D 136GP 83GC`.
- Cobertura de horários no recorte validado: `68/68`.

## Aplicação Em PRD

- Aplicado em PRD em 08/05/2026.
- Backup criado antes da aplicação: `/Users/rodrigo/Library/Application Support/StatsVasco/stats_vasco.sqlite3.backup_before_temporada_2001_20260508_122239`.
- `load_matches('/Users/rodrigo/Library/Application Support/StatsVasco/stats_vasco.sqlite3')` carregou `1757` partidas sem erro.
- Recorte NetVasco 2001 em PRD, excluindo `18/01/2001` por pertencer ao Brasileiro 2000: `68J 35V 16E 17D 136GP 83GC`.
- Amistosos inseridos em PRD: `08/07/2001 León 1 x 3 Vasco` e `10/07/2001 Tigres 2 x 2 Vasco`.

## Confirmado Para Corrigir/Enriquecer

- Faltando no banco: 08/07/2001 | Amistoso | León | 3x1
  - Gols Vasco na fonte: Pedrinho, Romário, Paulo César
  - Fonte: NetVasco Amistosos 2001 + SuperVasco
- Faltando no banco: 10/07/2001 | Amistoso | Tigres | 2x2
  - Gols Vasco na fonte: Romário, Gilberto
  - Fonte: NetVasco Amistosos 2001

## Precisa Revisão Manual

- Sobrando no recorte 2001: `215383` 18/01/2001 | Campeonato Brasileiro Serie A | São Caetano-SP | 3x1
  - Observação: fora do recorte NetVasco 2001; pertence à temporada 2000 se for a final contra o São Caetano

## Sem Divergência De Núcleo

- 17/01/2001 | Torneio Rio-São Paulo | São Paulo-SP | banco `0x2` = fonte `0x2` | local `fora` | técnico `Joel Santana` | gols banco: - | gols fonte: -
- 21/01/2001 | Campeonato Carioca | Madureira-RJ | banco `1x2` = fonte `1x2` | local `casa` | técnico `Joel Santana` | gols banco: Pedrinho:1 | gols fonte: Pedrinho
- 24/01/2001 | Torneio Rio-São Paulo | Palmeiras-SP | banco `0x0` = fonte `0x0` | local `casa` | técnico `Joel Santana` | gols banco: - | gols fonte: -
- 27/01/2001 | Campeonato Carioca | Friburguense | banco `2x1` = fonte `2x1` | local `fora` | técnico `Joel Santana` | gols banco: Ely Thadeu:1; Zada:1 | gols fonte: Ely Thadeu, Zada
- 31/01/2001 | Torneio Rio-São Paulo | Corinthians | banco `1x0` = fonte `1x0` | local `casa` | técnico `Joel Santana` | gols banco: Alex Oliveira:1 | gols fonte: Alex Oliveira
- 03/02/2001 | Campeonato Carioca | América | banco `1x0` = fonte `1x0` | local `fora` | técnico `Joel Santana` | gols banco: Maricá:1 | gols fonte: Maricá
- 07/02/2001 | Torneio Rio-São Paulo | Santos | banco `0x3` = fonte `0x3` | local `fora` | técnico `Joel Santana` | gols banco: - | gols fonte: -
- 11/02/2001 | Campeonato Carioca | Fluminense-RJ | banco `2x0` = fonte `2x0` | local `casa` | técnico `Joel Santana` | gols banco: Pedrinho:1; Euller:1 | gols fonte: Pedrinho, Euller
- 17/02/2001 | Campeonato Carioca | Cabofriense-RJ | banco `3x1` = fonte `3x1` | local `casa` | técnico `Joel Santana` | gols banco: Romário:2; Juninho Paulista:1 | gols fonte: Romário (2), Juninho Paulista
- 22/02/2001 | Campeonato Carioca | Flamengo-RJ | banco `0x1` = fonte `0x1` | local `fora` | técnico `Joel Santana` | gols banco: - | gols fonte: -
- 11/03/2001 | Campeonato Carioca | Cabofriense-RJ | banco `3x1` = fonte `3x1` | local `casa` | técnico `Joel Santana` | gols banco: Geder:1; Romário:2 | gols fonte: Geder, Romário (2)
- 14/03/2001 | Copa Libertadores | América Cáli | banco `3x0` = fonte `3x0` | local `fora` | técnico `Joel Santana` | gols banco: Juninho Paulista:1; Clébson:1; Euller:1 | gols fonte: Juninho Paulista, Clébson, Euller
- 17/03/2001 | Campeonato Carioca | Olaria-RJ | banco `1x0` = fonte `1x0` | local `fora` | técnico `Joel Santana` | gols banco: Romário:1 | gols fonte: Romário
- 21/03/2001 | Copa Libertadores | Dep. Táchira | banco `1x0` = fonte `1x0` | local `fora` | técnico `Joel Santana` | gols banco: Euller:1 | gols fonte: Euller
- 30/03/2001 | Campeonato Carioca | Madureira-RJ | banco `3x1` = fonte `3x1` | local `casa` | técnico `Joel Santana` | gols banco: Torres:1; Viola:1; Juninho Paulista:1 | gols fonte: Torres, Viola, Juninho Paulista
- 02/04/2001 | Campeonato Carioca | V. Redonda | banco `2x1` = fonte `2x1` | local `casa` | técnico `Joel Santana` | gols banco: Romário:1; Jorginho Paulista:1 | gols fonte: Romário, Jorginho Paulista
- 05/04/2001 | Copa Libertadores | Peñarol | banco `2x1` = fonte `2x1` | local `casa` | técnico `Joel Santana` | gols banco: Viola:2 | gols fonte: Viola (2)
- 08/04/2001 | Campeonato Carioca | Americano-RJ | banco `1x1` = fonte `1x1` | local `fora` | técnico `Joel Santana` | gols banco: Juninho Paulista:1 | gols fonte: Juninho Paulista
- 12/04/2001 | Copa Libertadores | América Cáli | banco `4x1` = fonte `4x1` | local `casa` | técnico `Joel Santana` | gols banco: Gol contra:1; Clébson:1; Romário:1; Jorginho Paulista:1 | gols fonte: Viáfara (contra), Clébson, Romário, Jorginho Paulista
- 15/04/2001 | Campeonato Carioca | Fluminense-RJ | banco `3x3` = fonte `3x3` | local `fora` | técnico `Joel Santana` | gols banco: Viola:1; Pedrinho:1; Dedé:1 | gols fonte: Viola, Pedrinho, Dedé
- 18/04/2001 | Campeonato Carioca | Friburguense | banco `2x0` = fonte `2x0` | local `fora` | técnico `Joel Santana` | gols banco: Dedé:1; Pedrinho:1 | gols fonte: Dedé, Pedrinho
- 21/04/2001 | Copa Libertadores | Dep. Táchira | banco `3x2` = fonte `3x2` | local `casa` | técnico `Joel Santana` | gols banco: Romário:2; Dedé:1 | gols fonte: Romário (2), Dedé
- 26/04/2001 | Campeonato Carioca | Bangu-RJ | banco `3x2` = fonte `3x2` | local `casa` | técnico `Joel Santana` | gols banco: Romário:2; Viola:1 | gols fonte: Romário (2), Viola
- 29/04/2001 | Campeonato Carioca | Botafogo | banco `7x0` = fonte `7x0` | local `casa` | técnico `Joel Santana` | gols banco: Romário:2; Juninho Paulista:3; Pedrinho:1; Euller:1 | gols fonte: Romário (2), Juninho Paulista (3), Pedrinho, Euller
- 02/05/2001 | Copa Libertadores | Peñarol | banco `3x1` = fonte `3x1` | local `fora` | técnico `Joel Santana` | gols banco: Dedé:2; Viola:1 | gols fonte: Dedé (2), Viola
- 05/05/2001 | Campeonato Carioca | América | banco `5x0` = fonte `5x0` | local `fora` | técnico `Joel Santana` | gols banco: Romário:3; Jorginho Paulista:1; Euller:1 | gols fonte: Romário (3), Jorginho Paulista, Euller
- 09/05/2001 | Copa Libertadores | Dep. Concepción | banco `3x1` = fonte `3x1` | local `fora` | técnico `Joel Santana` | gols banco: Juninho Paulista:2; Romário:1 | gols fonte: Juninho Paulista (2), Romário
- 13/05/2001 | Campeonato Carioca | Flamengo-RJ | banco `0x0` = fonte `0x0` | local `fora` | técnico `Joel Santana` | gols banco: - | gols fonte: -
- 16/05/2001 | Copa Libertadores | Dep. Concepción | banco `1x0` = fonte `1x0` | local `casa` | técnico `Joel Santana` | gols banco: Juninho Paulista:1 | gols fonte: Juninho Paulista
- 20/05/2001 | Campeonato Carioca | Flamengo-RJ | banco `2x1` = fonte `2x1` | local `fora` | técnico `Joel Santana` | gols banco: Viola:1; Juninho Paulista:1 | gols fonte: Viola, Juninho Paulista
- 23/05/2001 | Copa Libertadores | Boca Juniors | banco `0x1` = fonte `0x1` | local `casa` | técnico `Joel Santana` | gols banco: - | gols fonte: -
- 27/05/2001 | Campeonato Carioca | Flamengo-RJ | banco `1x3` = fonte `1x3` | local `casa` | técnico `Joel Santana` | gols banco: Juninho Paulista:1 | gols fonte: Juninho Paulista
- 30/05/2001 | Copa Libertadores | Boca Juniors | banco `0x3` = fonte `0x3` | local `fora` | técnico `Joel Santana` | gols banco: - | gols fonte: -
- 24/07/2001 | Copa Mercosul | U. Católica | banco `1x2` = fonte `1x2` | local `fora` | técnico `Hélio dos Anjos` | gols banco: Euller:1 | gols fonte: Euller
- 29/07/2001 | Copa Mercosul | Boca Juniors | banco `2x2` = fonte `2x2` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Pedrinho:1; Patrício:1 | gols fonte: Pedrinho, Patrício
- 01/08/2001 | Campeonato Brasileiro Serie A | Gama-DF | banco `0x0` = fonte `0x0` | local `fora` | técnico `Hélio dos Anjos` | gols banco: - | gols fonte: -
- 05/08/2001 | Campeonato Brasileiro Serie A | Guarani-SP | banco `7x1` = fonte `7x1` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Romário:4; Juninho Paulista:1; Jorginho:1; Botti:1 | gols fonte: Romário (4), Juninho Paulista, Jorginho, Botti
- 08/08/2001 | Campeonato Brasileiro Serie A | Coritiba-PR | banco `0x1` = fonte `0x1` | local `fora` | técnico `Hélio dos Anjos` | gols banco: - | gols fonte: -
- 11/08/2001 | Campeonato Brasileiro Serie A | Juventude-RS | banco `1x1` = fonte `1x1` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Dedé:1 | gols fonte: Dedé
- 15/08/2001 | Campeonato Brasileiro Serie A | Vitória-BA | banco `0x1` = fonte `0x1` | local `fora` | técnico `Hélio dos Anjos` | gols banco: - | gols fonte: -
- 18/08/2001 | Campeonato Brasileiro Serie A | Santa Cruz-PE | banco `1x1` = fonte `1x1` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Euller:1 | gols fonte: Euller
- 21/08/2001 | Copa Mercosul | C. Porteño | banco `1x2` = fonte `1x2` | local `fora` | técnico `Hélio dos Anjos` | gols banco: Juninho Paulista:1 | gols fonte: Juninho Paulista
- 26/08/2001 | Campeonato Brasileiro Serie A | Atlético-PR | banco `4x0` = fonte `4x0` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Euller:2; Juninho Paulista:1; Fabiano Eller:1 | gols fonte: Euller (2), Juninho Paulista, Fabiano Eller
- 29/08/2001 | Campeonato Brasileiro Serie A | América-MG | banco `1x1` = fonte `1x1` | local `fora` | técnico `Hélio dos Anjos` | gols banco: Euller:1 | gols fonte: Euller
- 02/09/2001 | Campeonato Brasileiro Serie A | Botafogo-SP | banco `2x2` = fonte `2x2` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Ricardo Bóvio:1; Bebeto:1 | gols fonte: Ricardo Bóvio, Bebeto
- 09/09/2001 | Campeonato Brasileiro Serie A | Sport-PE | banco `3x3` = fonte `3x3` | local `fora` | técnico `Hélio dos Anjos` | gols banco: Ricardo Bóvio:1; Bebeto:1; Euller:1 | gols fonte: Ricardo Bóvio, Bebeto, Euller
- 13/09/2001 | Copa Mercosul | U. Católica | banco `2x1` = fonte `2x1` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Romário:1; Juninho Paulista:1 | gols fonte: Romário, Juninho Paulista
- 16/09/2001 | Campeonato Brasileiro Serie A | Bahia-BA | banco `0x1` = fonte `0x1` | local `casa` | técnico `Hélio dos Anjos` | gols banco: - | gols fonte: -
- 19/09/2001 | Campeonato Brasileiro Serie A | Paraná-PR | banco `0x2` = fonte `0x2` | local `fora` | técnico `Hélio dos Anjos` | gols banco: - | gols fonte: -
- 22/09/2001 | Campeonato Brasileiro Serie A | Goiás-GO | banco `2x1` = fonte `2x1` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Paulo César:1; Juninho Paulista:1 | gols fonte: Paulo César, Juninho Paulista
- 25/09/2001 | Copa Mercosul | Boca Juniors | banco `2x2` = fonte `2x2` | local `fora` | técnico `Hélio dos Anjos` | gols banco: Odvan:1; Euller:1 | gols fonte: Odvan, Euller
- 30/09/2001 | Campeonato Brasileiro Serie A | Ponte Preta-SP | banco `2x2` = fonte `2x2` | local `fora` | técnico `Hélio dos Anjos` | gols banco: Fabiano Eller:2 | gols fonte: Fabiano Eller (2)
- 03/10/2001 | Campeonato Brasileiro Serie A | Cruzeiro-MG | banco `3x0` = fonte `3x0` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Romário:3 | gols fonte: Romário (3)
- 06/10/2001 | Campeonato Brasileiro Serie A | Flamengo-RJ | banco `5x1` = fonte `5x1` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Romário:3; Gilberto:1; Euller:1 | gols fonte: Romário (3), Gilberto, Euller
- 10/10/2001 | Campeonato Brasileiro Serie A | Inter-RS | banco `0x2` = fonte `0x2` | local `fora` | técnico `Hélio dos Anjos` | gols banco: - | gols fonte: -
- 13/10/2001 | Campeonato Brasileiro Serie A | Botafogo-RJ | banco `3x1` = fonte `3x1` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Romário:1; Gol contra:1; Rafael:1 | gols fonte: Romário, Tiago (contra), Rafael
- 17/10/2001 | Copa Mercosul | C. Porteño | banco `3x2` = fonte `3x2` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Léo Lima:1; Paulo César:1; Ely Thadeu:1 | gols fonte: Léo Lima, Paulo César, Ely Thadeu
- 20/10/2001 | Campeonato Brasileiro Serie A | São Caetano-SP | banco `1x2` = fonte `1x2` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Juninho Paulista:1 | gols fonte: Juninho Paulista
- 28/10/2001 | Campeonato Brasileiro Serie A | Fluminense-RJ | banco `2x2` = fonte `2x2` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Romário:2 | gols fonte: Romário (2)
- 04/11/2001 | Campeonato Brasileiro Serie A | Portuguesa | banco `4x5` = fonte `4x5` | local `fora` | técnico `Hélio dos Anjos` | gols banco: Romário:2; Gilberto:1; Gol contra:1 | gols fonte: Romário (2), Gilberto, Tiago Silva (contra)
- 08/11/2001 | Campeonato Brasileiro Serie A | Corinthians | banco `1x0` = fonte `1x0` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Jamir:1 | gols fonte: Jamir
- 11/11/2001 | Campeonato Brasileiro Serie A | Atlético-MG | banco `1x2` = fonte `1x2` | local `fora` | técnico `Hélio dos Anjos` | gols banco: Ely Thadeu:1 | gols fonte: Ely Thadeu
- 15/11/2001 | Campeonato Brasileiro Serie A | Grêmio-RS | banco `2x0` = fonte `2x0` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Romário:1; Léo Lima:1 | gols fonte: Romário, Léo Lima
- 18/11/2001 | Campeonato Brasileiro Serie A | Palmeiras-SP | banco `3x1` = fonte `3x1` | local `fora` | técnico `Hélio dos Anjos` | gols banco: Romário:2; Ely Thadeu:1 | gols fonte: Romário (2), Ely Thadeu
- 25/11/2001 | Campeonato Brasileiro Serie A | São Paulo-SP | banco `7x1` = fonte `7x1` | local `casa` | técnico `Hélio dos Anjos` | gols banco: Romário:3; Gilberto:1; Euller:1; Léo Lima:1; Dedé:1 | gols fonte: Romário (3), Gilberto, Euller, Léo Lima, Dedé
- 02/12/2001 | Campeonato Brasileiro Serie A | Santos | banco `2x2` = fonte `2x2` | local `fora` | técnico `Hélio dos Anjos` | gols banco: Gilberto:1; Dedé:1 | gols fonte: Gilberto, Dedé
