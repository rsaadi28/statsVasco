-- Auditoria temporada NetVasco 2000
-- Correções revisáveis para divergências confirmadas no núcleo da temporada 2000.
--
-- Fontes principais:
-- https://www.netvasco.com.br/n/379745/confira-os-jogos-do-vasco-na-historia-em-1-de-marco
-- https://www.folhadelondrina.com.br/esporte/lopes-reassume-o-comando-do-vasco-na-2-feira-258317.html
-- https://www.palmeiras.com.br/lightbox_galeria/torneio-rio-sao-paulo-2000/
--
-- Aplique primeiro em uma cópia do banco e rode:
-- python3 scripts/audit_temporada_2000.py --db /caminho/da/copia.sqlite3

BEGIN TRANSACTION;

-- Conferência antes da alteração.
SELECT m.id,
       m.date_text,
       t.name AS adversario,
       c.name AS competicao,
       m.location,
       m.vasco_goals,
       m.opponent_goals
FROM matches m
LEFT JOIN teams t ON t.id = m.opponent_team_id
LEFT JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2000-03-01'
  AND t.name = 'Palmeiras-SP'
  AND c.name = 'Torneio Rio-São Paulo';

-- Placar correto pela fonte: Vasco 0 x 4 Palmeiras-SP.
UPDATE matches
SET vasco_goals = 0,
    opponent_goals = 4
WHERE id IN (
    SELECT m.id
    FROM matches m
    LEFT JOIN teams t ON t.id = m.opponent_team_id
    LEFT JOIN competitions c ON c.id = m.competition_id
    WHERE m.date_iso = '2000-03-01'
      AND t.name = 'Palmeiras-SP'
      AND c.name = 'Torneio Rio-São Paulo'
);

-- Remove o registro incorreto "Gol contra: 4" para o Vasco.
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
  AND side = 'vasco'
  AND is_disallowed = 0
  AND player_name = 'Gol contra'
  AND goals = 4;

-- Conferência depois da alteração.
SELECT m.id,
       m.date_text,
       t.name AS adversario,
       c.name AS competicao,
       m.location,
       m.vasco_goals,
       m.opponent_goals
FROM matches m
LEFT JOIN teams t ON t.id = m.opponent_team_id
LEFT JOIN competitions c ON c.id = m.competition_id
WHERE m.date_iso = '2000-03-01'
  AND t.name = 'Palmeiras-SP'
  AND c.name = 'Torneio Rio-São Paulo';

-- Técnico confirmado para a reta final do Rio-São Paulo: Antônio Lopes.
-- O banco atual registra Alcir Portela nos 10 jogos do torneio, mas as fontes
-- indicam Alcir nos 6 primeiros jogos e Antônio Lopes nos 4 finais.
UPDATE matches
SET coach_id = (SELECT id FROM coaches WHERE name = 'Antônio Lopes' LIMIT 1)
WHERE date_iso IN ('2000-02-19', '2000-02-23', '2000-02-26', '2000-03-01')
  AND competition_id = (SELECT id FROM competitions WHERE name = 'Torneio Rio-São Paulo' LIMIT 1)
  AND EXISTS (SELECT 1 FROM coaches WHERE name = 'Antônio Lopes');

-- Conferência dos técnicos após a alteração.
SELECT m.id,
       m.date_text,
       t.name AS adversario,
       c.name AS competicao,
       ch.name AS tecnico
FROM matches m
LEFT JOIN teams t ON t.id = m.opponent_team_id
LEFT JOIN competitions c ON c.id = m.competition_id
LEFT JOIN coaches ch ON ch.id = m.coach_id
WHERE m.date_iso IN ('2000-02-19', '2000-02-23', '2000-02-26', '2000-03-01')
  AND c.name = 'Torneio Rio-São Paulo'
ORDER BY m.date_iso;

COMMIT;
