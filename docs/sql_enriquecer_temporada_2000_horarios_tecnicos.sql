-- Enriquecimento revisável da temporada 2000: horários e técnicos.
-- Gerado por scripts/audit_temporada_2000.py.
-- Fontes: páginas NetVasco por competição, Vaskipédia, Folha de Londrina, SuperVasco e fichas de finais.

BEGIN TRANSACTION;

-- 03/01/2000 | Amistoso | Sel. Argélia
UPDATE matches
SET match_time = '20:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2000-01-03'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Sel. Argélia' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Amistoso' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 06/01/2000 | Mundial de Clubes | South Melbourne
UPDATE matches
SET match_time = '20:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2000-01-06'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'South Melbourne' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Mundial de Clubes' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 08/01/2000 | Mundial de Clubes | Manchester United
UPDATE matches
SET match_time = '18:15',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2000-01-08'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Manchester United' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Mundial de Clubes' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 11/01/2000 | Mundial de Clubes | Necaxa
UPDATE matches
SET match_time = '20:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2000-01-11'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Necaxa' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Mundial de Clubes' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 14/01/2000 | Mundial de Clubes | Corinthians
UPDATE matches
SET match_time = '20:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2000-01-14'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Corinthians' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Mundial de Clubes' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 23/01/2000 | Torneio Rio-São Paulo | Palmeiras-SP
UPDATE matches
SET match_time = '19:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Alcir Portela' LIMIT 1)
WHERE date_iso = '2000-01-23'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Alcir Portela');

-- 27/01/2000 | Torneio Rio-São Paulo | Fluminense-RJ
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Alcir Portela' LIMIT 1)
WHERE date_iso = '2000-01-27'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Alcir Portela');

-- 30/01/2000 | Torneio Rio-São Paulo | Corinthians
UPDATE matches
SET match_time = '19:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Alcir Portela' LIMIT 1)
WHERE date_iso = '2000-01-30'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Corinthians' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Alcir Portela');

-- 05/02/2000 | Torneio Rio-São Paulo | Palmeiras-SP
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Alcir Portela' LIMIT 1)
WHERE date_iso = '2000-02-05'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Alcir Portela');

-- 09/02/2000 | Torneio Rio-São Paulo | Fluminense-RJ
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Alcir Portela' LIMIT 1)
WHERE date_iso = '2000-02-09'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Alcir Portela');

-- 13/02/2000 | Torneio Rio-São Paulo | Corinthians
UPDATE matches
SET match_time = '18:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Alcir Portela' LIMIT 1)
WHERE date_iso = '2000-02-13'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Corinthians' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Alcir Portela');

-- 19/02/2000 | Torneio Rio-São Paulo | São Paulo-SP
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2000-02-19'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Paulo-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 23/02/2000 | Torneio Rio-São Paulo | São Paulo-SP
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2000-02-23'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Paulo-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 26/02/2000 | Torneio Rio-São Paulo | Palmeiras-SP
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2000-02-26'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 01/03/2000 | Torneio Rio-São Paulo | Palmeiras-SP
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso = '2000-03-01'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- 12/03/2000 | Campeonato Carioca | Madureira-RJ
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-03-12'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Madureira-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 15/03/2000 | Copa do Brasil | Botafogo-PB
UPDATE matches
SET match_time = '15:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-03-15'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Botafogo-PB' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa do Brasil' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 18/03/2000 | Campeonato Carioca | Bangu-RJ
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-03-18'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bangu-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 22/03/2000 | Campeonato Carioca | Friburguense
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-03-22'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Friburguense' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 25/03/2000 | Campeonato Carioca | Americano-RJ
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-03-25'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Americano-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 29/03/2000 | Campeonato Carioca | Olaria-RJ
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-03-29'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Olaria-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 02/04/2000 | Campeonato Carioca | Fluminense-RJ
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-04-02'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 09/04/2000 | Campeonato Carioca | Botafogo
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-04-09'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Botafogo' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 12/04/2000 | Campeonato Carioca | V. Redonda
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-04-12'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'V. Redonda' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 15/04/2000 | Campeonato Carioca | América
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-04-15'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'América' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 19/04/2000 | Campeonato Carioca | Cabo Frio
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-04-19'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Cabo Frio' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 23/04/2000 | Campeonato Carioca | Flamengo-RJ
UPDATE matches
SET match_time = '18:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-04-23'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 27/04/2000 | Copa do Brasil | Ponte Preta-SP
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-04-27'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Ponte Preta-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa do Brasil' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 30/04/2000 | Campeonato Carioca | Madureira-RJ
UPDATE matches
SET match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-04-30'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Madureira-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 03/05/2000 | Copa do Brasil | Ponte Preta-SP
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-05-03'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Ponte Preta-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa do Brasil' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 06/05/2000 | Campeonato Carioca | América
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-05-06'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'América' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 10/05/2000 | Campeonato Carioca | Americano-RJ
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-05-10'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Americano-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 13/05/2000 | Campeonato Carioca | Olaria-RJ
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-05-13'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Olaria-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 17/05/2000 | Campeonato Carioca | Bangu-RJ
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-05-17'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bangu-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 21/05/2000 | Campeonato Carioca | Fluminense-RJ
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-05-21'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 24/05/2000 | Copa do Brasil | Fluminense-RJ
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-05-24'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa do Brasil' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 28/05/2000 | Campeonato Carioca | Flamengo-RJ
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-05-28'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 31/05/2000 | Copa do Brasil | Fluminense-RJ
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Abel Braga' LIMIT 1)
WHERE date_iso = '2000-05-31'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa do Brasil' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Abel Braga');

-- 04/06/2000 | Campeonato Carioca | Friburguense
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Alcir Portela' LIMIT 1)
WHERE date_iso = '2000-06-04'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Friburguense' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Alcir Portela');

-- 07/06/2000 | Campeonato Carioca | Botafogo
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Alcir Portela' LIMIT 1)
WHERE date_iso = '2000-06-07'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Botafogo' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Alcir Portela');

-- 11/06/2000 | Campeonato Carioca | Flamengo-RJ
UPDATE matches
SET match_time = '18:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Alcir Portela' LIMIT 1)
WHERE date_iso = '2000-06-11'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Alcir Portela');

-- 17/06/2000 | Campeonato Carioca | Flamengo-RJ
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Tita' LIMIT 1)
WHERE date_iso = '2000-06-17'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Carioca' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Tita');

-- 30/06/2000 | Amistoso | Rio Branco
UPDATE matches
SET match_time = '21:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Tita' LIMIT 1)
WHERE date_iso = '2000-06-30'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Rio Branco' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Amistoso' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Tita');

-- 22/07/2000 | Amistoso | São Cristóvão
UPDATE matches
SET match_time = '15:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-07-22'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Cristóvão' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Amistoso' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 29/07/2000 | Campeonato Brasileiro Serie A | Sport-PE
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-07-29'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Sport-PE' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 01/08/2000 | Copa Mercosul | Peñarol
UPDATE matches
SET match_time = '19:15',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-08-01'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Peñarol' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 06/08/2000 | Campeonato Brasileiro Serie A | Cruzeiro-MG
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-08-06'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Cruzeiro-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 11/08/2000 | Campeonato Brasileiro Serie A | Corinthians
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-08-11'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Corinthians' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 13/08/2000 | Campeonato Brasileiro Serie A | Guarani-SP
UPDATE matches
SET match_time = '18:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-08-13'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Guarani-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 16/08/2000 | Campeonato Brasileiro Serie A | Santa Cruz-PE
UPDATE matches
SET match_time = '22:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-08-16'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Santa Cruz-PE' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 20/08/2000 | Campeonato Brasileiro Serie A | Ponte Preta-SP
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-08-20'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Ponte Preta-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 24/08/2000 | Copa Mercosul | San Lorenzo
UPDATE matches
SET match_time = '19:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-08-24'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'San Lorenzo' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 27/08/2000 | Campeonato Brasileiro Serie A | Portuguesa
UPDATE matches
SET match_time = '18:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-08-27'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Portuguesa' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 31/08/2000 | Copa Mercosul | Atlético-MG
UPDATE matches
SET match_time = '21:15',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-08-31'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Atlético-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 05/09/2000 | Campeonato Brasileiro Serie A | Atlético-PR
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-09-05'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Atlético-PR' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 07/09/2000 | Copa Mercosul | Peñarol
UPDATE matches
SET match_time = '15:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-09-07'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Peñarol' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 10/09/2000 | Campeonato Brasileiro Serie A | Bahia-BA
UPDATE matches
SET match_time = '18:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-09-10'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bahia-BA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 13/09/2000 | Campeonato Brasileiro Serie A | Fluminense-RJ
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-09-13'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Fluminense-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 20/09/2000 | Campeonato Brasileiro Serie A | América-MG
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-09-20'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'América-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 24/09/2000 | Campeonato Brasileiro Serie A | Juventude-RS
UPDATE matches
SET match_time = '18:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-09-24'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Juventude-RS' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 28/09/2000 | Copa Mercosul | San Lorenzo
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-09-28'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'San Lorenzo' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 04/10/2000 | Campeonato Brasileiro Serie A | Atlético-MG
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-10-04'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Atlético-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 11/10/2000 | Campeonato Brasileiro Serie A | Vitória-BA
UPDATE matches
SET match_time = '22:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-10-11'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Vitória-BA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 14/10/2000 | Campeonato Brasileiro Serie A | Santos
UPDATE matches
SET match_time = '15:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-10-14'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Santos' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 17/10/2000 | Copa Mercosul | Atlético-MG
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-10-17'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Atlético-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 21/10/2000 | Campeonato Brasileiro Serie A | Gama-DF
UPDATE matches
SET match_time = '18:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-10-21'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Gama-DF' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 24/10/2000 | Campeonato Brasileiro Serie A | Goiás-GO
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-10-24'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Goiás-GO' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 27/10/2000 | Campeonato Brasileiro Serie A | Flamengo-RJ
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-10-27'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Flamengo-RJ' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 31/10/2000 | Copa Mercosul | R. Central
UPDATE matches
SET match_time = '19:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-10-31'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'R. Central' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 03/11/2000 | Campeonato Brasileiro Serie A | Coritiba-PR
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-11-03'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Coritiba-PR' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 05/11/2000 | Campeonato Brasileiro Serie A | Internacional-RS
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-11-05'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Internacional-RS' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 08/11/2000 | Copa Mercosul | R. Central
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-11-08'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'R. Central' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 10/11/2000 | Campeonato Brasileiro Serie A | Palmeiras-SP
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-11-10'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 12/11/2000 | Campeonato Brasileiro Serie A | Botafogo
UPDATE matches
SET match_time = '17:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-11-12'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Botafogo' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 16/11/2000 | Campeonato Brasileiro Serie A | Grêmio-RS
UPDATE matches
SET match_time = '20:30',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-11-16'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Grêmio-RS' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 19/11/2000 | Campeonato Brasileiro Serie A | São Paulo-SP
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-11-19'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Paulo-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 22/11/2000 | Copa Mercosul | River Plate
UPDATE matches
SET match_time = '22:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-11-22'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'River Plate' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 25/11/2000 | Campeonato Brasileiro Serie A | Bahia-BA
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-11-25'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bahia-BA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 28/11/2000 | Campeonato Brasileiro Serie A | Bahia-BA
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-11-28'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Bahia-BA' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 30/11/2000 | Copa Mercosul | River Plate
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-11-30'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'River Plate' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 03/12/2000 | Campeonato Brasileiro Serie A | Paraná-PR
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-12-03'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Paraná-PR' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 06/12/2000 | Copa Mercosul | Palmeiras-SP
UPDATE matches
SET match_time = '21:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-12-06'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 09/12/2000 | Campeonato Brasileiro Serie A | Paraná-PR
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-12-09'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Paraná-PR' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 12/12/2000 | Copa Mercosul | Palmeiras-SP
UPDATE matches
SET match_time = '21:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-12-12'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 16/12/2000 | Campeonato Brasileiro Serie A | Cruzeiro-MG
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Oswaldo de Oliveira' LIMIT 1)
WHERE date_iso = '2000-12-16'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Cruzeiro-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Oswaldo de Oliveira');

-- 20/12/2000 | Copa Mercosul | Palmeiras-SP
UPDATE matches
SET match_time = '21:45',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2000-12-20'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Palmeiras-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Copa Mercosul' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 23/12/2000 | Campeonato Brasileiro Serie A | Cruzeiro-MG
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2000-12-23'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'Cruzeiro-MG' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 27/12/2000 | Campeonato Brasileiro Serie A | São Caetano-SP
UPDATE matches
SET match_time = '21:40',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2000-12-27'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Caetano-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

-- 18/01/2001 | Campeonato Brasileiro Serie A | São Caetano-SP
UPDATE matches
SET match_time = '16:00',
    coach_id = (SELECT id FROM coaches WHERE name = 'Joel Santana' LIMIT 1)
WHERE date_iso = '2001-01-18'
  AND opponent_team_id = (SELECT id FROM teams WHERE name = 'São Caetano-SP' LIMIT 1)
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Campeonato Brasileiro Serie A' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Joel Santana');

SELECT COUNT(*) AS jogos_temporada_2000_com_horario
FROM matches
WHERE ((date_iso >= '2000-01-01' AND date_iso < '2001-01-01') OR date_iso = '2001-01-18')
  AND match_time <> '';

COMMIT;
