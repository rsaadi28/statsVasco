# Auditoria Dos Jogos Do Vasco - Temporada 2002

- Banco auditado: `/Users/rodrigo/Library/Application Support/StatsVasco/stats_vasco.sqlite3`
- Modo de leitura: SQLite `mode=ro`
- Recorte: temporada NetVasco 2002, com 76 jogos e sem amistosos listados nas estatísticas.
- Nota de técnico: fichas de junho/julho ainda trazem `Evaristo de Macedo`; fichas do Brasileiro trazem `Antônio Lopes` até o fim da temporada.

## Fontes
- indice_netvasco: https://www.netvasco.com.br/futebol/index2002.shtml
- estatisticas_netvasco: https://www.netvasco.com.br/futebol/estatisticas2002/
- rio_sao_paulo_netvasco: https://www.netvasco.com.br/futebol/riosaopaulo2002/
- estadual_netvasco: https://www.netvasco.com.br/futebol/estadual2002/
- copa_do_brasil_netvasco: https://www.netvasco.com.br/futebol/copadobrasil2002/
- copa_dos_campeoes_netvasco: https://www.netvasco.com.br/futebol/copadoscampeoes2002/
- brasileiro_netvasco: https://www.netvasco.com.br/futebol/brasileiro2002/
- evaristo_saida_dgabc: https://www.dgabc.com.br/Noticia/132458/evaristo-de-macedo-nao-e-mais-o-tecnico-do-vasco

## Totais

| Métrica | Banco atual ano civil 2002 | Referência NetVasco 2002 | Status |
| --- | ---: | ---: | --- |
| jogos | 76 | 76 | OK |
| vitorias | 35 | 35 | OK |
| empates | 17 | 17 | OK |
| derrotas | 24 | 24 | OK |
| gols_pro | 137 | 137 | OK |
| gols_contra | 108 | 108 | OK |

## Cobertura De Campos Ricos No Banco

| Campo salvo | Preenchidos no banco auditado | Observação |
| --- | ---: | --- |
| estadio | 0/76 | fichas NetVasco detalhadas trazem estádio em parte relevante; ainda não aplicado no SQL global |
| horario | 0/76 | tabelas NetVasco por competição trazem horário para os 76 jogos |
| capitao | 0/76 | aparece em várias fichas detalhadas; pendente extração e SQL específico |
| publico_pagante | 0/76 | fichas detalhadas trazem público em parte dos jogos; pendente SQL específico |
| publico_presente | 0/76 | fichas detalhadas trazem público em parte dos jogos; pendente SQL específico |
| renda | 0/76 | fichas detalhadas trazem renda em parte dos jogos; várias como não divulgada |
| arbitragem | 0/76 | fichas detalhadas trazem árbitro e auxiliares em parte dos jogos; pendente SQL específico |
| escalacao | 0/76 | fichas detalhadas trazem escalações e substituições em parte dos jogos; pendente SQL específico |

## Totais Por Competição

| Competição | Banco atual ano civil 2002 | Referência NetVasco 2002 | Status |
| --- | --- | --- | --- |
| Torneio Rio-São Paulo | 15J 6V 6E 3D 32GP 23GC | 15J 6V 6E 3D 32GP 23GC | OK |
| Copa do Brasil | 8J 4V 2E 2D 14GP 12GC | 8J 4V 2E 2D 14GP 12GC | OK |
| Campeonato Carioca | 25J 15V 4E 6D 50GP 30GC | 25J 15V 4E 6D 50GP 30GC | OK |
| Copa dos Campeões | 3J 0V 2E 1D 4GP 5GC | 3J 0V 2E 1D 4GP 5GC | OK |
| Campeonato Brasileiro Serie A | 25J 10V 3E 12D 37GP 38GC | 25J 10V 3E 12D 37GP 38GC | OK |

## Fontes Complementares Mapeadas

| Jogo/Grupo | Campos aproveitáveis | Fonte | Status |
| --- | --- | --- | --- |
| Torneio Rio-Sao Paulo 2002 | tabela completa com data, horario, mando, placar, gols do Vasco e links de ficha/noticia | NetVasco Rio-Sao Paulo 2002 | usado para horario e validacao de nucleo |
| Campeonato Carioca 2002 | tabela completa com data, horario, mando, placar, gols do Vasco e links de ficha/noticia | NetVasco Estadual 2002 | usado para horario e validacao de nucleo |
| Copa do Brasil 2002 | tabela completa com data, horario, mando, placar, gols do Vasco e links de ficha/noticia | NetVasco Copa do Brasil 2002 | usado para horario e validacao de nucleo |
| Copa dos Campeoes 2002 | tabela completa com data, horario, mando, placar, gols do Vasco e links de ficha/noticia | NetVasco Copa dos Campeoes 2002 | usado para horario, validacao de nucleo e tecnico Evaristo nas fichas |
| Campeonato Brasileiro 2002 | tabela completa com data, horario, mando, placar, gols do Vasco e links de ficha/noticia | NetVasco Brasileiro 2002 | usado para horario, validacao de nucleo e tecnico Antonio Lopes nas fichas |
| 20/01/2002 Vasco x Ponte Preta | estadio, arbitragem, publico, renda, escalação, substituições, gols/minutos e cartoes | NetVasco noticia 4726 | fonte rica mapeada, pendente SQL especifico de campos detalhados |
| 10/08/2002 Vasco x Figueirense | estadio, arbitragem, publico, escalação, substituições, gols/minutos, cartoes e estatisticas | NetVasco noticia 7612 | fonte rica mapeada, pendente SQL especifico de campos detalhados |
| 17/11/2002 Corinthians x Vasco | estadio, arbitragem, publico, renda, escalação, substituições, gols/minutos, cartoes e gol anulado citado no texto | NetVasco noticia 8993 | fonte rica mapeada, pendente SQL especifico de campos detalhados |

## Enriquecimento Global Preparado

- Horários: referência externa mapeada para os 76 jogos a partir das páginas NetVasco por competição.
- Técnicos: `Evaristo de Macedo` até a Copa dos Campeões; `Antônio Lopes` em todo o Brasileiro 2002.
- Correção de núcleo preparada: 15 jogos com técnico divergente no banco auditado.
- Campos ricos de fichas detalhadas foram mapeados no CSV, mas estádio/arbitragem/escalação/público/renda ficam para SQLs específicos por jogo/bloco.

## Validação Em Cópia Temporária

- Cópia validada: `/tmp/stats_vasco_2002_audit.sqlite3`.
- SQLs aplicados na cópia: correção de núcleo e horários/técnicos.
- `load_matches('/tmp/stats_vasco_2002_audit.sqlite3')` carregou `1758` partidas sem erro.
- Recorte NetVasco 2002 após aplicação: `76J 35V 17E 24D 137GP 108GC`.
- Cobertura de horários no recorte validado: `76/76`.
- Divergências de núcleo após aplicação na cópia: nenhuma.

## Aplicação Em DEV

- Aplicado em DEV em 12/05/2026.
- Banco DEV: `/Users/rodrigo/Documents/pessoal/Sistemas/stats_vasco/stats_vasco.sqlite3`.
- Backup criado antes da aplicação: `/Users/rodrigo/Documents/pessoal/Sistemas/stats_vasco/stats_vasco.sqlite3.backup_before_temporada_2002_20260512_133043`.
- `load_matches('/Users/rodrigo/Documents/pessoal/Sistemas/stats_vasco/stats_vasco.sqlite3')` carregou `1754` partidas sem erro.
- Recorte NetVasco 2002 em DEV: `76J 35V 17E 24D 137GP 108GC`.
- Cobertura de horários em DEV: `76/76`.
- Divergências de núcleo em DEV após aplicação: nenhuma.

## Aplicação Em PRD

- Aplicado em PRD em 12/05/2026.
- Banco PRD: `/Users/rodrigo/Library/Application Support/StatsVasco/stats_vasco.sqlite3`.
- Backup criado antes da aplicação: `/Users/rodrigo/Library/Application Support/StatsVasco/stats_vasco.sqlite3.backup_before_temporada_2002_20260512_133043`.
- `load_matches('/Users/rodrigo/Library/Application Support/StatsVasco/stats_vasco.sqlite3')` carregou `1758` partidas sem erro.
- Recorte NetVasco 2002 em PRD: `76J 35V 17E 24D 137GP 108GC`.
- Cobertura de horários em PRD: `76/76`.
- Divergências de núcleo em PRD após aplicação: nenhuma.

## Confirmado Para Corrigir/Enriquecer

- `217022` 02/06/2002 | Campeonato Carioca | Bangu-RJ: banco `1x4` vs fonte `1x4`
  - Divergências: técnico banco=Antônio Lopes fonte=Evaristo de Macedo
  - Gols Vasco no banco: Souza:1
  - Gols Vasco na fonte: Souza
  - Técnico esperado: Evaristo de Macedo; técnico no banco: Antônio Lopes
  - Fonte: NetVasco Estadual 2002; ficha: https://www.netvasco.com.br/news/noticias04/6743.shtml
- `217023` 05/06/2002 | Campeonato Carioca | Americano-RJ: banco `3x4` vs fonte `3x4`
  - Divergências: técnico banco=Antônio Lopes fonte=Evaristo de Macedo
  - Gols Vasco no banco: Ramon:1; Souza:1; Cadu:1
  - Gols Vasco na fonte: Ramon, Souza, Cadu
  - Técnico esperado: Evaristo de Macedo; técnico no banco: Antônio Lopes
  - Fonte: NetVasco Estadual 2002; ficha: https://www.netvasco.com.br/news/noticias04/6781.shtml
- `217024` 08/06/2002 | Campeonato Carioca | Botafogo: banco `0x1` vs fonte `0x1`
  - Divergências: técnico banco=Antônio Lopes fonte=Evaristo de Macedo
  - Gols Vasco no banco: -
  - Gols Vasco na fonte: -
  - Técnico esperado: Evaristo de Macedo; técnico no banco: Antônio Lopes
  - Fonte: NetVasco Estadual 2002; ficha: https://www.netvasco.com.br/news/noticias04/6814.shtml
- `217025` 03/07/2002 | Copa dos Campeões | Atlético-MG: banco `3x3` vs fonte `3x3`
  - Divergências: técnico banco=Antônio Lopes fonte=Evaristo de Macedo
  - Gols Vasco no banco: Ramon:2; Souza:1
  - Gols Vasco na fonte: Ramon (2), Souza
  - Técnico esperado: Evaristo de Macedo; técnico no banco: Antônio Lopes
  - Fonte: NetVasco Copa dos Campeões 2002; ficha: https://www.netvasco.com.br/news/noticias05/7033.shtml
- `217026` 10/07/2002 | Copa dos Campeões | Palmeiras-SP: banco `1x1` vs fonte `1x1`
  - Divergências: técnico banco=Antônio Lopes fonte=Evaristo de Macedo
  - Gols Vasco no banco: Gol contra:1
  - Gols Vasco na fonte: Alexandre (contra)
  - Técnico esperado: Evaristo de Macedo; técnico no banco: Antônio Lopes
  - Fonte: NetVasco Copa dos Campeões 2002; ficha: https://www.netvasco.com.br/news/noticias05/7135.shtml
- `217027` 14/07/2002 | Copa dos Campeões | Bahia-BA: banco `0x1` vs fonte `0x1`
  - Divergências: técnico banco=Antônio Lopes fonte=Evaristo de Macedo
  - Gols Vasco no banco: -
  - Gols Vasco na fonte: -
  - Técnico esperado: Evaristo de Macedo; técnico no banco: Antônio Lopes
  - Fonte: NetVasco Copa dos Campeões 2002; ficha: https://www.netvasco.com.br/news/noticias05/7196.shtml
- `216983` 16/10/2002 | Campeonato Brasileiro Serie A | Flamengo-RJ: banco `2x1` vs fonte `2x1`
  - Divergências: técnico banco=Gaúcho fonte=Antônio Lopes
  - Gols Vasco no banco: Ramon:2
  - Gols Vasco na fonte: Ramon (2)
  - Técnico esperado: Antônio Lopes; técnico no banco: Gaúcho
  - Fonte: NetVasco Brasileiro 2002; ficha: https://www.netvasco.com.br/news/noticias06/8567.shtml
- `216984` 19/10/2002 | Campeonato Brasileiro Serie A | Paraná-PR: banco `1x0` vs fonte `1x0`
  - Divergências: técnico banco=Gaúcho fonte=Antônio Lopes
  - Gols Vasco no banco: Ramon:1
  - Gols Vasco na fonte: Ramon
  - Técnico esperado: Antônio Lopes; técnico no banco: Gaúcho
  - Fonte: NetVasco Brasileiro 2002; ficha: https://www.netvasco.com.br/news/noticias06/8613.shtml
- `216985` 23/10/2002 | Campeonato Brasileiro Serie A | Bahia-BA: banco `2x4` vs fonte `2x4`
  - Divergências: técnico banco=Gaúcho fonte=Antônio Lopes
  - Gols Vasco no banco: Ramon:2
  - Gols Vasco na fonte: Ramon (2)
  - Técnico esperado: Antônio Lopes; técnico no banco: Gaúcho
  - Fonte: NetVasco Brasileiro 2002; ficha: https://www.netvasco.com.br/news/noticias06/8676.shtml
- `216986` 31/10/2002 | Campeonato Brasileiro Serie A | Fluminense-RJ: banco `1x2` vs fonte `1x2`
  - Divergências: técnico banco=Gaúcho fonte=Antônio Lopes
  - Gols Vasco no banco: Valdir:1
  - Gols Vasco na fonte: Valdir
  - Técnico esperado: Antônio Lopes; técnico no banco: Gaúcho
  - Fonte: NetVasco Brasileiro 2002; ficha: https://www.netvasco.com.br/news/noticias06/8778.shtml
- `216987` 03/11/2002 | Campeonato Brasileiro Serie A | Palmeiras-SP: banco `1x0` vs fonte `1x0`
  - Divergências: técnico banco=Gaúcho fonte=Antônio Lopes
  - Gols Vasco no banco: Léo Lima:1
  - Gols Vasco na fonte: Léo Lima
  - Técnico esperado: Antônio Lopes; técnico no banco: Gaúcho
  - Fonte: NetVasco Brasileiro 2002; ficha: https://www.netvasco.com.br/news/noticias06/8813.shtml
- `216988` 06/11/2002 | Campeonato Brasileiro Serie A | São Paulo-SP: banco `3x5` vs fonte `3x5`
  - Divergências: técnico banco=Gaúcho fonte=Antônio Lopes
  - Gols Vasco no banco: Ramon:2; Zé Carlos:1
  - Gols Vasco na fonte: Ramon (2), Zé Carlos
  - Técnico esperado: Antônio Lopes; técnico no banco: Gaúcho
  - Fonte: NetVasco Brasileiro 2002; ficha: https://www.netvasco.com.br/news/noticias06/8862.shtml
- `216989` 09/11/2002 | Campeonato Brasileiro Serie A | Vitória-BA: banco `4x1` vs fonte `4x1`
  - Divergências: técnico banco=Gaúcho fonte=Antônio Lopes
  - Gols Vasco no banco: Russo:1; Ramon:1; Petkovic:1; Valdir:1
  - Gols Vasco na fonte: Russo, Ramon, Petkovic, Valdir
  - Técnico esperado: Antônio Lopes; técnico no banco: Gaúcho
  - Fonte: NetVasco Brasileiro 2002; ficha: https://www.netvasco.com.br/news/noticias06/8894.shtml
- `216990` 13/11/2002 | Campeonato Brasileiro Serie A | Ponte Preta-SP: banco `2x0` vs fonte `2x0`
  - Divergências: técnico banco=Gaúcho fonte=Antônio Lopes
  - Gols Vasco no banco: Valdir:1; Ramon:1
  - Gols Vasco na fonte: Valdir, Ramon
  - Técnico esperado: Antônio Lopes; técnico no banco: Gaúcho
  - Fonte: NetVasco Brasileiro 2002; ficha: https://www.netvasco.com.br/news/noticias06/8949.shtml
- `216991` 17/11/2002 | Campeonato Brasileiro Serie A | Corinthians: banco `1x1` vs fonte `1x1`
  - Divergências: técnico banco=Gaúcho fonte=Antônio Lopes
  - Gols Vasco no banco: Ramon:1
  - Gols Vasco na fonte: Ramon
  - Técnico esperado: Antônio Lopes; técnico no banco: Gaúcho
  - Fonte: NetVasco Brasileiro 2002; ficha: https://www.netvasco.com.br/news/noticias06/8993.shtml

## Precisa Revisão Manual

- Nenhum caso pendente.

## Sem Divergência De Núcleo

- 20/01/2002 | Torneio Rio-São Paulo | Ponte Preta-SP | banco `3x3` = fonte `3x3` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Geder:1; Ely Thadeu:1; Romário:1 | gols fonte: Geder, Ely Thadeu, Romário
- 26/01/2002 | Campeonato Carioca | Bangu-RJ | banco `3x0` = fonte `3x0` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Ely Thadeu:1; André Leone:1; Souza:1 | gols fonte: Ely Thadeu, André Leone, Souza
- 27/01/2002 | Torneio Rio-São Paulo | São Paulo-SP | banco `3x2` = fonte `3x2` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Romário:2; Euller:1 | gols fonte: Romário (2), Euller
- 30/01/2002 | Torneio Rio-São Paulo | América | banco `2x0` = fonte `2x0` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Leonardo:1; Souza:1 | gols fonte: Leonardo, Souza
- 02/02/2002 | Campeonato Carioca | Madureira-RJ | banco `2x1` = fonte `2x1` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Ely Thadeu:1; André Ladaga:1 | gols fonte: Ely Thadeu, André Ladaga
- 03/02/2002 | Torneio Rio-São Paulo | Palmeiras-SP | banco `2x2` = fonte `2x2` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Romário:2 | gols fonte: Romário (2)
- 06/02/2002 | Campeonato Carioca | Entrerriense-RJ | banco `3x0` = fonte `3x0` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Souza:1; Ely Thadeu:1; Alex Oliveira:1 | gols fonte: Souza, Ely Thadeu, Alex Oliveira
- 09/02/2002 | Torneio Rio-São Paulo | Jundiaí | banco `2x2` = fonte `2x2` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Léo Lima:1; Ely Thadeu:1 | gols fonte: Léo Lima, Ely Thadeu
- 13/02/2002 | Copa do Brasil | Sergipe | banco `1x1` = fonte `1x1` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Felipe:1 | gols fonte: Felipe
- 17/02/2002 | Torneio Rio-São Paulo | Americano-RJ | banco `3x0` = fonte `3x0` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Romário:2; André Silva:1 | gols fonte: Romário (2), André Silva
- 18/02/2002 | Campeonato Carioca | Botafogo | banco `1x0` = fonte `1x0` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Cadu:1 | gols fonte: Cadu
- 20/02/2002 | Copa do Brasil | Sergipe | banco `2x1` = fonte `2x1` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Euller:1; Felipe:1 | gols fonte: Euller, Felipe
- 21/02/2002 | Campeonato Carioca | Olaria-RJ | banco `3x0` = fonte `3x0` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Souza:2; Cadu:1 | gols fonte: Souza (2), Cadu
- 24/02/2002 | Torneio Rio-São Paulo | São Caetano-SP | banco `0x3` = fonte `0x3` | local `fora` | técnico `Evaristo de Macedo` | gols banco: - | gols fonte: -
- 25/02/2002 | Campeonato Carioca | América | banco `2x1` = fonte `2x1` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Cadu:1; Geovani:1 | gols fonte: Cadu, Geovani
- 27/02/2002 | Copa do Brasil | Santa Cruz-PE | banco `2x1` = fonte `2x1` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Romário:1; Leonardo:1 | gols fonte: Romário, Leonardo
- 28/02/2002 | Campeonato Carioca | Friburguense | banco `1x0` = fonte `1x0` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Souza:1 | gols fonte: Souza
- 02/03/2002 | Torneio Rio-São Paulo | Portuguesa | banco `4x1` = fonte `4x1` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Romário:2; Alex Oliveira:1; Euller:1 | gols fonte: Romário (2), Alex Oliveira, Euller
- 06/03/2002 | Copa do Brasil | Santa Cruz-PE | banco `3x3` = fonte `3x3` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Euller:1; Léo Lima:1; Romário:1 | gols fonte: Euller, Léo Lima, Romário
- 07/03/2002 | Campeonato Carioca | Fluminense-RJ | banco `2x2` = fonte `2x2` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Haroldo:1; Cadu:1 | gols fonte: Haroldo, Cadu
- 10/03/2002 | Torneio Rio-São Paulo | Flamengo-RJ | banco `3x1` = fonte `3x1` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Euller:1; André Leone:1; Souza:1 | gols fonte: Euller, André Leone, Souza
- 11/03/2002 | Campeonato Carioca | V. Redonda | banco `2x0` = fonte `2x0` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Cadu:1; Ely Thadeu:1 | gols fonte: Cadu, Ely Thadeu
- 17/03/2002 | Torneio Rio-São Paulo | Guarani-SP | banco `1x1` = fonte `1x1` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Felipe:1 | gols fonte: Felipe
- 21/03/2002 | Torneio Rio-São Paulo | Botafogo | banco `2x2` = fonte `2x2` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Léo Lima:1; Romário:1 | gols fonte: Léo Lima, Romário
- 24/03/2002 | Torneio Rio-São Paulo | Fluminense-RJ | banco `1x3` = fonte `1x3` | local `casa` | técnico `Evaristo de Macedo` | gols banco: João Carlos:1 | gols fonte: João Carlos
- 25/03/2002 | Campeonato Carioca | Flamengo-RJ | banco `1x0` = fonte `1x0` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Léo Macaé:1 | gols fonte: Léo Macaé
- 27/03/2002 | Copa do Brasil | CSA | banco `1x2` = fonte `1x2` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Felipe:1 | gols fonte: Felipe
- 30/03/2002 | Torneio Rio-São Paulo | Santos | banco `1x1` = fonte `1x1` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Romário:1 | gols fonte: Romário
- 03/04/2002 | Copa do Brasil | CSA | banco `4x0` = fonte `4x0` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Romário:2; Euller:1; Léo Lima:1 | gols fonte: Romário (2), Euller, Léo Lima
- 07/04/2002 | Torneio Rio-São Paulo | Bangu-RJ | banco `5x1` = fonte `5x1` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Romário:2; Leonardo:1; Léo Lima:1; Felipe:1 | gols fonte: Romário (2), Leonardo, Léo Lima, Felipe
- 10/04/2002 | Copa do Brasil | São Paulo-SP | banco `1x0` = fonte `1x0` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Romário:1 | gols fonte: Romário
- 14/04/2002 | Torneio Rio-São Paulo | Corinthians | banco `0x1` = fonte `0x1` | local `fora` | técnico `Evaristo de Macedo` | gols banco: - | gols fonte: -
- 17/04/2002 | Copa do Brasil | São Paulo-SP | banco `0x4` = fonte `0x4` | local `fora` | técnico `Evaristo de Macedo` | gols banco: - | gols fonte: -
- 21/04/2002 | Campeonato Carioca | Madureira-RJ | banco `3x1` = fonte `3x1` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Romário:2; Leonardo:1 | gols fonte: Romário (2), Leonardo
- 24/04/2002 | Campeonato Carioca | Entrerriense-RJ | banco `6x1` = fonte `6x1` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Romário:4; Edinho:1; Souza:1 | gols fonte: Romário (4), Edinho, Souza
- 28/04/2002 | Campeonato Carioca | Americano-RJ | banco `1x2` = fonte `1x2` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Romário:1 | gols fonte: Romário
- 01/05/2002 | Campeonato Carioca | Olaria-RJ | banco `1x1` = fonte `1x1` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Alex Oliveira:1 | gols fonte: Alex Oliveira
- 05/05/2002 | Campeonato Carioca | América | banco `2x1` = fonte `2x1` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Romário:1; Felipe:1 | gols fonte: Romário, Felipe
- 08/05/2002 | Campeonato Carioca | Friburguense | banco `2x3` = fonte `2x3` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Léo Macaé:1; Leonardo:1 | gols fonte: Léo Macaé, Leonardo
- 11/05/2002 | Campeonato Carioca | Americano-RJ | banco `2x1` = fonte `2x1` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Jailson:1; Leonardo:1 | gols fonte: Jailson, Leonardo
- 15/05/2002 | Campeonato Carioca | Fluminense-RJ | banco `1x0` = fonte `1x0` | local `casa` | técnico `Evaristo de Macedo` | gols banco: Souza:1 | gols fonte: Souza
- 19/05/2002 | Campeonato Carioca | V. Redonda | banco `3x4` = fonte `3x4` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Jorginho:1; Ramon:1; Euller:1 | gols fonte: Jorginho, Ramon, Euller
- 23/05/2002 | Campeonato Carioca | Bangu-RJ | banco `3x1` = fonte `3x1` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Ramon:2; Euller:1 | gols fonte: Ramon (2), Euller
- 26/05/2002 | Campeonato Carioca | Flamengo-RJ | banco `0x0` = fonte `0x0` | local `casa` | técnico `Evaristo de Macedo` | gols banco: - | gols fonte: -
- 29/05/2002 | Campeonato Carioca | Botafogo | banco `2x2` = fonte `2x2` | local `fora` | técnico `Evaristo de Macedo` | gols banco: Léo Lima:1; Haroldo:1 | gols fonte: Léo Lima, Haroldo
- 10/08/2002 | Campeonato Brasileiro Serie A | Figueirense-SC | banco `2x0` = fonte `2x0` | local `casa` | técnico `Antônio Lopes` | gols banco: Ramon:2 | gols fonte: Ramon (2)
- 14/08/2002 | Campeonato Brasileiro Serie A | Grêmio-RS | banco `2x3` = fonte `2x3` | local `fora` | técnico `Antônio Lopes` | gols banco: Ramon:2 | gols fonte: Ramon (2)
- 17/08/2002 | Campeonato Brasileiro Serie A | Atlético-PR | banco `1x2` = fonte `1x2` | local `fora` | técnico `Antônio Lopes` | gols banco: Siston:1 | gols fonte: Siston
- 22/08/2002 | Campeonato Brasileiro Serie A | Gama-DF | banco `0x1` = fonte `0x1` | local `casa` | técnico `Antônio Lopes` | gols banco: - | gols fonte: -
- 25/08/2002 | Campeonato Brasileiro Serie A | Goiás-GO | banco `4x2` = fonte `4x2` | local `fora` | técnico `Antônio Lopes` | gols banco: Souza:1; Rodrigo Souto:1; Washington:1; Cadu:1 | gols fonte: Souza, Rodrigo Souto, Washington, Cadu
- 01/09/2002 | Campeonato Brasileiro Serie A | Juventude-RS | banco `0x1` = fonte `0x1` | local `fora` | técnico `Antônio Lopes` | gols banco: - | gols fonte: -
- 04/09/2002 | Campeonato Brasileiro Serie A | Atlético-MG | banco `1x2` = fonte `1x2` | local `casa` | técnico `Antônio Lopes` | gols banco: Cadu:1 | gols fonte: Cadu
- 07/09/2002 | Campeonato Brasileiro Serie A | Coritiba-PR | banco `1x0` = fonte `1x0` | local `casa` | técnico `Antônio Lopes` | gols banco: Petkovic:1 | gols fonte: Petkovic
- 11/09/2002 | Campeonato Brasileiro Serie A | Paysandu-PA | banco `0x2` = fonte `0x2` | local `fora` | técnico `Antônio Lopes` | gols banco: - | gols fonte: -
- 15/09/2002 | Campeonato Brasileiro Serie A | Botafogo | banco `1x1` = fonte `1x1` | local `fora` | técnico `Antônio Lopes` | gols banco: Cadu:1 | gols fonte: Cadu
- 18/09/2002 | Campeonato Brasileiro Serie A | Santos | banco `1x2` = fonte `1x2` | local `casa` | técnico `Antônio Lopes` | gols banco: Souza:1 | gols fonte: Souza
- 22/09/2002 | Campeonato Brasileiro Serie A | Internacional-RS | banco `1x1` = fonte `1x1` | local `casa` | técnico `Antônio Lopes` | gols banco: Ely Thadeu:1 | gols fonte: Ely Thadeu
- 25/09/2002 | Campeonato Brasileiro Serie A | Cruzeiro-MG | banco `0x4` = fonte `0x4` | local `fora` | técnico `Antônio Lopes` | gols banco: - | gols fonte: -
- 29/09/2002 | Campeonato Brasileiro Serie A | Portuguesa | banco `4x0` = fonte `4x0` | local `casa` | técnico `Antônio Lopes` | gols banco: Valdir:2; Geder:1; Léo Lima:1 | gols fonte: Valdir (2), Geder, Léo Lima
- 05/10/2002 | Campeonato Brasileiro Serie A | Guarani-SP | banco `2x1` = fonte `2x1` | local `fora` | técnico `Antônio Lopes` | gols banco: Rodrigo Souto:1; Ramon:1 | gols fonte: Rodrigo Souto, Ramon
- 12/10/2002 | Campeonato Brasileiro Serie A | São Caetano-SP | banco `0x2` = fonte `0x2` | local `fora` | técnico `Antônio Lopes` | gols banco: - | gols fonte: -
