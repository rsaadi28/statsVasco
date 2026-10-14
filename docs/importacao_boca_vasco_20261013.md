# Boca Juniors 0 x 1 Vasco - 13/10/2026

Importacao em 14/10/2026, apos reconciliacao Railway -> PRD local com backup.

## Fontes

- Ficha tecnica: https://www.netvasco.com.br/n/394376/vascao-vence-o-boca-juniors-na-bombonera-1-a-0
- Escalacoes, eventos e scouts: https://www.sofascore.com/pt/football/match/boca-juniors-vasco-da-gama/zOscob#id:17108316
- JSONs SofaScore: event/17108316, lineups, statistics e incidents.

## Dados confirmados

Semifinal de ida da Sul-Americana, La Bombonera, Buenos Aires, 21h30 de Brasilia.
Gol de Adson aos 25 minutos do primeiro tempo, assistencia de Andres Gomez.
Expulsao de Gomez por segundo amarelo aos 64 minutos no registro SofaScore.
Ficha NetVasco e relato divergem em um minuto nos eventos do segundo tempo;
foram adotados os minutos estruturados do SofaScore para substituicoes e expulsao.

Foram importados titulares, 12 reservas, cinco substituicoes, desfalques,
arbitragem, cartoes, scouts coletivos e scouts dos 16 jogadores que atuaram.
Scouts individuais foram mapeados apenas quando presentes na fonte.
Para atletas com zero finalizacoes confirmado, zero no gol decorre desse total.
Campos ausentes, incluindo desarmes individuais nao fornecidos, nao receberam zero.
Os sete reservas que nao atuaram nao receberam scouts artificiais.

Publico pagante, presente e renda nao foram confirmados e permanecem nulos.
Nao foram confirmados outros nao relacionados nem goleadores anulados.

## Preservacao e validacao

Antes da importacao foram trazidos do Railway o Remo de 10/10, a agenda
atualizada (incluindo a volta no Maracana) e o elenco atualizado.
Metadados extras remotos como cidade, rodada e fontes foram preservados em
settings.match_extra_metadata_json; storage_sqlite os restitui em load_matches
e preserva campos adicionais em save_matches.

Todos os campos dos 1785 jogos remotos anteriores foram comparados antes da
publicacao, descontando somente IDs internos SQLite recriados pelo gravador.
Elenco e historico remoto foram preservados. A partida realizada foi retirada
da agenda futura. Estado final: 1786 partidas, 11 futuras, 55 atletas atuais e
151 historicos. SQLite integrity_check OK.

Runtime publico Vercel validado com HTTP 200: placar 1-0, fase semifinal de ida,
16 scouts individuais, cinco substituicoes, nove finalizacoes e duas no gol.
