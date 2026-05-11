# Auditoria Dos Jogos Do Vasco - Temporada 2000

- Banco auditado: `/Users/rodrigo/Library/Application Support/StatsVasco/stats_vasco.sqlite3`
- Modo de leitura: SQLite `mode=ro`
- Recorte: temporada NetVasco 2000, incluindo `18/01/2001` como jogo válido por 2000

## Fontes
- indice_netvasco: https://www.netvasco.com.br/futebol/index2000.shtml
- estatisticas_netvasco: https://www.netvasco.com.br/futebol/estatisticas2000
- brasileiro_mauro_prais: https://www.netvasco.com.br/mauroprais/vasco/2000br.html
- confirmacao_2000_03_01: https://www.netvasco.com.br/n/379745/confira-os-jogos-do-vasco-na-historia-em-1-de-marco
- palmeiras_oficial_2000_03_01: https://www.palmeiras.com.br/lightbox_galeria/torneio-rio-sao-paulo-2000/
- verdazzo_2000_03_01: https://www.verdazzo.com.br/jogo/20000301-palmeiras-x-vasco-da-gama-torneio-rio-sao-paulo-2000/
- vaskipedia_tecnico_alcir: https://vaskipedia.com/treinador/alcir-portella/
- folha_londrina_lopes_reassume: https://www.folhadelondrina.com.br/esporte/lopes-reassume-o-comando-do-vasco-na-2-feira-258317.html
- vaskipedia_2000_06_11: https://vaskipedia.com/jogo/campeonato-estadual/vascoxflamengo/4827/
- supervasco_tita_2000: https://www.supervasco.com/noticias/vice-em-2000-tita-traz-pessimas-recordacoes-como-treinador-do-vasco-31439.html
- soccerzz_mundial_final: https://www.soccerzz.com/match/2000-01-14-corinthians-vasco/348077
- zerozero_mercosul_final: https://www.zerozero.pt/jogo/2000-12-20-palmeiras-vasco/1111830

## Totais

| Métrica | Banco atual | Referência externa | Status |
| --- | ---: | ---: | --- |
| jogos | 89 | 89 | OK |
| vitorias | 51 | 51 | OK |
| empates | 19 | 19 | OK |
| derrotas | 19 | 19 | OK |
| gols_pro | 176 | 176 | OK |
| gols_contra | 103 | 103 | OK |

## Cobertura De Campos Ricos No Banco

| Campo salvo | Preenchidos em PRD | Observação |
| --- | ---: | --- |
| estadio | 1/89 | buscar em fichas de jogo e páginas oficiais |
| horario | 89/89 | NetVasco cobre quase toda a tabela, conferir divergências com outras fontes |
| capitao | 0/89 | normalmente só em súmula/ficha detalhada |
| publico_pagante | 0/89 | buscar em borderôs/súmulas, oGol/Zerozero e imprensa |
| publico_presente | 0/89 | buscar em borderôs/súmulas, oGol/Zerozero e imprensa |
| renda | 0/89 | buscar em borderôs/súmulas, oGol/Zerozero e imprensa |
| arbitragem | 1/89 | fichas detalhadas, Soccerzz/Zerozero/Playmaker e fontes oficiais |
| escalacao | 1/89 | fichas detalhadas, Soccerzz/Zerozero/Playmaker, Football-Lineups e imprensa |

## Totais Por Competição

| Competição | Banco atual | Referência externa | Status |
| --- | --- | --- | --- |
| Amistoso | 3J 3V 0E 0D 12GP 0GC | 3J 3V 0E 0D 12GP 0GC | OK |
| Campeonato Brasileiro Serie A | 32J 15V 9E 8D 54GP 49GC | 32J 15V 9E 8D 54GP 49GC | OK |
| Campeonato Carioca | 22J 15V 3E 4D 57GP 20GC | 22J 15V 3E 4D 57GP 20GC | OK |
| Copa do Brasil | 5J 2V 3E 0D 8GP 5GC | 5J 2V 3E 0D 8GP 5GC | OK |
| Copa Mercosul | 13J 8V 1E 4D 23GP 13GC | 13J 8V 1E 4D 23GP 13GC | OK |
| Mundial de Clubes | 4J 3V 1E 0D 7GP 2GC | 4J 3V 1E 0D 7GP 2GC | OK |
| Torneio Rio-São Paulo | 10J 5V 2E 3D 15GP 14GC | 10J 5V 2E 3D 15GP 14GC | OK |

## Fontes Complementares Mapeadas

| Jogo/Grupo | Campos aproveitáveis | Fonte | Status |
| --- | --- | --- | --- |
| 01/03/2000 Palmeiras-SP x Vasco | estadio, arbitragem, cartões do Vasco, escalação, técnico, gols adversários | Palmeiras oficial + Verdazzo | confirmado para SQL de enriquecimento |
| 14/01/2000 Corinthians x Vasco | estadio, horario, arbitragem, publico, escalação, reservas, técnico | Soccerzz/Football-Lineups/Wikipedia | candidato para próxima leva |
| 20/12/2000 Palmeiras-SP x Vasco | estadio, arbitragem, cartões, escalação, técnico, gols e minutos | NetVasco especial + Zerozero/Playmaker/Verdazzo | candidato para próxima leva |
| Jogos de Brasileiro/Mercosul/Rio-SP | estadio, tecnico, escalação, gols, cartões quando disponível | oGol/Zerozero/PlaymakerStats/Soccerzz + páginas oficiais dos adversários | fonte complementar por jogo |

## Enriquecimento Global Preparado

- Horários: referência externa mapeada para os 89 jogos a partir das páginas de competição do NetVasco.
- Técnicos: regra temporal mapeada para os 89 jogos usando Vaskipédia, Folha de Londrina, SuperVasco, NetVasco/Mauro Prais e fontes das finais.
- Campos ricos restantes: `estadio`, `arbitragem`, `escalacao`, `cartoes`, `publico`, `renda` ficam marcados por jogo no CSV, com fonte candidata e status.
- Arquivos gerados para aplicação/repetição: `docs/auditoria_temporada_2000_mapa.csv` e `docs/sql_enriquecer_temporada_2000_horarios_tecnicos.sql`.

## Confirmado Para Corrigir

- Nenhuma divergência confirmada.

## Precisa Revisão Manual

- Nenhum caso pendente.

## Sem Divergência

- 03/01/2000 | Amistoso | Sel. Argélia | banco `7x0` = fonte `7x0` | local `casa` | técnico `Antônio Lopes` | gols banco: Donizete:2; Juninho:1; Romário:1; Felipe:1; Dedé:1; Viola:1 | gols fonte: Donizete (2), Juninho, Romário, Felipe, Dedé, Viola
- 06/01/2000 | Mundial de Clubes | South Melbourne | banco `2x0` = fonte `2x0` | local `casa` | técnico `Antônio Lopes` | gols banco: Felipe:1; Edmundo:1 | gols fonte: Felipe, Edmundo
- 08/01/2000 | Mundial de Clubes | Manchester United | banco `3x1` = fonte `3x1` | local `fora` | técnico `Antônio Lopes` | gols banco: Romário:2; Edmundo:1 | gols fonte: Romário (2), Edmundo
- 11/01/2000 | Mundial de Clubes | Necaxa | banco `2x1` = fonte `2x1` | local `casa` | técnico `Antônio Lopes` | gols banco: Odvan:1; Romário:1 | gols fonte: Odvan, Romário
- 14/01/2000 | Mundial de Clubes | Corinthians | banco `0x0` = fonte `0x0` | local `fora` | técnico `Antônio Lopes` | gols banco: - | gols fonte: -
- 23/01/2000 | Torneio Rio-São Paulo | Palmeiras-SP | banco `3x3` = fonte `3x3` | local `casa` | técnico `Alcir Portela` | gols banco: Romário:2; Viola:1 | gols fonte: Romário (2), Viola
- 27/01/2000 | Torneio Rio-São Paulo | Fluminense-RJ | banco `2x1` = fonte `2x1` | local `fora` | técnico `Alcir Portela` | gols banco: Romário:2 | gols fonte: Romário (2)
- 30/01/2000 | Torneio Rio-São Paulo | Corinthians | banco `1x0` = fonte `1x0` | local `casa` | técnico `Alcir Portela` | gols banco: Romário:1 | gols fonte: Romário
- 05/02/2000 | Torneio Rio-São Paulo | Palmeiras-SP | banco `1x2` = fonte `1x2` | local `fora` | técnico `Alcir Portela` | gols banco: Romário:1 | gols fonte: Romário
- 09/02/2000 | Torneio Rio-São Paulo | Fluminense-RJ | banco `1x0` = fonte `1x0` | local `casa` | técnico `Alcir Portela` | gols banco: Romário:1 | gols fonte: Romário
- 13/02/2000 | Torneio Rio-São Paulo | Corinthians | banco `1x1` = fonte `1x1` | local `fora` | técnico `Alcir Portela` | gols banco: Romário:1 | gols fonte: Romário
- 19/02/2000 | Torneio Rio-São Paulo | São Paulo-SP | banco `3x0` = fonte `3x0` | local `fora` | técnico `Antônio Lopes` | gols banco: Gilberto:1; Dedé:1; Romário:1 | gols fonte: Gilberto, Dedé, Romário
- 23/02/2000 | Torneio Rio-São Paulo | São Paulo-SP | banco `2x1` = fonte `2x1` | local `casa` | técnico `Antônio Lopes` | gols banco: Romário:2 | gols fonte: Romário (2)
- 26/02/2000 | Torneio Rio-São Paulo | Palmeiras-SP | banco `1x2` = fonte `1x2` | local `casa` | técnico `Antônio Lopes` | gols banco: Romário:1 | gols fonte: Romário
- 01/03/2000 | Torneio Rio-São Paulo | Palmeiras-SP | banco `0x4` = fonte `0x4` | local `fora` | técnico `Antônio Lopes` | gols banco: - | gols fonte: -
- 12/03/2000 | Campeonato Carioca | Madureira-RJ | banco `2x0` = fonte `2x0` | local `casa` | técnico `Abel Braga` | gols banco: Edmundo:2 | gols fonte: Edmundo (2)
- 15/03/2000 | Copa do Brasil | Botafogo-PB | banco `3x1` = fonte `3x1` | local `fora` | técnico `Abel Braga` | gols banco: Edmundo:1; Dedé:1; P. Miranda:1 | gols fonte: Edmundo, Dedé, P. Miranda
- 18/03/2000 | Campeonato Carioca | Bangu-RJ | banco `3x0` = fonte `3x0` | local `casa` | técnico `Abel Braga` | gols banco: Edmundo:1; A. Oliveira:1; Pedrinho:1 | gols fonte: Edmundo, A. Oliveira, Pedrinho
- 22/03/2000 | Campeonato Carioca | Friburguense | banco `1x0` = fonte `1x0` | local `fora` | técnico `Abel Braga` | gols banco: Edmundo:1 | gols fonte: Edmundo
- 25/03/2000 | Campeonato Carioca | Americano-RJ | banco `6x0` = fonte `6x0` | local `casa` | técnico `Abel Braga` | gols banco: Romário:4; Edmundo:1; P. Miranda:1 | gols fonte: Romário (4), Edmundo, P. Miranda
- 29/03/2000 | Campeonato Carioca | Olaria-RJ | banco `4x1` = fonte `4x1` | local `fora` | técnico `Abel Braga` | gols banco: Romário:3; Edmundo:1 | gols fonte: Romário (3), Edmundo
- 02/04/2000 | Campeonato Carioca | Fluminense-RJ | banco `3x2` = fonte `3x2` | local `fora` | técnico `Abel Braga` | gols banco: Gol contra:1; Romário:1; Edmundo:1 | gols fonte: Luciano (contra), Romário, Edmundo
- 09/04/2000 | Campeonato Carioca | Botafogo | banco `0x0` = fonte `0x0` | local `casa` | técnico `Abel Braga` | gols banco: - | gols fonte: -
- 12/04/2000 | Campeonato Carioca | V. Redonda | banco `3x0` = fonte `3x0` | local `fora` | técnico `Abel Braga` | gols banco: J. Baiano:1; P. Miranda:1; Odvan:1 | gols fonte: J. Baiano, P. Miranda, Odvan
- 15/04/2000 | Campeonato Carioca | América | banco `3x1` = fonte `3x1` | local `fora` | técnico `Abel Braga` | gols banco: Romário:2; Pedrinho:1 | gols fonte: Romário (2), Pedrinho
- 19/04/2000 | Campeonato Carioca | Cabo Frio | banco `5x0` = fonte `5x0` | local `casa` | técnico `Abel Braga` | gols banco: Romário:2; Odvan:1; Viola:1; P. Miranda:1 | gols fonte: Romário (2), Odvan, Viola, P. Miranda
- 23/04/2000 | Campeonato Carioca | Flamengo-RJ | banco `5x1` = fonte `5x1` | local `fora` | técnico `Abel Braga` | gols banco: Romário:3; Felipe:1; Pedrinho:1 | gols fonte: Romário (3), Felipe, Pedrinho
- 27/04/2000 | Copa do Brasil | Ponte Preta-SP | banco `1x1` = fonte `1x1` | local `casa` | técnico `Abel Braga` | gols banco: Romário:1 | gols fonte: Romário
- 30/04/2000 | Campeonato Carioca | Madureira-RJ | banco `3x1` = fonte `3x1` | local `fora` | técnico `Abel Braga` | gols banco: Pedrinho:2; Viola:1 | gols fonte: Pedrinho (2), Viola
- 03/05/2000 | Copa do Brasil | Ponte Preta-SP | banco `1x0` = fonte `1x0` | local `fora` | técnico `Abel Braga` | gols banco: Gilberto:1 | gols fonte: Gilberto
- 06/05/2000 | Campeonato Carioca | América | banco `1x2` = fonte `1x2` | local `casa` | técnico `Abel Braga` | gols banco: Viola:1 | gols fonte: Viola
- 10/05/2000 | Campeonato Carioca | Americano-RJ | banco `2x0` = fonte `2x0` | local `fora` | técnico `Abel Braga` | gols banco: Romário:1; Pedrinho:1 | gols fonte: Romário, Pedrinho
- 13/05/2000 | Campeonato Carioca | Olaria-RJ | banco `6x1` = fonte `6x1` | local `casa` | técnico `Abel Braga` | gols banco: Romário:2; Gilberto:1; Viola:1; Amaral:1; Gol contra:1 | gols fonte: Romário (2), Gilberto, Viola, Amaral, L. Cláudio (contra)
- 17/05/2000 | Campeonato Carioca | Bangu-RJ | banco `4x1` = fonte `4x1` | local `fora` | técnico `Abel Braga` | gols banco: Viola:2; Romário:1; Dedé:1 | gols fonte: Viola (2), Romário, Dedé
- 21/05/2000 | Campeonato Carioca | Fluminense-RJ | banco `0x1` = fonte `0x1` | local `casa` | técnico `Abel Braga` | gols banco: - | gols fonte: -
- 24/05/2000 | Copa do Brasil | Fluminense-RJ | banco `1x1` = fonte `1x1` | local `fora` | técnico `Abel Braga` | gols banco: Pedrinho:1 | gols fonte: Pedrinho
- 28/05/2000 | Campeonato Carioca | Flamengo-RJ | banco `3x3` = fonte `3x3` | local `casa` | técnico `Abel Braga` | gols banco: Edmundo:1; Juninho:1; Viola:1 | gols fonte: Edmundo, Juninho, Viola
- 31/05/2000 | Copa do Brasil | Fluminense-RJ | banco `2x2` = fonte `2x2` | local `casa` | técnico `Abel Braga` | gols banco: Edmundo:2 | gols fonte: Edmundo (2)
- 04/06/2000 | Campeonato Carioca | Friburguense | banco `1x0` = fonte `1x0` | local `casa` | técnico `Alcir Portela` | gols banco: Juninho:1 | gols fonte: Juninho
- 07/06/2000 | Campeonato Carioca | Botafogo | banco `1x1` = fonte `1x1` | local `fora` | técnico `Alcir Portela` | gols banco: Edmundo:1 | gols fonte: Edmundo
- 11/06/2000 | Campeonato Carioca | Flamengo-RJ | banco `0x3` = fonte `0x3` | local `fora` | técnico `Alcir Portela` | gols banco: - | gols fonte: -
- 17/06/2000 | Campeonato Carioca | Flamengo-RJ | banco `1x2` = fonte `1x2` | local `casa` | técnico `Tita` | gols banco: Viola:1 | gols fonte: Viola
- 30/06/2000 | Amistoso | Rio Branco | banco `2x0` = fonte `2x0` | local `fora` | técnico `Tita` | gols banco: Odvan:1; Gol contra:1 | gols fonte: Odvan
- 22/07/2000 | Amistoso | São Cristóvão | banco `3x0` = fonte `3x0` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: Luiz Cláudio:1; Felipe:1; Zada:1 | gols fonte: Luiz Cláudio, Felipe, Zada
- 29/07/2000 | Campeonato Brasileiro Serie A | Sport-PE | banco `0x2` = fonte `0x2` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: - | gols fonte: -
- 01/08/2000 | Copa Mercosul | Peñarol | banco `3x4` = fonte `3x4` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: Viola:2; Romário:1 | gols fonte: Viola (2), Romário
- 06/08/2000 | Campeonato Brasileiro Serie A | Cruzeiro-MG | banco `3x3` = fonte `3x3` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Viola:2; Romário:1 | gols fonte: Viola (2), Romário
- 11/08/2000 | Campeonato Brasileiro Serie A | Corinthians | banco `1x0` = fonte `1x0` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Romário:1 | gols fonte: Romário
- 13/08/2000 | Campeonato Brasileiro Serie A | Guarani-SP | banco `1x0` = fonte `1x0` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: Viola:1 | gols fonte: Viola
- 16/08/2000 | Campeonato Brasileiro Serie A | Santa Cruz-PE | banco `1x1` = fonte `1x1` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: Romário:1 | gols fonte: Romário
- 20/08/2000 | Campeonato Brasileiro Serie A | Ponte Preta-SP | banco `2x1` = fonte `2x1` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Romário:2 | gols fonte: Romário (2)
- 24/08/2000 | Copa Mercosul | San Lorenzo | banco `3x0` = fonte `3x0` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Romário:2; Fabiano Eller:1 | gols fonte: Romário (2), Fabiano Eller
- 27/08/2000 | Campeonato Brasileiro Serie A | Portuguesa | banco `2x2` = fonte `2x2` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: Luiz Cláudio:2 | gols fonte: Luiz Cláudio (2)
- 31/08/2000 | Copa Mercosul | Atlético-MG | banco `0x2` = fonte `0x2` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: - | gols fonte: -
- 05/09/2000 | Campeonato Brasileiro Serie A | Atlético-PR | banco `2x2` = fonte `2x2` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Viola:1; Romário:1 | gols fonte: Viola, Romário
- 07/09/2000 | Copa Mercosul | Peñarol | banco `1x1` = fonte `1x1` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Romário:1 | gols fonte: Romário
- 10/09/2000 | Campeonato Brasileiro Serie A | Bahia-BA | banco `1x3` = fonte `1x3` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: Felipe:1 | gols fonte: Felipe
- 13/09/2000 | Campeonato Brasileiro Serie A | Fluminense-RJ | banco `4x3` = fonte `4x3` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Romário:2; Juninho:1; Juninho Paulista:1 | gols fonte: Romário (2), Juninho, Juninho Paulista
- 20/09/2000 | Campeonato Brasileiro Serie A | América-MG | banco `4x0` = fonte `4x0` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Romário:2; Juninho:1; Euller:1 | gols fonte: Romário (2), Juninho, Euller
- 24/09/2000 | Campeonato Brasileiro Serie A | Juventude-RS | banco `2x1` = fonte `2x1` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: Romário:2 | gols fonte: Romário (2)
- 28/09/2000 | Copa Mercosul | San Lorenzo | banco `2x0` = fonte `2x0` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: Juninho:1; Romário:1 | gols fonte: Juninho, Romário
- 04/10/2000 | Campeonato Brasileiro Serie A | Atlético-MG | banco `4x0` = fonte `4x0` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Juninho:2; Nasa:1; Pedrinho:1 | gols fonte: Juninho (2), Nasa, Pedrinho
- 11/10/2000 | Campeonato Brasileiro Serie A | Vitória-BA | banco `2x2` = fonte `2x2` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Romário:1; Juninho Paulista:1 | gols fonte: Romário, Juninho Paulista
- 14/10/2000 | Campeonato Brasileiro Serie A | Santos | banco `1x1` = fonte `1x1` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: Juninho Paulista:1 | gols fonte: Juninho Paulista
- 17/10/2000 | Copa Mercosul | Atlético-MG | banco `2x0` = fonte `2x0` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Romário:1; Juninho Paulista:1 | gols fonte: Romário, Juninho Paulista
- 21/10/2000 | Campeonato Brasileiro Serie A | Gama-DF | banco `1x0` = fonte `1x0` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Romário:1 | gols fonte: Romário
- 24/10/2000 | Campeonato Brasileiro Serie A | Goiás-GO | banco `2x1` = fonte `2x1` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Juninho:1; Juninho Paulista:1 | gols fonte: Juninho, Juninho Paulista
- 27/10/2000 | Campeonato Brasileiro Serie A | Flamengo-RJ | banco `0x4` = fonte `0x4` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: - | gols fonte: -
- 31/10/2000 | Copa Mercosul | R. Central | banco `1x0` = fonte `1x0` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Juninho Paulista:1 | gols fonte: Juninho Paulista
- 03/11/2000 | Campeonato Brasileiro Serie A | Coritiba-PR | banco `1x0` = fonte `1x0` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: Júnior Baiano:1 | gols fonte: Júnior Baiano
- 05/11/2000 | Campeonato Brasileiro Serie A | Internacional-RS | banco `0x2` = fonte `0x2` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: - | gols fonte: -
- 08/11/2000 | Copa Mercosul | R. Central | banco `0x1` = fonte `0x1` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: - | gols fonte: -
- 10/11/2000 | Campeonato Brasileiro Serie A | Palmeiras-SP | banco `0x3` = fonte `0x3` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: - | gols fonte: -
- 12/11/2000 | Campeonato Brasileiro Serie A | Botafogo | banco `1x2` = fonte `1x2` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Pedrinho:1 | gols fonte: Pedrinho
- 16/11/2000 | Campeonato Brasileiro Serie A | Grêmio-RS | banco `1x0` = fonte `1x0` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: Jorginho:1 | gols fonte: Jorginho
- 19/11/2000 | Campeonato Brasileiro Serie A | São Paulo-SP | banco `0x4` = fonte `0x4` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: - | gols fonte: -
- 22/11/2000 | Copa Mercosul | River Plate | banco `4x1` = fonte `4x1` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: Romário:1; Júnior Baiano:1; Juninho Paulista:1; Pedrinho:1 | gols fonte: Romário, Júnior Baiano, Juninho Paulista, Pedrinho
- 25/11/2000 | Campeonato Brasileiro Serie A | Bahia-BA | banco `3x3` = fonte `3x3` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: Clébson:1; Romário:1; Juninho:1 | gols fonte: Clébson, Romário, Juninho
- 28/11/2000 | Campeonato Brasileiro Serie A | Bahia-BA | banco `3x2` = fonte `3x2` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Euller:2; Juninho Paulista:1 | gols fonte: Euller (2), Juninho Paulista
- 30/11/2000 | Copa Mercosul | River Plate | banco `1x0` = fonte `1x0` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Juninho Paulista:1 | gols fonte: Juninho Paulista
- 03/12/2000 | Campeonato Brasileiro Serie A | Paraná-PR | banco `3x1` = fonte `3x1` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Romário:2; Juninho Paulista:1 | gols fonte: Romário (2), Juninho Paulista
- 06/12/2000 | Copa Mercosul | Palmeiras-SP | banco `2x0` = fonte `2x0` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Juninho:1; Romário:1 | gols fonte: Juninho, Romário
- 09/12/2000 | Campeonato Brasileiro Serie A | Paraná-PR | banco `0x1` = fonte `0x1` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: - | gols fonte: -
- 12/12/2000 | Copa Mercosul | Palmeiras-SP | banco `0x1` = fonte `0x1` | local `fora` | técnico `Oswaldo de Oliveira` | gols banco: - | gols fonte: -
- 16/12/2000 | Campeonato Brasileiro Serie A | Cruzeiro-MG | banco `2x2` = fonte `2x2` | local `casa` | técnico `Oswaldo de Oliveira` | gols banco: Euller:2 | gols fonte: Euller (2)
- 20/12/2000 | Copa Mercosul | Palmeiras-SP | banco `4x3` = fonte `4x3` | local `fora` | técnico `Joel Santana` | gols banco: Romário:3; Juninho Paulista:1 | gols fonte: Romário (3), Juninho Paulista
- 23/12/2000 | Campeonato Brasileiro Serie A | Cruzeiro-MG | banco `3x1` = fonte `3x1` | local `fora` | técnico `Joel Santana` | gols banco: Juninho:1; Euller:1; Romário:1 | gols fonte: Juninho, Euller, Romário
- 27/12/2000 | Campeonato Brasileiro Serie A | São Caetano-SP | banco `1x1` = fonte `1x1` | local `fora` | técnico `Joel Santana` | gols banco: Romário:1 | gols fonte: Romário
- 18/01/2001 | Campeonato Brasileiro Serie A | São Caetano-SP | banco `3x1` = fonte `3x1` | local `casa` | técnico `Joel Santana` | gols banco: Juninho:1; Jorginho Paulista:1; Romário:1 | gols fonte: Juninho, Jorginho Paulista, Romário
