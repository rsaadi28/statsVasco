// Acervo Vasco — normalização compartilhada de competições e recortes comparáveis

(function attachCompetitionUtils(global) {
  const COMPETITION_LABELS = {
    "brasileiro-a": "Brasileiro A",
    "brasileiro-b": "Brasileiro B",
    "brasileiro-c": "Brasileiro C",
    carioca: "Carioca",
    "copa-do-brasil": "Copa do Brasil",
    "sul-americana": "Sul-Americana",
    libertadores: "Libertadores",
    mercosul: "Mercosul",
  };

  function normalizeCompetitionName(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
  }

  function competitionNameKey(value) {
    const normalized = normalizeCompetitionName(value);
    if (!normalized) return "";
    if (normalized.includes("brasileir") && normalized.includes("serie a")) return "brasileiro-a";
    if (normalized.includes("brasileir") && normalized.includes("serie b")) return "brasileiro-b";
    if (normalized.includes("brasileir") && normalized.includes("serie c")) return "brasileiro-c";
    if (normalized.includes("carioca")) return "carioca";
    if (normalized.includes("copa do brasil") || normalized === "copa brasil") return "copa-do-brasil";
    if (normalized.includes("sul americana") || normalized.includes("sudamericana")) return "sul-americana";
    if (normalized.includes("libertadores")) return "libertadores";
    if (normalized.includes("mercosul")) return "mercosul";
    return normalized;
  }

  function sameCompetitionName(value, target) {
    return !target || competitionNameKey(value) === competitionNameKey(target);
  }

  function competitionDisplayName(value) {
    const raw = String(value || "").trim();
    if (!raw) return "Sem competição";
    return COMPETITION_LABELS[competitionNameKey(raw)] || raw;
  }

  function groupMatchesByCompetition(matches) {
    const groups = new Map();
    (Array.isArray(matches) ? matches : []).forEach((match) => {
      const raw = match?.competicao;
      const key = competitionNameKey(raw) || "sem-competicao";
      if (!groups.has(key)) {
        groups.set(key, {
          key,
          label: competitionDisplayName(raw),
          count: 0,
        });
      }
      groups.get(key).count += 1;
    });
    return Array.from(groups.values())
      .sort((a, b) => a.label.localeCompare(b.label, "pt-BR"));
  }

  function comparableMatchSlices(currentMatches, previousMatches) {
    const currentAvailable = Array.isArray(currentMatches) ? currentMatches : [];
    const previousAvailable = Array.isArray(previousMatches) ? previousMatches : [];
    const count = Math.min(currentAvailable.length, previousAvailable.length);
    return {
      current: currentAvailable.slice(0, count),
      previous: previousAvailable.slice(0, count),
      count,
      currentAvailable: currentAvailable.length,
      previousAvailable: previousAvailable.length,
    };
  }

  const api = {
    normalizeCompetitionName,
    competitionNameKey,
    sameCompetitionName,
    competitionDisplayName,
    groupMatchesByCompetition,
    comparableMatchSlices,
  };
  Object.assign(global, api);
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
