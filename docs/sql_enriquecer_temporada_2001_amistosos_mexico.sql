-- Enriquecimento revisável dos amistosos do Vasco no México em 2001.
--
-- Execute após:
-- 1. docs/sql_jogadores_historicos_temporada_2001.sql
-- 2. docs/sql_corrigir_temporada_2001.sql
--
-- Fontes:
-- - https://www.netvasco.com.br/futebol/amistosos2001/
-- - https://www.netvasco.com.br/futebol/amistosos2001/34leovas.html
-- - https://www.netvasco.com.br/futebol/amistosos2001/35tigvas.html
-- - https://www.supervasco.com/noticias/ha-12-anos-vasco-vencia-amistoso-contra-o-leonmex-por-3-a-1-185670.html
--
-- Observação: as fichas individuais da NetVasco em /amistosos2001/ trazem 2000 no campo Data,
-- mas a página índice de amistosos 2001, a página de estatísticas 2001 e fontes cruzadas
-- confirmam que os jogos são de 08/07/2001 e 10/07/2001.

BEGIN TRANSACTION;

INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('estadios', 'Nou Camp');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('estadios', 'Universitário');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('arbitros', 'Germán Arredondo');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('arbitros', 'Eduardo Brizio Carter');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('auxiliares', 'Felipe González');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('auxiliares', 'Jaime Vázquez');

UPDATE matches
SET stadium = 'Nou Camp',
    match_time = '18:00',
    total_attendance = 25000,
    match_revenue = NULL,
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1),
    arbitration_json = '{"arbitro":"Germán Arredondo","auxiliares":["Felipe González","Jaime Vázquez"],"quarto_arbitro":"","var":""}',
    lineup_json = '{"titulares_por_posicao":{"Goleiro":["Fábio"],"Lateral-Direito":["Patrício"],"Zagueiro":["Geder","Torres","Henrique"],"Lateral-Esquerdo":["Gilberto"],"Volante":["Jorginho","William"],"Meio-Campista":["Botti"],"Atacante":["Pedrinho","Romário"]},"reservas":["Ricardo Bóvio","Paulo César","Léo Lima","Valdo","Siston"],"reservas_que_entraram":["Ricardo Bóvio","Paulo César","Léo Lima","Valdo","Siston"],"substituicoes":[{"jogador_saiu":"Henrique","jogador_entrou":"Ricardo Bóvio","minuto":68,"periodo":"2T"},{"jogador_saiu":"Jorginho","jogador_entrou":"Paulo César","minuto":68,"periodo":"2T"},{"jogador_saiu":"William","jogador_entrou":"Léo Lima","minuto":79,"periodo":"2T"},{"jogador_saiu":"Botti","jogador_entrou":"Valdo","minuto":85,"periodo":"2T"},{"jogador_saiu":"Pedrinho","jogador_entrou":"Siston","minuto":85,"periodo":"2T"}],"nao_relacionados":[],"lesionados":[],"suspensos":[],"servindo_selecao":[]}'
WHERE date_iso = '2001-07-08'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'León' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Amistoso' LIMIT 1);

UPDATE matches
SET stadium = 'Universitário',
    match_time = '22:45',
    total_attendance = 25000,
    match_revenue = NULL,
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1),
    arbitration_json = '{"arbitro":"Eduardo Brizio Carter","auxiliares":[],"quarto_arbitro":"","var":""}',
    lineup_json = '{"titulares_por_posicao":{"Goleiro":["Fábio"],"Lateral-Direito":["Patrício"],"Zagueiro":["Geder","Torres","Ricardo Bóvio"],"Lateral-Esquerdo":["Gilberto"],"Volante":["Jorginho","William"],"Meio-Campista":["Botti"],"Atacante":["Pedrinho","Romário"]},"reservas":["Léo Lima","Ely Thadeu","Siston","Paulo César"],"reservas_que_entraram":["Léo Lima","Ely Thadeu","Siston","Paulo César"],"substituicoes":[{"jogador_saiu":"Jorginho","jogador_entrou":"Léo Lima","minuto":46,"periodo":"2T"},{"jogador_saiu":"Pedrinho","jogador_entrou":"Siston","minuto":58,"periodo":"2T"},{"jogador_saiu":"Botti","jogador_entrou":"Ely Thadeu","minuto":63,"periodo":"2T"},{"jogador_saiu":"Romário","jogador_entrou":"Paulo César","minuto":66,"periodo":"2T"}],"nao_relacionados":[],"lesionados":["Romário"],"suspensos":[],"servindo_selecao":[]}'
WHERE date_iso = '2001-07-10'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Tigres' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Amistoso' LIMIT 1);

DELETE FROM match_goals
WHERE match_id IN (
    SELECT m.id
    FROM matches m
    JOIN teams t ON t.id = m.opponent_team_id
    JOIN competitions c ON c.id = m.competition_id
    WHERE c.name = 'Amistoso'
      AND ((m.date_iso = '2001-07-08' AND t.name = 'León')
        OR (m.date_iso = '2001-07-10' AND t.name = 'Tigres'))
);

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed, goal_minutes_json, goal_periods_json)
SELECT m.id, 'adversario', NULL, 'Valenzuela', 1, 'León', 0, '[24]', '["1T"]'
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-08' AND t.name = 'León' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed, goal_minutes_json, goal_periods_json)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Pedrinho' LIMIT 1), 'Pedrinho', 1, NULL, 0, '[43]', '["1T"]'
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-08' AND t.name = 'León' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed, goal_minutes_json, goal_periods_json)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Romário' LIMIT 1), 'Romário', 1, NULL, 0, '[69]', '["2T"]'
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-08' AND t.name = 'León' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed, goal_minutes_json, goal_periods_json)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Paulo César' LIMIT 1), 'Paulo César', 1, NULL, 0, '[83]', '["2T"]'
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-08' AND t.name = 'León' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed, goal_minutes_json, goal_periods_json)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Romário' LIMIT 1), 'Romário', 1, NULL, 0, '[46]', '["2T"]'
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-10' AND t.name = 'Tigres' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed, goal_minutes_json, goal_periods_json)
SELECT m.id, 'adversario', NULL, 'Marcelo Fernandes', 1, 'Tigres', 0, '[78]', '["2T"]'
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-10' AND t.name = 'Tigres' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed, goal_minutes_json, goal_periods_json)
SELECT m.id, 'adversario', NULL, 'Olalde', 1, 'Tigres', 0, '[82]', '["2T"]'
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-10' AND t.name = 'Tigres' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed, goal_minutes_json, goal_periods_json)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Gilberto' LIMIT 1), 'Gilberto', 1, NULL, 0, '[94]', '["2T"]'
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-10' AND t.name = 'Tigres' AND c.name = 'Amistoso';

DELETE FROM match_cards
WHERE match_id IN (
    SELECT m.id
    FROM matches m
    JOIN teams t ON t.id = m.opponent_team_id
    JOIN competitions c ON c.id = m.competition_id
    WHERE c.name = 'Amistoso'
      AND ((m.date_iso = '2001-07-08' AND t.name = 'León')
        OR (m.date_iso = '2001-07-10' AND t.name = 'Tigres'))
)
  AND side = 'vasco';

INSERT INTO match_cards(match_id, side, player_id, player_name, card_type, card_count, club_name)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Léo Lima' LIMIT 1), 'Léo Lima', 'amarelo', 1, NULL
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-08' AND t.name = 'León' AND c.name = 'Amistoso';

INSERT INTO match_cards(match_id, side, player_id, player_name, card_type, card_count, club_name)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Jorginho' LIMIT 1), 'Jorginho', 'amarelo', 1, NULL
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-10' AND t.name = 'Tigres' AND c.name = 'Amistoso';

INSERT INTO match_cards(match_id, side, player_id, player_name, card_type, card_count, club_name)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Geder' LIMIT 1), 'Geder', 'amarelo', 1, NULL
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-10' AND t.name = 'Tigres' AND c.name = 'Amistoso';

INSERT INTO match_cards(match_id, side, player_id, player_name, card_type, card_count, club_name)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Botti' LIMIT 1), 'Botti', 'amarelo', 1, NULL
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-10' AND t.name = 'Tigres' AND c.name = 'Amistoso';

SELECT m.id,
       m.date_text,
       t.name AS adversario,
       m.stadium,
       m.match_time,
       ch.name AS tecnico,
       m.total_attendance,
       m.arbitration_json,
       m.lineup_json
FROM matches m
JOIN teams t ON t.id = m.opponent_team_id
JOIN competitions c ON c.id = m.competition_id
LEFT JOIN coaches ch ON ch.id = m.coach_id
WHERE c.name = 'Amistoso'
  AND m.date_iso IN ('2001-07-08', '2001-07-10')
ORDER BY m.date_iso;

COMMIT;
