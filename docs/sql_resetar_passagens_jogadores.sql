-- Reseta as datas/passagens do histórico dos jogadores para recomeçar a contagem a partir de hoje.
--
-- Efeito:
-- - Jogadores no elenco atual:
--   ficam com uma passagem aberta iniciando hoje
-- - Jogadores fora do elenco:
--   ficam com uma passagem fechada hoje-hoje
--
-- Isso não apaga jogos, só redefine o recorte temporal usado nos detalhes do jogador.
--
-- Banco em desenvolvimento local:
--   /Users/rodrigo/Documents/pessoal/Sistemas/stats_vasco/stats_vasco.sqlite3
--
-- Banco no app empacotado no macOS:
--   ~/Library/Application Support/StatsVasco/stats_vasco.sqlite3

BEGIN TRANSACTION;

UPDATE historic_players
SET
    registered_date_text = strftime('%d/%m/%Y', 'now', 'localtime'),
    joined_date_text = strftime('%d/%m/%Y', 'now', 'localtime'),
    left_date_text = CASE
        WHEN player_id IN (SELECT player_id FROM current_squad) THEN ''
        ELSE strftime('%d/%m/%Y', 'now', 'localtime')
    END,
    passages_json = CASE
        WHEN player_id IN (SELECT player_id FROM current_squad) THEN
            json_array(
                json_object(
                    'data_entrada', strftime('%d/%m/%Y', 'now', 'localtime'),
                    'data_saida', ''
                )
            )
        ELSE
            json_array(
                json_object(
                    'data_entrada', strftime('%d/%m/%Y', 'now', 'localtime'),
                    'data_saida', strftime('%d/%m/%Y', 'now', 'localtime')
                )
            )
    END;

COMMIT;

-- Conferência rápida:
SELECT
    h.player_id,
    p.name,
    h.joined_date_text,
    h.left_date_text,
    h.passages_json
FROM historic_players h
JOIN players p ON p.id = h.player_id
ORDER BY p.name
LIMIT 50;
