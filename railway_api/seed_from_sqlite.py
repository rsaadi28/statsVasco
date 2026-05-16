from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storage_sqlite import (  # noqa: E402
    bootstrap_database,
    db_path_for,
    load_current_squad,
    load_future_matches,
    load_historic_players,
    load_matches,
)

from railway_api.state import replace_state  # noqa: E402


def main() -> None:
    db_path = Path(db_path_for(str(ROOT))).resolve()
    bootstrap_database(str(db_path))
    state = {
        "matches": load_matches(str(db_path)),
        "future_matches": load_future_matches(str(db_path)),
        "current_squad": load_current_squad(str(db_path)),
        "historic_players": load_historic_players(str(db_path)),
    }
    replace_state(state)
    print(
        "Seed concluído: "
        f"{len(state['matches'])} jogos, "
        f"{len(state['future_matches'])} futuros, "
        f"{len(state['current_squad'].get('jogadores', []))} jogadores no elenco."
    )


if __name__ == "__main__":
    main()
