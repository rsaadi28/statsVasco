# Vasco 1 x 3 Boca Juniors - 20/10/2026

Importado em 21/10/2026 apos pull e reconciliacao do elenco Railway -> PRD local.
Backup anterior a importacao preservado. Todos os campos dos jogos remotos
anteriores foram comparados antes da publicacao, exceto IDs internos SQLite.

## Fontes

- https://www.netvasco.com.br/n/394869/vasco-perde-para-o-boca-juniors-no-maracana-e-deixa-a-sul-americana-3-a-1
- https://www.netvasco.com.br/n/394798/confira-desfalques-e-pendurados-de-vasco-e-boca-juniors
- https://www.sofascore.com/pt/football/match/boca-juniors-vasco-da-gama/zOscob#id:17108465
- SuperVasco, "Publico e renda de Vasco x Boca Juniors": 66.026 presentes,
  61.885 pagantes e R$ 6.962.208,50, citando X Fim de Jogo.

Scouts coletivos e individuais obtidos nos endpoints event/17108465/lineups,
statistics e incidents. Foram preservados apenas campos fornecidos pela fonte.
Zero finalizacoes no gol para quem teve zero finalizacoes decorre do total.
Nao foram atribuidos scouts aos oito reservas que nao atuaram.
Desarmes individuais ausentes nao foram preenchidos artificialmente com zero.

Escalacao confirmada: 11 titulares, 12 reservas e quatro substituicoes.
Spinelli constava como lesionado na previa, mas atuou; prevaleceu a escalação
confirmada. Colidio nao estava inscrito e Gomez estava suspenso.
Mateus Carvalho estava em transicao fisica; Cauan Barros estava lesionado.
As duas trocas do intervalo foram registradas como INT, minuto zero.
O SofaScore registra a troca final aos 90 e 1 minuto de Spinelli; os scouts
individuais foram mantidos exatamente como fornecidos.

Gols: Di Lollo aos 4 (assistencia Blanco), Merentiel aos 34 (Villa),
Puma Rodriguez aos 66 (sem assistencia confirmada), Paredes aos 88 (Delgado).
Thiago Mendes recebeu amarelo aos 40. Nao houve vermelho do Vasco.
O jogo terminou 1-3, agregado 2-3, semifinal de volta da Sul-Americana.

Validacoes: SQLite integrity_check OK, 15 atletas com scouts, 12 finalizacoes,
duas no gol. Estado publicado: 1788 partidas, nove futuras, 55 atletas atuais,
151 historicos. A partida realizada foi removida da agenda futura.
Runtime publico Vercel respondeu HTTP 200 e confirmou placar, 15 scouts,
quatro substituicoes e bilheteria. Nenhum deploy de frontend foi necessario.
