# Template de pedido para auditoria de temporada

Use este texto quando quiser pedir a auditoria completa de qualquer ano.

```text
Execute o MAPA_AUDITORIA_TEMPORADAS.md para a temporada <ANO>.

Quero que pesquise o máximo absoluto de dados disponíveis na internet para todos os jogos do Vasco desse ano e prepare tudo para o banco do app:

- data, horário, competição, fase/rodada, adversário, mando, estádio, cidade/país;
- placar, gols do Vasco e do adversário, gols contra, gols anulados, minutos e períodos dos gols;
- disputa por pênaltis, se houver;
- técnico, capitão, observação/contexto;
- público pagante, público presente e renda;
- arbitragem completa: árbitro, auxiliares, quarto árbitro e VAR quando existir;
- cartões amarelos e vermelhos do Vasco, com minuto no CSV quando a fonte trouxer;
- cartões do adversário no CSV quando encontrar fonte;
- escalação titular do Vasco por posição;
- reservas/banco completo quando houver fonte;
- reservas que entraram;
- substituições com jogador que saiu, jogador que entrou, minuto e período;
- lesionados, suspensos, não relacionados e servindo seleção;
- jogadores históricos/atuais citados nas fontes para aparecerem na aba de jogadores.

Use múltiplas fontes: NetVasco, Vaskipédia, oGol/Zerozero/PlaymakerStats, Soccerzz, Football-Lineups, sites oficiais, páginas de adversários, competições e hemerotecas.

Se uma informação não for encontrada, deixe em branco e marque o status no CSV como não encontrado. Se houver conflito, marque como conflito e não gere SQL para aquele campo.

Faça a missão em partes:
- primeiro audite o núcleo da temporada inteira;
- depois pesquise campos ricos em lotes pequenos de jogos consecutivos;
- comece com 5 a 8 jogos por lote;
- se as fontes estiverem limpas, avance para até 10 jogos por lote;
- se a ficha estiver quebrada ou conflitante, reduza para 1 a 3 jogos;
- para cada lote, traga para o banco tudo que estiver confirmado e deixe em branco o que não conseguir ler com segurança.

Não altere PRD no primeiro momento. Gere:
- script de auditoria da temporada;
- relatório Markdown;
- mapa CSV jogo a jogo;
- SQLs revisáveis de correção/enriquecimento;
- SQL de jogadores históricos, se houver jogadores ausentes.

Valide cada lote em cópia temporária do banco e rode load_matches antes de qualquer aplicação em DEV/PRD. Depois de validado, aplique em DEV e PRD com backup antes de cada aplicação.
```
