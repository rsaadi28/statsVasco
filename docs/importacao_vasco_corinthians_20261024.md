# Vasco 3 x 2 Corinthians - 24/10/2026

Importacao em 26/10/2026 apos pull, backup e reconciliacao do elenco Railway.
Comparados todos os campos dos jogos remotos anteriores, exceto IDs internos
SQLite. Historico e elenco remotos preservados antes da publicacao.

## Fontes

- https://www.netvasco.com.br/n/395087/marino-marca-2-e-vasco-vence-o-corinthians-de-revirada-em-sao-januario-3-a-2
- https://www.sofascore.com/pt/football/match/vasco-da-gama-corinthians/hOszO#id:15238200
- NetVasco, "Sao Januario recebeu 19.048 torcedores para Vasco x Corinthians",
  24/10/2026, citando Fim de Jogo: 18.335 pagantes e R$ 1.042.402,50.
- O Globo e informativo de ingressos NetVasco confirmam Vasco x Flamengo em
  29/10, 20h, no Nilton Santos. Agenda atualizada com esse estadio.

## Coleta e validacao

Scouts extraidos dos endpoints lineups, statistics e incidents do SofaScore.
Foram salvos 16 atletas que atuaram, 11 titulares, 12 reservas, cinco trocas,
gols, assistencias confirmadas, arbitragem e bilheteria.
Os minutos dos eventos seguem o SofaScore, que diverge da ficha NetVasco:
Puma aos 35; Gustavo Henrique aos 50; Matheus Bidu aos 57; Marino aos 88 e 90.
Assistencia de David no gol da vitoria. Gol anulado de Bruno Duarte confirmado
pela NetVasco, sem minuto exato confirmado; salvo com periodo 1T.

Campos individuais ausentes nao receberam zeros artificiais. Atletas sem
participacao nao receberam scouts. Para quem nao finalizou, zero no gol e
consequencia do total confirmado de finalizacoes. Ausencias medicas confirmadas
na pagina SofaScore: Carlos Cuesta e Mateus Carvalho.

Validacao em copia temporaria e PRD: integrity_check OK; 25 finalizacoes e oito
no gol somam os scouts individuais. Estado publicado: 1789 jogos, oito futuros,
55 atletas atuais e 151 historicos. Nenhum dado remoto anterior foi substituido
por versao local atrasada. Runtime publico validado apos a publicacao.
