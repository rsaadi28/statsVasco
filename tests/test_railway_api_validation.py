from __future__ import annotations

import importlib.util
import sys
import types
import unittest


if importlib.util.find_spec("fastapi") is None:
    fastapi = types.ModuleType("fastapi")

    class FastAPI:
        def __init__(self, **_kwargs):
            pass

        def add_middleware(self, *_args, **_kwargs):
            pass

        def _route(self, *_args, **_kwargs):
            return lambda function: function

        get = post = on_event = _route

    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    fastapi.FastAPI = FastAPI
    fastapi.Header = lambda default=None: default
    fastapi.HTTPException = HTTPException
    fastapi.Request = object
    middleware = types.ModuleType("fastapi.middleware")
    cors = types.ModuleType("fastapi.middleware.cors")
    cors.CORSMiddleware = object
    responses = types.ModuleType("fastapi.responses")
    responses.JSONResponse = responses.Response = object
    sys.modules.update(
        {
            "fastapi": fastapi,
            "fastapi.middleware": middleware,
            "fastapi.middleware.cors": cors,
            "fastapi.responses": responses,
        }
    )

if importlib.util.find_spec("psycopg") is None:
    psycopg = types.ModuleType("psycopg")
    psycopg.connect = lambda *_args, **_kwargs: None
    psycopg.types = types.SimpleNamespace(json=types.SimpleNamespace(Jsonb=object))
    rows = types.ModuleType("psycopg.rows")
    rows.dict_row = object()
    sys.modules.update({"psycopg": psycopg, "psycopg.rows": rows})

from railway_api.app import (
    apply_current_squad_patch,
    validate_current_squad_patch,
    validate_partial_state_payload,
)


class PartialStateValidationTests(unittest.TestCase):
    def test_accepts_future_matches_without_matches(self) -> None:
        result = validate_partial_state_payload(
            {
                "future_matches": [
                    {
                        "jogo": "Vasco x Bahia",
                        "data": "10/09/2026",
                        "em_casa": True,
                        "estadio": "São Januário",
                        "horario": "19:00",
                        "competicao": "Brasileirão Série A",
                    }
                ]
            }
        )

        self.assertEqual(set(result), {"future_matches"})
        self.assertEqual(result["future_matches"][0]["local"], "São Januário")
        self.assertEqual(result["future_matches"][0]["hora"], "19:00")

    def test_accepts_squad_and_historic_players_together(self) -> None:
        result = validate_partial_state_payload(
            {
                "state": {
                    "current_squad": {
                        "tecnico": "Técnico",
                        "jogadores": [
                            {
                                "nome": "Jogador",
                                "posicao": "Atacante",
                                "condicao": "Lesionado",
                                "capitao": True,
                            }
                        ],
                    },
                    "historic_players": {
                        "jogadores": [{"nome": "Ex-jogador", "posicao": "Zagueiro"}]
                    },
                }
            }
        )

        self.assertEqual(set(result), {"current_squad", "historic_players"})
        self.assertTrue(result["current_squad"]["jogadores"][0]["capitao"])

    def test_rejects_empty_or_matches_only_payload(self) -> None:
        with self.assertRaisesRegex(ValueError, "Informe ao menos"):
            validate_partial_state_payload({})
        with self.assertRaisesRegex(ValueError, "Informe ao menos"):
            validate_partial_state_payload({"matches": []})

    def test_rejects_non_list_future_matches(self) -> None:
        with self.assertRaisesRegex(ValueError, "future_matches precisa ser lista"):
            validate_partial_state_payload({"future_matches": {}})


class CurrentSquadPatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.current = {
            "jogadores": [
                {
                    "nome": "Jogador A",
                    "posicao": "Atacante",
                    "condicao": "Titular",
                    "capitao": False,
                    "campo_legado": "preservar",
                },
                {
                    "nome": "Jogador B",
                    "posicao": "Goleiro",
                    "condicao": "Reserva",
                    "capitao": True,
                },
            ],
            "tecnico": "Técnico",
            "fonte": "produção",
        }

    def test_upsert_preserves_unmentioned_data_and_unknown_fields(self) -> None:
        patch = validate_current_squad_patch(
            {
                "upsert_players": [
                    {"nome": "Jogador A", "condicao": "Reserva"},
                    {
                        "nome": "Paulinho",
                        "posicao": "Lateral-Esquerdo",
                        "condicao": "Reserva",
                        "capitao": False,
                    },
                ]
            }
        )

        result, stats = apply_current_squad_patch(self.current, patch)

        self.assertEqual(result["fonte"], "produção")
        self.assertEqual(result["tecnico"], "Técnico")
        self.assertEqual(result["jogadores"][0]["posicao"], "Atacante")
        self.assertEqual(result["jogadores"][0]["condicao"], "Reserva")
        self.assertEqual(result["jogadores"][0]["campo_legado"], "preservar")
        self.assertEqual(result["jogadores"][1], self.current["jogadores"][1])
        self.assertEqual(result["jogadores"][2]["nome"], "Paulinho")
        self.assertEqual(stats["inserted"], 1)
        self.assertEqual(stats["updated"], 1)
        self.assertEqual(self.current["jogadores"][0]["condicao"], "Titular")

    def test_repeating_same_upsert_is_idempotent(self) -> None:
        patch = validate_current_squad_patch(
            {
                "upsert_players": [
                    {
                        "nome": "Jogador B",
                        "posicao": "Goleiro",
                        "condicao": "Reserva",
                        "capitao": True,
                    }
                ]
            }
        )

        result, stats = apply_current_squad_patch(self.current, patch)

        self.assertEqual(result, self.current)
        self.assertEqual(stats["unchanged"], 1)
        self.assertEqual(stats["inserted"], 0)
        self.assertEqual(stats["updated"], 0)

    def test_removal_is_case_insensitive_and_preserves_other_players(self) -> None:
        patch = validate_current_squad_patch({"remove_players": ["jogador a"]})

        result, stats = apply_current_squad_patch(self.current, patch)

        self.assertEqual(result["jogadores"], [self.current["jogadores"][1]])
        self.assertEqual(result["fonte"], "produção")
        self.assertEqual(stats["removed"], 1)
        self.assertEqual(stats["remove_missing"], 0)

    def test_rejects_conflicting_or_unknown_operations(self) -> None:
        with self.assertRaisesRegex(ValueError, "atualizado e removido"):
            validate_current_squad_patch(
                {
                    "upsert_players": [{"nome": "Jogador A"}],
                    "remove_players": ["jogador a"],
                }
            )
        with self.assertRaisesRegex(ValueError, "Campos inválidos"):
            validate_current_squad_patch({"substituir_tudo": True})


if __name__ == "__main__":
    unittest.main()
