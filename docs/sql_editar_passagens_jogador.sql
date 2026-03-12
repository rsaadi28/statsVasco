-- Ajuste manual de entrada/saida/passagens de jogador no SQLite
--
-- Como usar:
-- 1) Abra este arquivo e troque os valores marcados com TROCAR_*.
-- 2) Execute no banco do app com sqlite3.
--
-- Banco em desenvolvimento local:
--   /Users/rodrigo/Documents/pessoal/Sistemas/stats_vasco/stats_vasco.sqlite3
--
-- Banco no app empacotado no macOS:
--   ~/Library/Application Support/StatsVasco/stats_vasco.sqlite3

-- ------------------------------------------------------------
-- 1) Descobrir o ID do jogador
-- ------------------------------------------------------------
SELECT
    h.player_id,
    p.name,
    h.joined_date_text,
    h.left_date_text,
    h.passages_json
FROM historic_players h
JOIN players p ON p.id = h.player_id
WHERE lower(p.name) LIKE lower('%TROCAR_NOME_DO_JOGADOR%')
ORDER BY p.name;

-- ------------------------------------------------------------
-- 2) Conferir o registro atual por ID
-- ------------------------------------------------------------
SELECT
    h.player_id,
    p.name,
    h.joined_date_text,
    h.left_date_text,
    h.passages_json
FROM historic_players h
JOIN players p ON p.id = h.player_id
WHERE h.player_id = TROCAR_PLAYER_ID;

-- ------------------------------------------------------------
-- 3) Atualizar datas e passagens do jogador
--
-- Regras:
-- - joined_date_text: resumo da primeira entrada
-- - left_date_text: resumo da saida atual/final
--   Use '' se o jogador ainda estiver no elenco
-- - passages_json: lista completa das passagens
--   Cada item precisa ter:
--     {"data_entrada":"DD/MM/AAAA","data_saida":"DD/MM/AAAA ou vazio"}
-- ------------------------------------------------------------
BEGIN TRANSACTION;

UPDATE historic_players
SET
    joined_date_text = 'TROCAR_PRIMEIRA_ENTRADA',
    left_date_text = 'TROCAR_SAIDA_FINAL_OU_VAZIO',
    passages_json = json_array(
        json_object(
            'data_entrada', 'TROCAR_PASSAGEM_1_ENTRADA',
            'data_saida', 'TROCAR_PASSAGEM_1_SAIDA'
        ),
        json_object(
            'data_entrada', 'TROCAR_PASSAGEM_2_ENTRADA',
            'data_saida', 'TROCAR_PASSAGEM_2_SAIDA'
        )
    )
WHERE player_id = TROCAR_PLAYER_ID;

COMMIT;

-- ------------------------------------------------------------
-- 4) Conferir como ficou
-- ------------------------------------------------------------
SELECT
    h.player_id,
    p.name,
    h.joined_date_text,
    h.left_date_text,
    h.passages_json
FROM historic_players h
JOIN players p ON p.id = h.player_id
WHERE h.player_id = TROCAR_PLAYER_ID;

-- ------------------------------------------------------------
-- Exemplo preenchido
--
-- UPDATE historic_players
-- SET
--     joined_date_text = '10/01/2024',
--     left_date_text = '',
--     passages_json = json_array(
--         json_object(
--             'data_entrada', '10/01/2024',
--             'data_saida', '20/12/2024'
--         ),
--         json_object(
--             'data_entrada', '05/01/2025',
--             'data_saida', ''
--         )
--     )
-- WHERE player_id = 123;
