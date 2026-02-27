# Diagrama de Relacionamentos (SQLite)

```mermaid
erDiagram
    teams ||--o{ matches : "adversario"
    competitions ||--o{ matches : "competicao"
    coaches ||--o{ matches : "tecnico"

    matches ||--o{ match_goals : "gols"
    players ||--o{ match_goals : "autor"

    competitions ||--o{ future_matches : "campeonato"
    teams ||--o{ future_matches : "adversario"

    players ||--o| current_squad : "elenco_atual"
    players ||--o| historic_players : "historico"

    settings {
        text key PK
        text value
    }

    list_entries {
        text list_type PK
        text value PK
    }

    teams {
        int id PK
        text name UK
        text team_type
    }

    players {
        int id PK
        text name UK
    }

    coaches {
        int id PK
        text name UK
    }

    competitions {
        int id PK
        text name UK
    }

    matches {
        int id PK
        text date_text
        text date_iso
        int opponent_team_id FK
        int competition_id FK
        text location
        int vasco_goals
        int opponent_goals
        text observation
        int coach_id FK
        int table_position
        text lineup_json
    }

    match_goals {
        int id PK
        int match_id FK
        text side
        int player_id FK
        text player_name
        int goals
        text club_name
        int is_disallowed
    }

    future_matches {
        int id PK
        text date_text
        text date_iso
        text match_text
        int is_home
        int competition_id FK
        int opponent_team_id FK
    }

    current_squad {
        int player_id PK, FK
        text position
        text condition
    }

    historic_players {
        int player_id PK, FK
        text position
    }
```

## Observações
- A tabela `list_entries` preserva as listas auxiliares do app (clubes, jogadores, competições e técnicos).
- `settings` guarda configurações globais, como `tecnico_atual` e `elenco_tecnico`.
- `lineup_json` mantém a estrutura de escalação atual sem perda de compatibilidade com a UI existente.
