# Vasco 2 x 1 Palmeiras - 08/11/2026

Importado em 09/11/2026 apos pull, backup e reconciliacao de agenda e elenco
Railway -> PRD local. Resultado do jogo: vitoria 2-1. Agregado: 2-2.
Disputa de penaltis: Vasco 4-5 Palmeiras, que se classificou.

## Fontes

- https://www.netvasco.com.br/n/396001/vasco-perde-para-o-palmeiras-nos-penaltis-e-deixa-a-copa-do-brasil
- https://www.netvasco.com.br/n/395998/sao-januario-recebeu-21275-torcedores-para-vasco-x-palmeiras
- https://www.sofascore.com/pt/football/match/vasco-da-gama-palmeiras/nOszO#id:17166359
- iG/Jogada10, "Palmeiras elimina o Vasco nos penaltis e volta a final da Copa
  do BR": renda R$ 2.474.907,00; pagantes 20.416. Estadão e outras materias
  indicam 20.418 pagantes. Diante da divergencia, pagantes ficou nulo.

## Dados e verificacao

Scouts obtidos em lineups, statistics e incidents do SofaScore. Importados
11 titulares, 12 reservas, quatro substituicoes e scouts dos 15 que atuaram.
Totais individuais conferem: 11 finalizacoes e tres no gol, sem incluir a
disputa de penaltis. Campos ausentes nao receberam zeros artificiais; zero
no gol para atleta com zero chutes decorre do total confirmado.
xG/xGOT nao foram fornecidos pelo endpoint desta partida e ficaram ausentes.

Gols: Colidio aos 16 (Cuiabano), Piquerez aos 55 (Lucas Evangelista), Puma aos
76 (Alan Lescano). Minutos estruturados seguem SofaScore. Cartoes incluem
Gomez, ausente da ficha resumida NetVasco, e Daniel Fuzato no banco antes
do jogo. Fuzato nao recebeu scout de atuacao. Saldivia estava suspenso.

Doze cobrancas salvas separadamente em disputa_penaltis. Palmeiras: Vitor
Roque, Gustavo Gomez, Ramon Sosa, Andreas Pereira e Marlon Freitas marcaram;
Giay teve a cobranca defendida. Vasco: Thiago Mendes, Santiago Sosa, Colidio
e Puma marcaram; Lescano e Andres Gomez tiveram as cobrancas defendidas.
Placar normal, agregado e penaltis foram preservados em campos separados.

SQLite integrity_check OK. Comparados todos os jogos remotos anteriores com
normalizacao de IDs e campos equivalentes. Elenco, historico e titles remoto
preservados. Publicacao: 1793 jogos, cinco futuros, 55 atletas e 151 historicos.
Runtime Vercel HTTP 200 validou placar, fase, 15 scouts, quatro substituicoes
e 21.275 presentes. O exportador atual nao expoe agregado/penaltis em campos
proprios do detalhe; eles estao no SQLite e Railway e a eliminacao consta na
sintese do jogo. Nao foi feito deploy de codigo da API nesta execucao.
