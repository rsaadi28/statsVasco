-- Correções revisáveis de núcleo da temporada 2002.
-- Corrige técnicos confirmados nas fichas NetVasco.
-- Não aplique direto em PRD sem testar numa cópia.

BEGIN TRANSACTION;

INSERT OR IGNORE INTO coaches(name) VALUES ('Evaristo de Macedo');
INSERT OR IGNORE INTO coaches(name) VALUES ('Antônio Lopes');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('tecnicos', 'Evaristo de Macedo');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('tecnicos', 'Antônio Lopes');

-- 02/06/2002 | Campeonato Carioca | Bangu-RJ
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-06-02'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bangu-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 05/06/2002 | Campeonato Carioca | Americano-RJ
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-06-05'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Americano-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 08/06/2002 | Campeonato Carioca | Botafogo
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-06-08'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Botafogo' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 03/07/2002 | Copa dos Campeões | Atlético-MG
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-07-03'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Atlético-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa dos Campeões' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 10/07/2002 | Copa dos Campeões | Palmeiras-SP
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-07-10'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa dos Campeões' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 14/07/2002 | Copa dos Campeões | Bahia-BA
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-07-14'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bahia-BA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa dos Campeões' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 16/10/2002 | Campeonato Brasileiro Serie A | Flamengo-RJ
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-10-16'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 19/10/2002 | Campeonato Brasileiro Serie A | Paraná-PR
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-10-19'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Paraná-PR' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 23/10/2002 | Campeonato Brasileiro Serie A | Bahia-BA
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-10-23'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bahia-BA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 31/10/2002 | Campeonato Brasileiro Serie A | Fluminense-RJ
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-10-31'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 03/11/2002 | Campeonato Brasileiro Serie A | Palmeiras-SP
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-11-03'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 06/11/2002 | Campeonato Brasileiro Serie A | São Paulo-SP
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-11-06'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Paulo-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 09/11/2002 | Campeonato Brasileiro Serie A | Vitória-BA
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-11-09'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Vitória-BA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 13/11/2002 | Campeonato Brasileiro Serie A | Ponte Preta-SP
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-11-13'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Ponte Preta-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 17/11/2002 | Campeonato Brasileiro Serie A | Corinthians
UPDATE matches
SET     coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-11-17'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Corinthians' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

SELECT m.date_text, c.name AS competicao, t.name AS adversario, ch.name AS tecnico
FROM matches m
JOIN teams t ON t.id = m.opponent_team_id
JOIN competitions c ON c.id = m.competition_id
LEFT JOIN coaches ch ON ch.id = m.coach_id
WHERE m.date_iso >= '2002-06-01' AND m.date_iso < '2002-12-01'
  AND (m.date_iso <= '2002-07-14' OR m.date_iso >= '2002-10-16')
ORDER BY m.date_iso;

COMMIT;
