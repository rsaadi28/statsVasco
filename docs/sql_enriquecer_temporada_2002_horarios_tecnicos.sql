-- Enriquecimento revisável da temporada 2002: horários e técnicos.
-- Gerado por scripts/audit_temporada_2002.py.
-- Fontes: páginas NetVasco por competição e fichas detalhadas linkadas.

BEGIN TRANSACTION;

INSERT OR IGNORE INTO coaches(name) VALUES ('Evaristo de Macedo');
INSERT OR IGNORE INTO coaches(name) VALUES ('Antônio Lopes');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('tecnicos', 'Evaristo de Macedo');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('tecnicos', 'Antônio Lopes');

-- 20/01/2002 | Torneio Rio-São Paulo | Ponte Preta-SP
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-01-20'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Ponte Preta-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 26/01/2002 | Campeonato Carioca | Bangu-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-01-26'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bangu-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 27/01/2002 | Torneio Rio-São Paulo | São Paulo-SP
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-01-27'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Paulo-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 30/01/2002 | Torneio Rio-São Paulo | América
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-01-30'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'América' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 02/02/2002 | Campeonato Carioca | Madureira-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-02-02'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Madureira-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 03/02/2002 | Torneio Rio-São Paulo | Palmeiras-SP
UPDATE matches
SET     match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-02-03'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 06/02/2002 | Campeonato Carioca | Entrerriense-RJ
UPDATE matches
SET     match_time = '19:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-02-06'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Entrerriense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 09/02/2002 | Torneio Rio-São Paulo | Jundiaí
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-02-09'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Jundiaí' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 13/02/2002 | Copa do Brasil | Sergipe
UPDATE matches
SET     match_time = '21:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-02-13'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Sergipe' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa do Brasil' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 17/02/2002 | Torneio Rio-São Paulo | Americano-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-02-17'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Americano-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 18/02/2002 | Campeonato Carioca | Botafogo
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-02-18'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Botafogo' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 20/02/2002 | Copa do Brasil | Sergipe
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-02-20'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Sergipe' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa do Brasil' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 21/02/2002 | Campeonato Carioca | Olaria-RJ
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-02-21'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Olaria-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 24/02/2002 | Torneio Rio-São Paulo | São Caetano-SP
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-02-24'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Caetano-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 25/02/2002 | Campeonato Carioca | América
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-02-25'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'América' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 27/02/2002 | Copa do Brasil | Santa Cruz-PE
UPDATE matches
SET     match_time = '21:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-02-27'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Santa Cruz-PE' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa do Brasil' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 28/02/2002 | Campeonato Carioca | Friburguense
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-02-28'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Friburguense' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 02/03/2002 | Torneio Rio-São Paulo | Portuguesa
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-03-02'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Portuguesa' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 06/03/2002 | Copa do Brasil | Santa Cruz-PE
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-03-06'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Santa Cruz-PE' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa do Brasil' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 07/03/2002 | Campeonato Carioca | Fluminense-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-03-07'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 10/03/2002 | Torneio Rio-São Paulo | Flamengo-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-03-10'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 11/03/2002 | Campeonato Carioca | V. Redonda
UPDATE matches
SET     match_time = '16:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-03-11'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'V. Redonda' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 17/03/2002 | Torneio Rio-São Paulo | Guarani-SP
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-03-17'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Guarani-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 21/03/2002 | Torneio Rio-São Paulo | Botafogo
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-03-21'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Botafogo' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 24/03/2002 | Torneio Rio-São Paulo | Fluminense-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-03-24'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 25/03/2002 | Campeonato Carioca | Flamengo-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-03-25'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 27/03/2002 | Copa do Brasil | CSA
UPDATE matches
SET     match_time = '19:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-03-27'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'CSA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa do Brasil' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 30/03/2002 | Torneio Rio-São Paulo | Santos
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-03-30'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Santos' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 03/04/2002 | Copa do Brasil | CSA
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-04-03'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'CSA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa do Brasil' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 07/04/2002 | Torneio Rio-São Paulo | Bangu-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-04-07'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bangu-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 10/04/2002 | Copa do Brasil | São Paulo-SP
UPDATE matches
SET     match_time = '21:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-04-10'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Paulo-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa do Brasil' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 14/04/2002 | Torneio Rio-São Paulo | Corinthians
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-04-14'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Corinthians' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 17/04/2002 | Copa do Brasil | São Paulo-SP
UPDATE matches
SET     match_time = '21:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-04-17'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Paulo-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa do Brasil' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 21/04/2002 | Campeonato Carioca | Madureira-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-04-21'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Madureira-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 24/04/2002 | Campeonato Carioca | Entrerriense-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-04-24'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Entrerriense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 28/04/2002 | Campeonato Carioca | Americano-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-04-28'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Americano-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 01/05/2002 | Campeonato Carioca | Olaria-RJ
UPDATE matches
SET     match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-05-01'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Olaria-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 05/05/2002 | Campeonato Carioca | América
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-05-05'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'América' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 08/05/2002 | Campeonato Carioca | Friburguense
UPDATE matches
SET     match_time = '20:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-05-08'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Friburguense' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 11/05/2002 | Campeonato Carioca | Americano-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-05-11'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Americano-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 15/05/2002 | Campeonato Carioca | Fluminense-RJ
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-05-15'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 19/05/2002 | Campeonato Carioca | V. Redonda
UPDATE matches
SET     match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-05-19'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'V. Redonda' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 23/05/2002 | Campeonato Carioca | Bangu-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-05-23'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bangu-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 26/05/2002 | Campeonato Carioca | Flamengo-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-05-26'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 29/05/2002 | Campeonato Carioca | Botafogo
UPDATE matches
SET     match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-05-29'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Botafogo' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 02/06/2002 | Campeonato Carioca | Bangu-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-06-02'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bangu-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 05/06/2002 | Campeonato Carioca | Americano-RJ
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-06-05'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Americano-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 08/06/2002 | Campeonato Carioca | Botafogo
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-06-08'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Botafogo' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 03/07/2002 | Copa dos Campeões | Atlético-MG
UPDATE matches
SET     match_time = '21:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-07-03'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Atlético-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa dos Campeões' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 10/07/2002 | Copa dos Campeões | Palmeiras-SP
UPDATE matches
SET     match_time = '21:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-07-10'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa dos Campeões' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 14/07/2002 | Copa dos Campeões | Bahia-BA
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Evaristo de Macedo' LIMIT 1)
WHERE date_iso = '2002-07-14'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bahia-BA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa dos Campeões' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Evaristo de Macedo');

-- 10/08/2002 | Campeonato Brasileiro Serie A | Figueirense-SC
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-08-10'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Figueirense-SC' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 14/08/2002 | Campeonato Brasileiro Serie A | Grêmio-RS
UPDATE matches
SET     match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-08-14'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Grêmio-RS' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 17/08/2002 | Campeonato Brasileiro Serie A | Atlético-PR
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-08-17'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Atlético-PR' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 22/08/2002 | Campeonato Brasileiro Serie A | Gama-DF
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-08-22'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Gama-DF' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 25/08/2002 | Campeonato Brasileiro Serie A | Goiás-GO
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-08-25'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Goiás-GO' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 01/09/2002 | Campeonato Brasileiro Serie A | Juventude-RS
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-09-01'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Juventude-RS' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 04/09/2002 | Campeonato Brasileiro Serie A | Atlético-MG
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-09-04'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Atlético-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 07/09/2002 | Campeonato Brasileiro Serie A | Coritiba-PR
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-09-07'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Coritiba-PR' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 11/09/2002 | Campeonato Brasileiro Serie A | Paysandu-PA
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-09-11'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Paysandu-PA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 15/09/2002 | Campeonato Brasileiro Serie A | Botafogo
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-09-15'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Botafogo' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 18/09/2002 | Campeonato Brasileiro Serie A | Santos
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-09-18'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Santos' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 22/09/2002 | Campeonato Brasileiro Serie A | Internacional-RS
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-09-22'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Internacional-RS' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 25/09/2002 | Campeonato Brasileiro Serie A | Cruzeiro-MG
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-09-25'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Cruzeiro-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 29/09/2002 | Campeonato Brasileiro Serie A | Portuguesa
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-09-29'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Portuguesa' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 05/10/2002 | Campeonato Brasileiro Serie A | Guarani-SP
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-10-05'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Guarani-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 12/10/2002 | Campeonato Brasileiro Serie A | São Caetano-SP
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-10-12'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Caetano-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 16/10/2002 | Campeonato Brasileiro Serie A | Flamengo-RJ
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-10-16'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 19/10/2002 | Campeonato Brasileiro Serie A | Paraná-PR
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-10-19'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Paraná-PR' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 23/10/2002 | Campeonato Brasileiro Serie A | Bahia-BA
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-10-23'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bahia-BA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 31/10/2002 | Campeonato Brasileiro Serie A | Fluminense-RJ
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-10-31'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 03/11/2002 | Campeonato Brasileiro Serie A | Palmeiras-SP
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-11-03'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 06/11/2002 | Campeonato Brasileiro Serie A | São Paulo-SP
UPDATE matches
SET     match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-11-06'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Paulo-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 09/11/2002 | Campeonato Brasileiro Serie A | Vitória-BA
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-11-09'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Vitória-BA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 13/11/2002 | Campeonato Brasileiro Serie A | Ponte Preta-SP
UPDATE matches
SET     match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-11-13'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Ponte Preta-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 17/11/2002 | Campeonato Brasileiro Serie A | Corinthians
UPDATE matches
SET     match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2002-11-17'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Corinthians' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

SELECT COUNT(*) AS jogos_temporada_2002_com_horario
FROM matches
WHERE date_iso >= '2002-01-01' AND date_iso < '2003-01-01'
  AND match_time <> '';

COMMIT;
