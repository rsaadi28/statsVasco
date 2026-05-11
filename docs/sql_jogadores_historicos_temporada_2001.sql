-- Cadastro histórico mínimo de jogadores citados nas fichas de 2001 e ausentes no banco auditado.
--
-- Não aplique direto em PRD sem testar numa cópia.
--
-- Detectados ao preparar os amistosos México 2001:
-- - Valdo: citado como substituto contra León; observação da ficha diz ser zagueiro, ex-Rio Branco-MG.
-- - William: titular contra León e Tigres; a ficha confirma nome, mas não traz dados pessoais.
--
-- Alexandre Torres aparece nas fontes como nome completo, mas o banco já possui `Torres`.
-- Por isso, não há inserção automática para evitar duplicidade de alias.

BEGIN TRANSACTION;

INSERT OR IGNORE INTO players(name) VALUES ('Valdo');
INSERT OR IGNORE INTO players(name) VALUES ('William');

INSERT OR IGNORE INTO historic_players(player_id, position, registered_date_text, joined_date_text, left_date_text, passages_json, matches_played_for_vasco)
SELECT id, 'Zagueiro', '', '', '', '[]', NULL
FROM players
WHERE name = 'Valdo';

INSERT OR IGNORE INTO historic_players(player_id, position, registered_date_text, joined_date_text, left_date_text, passages_json, matches_played_for_vasco)
SELECT id, '', '', '', '', '[]', NULL
FROM players
WHERE name = 'William';

INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('jogadores_vasco', 'Valdo');
INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('jogadores_vasco', 'William');

SELECT p.id, p.name, hp.position
FROM players p
LEFT JOIN historic_players hp ON hp.player_id = p.id
WHERE p.name IN ('Valdo', 'William')
ORDER BY p.name;

COMMIT;
