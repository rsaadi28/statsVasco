-- Correções revisáveis de núcleo da temporada 2001.
--
-- Não aplique direto em PRD sem testar numa cópia.
--
-- Correção confirmada:
-- - A referência NetVasco 2001 tem 68 jogos, incluindo dois amistosos no México.
-- - O banco auditado não contém León 1 x 3 Vasco (08/07/2001) nem Tigres 2 x 2 Vasco (10/07/2001).
-- - O jogo Vasco 3 x 1 São Caetano em 18/01/2001 fica preservado, pois pertence ao Brasileiro 2000.
--
-- Fontes:
-- - https://www.netvasco.com.br/futebol/amistosos2001/
-- - https://www.netvasco.com.br/futebol/amistosos2001/34leovas.html
-- - https://www.netvasco.com.br/futebol/amistosos2001/35tigvas.html
-- - https://www.supervasco.com/noticias/ha-12-anos-vasco-vencia-amistoso-contra-o-leonmex-por-3-a-1-185670.html

BEGIN TRANSACTION;

INSERT OR IGNORE INTO competitions(name) VALUES ('Amistoso');
INSERT OR IGNORE INTO coaches(name) VALUES ('Joel Santana');

INSERT OR IGNORE INTO teams(name, team_type) VALUES ('León', 'adversario');
INSERT OR IGNORE INTO teams(name, team_type) VALUES ('Tigres', 'adversario');

INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('competicoes', 'Amistoso');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('tecnicos', 'Joel Santana');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('clubes_adversarios', 'León');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('clubes_adversarios', 'Tigres');

INSERT INTO matches(
    date_text, date_iso, opponent_team_id, competition_id, location,
    vasco_goals, opponent_goals, observation, coach_id, stadium, match_time,
    total_attendance, arbitration_json
)
SELECT '08/07/2001',
       '2001-07-08',
       (SELECT id FROM teams WHERE name = 'León' LIMIT 1),
       (SELECT id FROM competitions WHERE name = 'Amistoso' LIMIT 1),
       'fora',
       3,
       1,
       'Amistoso internacional no México; ficha NetVasco em /amistosos2001/34leovas.html traz 08.07.2000, mas índice/estatísticas 2001 e fontes cruzadas confirmam 08/07/2001.',
       (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1),
       'Nou Camp',
       '18:00',
       25000,
       '{"arbitro":"Germán Arredondo","auxiliares":["Felipe González","Jaime Vázquez"],"var":""}'
WHERE NOT EXISTS (
    SELECT 1
    FROM matches m
    JOIN teams t ON t.id = m.opponent_team_id
    JOIN competitions c ON c.id = m.competition_id
    WHERE m.date_iso = '2001-07-08'
      AND t.name = 'León'
      AND c.name = 'Amistoso'
);

INSERT INTO matches(
    date_text, date_iso, opponent_team_id, competition_id, location,
    vasco_goals, opponent_goals, observation, coach_id, stadium, match_time,
    total_attendance, arbitration_json
)
SELECT '10/07/2001',
       '2001-07-10',
       (SELECT id FROM teams WHERE name = 'Tigres' LIMIT 1),
       (SELECT id FROM competitions WHERE name = 'Amistoso' LIMIT 1),
       'fora',
       2,
       2,
       'Amistoso internacional no México; ficha NetVasco em /amistosos2001/35tigvas.html traz 10.07.2000, mas índice/estatísticas 2001 e contexto da excursão confirmam 10/07/2001.',
       (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1),
       'Universitário',
       '22:45',
       25000,
       '{"arbitro":"Eduardo Brizio Carter","auxiliares":[],"var":""}'
WHERE NOT EXISTS (
    SELECT 1
    FROM matches m
    JOIN teams t ON t.id = m.opponent_team_id
    JOIN competitions c ON c.id = m.competition_id
    WHERE m.date_iso = '2001-07-10'
      AND t.name = 'Tigres'
      AND c.name = 'Amistoso'
);

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

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Pedrinho' LIMIT 1), 'Pedrinho', 1, NULL, 0
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-08' AND t.name = 'León' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Romário' LIMIT 1), 'Romário', 1, NULL, 0
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-08' AND t.name = 'León' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Paulo César' LIMIT 1), 'Paulo César', 1, NULL, 0
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-08' AND t.name = 'León' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed)
SELECT m.id, 'adversario', NULL, 'Valenzuela', 1, 'León', 0
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-08' AND t.name = 'León' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Romário' LIMIT 1), 'Romário', 1, NULL, 0
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-10' AND t.name = 'Tigres' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed)
SELECT m.id, 'vasco', (SELECT id FROM players WHERE name = 'Gilberto' LIMIT 1), 'Gilberto', 1, NULL, 0
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-10' AND t.name = 'Tigres' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed)
SELECT m.id, 'adversario', NULL, 'Marcelo Fernandes', 1, 'Tigres', 0
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-10' AND t.name = 'Tigres' AND c.name = 'Amistoso';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed)
SELECT m.id, 'adversario', NULL, 'Olalde', 1, 'Tigres', 0
FROM matches m JOIN teams t ON t.id = m.opponent_team_id JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2001-07-10' AND t.name = 'Tigres' AND c.name = 'Amistoso';

SELECT m.id,
       m.date_text,
       t.name AS adversario,
       c.name AS competicao,
       m.location,
       m.vasco_goals,
       m.opponent_goals,
       m.match_time,
       ch.name AS tecnico
FROM matches m
JOIN teams t ON t.id = m.opponent_team_id
JOIN competitions c ON c.id = m.competition_id
LEFT JOIN coaches ch ON ch.id = m.coach_id
WHERE c.name = 'Amistoso'
  AND m.date_iso IN ('2001-07-08', '2001-07-10')
ORDER BY m.date_iso;

COMMIT;
