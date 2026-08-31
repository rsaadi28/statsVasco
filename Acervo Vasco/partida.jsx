// Acervo Vasco — detalhe de uma partida

const PlayerOpenCtx = React.createContext(null);

function Plink({ name, children, style }) {
  const open = React.useContext(PlayerOpenCtx);
  if (!open || !name) return <span style={style}>{children || name}</span>;
  return (
    <button className="plink" onClick={(e)=>{ e.stopPropagation(); open(name); }} style={style}>
      {children || name}
    </button>
  );
}

// converte período+minuto em "minuto absoluto" pra ordenação
function absMin(min, periodo) {
  if (min == null || min === "" || !periodo) return 9999;
  if (periodo === "1T") return Math.min(min, 45);
  // 2T: minuto 1 = 46, minuto 45 = 90
  return 45 + min;
}
function fmtMin(min, periodo) {
  if (min == null || min === "" || !periodo) return "s/min";
  return `${min}'/${periodo}`;
}

const TEAM_STAT_ORDER = [
  "posse_bola",
  "passes_certos",
  "passes_errados",
  "passes_tentados",
  "precisao_passes",
  "finalizacoes",
  "finalizacoes_no_gol",
  "finalizacoes_fora",
  "finalizacoes_bloqueadas",
  "escanteios",
  "impedimentos",
  "faltas_cometidas",
  "faltas_recebidas",
  "desarmes",
  "interceptacoes",
  "cruzamentos_certos",
  "cruzamentos_errados",
  "cruzamentos_tentados",
  "lancamentos_certos",
  "lancamentos_errados",
  "lancamentos_tentados",
  "xg",
];

const PLAYER_STAT_ORDER = [
  "minutos",
  "nota_sofascore",
  "nota",
  "passes_certos",
  "passes_errados",
  "passes_tentados",
  "precisao_passes",
  "finalizacoes",
  "finalizacoes_no_gol",
  "assistencias",
  "chances_criadas",
  "desarmes",
  "interceptacoes",
  "duelos_ganhos",
  "duelos_aereos_ganhos",
  "faltas_cometidas",
  "faltas_recebidas",
  "defesas",
  "cruzamentos_certos",
  "cruzamentos_errados",
  "lancamentos_certos",
  "lancamentos_errados",
];

const STAT_LABELS = {
  assistencias: "Assistências",
  chances_criadas: "Chances criadas",
  cruzamentos_certos: "Cruzamentos certos",
  cruzamentos_errados: "Cruzamentos errados",
  cruzamentos_tentados: "Cruzamentos tentados",
  defesas: "Defesas",
  desarmes: "Desarmes",
  duelos_aereos_ganhos: "Duelos aéreos ganhos",
  duelos_ganhos: "Duelos ganhos",
  escanteios: "Escanteios",
  faltas_cometidas: "Faltas cometidas",
  faltas_recebidas: "Faltas recebidas",
  finalizacoes: "Finalizações",
  finalizacoes_bloqueadas: "Finalizações bloqueadas",
  finalizacoes_fora: "Finalizações fora",
  finalizacoes_no_gol: "Finalizações no gol",
  impedimentos: "Impedimentos",
  interceptacoes: "Interceptações",
  lancamentos_certos: "Lançamentos certos",
  lancamentos_errados: "Lançamentos errados",
  lancamentos_tentados: "Lançamentos tentados",
  minutos: "Minutos",
  nota: "Nota",
  nota_sofascore: "Nota SofaScore",
  passes_certos: "Passes certos",
  passes_errados: "Passes errados",
  passes_tentados: "Passes tentados",
  posse_bola: "Posse de bola",
  precisao_passes: "Precisão dos passes",
  xg: "xG",
};

const PERCENT_STATS = new Set([
  "posse_bola",
  "precisao_cruzamentos",
  "precisao_lancamentos",
  "precisao_passes",
]);

function filledStat(v) {
  return v !== null && v !== undefined && v !== "";
}

function statNameKey(name) {
  return String(name || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^\w\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function samePlayerName(a, b) {
  return statNameKey(a) === statNameKey(b) && statNameKey(a) !== "";
}

function statLabel(key) {
  if (STAT_LABELS[key]) return STAT_LABELS[key];
  return String(key || "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, ch => ch.toUpperCase());
}

function fmtStatValue(key, value) {
  if (!filledStat(value)) return "—";
  const n = Number(value);
  if (Number.isFinite(n)) {
    const formatted = n.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
    return PERCENT_STATS.has(key) ? `${formatted}%` : formatted;
  }
  return String(value);
}

function orderedStatRows(stats, order) {
  if (!stats || typeof stats !== "object") return [];
  const used = new Set(["nome"]);
  const rows = [];
  order.forEach(key => {
    if (!filledStat(stats[key])) return;
    used.add(key);
    rows.push({ key, label: statLabel(key), value: stats[key] });
  });
  Object.keys(stats)
    .filter(key => !used.has(key) && filledStat(stats[key]))
    .sort((a, b) => statLabel(a).localeCompare(statLabel(b), "pt-BR"))
    .forEach(key => rows.push({ key, label: statLabel(key), value: stats[key] }));
  return rows;
}

function playerStatsFor(p, name) {
  const rows = Array.isArray(p?.estatisticas_jogadores_vasco)
    ? p.estatisticas_jogadores_vasco
    : [];
  return rows.find(item => samePlayerName(item?.nome, name)) || null;
}

function allLineupPlayers(p) {
  const out = [];
  const seen = new Set();
  const add = (name, role, detail) => {
    const clean = String(name || "").trim();
    const key = statNameKey(clean);
    if (!key || seen.has(key)) return;
    seen.add(key);
    out.push({ name: clean, role, detail });
  };
  const tit = p?.escalacao?.titulares_por_posicao || {};
  Object.entries(tit).forEach(([pos, names]) => {
    (Array.isArray(names) ? names : []).forEach(name => add(name, "Titular", pos));
  });
  (p?.escalacao?.reservas || []).forEach(name => add(name, "Reserva", "Banco"));
  return out;
}

function participationFor(p, name) {
  const player = allLineupPlayers(p).find(item => samePlayerName(item.name, name));
  const subs = p?.escalacao?.substituicoes || [];
  const entrou = subs.find(s => samePlayerName(s.entra, name));
  const saiu = subs.find(s => samePlayerName(s.sai, name));
  if (!player) {
    return { role: "Vasco", detail: "Relacionado no scout" };
  }
  if (player.role === "Titular" && saiu) {
    return { role: "Titular", detail: `${player.detail} · saiu ${fmtMin(saiu.minuto, saiu.periodo)}` };
  }
  if (player.role === "Reserva" && entrou) {
    return { role: "Reserva utilizado", detail: `entrou ${fmtMin(entrou.minuto, entrou.periodo)}` };
  }
  if (player.role === "Reserva") {
    return { role: "Reserva", detail: "não utilizado" };
  }
  return player;
}

function playerEventRows(p, name) {
  const goals = (p?.gols_vasco || []).filter(g => samePlayerName(g.nome, name)).length;
  const assists = (p?.gols_vasco || []).filter(g => samePlayerName(g.assistencia, name)).length;
  const yellows = (p?.cartoes_amarelos_vasco || []).filter(n => samePlayerName(n, name)).length;
  const reds = (p?.cartoes_vermelhos_vasco || []).filter(c => samePlayerName(c?.nome, name)).length;
  return [
    ["Gols", goals],
    ["Assistências", assists],
    ["Amarelos", yellows],
    ["Vermelhos", reds],
  ].filter(([, value]) => value > 0);
}

function matchDateValue(dateText) {
  const parts = String(dateText || "").split("/").map(Number);
  return parts.length === 3 ? new Date(parts[2], parts[1] - 1, parts[0]).getTime() : 0;
}

function teamNameKey(name) {
  return String(name || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/-?(RJ|SP|MG|RS|PR|SC|BA|PE|CE|PA|GO|AL|RN|SE|MT|MS|ES|DF)$/i, "")
    .replace(/[^a-z0-9]+/gi, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function normalizeForecastMatch(raw, index = 0, ano = null) {
  const placarArr = Array.isArray(raw?.placar)
    ? raw.placar
    : [raw?.placar?.vasco, raw?.placar?.adversario];
  const gp = Number(placarArr[0] || 0);
  const gc = Number(placarArr[1] || 0);
  const result = raw?.resultado || raw?.res || (gp > gc ? "V" : gp < gc ? "D" : "E");
  const parsedYear = Number(String(raw?.data || "").split("/")[2]);
  return {
    id: raw?.id ?? raw?.db_match_id ?? null,
    data: raw?.data || "",
    dataValue: matchDateValue(raw?.data),
    ano: Number.isFinite(parsedYear) ? parsedYear : ano,
    adversario: raw?.adversario || raw?.adv || "",
    advKey: teamNameKey(raw?.adversario || raw?.adv),
    local: raw?.local || "",
    competicao: raw?.competicao || "",
    resultado: result,
    placar: [gp, gc],
    sourceIndex: index,
  };
}

function allForecastMatches() {
  const seasons = window.ACERVO_SEASONS || {};
  return Object.entries(seasons)
    .flatMap(([ano, season]) => (season?.jogos || []).map((game, index) => normalizeForecastMatch(game, index, Number(ano))))
    .filter(game => game.data && game.adversario && ["V", "E", "D"].includes(game.resultado))
    .sort((a, b) => a.dataValue - b.dataValue || a.sourceIndex - b.sourceIndex || String(a.id || "").localeCompare(String(b.id || "")));
}

function currentForecastMatch(p, allGames) {
  const current = normalizeForecastMatch(p);
  return allGames.find(game => game.id != null && current.id != null && String(game.id) === String(current.id))
    || allGames.find(game => game.data === current.data && game.advKey === current.advKey)
    || current;
}

function countForecastGames(games) {
  const counts = { v: 0, e: 0, d: 0, total: 0, gp: 0, gc: 0 };
  (games || []).forEach((game) => {
    if (game.resultado === "V") counts.v += 1;
    else if (game.resultado === "E") counts.e += 1;
    else if (game.resultado === "D") counts.d += 1;
    else return;
    counts.total += 1;
    counts.gp += Number(game.placar?.[0] || 0);
    counts.gc += Number(game.placar?.[1] || 0);
  });
  return counts;
}

function forecastDistribution(counts) {
  const total = counts.total + 3;
  return {
    v: (counts.v + 1) / total,
    e: (counts.e + 1) / total,
    d: (counts.d + 1) / total,
  };
}

function pctForecast(value) {
  return `${Math.round(value * 100)}%`;
}

function forecastResultLabel(result) {
  return ({ V: "Vitória", E: "Empate", D: "Derrota" })[result] || "—";
}

function scoreFromExpected(gp, gc, result) {
  let vasco = Math.max(0, Math.round(gp));
  let adv = Math.max(0, Math.round(gc));
  if (result === "V" && vasco <= adv) vasco = adv + 1;
  if (result === "D" && vasco >= adv) adv = vasco + 1;
  if (result === "E") {
    const draw = Math.max(0, Math.round((gp + gc) / 2));
    vasco = draw;
    adv = draw;
  }
  return [Math.min(5, vasco), Math.min(5, adv)];
}

function buildMatchForecastFromPrior(match, priorGames) {
  const sameOpponent = priorGames.filter(game => game.advKey === match.advKey);
  const sameOpponentVenue = sameOpponent.filter(game => game.local === match.local);
  const recentOpponent = sameOpponent.slice(-5);
  const sameYear = priorGames.filter(game => game.ano === match.ano);
  const recentSeason = sameYear.slice(-10);
  const sameVenueSeason = sameYear.filter(game => game.local === match.local);

  const pieces = [
    { key: "geral", label: "Retrospecto geral", weight: 0.30, counts: countForecastGames(sameOpponent) },
    { key: "mando", label: match.local === "casa" ? "Contra o adversário em casa" : "Contra o adversário fora", weight: 0.25, counts: countForecastGames(sameOpponentVenue) },
    { key: "recentes", label: "Últimos 5 confrontos", weight: 0.20, counts: countForecastGames(recentOpponent) },
    { key: "forma", label: "Forma recente no ano", weight: 0.15, counts: countForecastGames(recentSeason) },
    { key: "mando_temporada", label: match.local === "casa" ? "Vasco em casa no ano" : "Vasco fora no ano", weight: 0.10, counts: countForecastGames(sameVenueSeason) },
  ].filter(piece => piece.counts.total > 0);

  const fallbackPieces = pieces.length
    ? pieces
    : [{ key: "neutro", label: "Sem amostra anterior", weight: 1, counts: { v: 0, e: 0, d: 0, total: 0, gp: 0, gc: 0 } }];
  const weightTotal = fallbackPieces.reduce((sum, piece) => sum + piece.weight, 0) || 1;
  const probability = fallbackPieces.reduce((acc, piece) => {
    const dist = forecastDistribution(piece.counts);
    const weight = piece.weight / weightTotal;
    acc.v += dist.v * weight;
    acc.e += dist.e * weight;
    acc.d += dist.d * weight;
    if (piece.counts.total > 0) {
      acc.xgFor += (piece.counts.gp / piece.counts.total) * weight;
      acc.xgAgainst += (piece.counts.gc / piece.counts.total) * weight;
    }
    return acc;
  }, { v: 0, e: 0, d: 0, xgFor: 0, xgAgainst: 0 });
  const probTotal = probability.v + probability.e + probability.d || 1;
  probability.v /= probTotal;
  probability.e /= probTotal;
  probability.d /= probTotal;

  if (!Number.isFinite(probability.xgFor) || probability.xgFor === 0) probability.xgFor = 1;
  if (!Number.isFinite(probability.xgAgainst) || probability.xgAgainst === 0) probability.xgAgainst = 1;

  const predicted = [
    ["V", probability.v],
    ["E", probability.e],
    ["D", probability.d],
  ].sort((a, b) => b[1] - a[1])[0][0];
  const predictedScore = scoreFromExpected(probability.xgFor, probability.xgAgainst, predicted);
  const actualScore = match.placar || [0, 0];
  const actual = match.resultado;
  const hitResult = predicted === actual;
  const hitScore = predictedScore[0] === actualScore[0] && predictedScore[1] === actualScore[1];
  const confidence = sameOpponent.length >= 20 && sameOpponentVenue.length >= 8
    ? "alta"
    : sameOpponent.length >= 8 || sameOpponentVenue.length >= 5 || recentSeason.length >= 8
      ? "média"
      : "baixa";

  return {
    match,
    probability,
    predicted,
    predictedScore,
    actual,
    actualScore,
    hitResult,
    hitScore,
    confidence,
    pieces: fallbackPieces,
    general: countForecastGames(sameOpponent),
    venue: countForecastGames(sameOpponentVenue),
    recent: countForecastGames(recentOpponent),
    season: countForecastGames(recentSeason),
    seasonVenue: countForecastGames(sameVenueSeason),
  };
}

function buildForecastAudit(currentMatch) {
  const allGames = allForecastMatches();
  const current = currentForecastMatch(currentMatch, allGames);
  const currentIndex = allGames.findIndex(game =>
    (game.id != null && current.id != null && String(game.id) === String(current.id)) ||
    (game.data === current.data && game.advKey === current.advKey)
  );
  const priorGames = currentIndex >= 0 ? allGames.slice(0, currentIndex) : allGames.filter(game => game.dataValue < current.dataValue);
  const selected = buildMatchForecastFromPrior(current, priorGames);
  const predictions = [];
  allGames.forEach((game, index) => {
    const prior = allGames.slice(0, index);
    if (prior.length < 5) return;
    predictions.push(buildMatchForecastFromPrior(game, prior));
  });
  const resultHits = predictions.filter(item => item.hitResult).length;
  const scoreHits = predictions.filter(item => item.hitScore).length;
  return {
    selected,
    history: {
      total: predictions.length,
      acertos: resultHits,
      erros: predictions.length - resultHits,
      placarAcertos: scoreHits,
      aproveitamento: predictions.length ? (resultHits / predictions.length) * 100 : 0,
      placarAproveitamento: predictions.length ? (scoreHits / predictions.length) * 100 : 0,
    },
  };
}

function Partida({ partida, onBack, onOpenPlayer }) {
  const [tab, setTab] = useState("resumo");
  const [matchPlayer, setMatchPlayer] = useState(null);
  React.useEffect(() => setMatchPlayer(null), [partida?.id]);
  const openMatchPlayer = (name) => {
    const clean = String(name || "").trim();
    if (clean && clean !== "—") setMatchPlayer(clean);
  };
  return (
    <PlayerOpenCtx.Provider value={openMatchPlayer}>
    <div className="main">
      <button className="detail-back" onClick={onBack}>
        <span className="arrow">‹</span> Voltar para temporada 2026
      </button>
      <DetailHero p={partida} />
      <nav className="detail-tabs">
        {[
          ["resumo","Resumo"],
          ["escalacao","Escalação"],
          ["eventos","Eventos"],
          ["estatisticas","Estatísticas"],
          ["previsao","Previsão"],
          ["arbitragem","Arbitragem"],
          ["bilheteria","Bilheteria"],
        ].map(([k,l]) => (
          <button key={k} className={tab===k?"active":""} onClick={()=>setTab(k)}>{l}</button>
        ))}
      </nav>
      {tab==="resumo"     && <TabResumo p={partida} />}
      {tab==="escalacao"  && <TabEscalacao p={partida} />}
      {tab==="eventos"    && <TabEventos p={partida} />}
      {tab==="estatisticas" && <TabEstatisticas p={partida} />}
      {tab==="previsao"   && <TabPrevisao p={partida} />}
      {tab==="arbitragem" && <TabArbitragem p={partida} />}
      {tab==="bilheteria" && <TabBilheteria p={partida} />}
      {matchPlayer && (
        <PlayerMatchStatsModal
          p={partida}
          name={matchPlayer}
          onClose={() => setMatchPlayer(null)}
          onOpenPlayer={onOpenPlayer}
        />
      )}
    </div>
    </PlayerOpenCtx.Provider>
  );
}

// ============ Hero do detalhe ============
function DetailHero({ p }) {
  const vasco_casa = p.local === "casa";
  return (
    <section className="detail-hero">
      <div className="detail-meta">
        <span><strong>{p.competicao}</strong></span>
        <span className="dot">·</span>
        <span>{p.fase}</span>
        <span className="dot">·</span>
        <span>{p.data} <strong>{p.horario}</strong></span>
        <span className="dot">·</span>
        <span><strong>{p.estadio}</strong> · {vasco_casa ? "Casa" : "Visitante"}</span>
        <span className="dot">·</span>
        <span>Técnico: <strong>{p.tecnico}</strong></span>
        <span className="dot">·</span>
        <span>Capitão: <strong>{p.capitao}</strong></span>
      </div>
      <div className="detail-scoreline">
        <div className="team-block">
          <div className="team-header">
            <Monogram club="Vasco" vasco size="lg" />
            <div className="name">Vasco</div>
          </div>
          {p.gols_vasco.length > 0 && (
            <div className="scorers">
              {p.gols_vasco.map((g, i) => (
                <div key={i}>
                  <span className="who"><Plink name={g.nome}/>{g.penalti ? " (pen)" : ""}</span>
                  <span className="min">{fmtMin(g.minuto, g.periodo)}{g.assistencia ? ` · ass. ${g.assistencia}` : ""}</span>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="detail-score">
          {p.placar.vasco}<span className="x">×</span>{p.placar.adversario}
        </div>
        <div className="team-block away">
          <div className="team-header">
            <div className="name" style={{textAlign:"right"}}>{p.adversario}</div>
            <Monogram club={p.adversario} size="lg" />
          </div>
          {p.gols_adversario.length > 0 && (
            <div className="scorers">
              {p.gols_adversario.map((g, i) => (
                <div key={i}>
                  <span className="min">{fmtMin(g.minuto, g.periodo)}</span>
                  <span className="who">{g.nome}{g.contra ? " (contra)" : ""}{g.assistencia ? ` · ass. ${g.assistencia}` : ""}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      {p.agregado && (
        <div className="detail-aggregate">
          Agregado <strong>{p.agregado.vasco} × {p.agregado.adversario}</strong> · <strong>{p.agregado.classificado}</strong> classificado para as oitavas
        </div>
      )}
    </section>
  );
}

// ============ Resumo ============
function TabResumo({ p }) {
  const v = p.placar.vasco, a = p.placar.adversario;
  const result = v > a ? "Vitória" : v < a ? "Derrota" : "Empate";
  return (
    <div className="resumo-grid">
      <div>
        <p className="resumo-text">{p.observacao}</p>
      </div>
      <div className="resumo-side">
        <div className="kv"><span className="k">Resultado</span><span className="v">{result}</span></div>
        <div className="kv"><span className="k">Placar</span><span className="v">{v} × {a}</span></div>
        {p.agregado && (
          <div className="kv"><span className="k">Agregado</span><span className="v">{p.agregado.vasco} × {p.agregado.adversario}</span></div>
        )}
        <div className="kv"><span className="k">Estádio</span><span className="v">{p.estadio}</span></div>
        <div className="kv"><span className="k">Horário</span><span className="v">{p.horario}</span></div>
        <div className="kv"><span className="k">Competição</span><span className="v">{p.competicao}</span></div>
        <div className="kv"><span className="k">Técnico</span><span className="v">{p.tecnico}</span></div>
        <div className="kv"><span className="k">Capitão</span><span className="v"><Plink name={p.capitao}/></span></div>
        <div className="kv"><span className="k">Formação</span><span className="v">{p.escalacao.formacao}</span></div>
        <div className="kv"><span className="k">Cartões amarelos</span><span className="v">{p.cartoes_amarelos_vasco.length}</span></div>
        <div className="kv"><span className="k">Cartão vermelho</span><span className="v">{p.cartoes_vermelhos_vasco.length}</span></div>
        <div className="kv"><span className="k">Substituições</span><span className="v">{p.escalacao.substituicoes.length}</span></div>
      </div>
    </div>
  );
}

// ============ Escalação ============
// Vasco atacando pra cima. Eixo Y de baixo (0) pra cima (100); X da esquerda à direita.
const PITCH_POS_Y = {
  Goleiro: 90,
  "Lateral-Direito": 76,
  Zagueiro: 76,
  "Lateral-Esquerdo": 76,
  Volante: 56,
  "Meio-Campista": 36,
  Atacante: 16,
};

function pitchLineXs(count, pos) {
  if (pos === "Goleiro") return [50];
  if (pos === "Lateral-Direito") return [85];
  if (pos === "Lateral-Esquerdo") return [15];
  if (count <= 1) return [50];
  if (pos === "Zagueiro") {
    if (count === 2) return [38, 62];
    if (count === 3) return [28, 50, 72];
  }
  if (count === 2) return [36, 64];
  if (pos === "Atacante" && count === 3) return [26, 74, 50];
  if (count === 3) return [26, 50, 74];
  if (count === 4) return [18, 39, 61, 82];
  const step = 68 / Math.max(1, count - 1);
  return Array.from({ length: count }, (_, i) => 16 + i * step);
}

function pitchCoordsFor(pos, count) {
  const y = PITCH_POS_Y[pos] ?? 50;
  return pitchLineXs(count, pos).map((x) => [x, y]);
}

function playerInitials(name) {
  const parts = name.split(/\s+/).filter(Boolean);
  if (parts.length === 1) return parts[0].slice(0,2).toUpperCase();
  return (parts[0][0] + parts[parts.length-1][0]).toUpperCase();
}

function TabEscalacao({ p }) {
  const [mode, setMode] = useState("campo"); // campo | lista
  const tit = p.escalacao.titulares_por_posicao;
  return (
    <div>
      <div className="lineup-toggle">
        <button className={mode==="campo"?"active":""} onClick={()=>setMode("campo")}>Campo</button>
        <button className={mode==="lista"?"active":""} onClick={()=>setMode("lista")}>Por posição</button>
      </div>
      {mode==="campo" ? <LineupPitch p={p} /> : <LineupList p={p} />}
      <BenchAndOuts p={p} />
    </div>
  );
}

function LineupPitch({ p }) {
  const tit = p.escalacao.titulares_por_posicao;
  const placed = [];
  Object.entries(tit).forEach(([pos, players]) => {
    const coords = pitchCoordsFor(pos, players.length);
    players.forEach((name, i) => {
      const c = coords[i] || [50, 50];
      placed.push({ name, pos, x: c[0], y: c[1] /* GK em baixo, ataque em cima */ });
    });
  });
  const isCaptain = (name) => name === p.capitao;
  const isGK = (pos) => pos === "Goleiro";
  return (
    <div className="lineup-grid">
      <div className="pitch">
        <div className="pitch-stripes"/>
        <div className="pitch-center"/>
        <div className="pitch-top-box"/>
        {/* área inferior */}
        <div style={{position:"absolute", left:"18%", right:"18%", bottom:0, height:"18%", border:"1px solid rgba(255,255,255,0.45)", borderBottom:0}}/>
        {placed.map((pl, i) => (
          <div key={i} className={`player-dot ${isGK(pl.pos)?"gk":""} ${isCaptain(pl.name)?"cap":""}`} style={{ left: `${pl.x}%`, top: `${pl.y}%` }}>
            <div className="num">{playerInitials(pl.name)}</div>
            <div className="nm"><Plink name={pl.name}/></div>
          </div>
        ))}
      </div>
      <div className="lineup-side">
        <h4>Reservas no banco · {p.escalacao.reservas.length}</h4>
        <ul>{p.escalacao.reservas.map(n => <li key={n}><Plink name={n}/></li>)}</ul>
        <h4>Substituições</h4>
        <ul style={{gridTemplateColumns:"1fr", display:"block", fontSize:13.5}}>
          {p.escalacao.substituicoes.map((s, i) => (
            <li key={i} style={{padding:"5px 0", display:"flex", justifyContent:"space-between", borderBottom:"1px dotted var(--rule)"}}>
              <span><span style={{color:"var(--r-d)"}}>−</span> <Plink name={s.sai}/> <span style={{color:"var(--ink-mute)", fontFamily:"var(--ff-mono)", fontSize:11}}>›</span> <span style={{color:"var(--r-v)"}}>+</span> <Plink name={s.entra}/></span>
              <span style={{fontFamily:"var(--ff-mono)", fontSize:11, color:"var(--ink-mute)"}}>{s.minuto}'/{s.periodo}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function LineupList({ p }) {
  const tit = p.escalacao.titulares_por_posicao;
  const isCaptain = (name) => name === p.capitao;
  const POS_ORDER = ["Goleiro","Lateral-Direito","Zagueiro","Lateral-Esquerdo","Volante","Meio-Campista","Atacante"];
  return (
    <div className="lineup-list-only">
      {POS_ORDER.map(pos => (
        <div className="pos-group" key={pos}>
          <h5>{pos}</h5>
          {(tit[pos]||[]).map(n => (
            <div className="pl" key={n}>
              <span><Plink name={n}/>{isCaptain(n) && <span style={{color:"var(--red)", marginLeft:6, fontFamily:"var(--ff-display)", fontSize:11}}>(C)</span>}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function BenchAndOuts({ p }) {
  return (
    <div style={{marginTop:32, display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:32, borderTop:"1px solid var(--rule)", paddingTop:20}}>
      <div>
        <h4 style={{fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)", margin:"0 0 8px"}}>Não relacionados · {p.escalacao.nao_relacionados.length}</h4>
        <ul style={{listStyle:"none", padding:0, margin:0, fontFamily:"var(--ff-serif)", fontSize:13.5, columns:2, columnGap:24}}>
          {p.escalacao.nao_relacionados.map(n => <li key={n} style={{padding:"3px 0", breakInside:"avoid"}}><Plink name={n}/></li>)}
        </ul>
      </div>
      <div>
        <h4 style={{fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)", margin:"0 0 8px"}}>Lesionados · {p.escalacao.lesionados.length}</h4>
        <ul style={{listStyle:"none", padding:0, margin:0, fontFamily:"var(--ff-serif)", fontSize:13.5}}>
          {p.escalacao.lesionados.map(n => <li key={n} style={{padding:"3px 0", color:"var(--r-d)"}}><Plink name={n}/></li>)}
        </ul>
      </div>
      <div>
        <h4 style={{fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)", margin:"0 0 8px"}}>Suspensos · {p.escalacao.suspensos.length}</h4>
        <ul style={{listStyle:"none", padding:0, margin:0, fontFamily:"var(--ff-serif)", fontSize:13.5, color:"var(--ink-mute)"}}>
          {p.escalacao.suspensos.length===0 ? <li style={{fontStyle:"italic"}}>nenhum</li> : p.escalacao.suspensos.map(n => <li key={n} style={{padding:"3px 0"}}><Plink name={n}/></li>)}
        </ul>
      </div>
    </div>
  );
}

// ============ Eventos ============
function TabEventos({ p }) {
  // monta lista de eventos lado-a-lado
  const events = [];
  p.gols_vasco.forEach(g => events.push({
    side: "vasco", kind: g.penalti ? "pen" : "goal",
    name: g.nome, label: g.penalti ? "Gol (pênalti)" : "Gol",
    detail: g.assistencia ? `assistência ${g.assistencia}` : "",
    minuto: g.minuto, periodo: g.periodo, abs: absMin(g.minuto, g.periodo),
  }));
  p.gols_adversario.forEach(g => events.push({
    side: "adv", kind: g.contra ? "og" : "goal",
    name: g.nome, label: g.contra ? "Gol contra · Saldivia" : "Gol",
    detail: g.assistencia ? `assistência ${g.assistencia}` : "",
    minuto: g.minuto, periodo: g.periodo, abs: absMin(g.minuto, g.periodo),
  }));
  p.cartoes_amarelos_vasco.forEach(n => events.push({
    side: "vasco", kind: "yellow", name: n, label: "Amarelo",
    minuto: null, periodo: null, abs: 9999, // sem minuto conhecido → ao final
  }));
  p.cartoes_vermelhos_vasco.forEach(c => events.push({
    side: "vasco", kind: "red", name: c.nome, label: `Vermelho · ${c.motivo}`,
    minuto: c.minuto, periodo: c.periodo, abs: absMin(c.minuto, c.periodo),
  }));
  p.escalacao.substituicoes.forEach(s => events.push({
    side: "vasco", kind: "sub", name: `${s.entra}`, label: `entra por ${s.sai}`,
    minuto: s.minuto, periodo: s.periodo, abs: absMin(s.minuto, s.periodo),
  }));
  events.sort((a,b)=>a.abs-b.abs);

  // separa por período pra inserir marker do intervalo
  const firstHalf = events.filter(e => (e.periodo==="1T") || (e.abs<=45 && e.minuto!=null));
  const secondHalf = events.filter(e => e.periodo==="2T");
  const unknown = events.filter(e => e.minuto==null);

  const eventRow = (event, key) => (
    <div className="timeline-row" key={key}>
      <div className="timeline-side left">
        {event.side === "vasco" ? <EventRow {...event} /> : <EventRow empty />}
      </div>
      <div className="timeline-min">{event.minuto}'</div>
      <div className="timeline-side right">
        {event.side === "adv" ? <EventRow {...event} /> : <EventRow empty />}
      </div>
    </div>
  );

  return (
    <div className="timeline">
      <div className="timeline-row timeline-header">
        <div className="timeline-side left">
          <EventRow label={<span style={{fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)"}}>Vasco</span>} kind="header" />
        </div>
        <div className="timeline-min header">Min.</div>
        <div className="timeline-side right">
          <EventRow label={<span style={{fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)"}}>{p.adversario}</span>} kind="header" />
        </div>
      </div>
      {firstHalf.map((event, index) => eventRow(event, `first-${index}`))}
      <div className="timeline-row timeline-marker">
        <div className="timeline-side left"><EventRow kind="halfTime" /></div>
        <div className="timeline-min half">Intervalo</div>
        <div className="timeline-side right"><EventRow kind="halfTime" /></div>
      </div>
      {secondHalf.map((event, index) => eventRow(event, `second-${index}`))}
      {unknown.length > 0 && (
        <>
          <div className="timeline-row timeline-marker">
            <div className="timeline-side left"><EventRow kind="indet" /></div>
            <div className="timeline-min half">—</div>
            <div className="timeline-side right">
            <EventRow kind="indet" />
            </div>
          </div>
          {unknown.map((event, index) => (
            <div className="timeline-row" key={`unknown-${index}`}>
              <div className="timeline-side left">
                {event.side === "vasco" ? <EventRow {...event} /> : <EventRow empty />}
              </div>
              <div className="timeline-min">?</div>
              <div className="timeline-side right">
                {event.side === "adv" ? <EventRow {...event} /> : <EventRow empty />}
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
}

function EventRow({ kind, name, label, detail, minuto, periodo, empty }) {
  if (empty) return <div className="evt empty" />;
  if (kind === "halfTime") return <div className="evt" style={{minHeight:35, background:"var(--paper-deep)", fontFamily:"var(--ff-sans)", fontSize:9, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink)", fontWeight:600, padding:"8px 18px"}}>Intervalo</div>;
  if (kind === "indet") return <div className="evt" style={{minHeight:35, background:"var(--paper-deep)", fontFamily:"var(--ff-sans)", fontSize:9, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)", padding:"8px 18px"}}>Sem minuto registrado</div>;
  if (kind === "header") return <div className="evt" style={{minHeight:30, background:"var(--paper-deep)", padding:"6px 18px"}}>{label}</div>;
  const iconChar = kind==="goal" ? "⚽" : kind==="pen" ? "P" : kind==="og" ? "OG" : kind==="sub" ? "⇄" : "";
  return (
    <div className="evt">
      <span className={"icon " + kind}>{iconChar}</span>
      <span className="label">
        <strong style={{fontFamily:"var(--ff-serif)", fontWeight:700}}><Plink name={name}/></strong>
        <small>{label}{detail ? ` · ${detail}` : ""}</small>
      </span>
    </div>
  );
}

// ============ Estatísticas ============
function TabEstatisticas({ p }) {
  const teamStats = p.estatisticas_vasco || {};
  const teamRows = orderedStatRows(teamStats, TEAM_STAT_ORDER);
  const hasTeamStats = teamRows.length > 0;
  const kpis = [
    "posse_bola",
    "passes_certos",
    "passes_errados",
    "passes_tentados",
    "precisao_passes",
    "finalizacoes",
  ].filter(key => filledStat(teamStats[key]));

  return (
    <div className="match-stats">
      {kpis.length > 0 && (
        <div className="stats-kpi-grid">
          {kpis.map(key => (
            <div key={key}>
              <div className="kpi-label">{statLabel(key)}</div>
              <div className="kpi-value">{fmtStatValue(key, teamStats[key])}</div>
            </div>
          ))}
        </div>
      )}

      <div className="match-stats-layout">
        <section className="stats-section">
          <h4>Vasco</h4>
          {hasTeamStats ? (
            <div className="stats-kv-grid">
              {teamRows.map(row => (
                <div className="stats-kv" key={row.key}>
                  <span>{row.label}</span>
                  <strong>{fmtStatValue(row.key, row.value)}</strong>
                </div>
              ))}
            </div>
          ) : (
            <div className="stats-empty">Scout coletivo ainda não cadastrado para esta partida.</div>
          )}
        </section>

        <section className="stats-section">
          <h4>Jogadores do Vasco</h4>
          <PlayerStatsTable p={p} />
        </section>
      </div>
    </div>
  );
}

function PlayerStatsTable({ p }) {
  const open = React.useContext(PlayerOpenCtx);
  const rawRows = Array.isArray(p.estatisticas_jogadores_vasco) ? p.estatisticas_jogadores_vasco : [];
  if (!rawRows.length) {
    return <div className="stats-empty">Scout individual ainda não cadastrado para esta partida.</div>;
  }

  const order = new Map();
  allLineupPlayers(p).forEach((item, idx) => order.set(statNameKey(item.name), idx));
  const rows = [...rawRows].sort((a, b) => {
    const oa = order.has(statNameKey(a.nome)) ? order.get(statNameKey(a.nome)) : 999;
    const ob = order.has(statNameKey(b.nome)) ? order.get(statNameKey(b.nome)) : 999;
    if (oa !== ob) return oa - ob;
    return String(a.nome || "").localeCompare(String(b.nome || ""), "pt-BR");
  });

  return (
    <div className="stats-table-wrap">
      <table className="stats-table">
        <thead>
          <tr>
            <th>Jogador</th>
            <th>Função</th>
            <th>Min</th>
            <th>Nota</th>
            <th>Passes C/E/T</th>
            <th>Prec.</th>
            <th>Fin.</th>
            <th>No gol</th>
            <th>Desarmes</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => {
            const participation = participationFor(p, row.nome);
            return (
              <tr key={`${row.nome}-${i}`} className="has-detail" onClick={() => open && open(row.nome)}>
                <td><Plink name={row.nome}/></td>
                <td>{participation.role}</td>
                <td>{fmtStatValue("minutos", row.minutos)}</td>
                <td>{fmtStatValue("nota_sofascore", row.nota_sofascore ?? row.nota)}</td>
                <td>
                  {[
                    fmtStatValue("passes_certos", row.passes_certos),
                    fmtStatValue("passes_errados", row.passes_errados),
                    fmtStatValue("passes_tentados", row.passes_tentados),
                  ].join(" / ")}
                </td>
                <td>{fmtStatValue("precisao_passes", row.precisao_passes)}</td>
                <td>{fmtStatValue("finalizacoes", row.finalizacoes)}</td>
                <td>{fmtStatValue("finalizacoes_no_gol", row.finalizacoes_no_gol)}</td>
                <td>{fmtStatValue("desarmes", row.desarmes)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function TabPrevisao({ p }) {
  const audit = useMemo(() => buildForecastAudit(p), [p?.id, p?.data, p?.adversario]);
  const forecast = audit.selected;
  const rows = [
    ["Vitória", forecast.probability.v, "V"],
    ["Empate", forecast.probability.e, "E"],
    ["Derrota", forecast.probability.d, "D"],
  ];
  return (
    <div className="match-forecast">
      <section className="match-forecast-hero">
        <div className="match-forecast-card">
          <span>Previsão antes do jogo</span>
          <strong className={`tone-${forecast.predicted}`}>{forecastResultLabel(forecast.predicted)}</strong>
          <small>confiança {forecast.confidence}</small>
        </div>
        <div className="match-forecast-score">
          <div>
            <span>Placar previsto</span>
            <strong>{forecast.predictedScore[0]} × {forecast.predictedScore[1]}</strong>
          </div>
          <div>
            <span>Resultado oficial</span>
            <strong className={`tone-${forecast.actual}`}>{forecastResultLabel(forecast.actual)}</strong>
            <small>{forecast.actualScore[0]} × {forecast.actualScore[1]}</small>
          </div>
          <div>
            <span>Status da previsão</span>
            <strong className={forecast.hitResult ? "tone-V" : "tone-D"}>{forecast.hitResult ? "Acertou" : "Errou"}</strong>
            <small>{forecast.hitScore ? "placar exato" : "placar diferente"}</small>
          </div>
        </div>
      </section>

      <section className="match-forecast-bars">
        {rows.map(([label, value, key]) => (
          <div className="match-forecast-row" key={key}>
            <div className="match-forecast-row-head">
              <span>{label}</span>
              <strong className={`tone-${key}`}>{pctForecast(value)}</strong>
            </div>
            <div className="match-forecast-track">
              <i className={`tone-${key}`} style={{width: pctForecast(value)}} />
            </div>
          </div>
        ))}
      </section>

      <section className="match-forecast-audit">
        <div>
          <span>Histórico simulado do modelo</span>
          <strong>{audit.history.acertos} × {audit.history.erros}</strong>
          <small>{audit.history.total} jogos com ao menos 5 partidas anteriores no acervo</small>
        </div>
        <div>
          <span>Aproveitamento V/E/D</span>
          <strong>{audit.history.aproveitamento.toFixed(1)}%</strong>
          <small>acertos do resultado provável</small>
        </div>
        <div>
          <span>Placares exatos</span>
          <strong>{audit.history.placarAcertos}</strong>
          <small>{audit.history.placarAproveitamento.toFixed(1)}% dos jogos simulados</small>
        </div>
      </section>

      <section className="match-forecast-samples">
        <ForecastBox title="Confronto geral" counts={forecast.general} />
        <ForecastBox title={p.local === "casa" ? "Confronto em casa" : "Confronto fora"} counts={forecast.venue} />
        <ForecastBox title="Últimos 5 confrontos" counts={forecast.recent} />
        <ForecastBox title="Forma recente no ano" counts={forecast.season} />
        <ForecastBox title={p.local === "casa" ? "Vasco em casa no ano" : "Vasco fora no ano"} counts={forecast.seasonVenue} />
      </section>

      <section className="match-forecast-method">
        <h4>Base usada</h4>
        <ul>
          {forecast.pieces.map(piece => {
            const totalWeight = forecast.pieces.reduce((sum, item) => sum + item.weight, 0) || 1;
            return (
              <li key={piece.key}>
                <span>{piece.label}</span>
                <strong>{Math.round((piece.weight / totalWeight) * 100)}%</strong>
                <em>{piece.counts.total} jogos anteriores</em>
              </li>
            );
          })}
        </ul>
        <p>
          A simulação usa somente partidas anteriores ao jogo selecionado. O placar previsto vem das médias ponderadas
          de gols pró e contra nas mesmas amostras usadas para calcular V/E/D.
        </p>
      </section>
    </div>
  );
}

function ForecastBox({ title, counts }) {
  return (
    <div className="match-forecast-box">
      <span>{title}</span>
      <strong><b className="tone-V">{counts.v}</b>V · <b className="tone-E">{counts.e}</b>E · <b className="tone-D">{counts.d}</b>D</strong>
      <small>{counts.total} jogos · {counts.gp}–{counts.gc}</small>
    </div>
  );
}

function PlayerMatchStatsModal({ p, name, onClose, onOpenPlayer }) {
  const stats = playerStatsFor(p, name);
  const participation = participationFor(p, name);
  const rows = orderedStatRows(stats || {}, PLAYER_STAT_ORDER);
  const eventRows = playerEventRows(p, name);

  React.useEffect(() => {
    const onKey = (event) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="match-player-modal" onClick={onClose}>
      <div className="match-player-dialog" role="dialog" aria-modal="true" aria-label={`Números de ${name}`} onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Fechar">×</button>
        <div className="modal-player-head">
          <div>
            <span className="modal-eyebrow">{participation.role}</span>
            <h3>{name}</h3>
            <p>{participation.detail}</p>
          </div>
          {filledStat(stats?.nota_sofascore ?? stats?.nota) && (
            <div className="modal-rating">
              <span>Nota</span>
              <strong>{fmtStatValue("nota_sofascore", stats?.nota_sofascore ?? stats?.nota)}</strong>
            </div>
          )}
        </div>

        {eventRows.length > 0 && (
          <div className="modal-event-grid">
            {eventRows.map(([label, value]) => (
              <div key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        )}

        {rows.length > 0 ? (
          <div className="modal-stat-grid">
            {rows.map(row => (
              <div className="modal-stat" key={row.key}>
                <span>{row.label}</span>
                <strong>{fmtStatValue(row.key, row.value)}</strong>
              </div>
            ))}
          </div>
        ) : (
          <div className="stats-empty">Scout individual ainda não cadastrado para este jogador nesta partida.</div>
        )}

        {onOpenPlayer && (
          <button
            className="modal-profile-btn"
            onClick={() => {
              onClose();
              onOpenPlayer(name);
            }}
          >
            Ver perfil completo
          </button>
        )}
      </div>
    </div>
  );
}

// ============ Arbitragem ============
function TabArbitragem({ p }) {
  return (
    <div className="arb-list">
      <div className="arb-card">
        <h4>Árbitro principal</h4>
        <div className="nm">{p.arbitragem.arbitro}</div>
      </div>
      <div className="arb-card">
        <h4>VAR</h4>
        <div className="nm">{p.arbitragem.var}</div>
      </div>
      <div className="arb-card" style={{gridColumn:"1 / -1"}}>
        <h4>Auxiliares</h4>
        <ul>
          {p.arbitragem.auxiliares.map(n => <li key={n}>{n}</li>)}
        </ul>
      </div>
    </div>
  );
}

// ============ Bilheteria ============
function TabBilheteria({ p }) {
  const publicoPagante = Number(p.publico_pagante || 0);
  const publicoPresente = Number(p.publico_presente || 0);
  const renda = Number(p.renda || 0);
  const naoPagantes = Math.max(0, publicoPresente - publicoPagante);
  const mediaTicket = publicoPagante ? renda / publicoPagante : 0;
  return (
    <div>
      <div className="kpi-grid">
        <div>
          <div className="kpi-label">Público pagante</div>
          <div className="kpi-value">{fmtN(publicoPagante)}</div>
          <div className="kpi-sub">torcedores com ingresso</div>
        </div>
        <div>
          <div className="kpi-label">Público presente</div>
          <div className="kpi-value">{fmtN(publicoPresente)}</div>
          <div className="kpi-sub">+{fmtN(naoPagantes)} não-pagantes (sócios, cortesias)</div>
        </div>
        <div>
          <div className="kpi-label">Renda</div>
          <div className="kpi-value" style={{fontSize:32}}>{fmtBRL(renda)}</div>
          <div className="kpi-sub">ticket médio {fmtBRL(mediaTicket)}</div>
        </div>
      </div>
      <div style={{marginTop:32, display:"grid", gridTemplateColumns:"2fr 1fr", gap:36}}>
        <div>
          <h4 style={{fontFamily:"var(--ff-display)", fontSize:22, letterSpacing:"0.04em", margin:"0 0 12px"}}>Ocupação do estádio</h4>
          <div style={{background:"var(--paper-card)", border:"1px solid var(--rule)", padding:20}}>
            <div style={{display:"flex", justifyContent:"space-between", fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.18em", textTransform:"uppercase", color:"var(--ink-mute)", marginBottom:10}}>
              <span>São Januário</span>
              <span>capacidade ≈ 21.880</span>
            </div>
            <div style={{height:24, background:"var(--paper-deep)", position:"relative", border:"1px solid var(--rule)"}}>
              <div style={{height:"100%", width:`${(publicoPagante/21880)*100}%`, background:"var(--ink)"}}/>
              <div style={{height:"100%", width:`${((publicoPresente-publicoPagante)/21880)*100}%`, background:"var(--red)", position:"absolute", left:`${(publicoPagante/21880)*100}%`, top:0, opacity:0.85}}/>
            </div>
            <div style={{display:"flex", gap:18, marginTop:12, fontFamily:"var(--ff-sans)", fontSize:11}}>
              <span style={{display:"flex", alignItems:"center", gap:6}}><span style={{width:12,height:10,background:"var(--ink)"}}/>Pagantes</span>
              <span style={{display:"flex", alignItems:"center", gap:6}}><span style={{width:12,height:10,background:"var(--red)"}}/>Não-pagantes</span>
              <span style={{color:"var(--ink-mute)", marginLeft:"auto"}}>{((publicoPresente/21880)*100).toFixed(1)}% de ocupação</span>
            </div>
          </div>
        </div>
        <div>
          <h4 style={{fontFamily:"var(--ff-display)", fontSize:22, letterSpacing:"0.04em", margin:"0 0 12px"}}>Notas</h4>
          <p style={{fontFamily:"var(--ff-serif)", fontSize:14, lineHeight:1.5, color:"var(--ink-soft)", fontStyle:"italic"}}>
            Boletim financeiro confirmado por imagem da súmula CBF enviada pelo usuário. Renda bruta sem deduções de borderô.
          </p>
        </div>
      </div>
    </div>
  );
}

window.Partida = Partida;
