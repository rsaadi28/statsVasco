-- Script para executar no DBeaver e unificar o time "Paysandu" em "Paysandu-PA".
-- Antes de rodar, confirme que o DBeaver está conectado ao banco correto.

PRAGMA foreign_keys = ON;

CREATE TEMP TABLE IF NOT EXISTS _team_merge (
    source_id INTEGER,
    target_id INTEGER
);

DELETE FROM _team_merge;

INSERT INTO _team_merge (source_id, target_id)
SELECT src.id, dst.id
FROM teams AS src
JOIN teams AS dst ON dst.name = 'Paysandu-PA'
WHERE src.name = 'Paysandu';

UPDATE teams
SET name = 'Paysandu-PA'
WHERE name = 'Paysandu'
  AND NOT EXISTS (
      SELECT 1
      FROM teams
      WHERE name = 'Paysandu-PA'
  );

INSERT OR IGNORE INTO team_stadiums (team_id, stadium_id, is_primary)
SELECT m.target_id, ts.stadium_id, ts.is_primary
FROM team_stadiums AS ts
JOIN _team_merge AS m ON m.source_id = ts.team_id;

UPDATE team_stadiums
SET is_primary = 1
WHERE team_id IN (SELECT target_id FROM _team_merge)
  AND stadium_id IN (
      SELECT ts.stadium_id
      FROM team_stadiums AS ts
      JOIN _team_merge AS m ON m.source_id = ts.team_id
      WHERE ts.is_primary = 1
  );

UPDATE matches
SET opponent_team_id = (
    SELECT target_id
    FROM _team_merge
    LIMIT 1
)
WHERE opponent_team_id IN (SELECT source_id FROM _team_merge);

UPDATE future_matches
SET opponent_team_id = (
    SELECT target_id
    FROM _team_merge
    LIMIT 1
)
WHERE opponent_team_id IN (SELECT source_id FROM _team_merge);

DELETE FROM team_stadiums
WHERE team_id IN (SELECT source_id FROM _team_merge);

DELETE FROM teams
WHERE id IN (SELECT source_id FROM _team_merge);

INSERT OR IGNORE INTO list_entries (list_type, value)
VALUES ('clubes_adversarios', 'Paysandu-PA');

DELETE FROM list_entries
WHERE list_type = 'clubes_adversarios'
  AND value = 'Paysandu';

UPDATE match_goals
SET club_name = 'Paysandu-PA'
WHERE club_name = 'Paysandu';

UPDATE match_cards
SET club_name = 'Paysandu-PA'
WHERE club_name = 'Paysandu';

DROP TABLE _team_merge;

SELECT id, name
FROM teams
WHERE name LIKE 'Paysandu%';

SELECT 'matches' AS tabela, COUNT(*) AS total
FROM matches
WHERE opponent_team_id = (SELECT id FROM teams WHERE name = 'Paysandu-PA')
UNION ALL
SELECT 'future_matches' AS tabela, COUNT(*) AS total
FROM future_matches
WHERE opponent_team_id = (SELECT id FROM teams WHERE name = 'Paysandu-PA')
UNION ALL
SELECT 'match_goals' AS tabela, COUNT(*) AS total
FROM match_goals
WHERE club_name = 'Paysandu-PA'
UNION ALL
SELECT 'match_cards' AS tabela, COUNT(*) AS total
FROM match_cards
WHERE club_name = 'Paysandu-PA'
UNION ALL
SELECT 'list_entries' AS tabela, COUNT(*) AS total
FROM list_entries
WHERE list_type = 'clubes_adversarios'
  AND value = 'Paysandu-PA';
