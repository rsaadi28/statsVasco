# Athletico-PR 1 x 3 Vasco - 04/11/2026

Importacao em 05/11/2026, apos pull, backup e reconciliacao do elenco Railway.

## Fontes

- https://netvasco.com.br/n/395712/vascao-vence-o-athletico-pr-na-arena-da-baixada-de-virada-3-a-1
- https://www.sofascore.com/pt/football/match/vasco-da-gama-athletico/rOszO#id:15238239
- Site oficial do Athletico, "Athletico e superado pelo Vasco na Arena da
  Baixada": 20.872 presentes, 20.063 pagantes, renda R$ 994.380,00.

Scouts obtidos nos endpoints lineups, statistics e incidents do evento acima.
Titulares, 12 reservas, cinco substituicoes e scouts dos 16 atletas que atuaram
foram confirmados. Nao foram criados scouts para reservas sem participacao.
Campos ausentes ficaram sem preencher. Zero no gol para atleta sem nenhuma
finalizacao decorre do total confirmado; nao foram inventados desarmes zero.

Gols: Mendoza aos 22 (Luiz Gustavo), Aguirre contra aos 61, Bruno Duarte aos
63 (Puma Rodriguez) e Gabriel Pereira aos 67 (Facundo Colidio). A autoria de
Aguirre foi preservada em gol_contra_autor; o registro como Gol contra evita
creditar o adversario entre os artilheiros do Vasco. Lescano recebeu amarelo
aos 55. O vermelho de Viveros pertence ao adversario, nao ao Vasco.
Trocas no intervalo foram registradas como INT, minuto zero.

Arbitragem: Ramon Abatti Abel, Bruno Raphael Pires, Alexandre de Medeiros
Lodetti e VAR Daniel Nobre Bins. Esquema inicial 3-5-2; capitao Thiago Mendes.
Desfalques medicos na pagina SofaScore: Cuesta, Cauan Barros e Mateus Carvalho.
Marino nao relacionado; SofaScore indica descanso, enquanto o elenco remoto
ja o marcava como lesionado. O status do elenco remoto foi preservado.
O lance de Brenner com reclamacao de penalti nao foi salvo como penalti dado.

Validado primeiro em SQLite temporario e depois no PRD: integrity_check OK,
sete finalizacoes e tres no gol somam os scouts individuais. Todos os jogos
remotos anteriores foram comparados com normalizacao de IDs e campos
equivalentes; elenco, historico e a secao remota titles foram preservados.
Publicacao: 1792 partidas, seis futuras, 55 atletas atuais e 151 historicos.
Agenda removida apenas da partida realizada; demais datas remotas mantidas.
