"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");

const {
  competitionNameKey,
  sameCompetitionName,
  groupMatchesByCompetition,
  comparableMatchSlices,
} = require("../Acervo Vasco/competition-utils.js");

test("aliases da Sul-Americana pertencem ao mesmo filtro", () => {
  const matches = [
    ...Array.from({ length: 10 }, () => ({ competicao: "Copa Sul-Americana" })),
    { competicao: "Sul-Americana" },
  ];

  assert.equal(competitionNameKey("Copa Sul-Americana"), "sul-americana");
  assert.equal(competitionNameKey("Sul–Americana"), "sul-americana");
  assert.equal(sameCompetitionName("CONMEBOL Sudamericana", "Copa Sul-Americana"), true);
  assert.deepEqual(groupMatchesByCompetition(matches), [
    { key: "sul-americana", label: "Sul-Americana", count: 11 },
  ]);
});

test("acentos e variantes comuns não criam filtros duplicados", () => {
  const matches = [
    { competicao: "Campeonato Brasileiro Série A" },
    { competicao: "Campeonato Brasileiro Serie A" },
    { competicao: "Brasileirão Série A" },
    { competicao: "Copa do Brasil" },
  ];

  assert.deepEqual(groupMatchesByCompetition(matches), [
    { key: "brasileiro-a", label: "Brasileiro A", count: 3 },
    { key: "copa-do-brasil", label: "Copa do Brasil", count: 1 },
  ]);
});

test("comparativo corta os dois anos pelo menor total disponível", () => {
  const current = Array.from({ length: 11 }, (_, index) => ({ id: `2026-${index + 1}` }));
  const previous = Array.from({ length: 8 }, (_, index) => ({ id: `2025-${index + 1}` }));

  const result = comparableMatchSlices(current, previous);

  assert.equal(result.count, 8);
  assert.equal(result.currentAvailable, 11);
  assert.equal(result.previousAvailable, 8);
  assert.equal(result.current.length, 8);
  assert.equal(result.previous.length, 8);
  assert.equal(current.length, 11);
  assert.equal(previous.length, 8);
});
