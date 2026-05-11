-- Enriquecimento revisável para Palmeiras-SP 4 x 0 Vasco, 01/03/2000.
--
-- Este SQL complementa a correção do placar em docs/sql_corrigir_temporada_2000.sql.
-- Não aplique direto em PRD sem testar numa cópia.
--
-- Fontes:
-- - Palmeiras oficial:
--   https://www.palmeiras.com.br/lightbox_galeria/torneio-rio-sao-paulo-2000/
-- - Verdazzo:
--   https://www.verdazzo.com.br/jogo/20000301-palmeiras-x-vasco-da-gama-torneio-rio-sao-paulo-2000/
-- - NetVasco Rio-São Paulo 2000, para horário:
--   https://netvasco.com/futebol/riosaopaulo2000/index.html

BEGIN TRANSACTION;

-- Identificador esperado em PRD local hoje: 215437.
-- A seleção por data/adversário/competição evita depender do id.
WITH alvo AS (
    SELECT m.id AS match_id
    FROM matches m
    LEFT JOIN teams t ON t.id = m.opponent_team_id
    LEFT JOIN competitions c ON c.id = m.competition_id
    WHERE m.date_iso = '2000-03-01'
      AND t.name = 'Palmeiras-SP'
      AND c.name = 'Torneio Rio-São Paulo'
)
UPDATE matches
SET stadium = 'Morumbi',
    match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1),
    arbitration_json = '{"arbitro":"Jorge Travassos dos Santos","auxiliares":[],"var":""}',
    lineup_json = '{"titulares_por_posicao":{"Goleiro":["Helton"],"Lateral-direito":["Paulo Miranda"],"Zagueiro":["Odvan","Mauro Galvão"],"Lateral-esquerdo":["Gilberto"],"Volante":["Amaral","Válber"],"Meia":["Juninho Pernambucano","Alex Oliveira"],"Atacante":["Edmundo","Romário"]},"reservas":["Maricá","Pedrinho","Viola"],"substituicoes":[],"nao_relacionados":[],"lesionados":[],"suspensos":[],"servindo_selecao":[]}'
WHERE id IN (SELECT match_id FROM alvo);

INSERT OR IGNORE INTO list_entries(list_type, value)
VALUES ('arbitros', 'Jorge Travassos dos Santos');

-- Recria gols do adversário confirmados na ficha.
DELETE FROM match_goals
WHERE match_id IN (
    SELECT m.id
    FROM matches m
    LEFT JOIN teams t ON t.id = m.opponent_team_id
    LEFT JOIN competitions c ON c.id = m.competition_id
    WHERE m.date_iso = '2000-03-01'
      AND t.name = 'Palmeiras-SP'
      AND c.name = 'Torneio Rio-São Paulo'
)
  AND side = 'adversario'
  AND is_disallowed = 0;

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed, goal_minutes_json, goal_periods_json)
SELECT m.id, 'adversario', NULL, 'Pena', 1, 'Palmeiras-SP', 0, '[27]', '["1T"]'
FROM matches m
LEFT JOIN teams t ON t.id = m.opponent_team_id
LEFT JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2000-03-01'
  AND t.name = 'Palmeiras-SP'
  AND c.name = 'Torneio Rio-São Paulo';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed, goal_minutes_json, goal_periods_json)
SELECT m.id, 'adversario', NULL, 'Argel', 1, 'Palmeiras-SP', 0, '[31]', '["1T"]'
FROM matches m
LEFT JOIN teams t ON t.id = m.opponent_team_id
LEFT JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2000-03-01'
  AND t.name = 'Palmeiras-SP'
  AND c.name = 'Torneio Rio-São Paulo';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed, goal_minutes_json, goal_periods_json)
SELECT m.id, 'adversario', NULL, 'Euller', 1, 'Palmeiras-SP', 0, '[34]', '["1T"]'
FROM matches m
LEFT JOIN teams t ON t.id = m.opponent_team_id
LEFT JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2000-03-01'
  AND t.name = 'Palmeiras-SP'
  AND c.name = 'Torneio Rio-São Paulo';

INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed, goal_minutes_json, goal_periods_json)
SELECT m.id, 'adversario', NULL, 'Arce', 1, 'Palmeiras-SP', 0, '[23]', '["2T"]'
FROM matches m
LEFT JOIN teams t ON t.id = m.opponent_team_id
LEFT JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2000-03-01'
  AND t.name = 'Palmeiras-SP'
  AND c.name = 'Torneio Rio-São Paulo';

-- Cartões amarelos do Vasco informados pela ficha do Palmeiras.
DELETE FROM match_cards
WHERE match_id IN (
    SELECT m.id
    FROM matches m
    LEFT JOIN teams t ON t.id = m.opponent_team_id
    LEFT JOIN competitions c ON c.id = m.competition_id
    WHERE m.date_iso = '2000-03-01'
      AND t.name = 'Palmeiras-SP'
      AND c.name = 'Torneio Rio-São Paulo'
)
  AND side = 'vasco'
  AND card_type = 'amarelo';

INSERT INTO match_cards(match_id, side, player_id, player_name, card_type, card_count, club_name)
SELECT m.id, 'vasco', NULL, 'Amaral', 'amarelo', 1, NULL
FROM matches m
LEFT JOIN teams t ON t.id = m.opponent_team_id
LEFT JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2000-03-01'
  AND t.name = 'Palmeiras-SP'
  AND c.name = 'Torneio Rio-São Paulo';

INSERT INTO match_cards(match_id, side, player_id, player_name, card_type, card_count, club_name)
SELECT m.id, 'vasco', NULL, 'Edmundo', 'amarelo', 1, NULL
FROM matches m
LEFT JOIN teams t ON t.id = m.opponent_team_id
LEFT JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2000-03-01'
  AND t.name = 'Palmeiras-SP'
  AND c.name = 'Torneio Rio-São Paulo';

INSERT INTO match_cards(match_id, side, player_id, player_name, card_type, card_count, club_name)
SELECT m.id, 'vasco', NULL, 'Gilberto', 'amarelo', 1, NULL
FROM matches m
LEFT JOIN teams t ON t.id = m.opponent_team_id
LEFT JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2000-03-01'
  AND t.name = 'Palmeiras-SP'
  AND c.name = 'Torneio Rio-São Paulo';

SELECT m.id,
       m.date_text,
       t.name AS adversario,
       c.name AS competicao,
       m.stadium,
       m.match_time,
       ch.name AS tecnico,
       m.vasco_goals,
       m.opponent_goals,
       m.arbitration_json,
       m.lineup_json
FROM matches m
LEFT JOIN teams t ON t.id = m.opponent_team_id
LEFT JOIN competitions c ON c.id = m.competition_id
LEFT JOIN coaches ch ON ch.id = m.coach_id
WHERE m.date_iso = '2000-03-01'
  AND t.name = 'Palmeiras-SP'
  AND c.name = 'Torneio Rio-São Paulo';

COMMIT;
