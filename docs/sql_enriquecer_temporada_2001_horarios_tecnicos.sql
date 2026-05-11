-- Enriquecimento revisável da temporada 2001: horários e técnicos.
-- Gerado por scripts/audit_temporada_2001.py.
-- Fontes: páginas NetVasco por competição e fichas detalhadas dos amistosos.
-- Não aplique direto em PRD sem testar numa cópia.

BEGIN TRANSACTION;

-- 17/01/2001 | Torneio Rio-São Paulo | São Paulo-SP
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-01-17'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Paulo-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 21/01/2001 | Campeonato Carioca | Madureira-RJ
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-01-21'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Madureira-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 24/01/2001 | Torneio Rio-São Paulo | Palmeiras-SP
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-01-24'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 27/01/2001 | Campeonato Carioca | Friburguense
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-01-27'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Friburguense' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 31/01/2001 | Torneio Rio-São Paulo | Corinthians
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-01-31'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Corinthians' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 03/02/2001 | Campeonato Carioca | América
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-02-03'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'América' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 07/02/2001 | Torneio Rio-São Paulo | Santos
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-02-07'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Santos' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 11/02/2001 | Campeonato Carioca | Fluminense-RJ
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-02-11'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 17/02/2001 | Campeonato Carioca | Cabofriense-RJ
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-02-17'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Cabofriense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 22/02/2001 | Campeonato Carioca | Flamengo-RJ
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-02-22'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 11/03/2001 | Campeonato Carioca | Cabofriense-RJ
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-03-11'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Cabofriense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 14/03/2001 | Copa Libertadores | América Cáli
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-03-14'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'América Cáli' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Libertadores' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 17/03/2001 | Campeonato Carioca | Olaria-RJ
UPDATE matches
SET match_time = '18:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-03-17'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Olaria-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 21/03/2001 | Copa Libertadores | Dep. Táchira
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-03-21'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Dep. Táchira' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Libertadores' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 30/03/2001 | Campeonato Carioca | Madureira-RJ
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-03-30'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Madureira-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 02/04/2001 | Campeonato Carioca | V. Redonda
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-04-02'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'V. Redonda' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 05/04/2001 | Copa Libertadores | Peñarol
UPDATE matches
SET match_time = '20:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-04-05'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Peñarol' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Libertadores' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 08/04/2001 | Campeonato Carioca | Americano-RJ
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-04-08'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Americano-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 12/04/2001 | Copa Libertadores | América Cáli
UPDATE matches
SET match_time = '21:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-04-12'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'América Cáli' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Libertadores' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 15/04/2001 | Campeonato Carioca | Fluminense-RJ
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-04-15'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 18/04/2001 | Campeonato Carioca | Friburguense
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-04-18'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Friburguense' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 21/04/2001 | Copa Libertadores | Dep. Táchira
UPDATE matches
SET match_time = '18:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-04-21'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Dep. Táchira' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Libertadores' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 26/04/2001 | Campeonato Carioca | Bangu-RJ
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-04-26'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bangu-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 29/04/2001 | Campeonato Carioca | Botafogo
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-04-29'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Botafogo' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 02/05/2001 | Copa Libertadores | Peñarol
UPDATE matches
SET match_time = '21:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-05-02'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Peñarol' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Libertadores' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 05/05/2001 | Campeonato Carioca | América
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-05-05'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'América' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 09/05/2001 | Copa Libertadores | Dep. Concepción
UPDATE matches
SET match_time = '19:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-05-09'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Dep. Concepción' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Libertadores' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 13/05/2001 | Campeonato Carioca | Flamengo-RJ
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-05-13'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 16/05/2001 | Copa Libertadores | Dep. Concepción
UPDATE matches
SET match_time = '21:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-05-16'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Dep. Concepción' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Libertadores' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 20/05/2001 | Campeonato Carioca | Flamengo-RJ
UPDATE matches
SET match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-05-20'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 23/05/2001 | Copa Libertadores | Boca Juniors
UPDATE matches
SET match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-05-23'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Boca Juniors' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Libertadores' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 27/05/2001 | Campeonato Carioca | Flamengo-RJ
UPDATE matches
SET match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-05-27'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 30/05/2001 | Copa Libertadores | Boca Juniors
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-05-30'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Boca Juniors' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Libertadores' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 08/07/2001 | Amistoso | León
UPDATE matches
SET match_time = '18:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-07-08'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'León' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Amistoso' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 10/07/2001 | Amistoso | Tigres
UPDATE matches
SET match_time = '22:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-07-10'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Tigres' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Amistoso' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 24/07/2001 | Copa Mercosul | U. Católica
UPDATE matches
SET match_time = '19:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-07-24'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'U. Católica' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 29/07/2001 | Copa Mercosul | Boca Juniors
UPDATE matches
SET match_time = '15:10',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-07-29'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Boca Juniors' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 01/08/2001 | Campeonato Brasileiro Serie A | Gama-DF
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-08-01'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Gama-DF' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 05/08/2001 | Campeonato Brasileiro Serie A | Guarani-SP
UPDATE matches
SET match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-08-05'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Guarani-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 08/08/2001 | Campeonato Brasileiro Serie A | Coritiba-PR
UPDATE matches
SET match_time = '21:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-08-08'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Coritiba-PR' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 11/08/2001 | Campeonato Brasileiro Serie A | Juventude-RS
UPDATE matches
SET match_time = '14:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-08-11'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Juventude-RS' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 15/08/2001 | Campeonato Brasileiro Serie A | Vitória-BA
UPDATE matches
SET match_time = '18:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-08-15'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Vitória-BA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 18/08/2001 | Campeonato Brasileiro Serie A | Santa Cruz-PE
UPDATE matches
SET match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-08-18'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Santa Cruz-PE' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 21/08/2001 | Copa Mercosul | C. Porteño
UPDATE matches
SET match_time = '22:10',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-08-21'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'C. Porteño' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 26/08/2001 | Campeonato Brasileiro Serie A | Atlético-PR
UPDATE matches
SET match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-08-26'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Atlético-PR' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 29/08/2001 | Campeonato Brasileiro Serie A | América-MG
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-08-29'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'América-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 02/09/2001 | Campeonato Brasileiro Serie A | Botafogo-SP
UPDATE matches
SET match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-09-02'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Botafogo-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 09/09/2001 | Campeonato Brasileiro Serie A | Sport-PE
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-09-09'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Sport-PE' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 13/09/2001 | Copa Mercosul | U. Católica
UPDATE matches
SET match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-09-13'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'U. Católica' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 16/09/2001 | Campeonato Brasileiro Serie A | Bahia-BA
UPDATE matches
SET match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-09-16'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bahia-BA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 19/09/2001 | Campeonato Brasileiro Serie A | Paraná-PR
UPDATE matches
SET match_time = '21:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-09-19'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Paraná-PR' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 22/09/2001 | Campeonato Brasileiro Serie A | Goiás-GO
UPDATE matches
SET match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-09-22'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Goiás-GO' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 25/09/2001 | Copa Mercosul | Boca Juniors
UPDATE matches
SET match_time = '21:10',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-09-25'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Boca Juniors' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 30/09/2001 | Campeonato Brasileiro Serie A | Ponte Preta-SP
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-09-30'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Ponte Preta-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 03/10/2001 | Campeonato Brasileiro Serie A | Cruzeiro-MG
UPDATE matches
SET match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-10-03'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Cruzeiro-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 06/10/2001 | Campeonato Brasileiro Serie A | Flamengo-RJ
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-10-06'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 10/10/2001 | Campeonato Brasileiro Serie A | Inter-RS
UPDATE matches
SET match_time = '21:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-10-10'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Inter-RS' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 13/10/2001 | Campeonato Brasileiro Serie A | Botafogo-RJ
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-10-13'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Botafogo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 17/10/2001 | Copa Mercosul | C. Porteño
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-10-17'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'C. Porteño' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 20/10/2001 | Campeonato Brasileiro Serie A | São Caetano-SP
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-10-20'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Caetano-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 28/10/2001 | Campeonato Brasileiro Serie A | Fluminense-RJ
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-10-28'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 04/11/2001 | Campeonato Brasileiro Serie A | Portuguesa
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-11-04'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Portuguesa' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 08/11/2001 | Campeonato Brasileiro Serie A | Corinthians
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-11-08'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Corinthians' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 11/11/2001 | Campeonato Brasileiro Serie A | Atlético-MG
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-11-11'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Atlético-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 15/11/2001 | Campeonato Brasileiro Serie A | Grêmio-RS
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-11-15'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Grêmio-RS' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 18/11/2001 | Campeonato Brasileiro Serie A | Palmeiras-SP
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-11-18'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 25/11/2001 | Campeonato Brasileiro Serie A | São Paulo-SP
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-11-25'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Paulo-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

-- 02/12/2001 | Campeonato Brasileiro Serie A | Santos
UPDATE matches
SET match_time = '15:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Hélio dos Anjos' LIMIT 1)
WHERE date_iso = '2001-12-02'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Santos' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Hélio dos Anjos');

SELECT COUNT(*) AS jogos_temporada_2001_com_horario
FROM matches
WHERE date_iso >= '2001-01-01' AND date_iso < '2002-01-01'
  AND date_iso <> '2001-01-18'
  AND match_time <> '';

COMMIT;
