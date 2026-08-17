// Acervo Vasco — aba Temporadas

const COMP_SHORT = {
  "Campeonato Brasileiro Série A": "Brasileiro A",
  "Campeonato Carioca": "Carioca",
  "Copa do Brasil": "Copa do Brasil",
  "Copa Sul-Americana": "Sul-Americana",
  "Copa Libertadores": "Libertadores",
};

function shortComp(c) { return COMP_SHORT[c] || c; }

// Derivados da temporada
function computeRollingStats(jogos) {
  let v=0, e=0, d=0, gp=0, gc=0;
  const saldoSeries = [];
  const aproveitamentoSeries = [];
  jogos.forEach((j) => {
    if (j.resultado === "V") v++;
    else if (j.resultado === "E") e++;
    else d++;
    gp += j.placar[0];
    gc += j.placar[1];
    saldoSeries.push(gp - gc);
    const total = v + e + d;
    aproveitamentoSeries.push(((v * 3 + e) / (total * 3)) * 100);
  });
  return { saldoSeries, aproveitamentoSeries };
}

function lastN(arr, n, idx) {
  const start = Math.max(0, idx - n + 1);
  return arr.slice(start, idx + 1);
}

function formatShortDate(dateText) {
  const parts = String(dateText || "").split("/");
  return parts.length >= 2 ? `${parts[0]}/${parts[1]}` : "--/--";
}

function formatLatestMatch(jogos) {
  const latest = Array.isArray(jogos) && jogos.length ? jogos[jogos.length - 1] : null;
  if (!latest) return "--";
  const placar = Array.isArray(latest.placar) ? `${latest.placar[0]}x${latest.placar[1]}` : "--";
  return `${formatShortDate(latest.data)} · ${placar} ${latest.adversario || ""}`.trim();
}

function formatCurrentSequence(jogos) {
  if (!Array.isArray(jogos) || !jogos.length) return "--";
  const latestResult = jogos[jogos.length - 1]?.resultado;
  if (!latestResult) return "--";
  let count = 0;
  for (let idx = jogos.length - 1; idx >= 0; idx--) {
    if (jogos[idx]?.resultado !== latestResult) break;
    count += 1;
  }
  return `${count}${latestResult}`;
}

function partidaDetalhada(jogo) {
  const detalhes = window.PARTIDAS_DETALHES || {};
  const idKey = jogo?.id != null ? String(jogo.id) : "";
  const legacyKey = `${jogo?.data || ""}|${jogo?.adversario || ""}`;
  return detalhes[idKey] || detalhes[legacyKey] || jogo;
}

function computeArtilheiros(jogos, season) {
  const tieOrder = new Map((season.artilheiros || []).map((p, i) => [p.nome, i]));
  const gols = new Map();
  jogos.forEach((jogo) => {
    const detalhe = partidaDetalhada(jogo);
    (detalhe?.gols_vasco || []).forEach((gol) => {
      const nome = String(gol?.nome || "").trim();
      if (!nome || gol?.contra || /^gol contra$/i.test(nome)) return;
      gols.set(nome, (gols.get(nome) || 0) + 1);
    });
  });
  return Array.from(gols, ([nome, qtde]) => ({ nome, gols: qtde }))
    .sort((a, b) =>
      b.gols - a.gols ||
      (tieOrder.get(a.nome) ?? 9999) - (tieOrder.get(b.nome) ?? 9999) ||
      a.nome.localeCompare(b.nome, "pt-BR")
    );
}

const SEASON_SCOUT_TEAM_ORDER = [
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

const SEASON_SCOUT_PLAYER_ORDER = [
  "minutos",
  "nota_sofascore",
  "nota",
  "gols",
  "assistencias",
  "passes_certos",
  "passes_errados",
  "passes_tentados",
  "precisao_passes",
  "finalizacoes",
  "finalizacoes_no_gol",
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

const SEASON_SCOUT_LABELS = {
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
  gols: "Gols",
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

const SEASON_SCOUT_PERCENT_STATS = new Set([
  "posse_bola",
  "precisao_cruzamentos",
  "precisao_lancamentos",
  "precisao_passes",
]);

const SEASON_SCOUT_AVG_ONLY_STATS = new Set([
  "posse_bola",
  "precisao_cruzamentos",
  "precisao_lancamentos",
  "precisao_passes",
  "nota",
  "nota_sofascore",
]);

function seasonScoutLabel(key) {
  if (SEASON_SCOUT_LABELS[key]) return SEASON_SCOUT_LABELS[key];
  return String(key || "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, ch => ch.toUpperCase());
}

function seasonScoutNumber(value) {
  if (value === null || value === undefined || value === "") return null;
  if (typeof value === "number") return Number.isFinite(value) ? value : null;
  const normalized = String(value).replace("%", "").replace(/\s+/g, "").replace(",", ".");
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

function seasonScoutAdd(map, key, value) {
  const n = seasonScoutNumber(value);
  if (n === null) return false;
  const current = map.get(key) || { total: 0, count: 0 };
  current.total += n;
  current.count += 1;
  map.set(key, current);
  return true;
}

function seasonScoutOrderedKeys(map, order) {
  const orderIndex = new Map(order.map((key, idx) => [key, idx]));
  return Array.from(map.keys()).sort((a, b) => {
    const ai = orderIndex.has(a) ? orderIndex.get(a) : 9999;
    const bi = orderIndex.has(b) ? orderIndex.get(b) : 9999;
    return ai - bi || seasonScoutLabel(a).localeCompare(seasonScoutLabel(b), "pt-BR");
  });
}

function seasonScoutFormat(key, value, mode) {
  if (value === null || value === undefined || !Number.isFinite(value)) return "—";
  const digits = mode === "media" || SEASON_SCOUT_PERCENT_STATS.has(key) || key === "nota" || key === "nota_sofascore" || key === "xg" ? 2 : 0;
  const text = value.toLocaleString("pt-BR", {
    minimumFractionDigits: 0,
    maximumFractionDigits: digits,
  });
  return SEASON_SCOUT_PERCENT_STATS.has(key) ? `${text}%` : text;
}

function seasonScoutBuildRows(map, order) {
  return seasonScoutOrderedKeys(map, order).map((key) => {
    const acc = map.get(key);
    const media = acc.count ? acc.total / acc.count : 0;
    return {
      key,
      estatistica: seasonScoutLabel(key),
      total: SEASON_SCOUT_AVG_ONLY_STATS.has(key) ? "—" : seasonScoutFormat(key, acc.total, "total"),
      media: seasonScoutFormat(key, media, "media"),
      jogos: acc.count,
    };
  });
}

function aggregateSeasonScouts(jogos) {
  const team = new Map();
  const players = new Map();
  let jogosComScoutTime = 0;
  let jogosComScoutJogadores = 0;

  jogos.forEach((jogo) => {
    const detalhe = partidaDetalhada(jogo);
    const statsTime = detalhe?.estatisticas_vasco && typeof detalhe.estatisticas_vasco === "object"
      ? detalhe.estatisticas_vasco
      : null;
    let hasTeamScout = false;
    if (statsTime) {
      Object.entries(statsTime).forEach(([key, value]) => {
        if (seasonScoutAdd(team, key, value)) hasTeamScout = true;
      });
    }
    if (hasTeamScout) jogosComScoutTime += 1;

    const statsJogadores = Array.isArray(detalhe?.estatisticas_jogadores_vasco)
      ? detalhe.estatisticas_jogadores_vasco
      : [];
    let hasPlayerScout = false;
    statsJogadores.forEach((item) => {
      if (!item || typeof item !== "object") return;
      const nome = String(item.nome || "").trim();
      if (!nome) return;
      if (!players.has(nome)) players.set(nome, { nome, stats: new Map() });
      const player = players.get(nome);
      Object.entries(item).forEach(([key, value]) => {
        if (key === "nome") return;
        if (seasonScoutAdd(player.stats, key, value)) hasPlayerScout = true;
      });
    });
    if (hasPlayerScout) jogosComScoutJogadores += 1;
  });

  const playerRows = Array.from(players.values())
    .sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"))
    .flatMap((player) => seasonScoutBuildRows(player.stats, SEASON_SCOUT_PLAYER_ORDER)
      .map((row) => ({ ...row, jogador: player.nome })));

  const posse = team.get("posse_bola");
  const passesCertos = team.get("passes_certos");
  const passesTentados = team.get("passes_tentados");
  const finalizacoes = team.get("finalizacoes");
  const noGol = team.get("finalizacoes_no_gol");

  return {
    teamRows: seasonScoutBuildRows(team, SEASON_SCOUT_TEAM_ORDER),
    playerRows,
    summary: {
      jogos: jogos.length,
      jogosComScoutTime,
      jogosComScoutJogadores,
      posseMedia: posse?.count ? posse.total / posse.count : null,
      passesCertosTotal: passesCertos?.total || 0,
      passesTentadosTotal: passesTentados?.total || 0,
      finalizacoesTotal: finalizacoes?.total || 0,
      finalizacoesNoGolTotal: noGol?.total || 0,
    },
  };
}

// ============ Temporadas Page ============
function Temporadas({ season, onOpenMatch }) {
  const [recorte, setRecorte] = useState("todos"); // todos | casa | fora
  const [view, setView] = useState("table"); // table | cards
  const [comp, setComp] = useState("todas");
  const [search, setSearch] = useState("");
  const [showScouts, setShowScouts] = useState(false);

  const allJogos = season.jogos;
  const filtered = useMemo(() => {
    return allJogos.filter((j) => {
      if (recorte === "casa" && j.local !== "casa") return false;
      if (recorte === "fora" && j.local !== "fora") return false;
      if (comp !== "todas" && j.competicao !== comp) return false;
      if (search.trim()) {
        const s = search.trim().toLowerCase();
        const hay = `${j.adversario} ${j.competicao} ${j.placar[0]} ${j.placar[1]} ${j.resultado}`.toLowerCase();
        if (!hay.includes(s)) return false;
      }
      return true;
    });
  }, [allJogos, recorte, comp, search]);

  // resumo do recorte
  const resumo = useMemo(() => {
    let v=0,e=0,d=0,gp=0,gc=0;
    filtered.forEach((j)=>{
      if(j.resultado==="V")v++;else if(j.resultado==="E")e++;else d++;
      gp+=j.placar[0]; gc+=j.placar[1];
    });
    const total = v+e+d;
    const aprov = total ? ((v*3+e)/(total*3))*100 : 0;
    return { v,e,d,gp,gc, total, saldo: gp-gc, aprov };
  }, [filtered]);

  const { saldoSeries, aproveitamentoSeries } = useMemo(() => computeRollingStats(filtered), [filtered]);
  const scouts = useMemo(() => aggregateSeasonScouts(filtered), [filtered]);

  const allResults = filtered.map(j => j.resultado);

  // contagem por competição (do recorte todos/casa/fora, antes do filtro de comp)
  const compCounts = useMemo(() => {
    const map = {};
    allJogos.forEach((j) => {
      if (recorte === "casa" && j.local !== "casa") return;
      if (recorte === "fora" && j.local !== "fora") return;
      map[j.competicao] = (map[j.competicao] || 0) + 1;
    });
    return map;
  }, [allJogos, recorte]);

  const comps = Object.keys(compCounts).sort();
  const displayJogos = useMemo(() => [...filtered].reverse(), [filtered]);

  return (
    <div className="main">
      <Hero season={season} resumo={resumo} recorte={recorte} setRecorte={setRecorte} />
      <SummaryRow
        resumo={resumo}
        saldoSeries={saldoSeries}
        aproveitamentoSeries={aproveitamentoSeries}
        allResults={allResults}
        allJogos={filtered}
        season={season}
      />
      <ScoutSummaryStrip scouts={scouts} onOpenScouts={() => setShowScouts(true)} />
      <Toolbar
        comps={comps}
        compCounts={compCounts}
        comp={comp} setComp={setComp}
        view={view} setView={setView}
        search={search} setSearch={setSearch}
        total={filtered.length}
      />
      {view === "table"
        ? <GamesTable jogos={displayJogos} chronologicalResults={allResults} chronologicalJogos={filtered} onOpen={onOpenMatch} />
        : <GamesCards jogos={displayJogos} onOpen={onOpenMatch} />}
      <SidePanels season={season} jogos={filtered} />
      {showScouts && <SeasonScoutsModal scouts={scouts} onClose={() => setShowScouts(false)} />}
    </div>
  );
}

// ============ Hero ============
function Hero({ season, resumo, recorte, setRecorte }) {
  const tecnicos = season.tecnicos;
  const jogos = Array.isArray(season.jogos) ? season.jogos : [];
  const sequenciaAtual = formatCurrentSequence(jogos);
  const ultimaPartida = formatLatestMatch(jogos);
  return (
    <section className="hero">
      <div className="hero-left">
        <div className="hero-eyebrow">Temporada · Acervo Vasco</div>
        <h1 className="hero-year">
          {season.ano}
        </h1>
        <div className="hero-meta">
          <span><strong>Técnicos:</strong> {tecnicos.map(t => t.nome).join(" → ")}</span>
          <span className="dot">·</span>
          <span><strong>Sequência atual:</strong> {sequenciaAtual}</span>
          <span className="dot">·</span>
          <span><strong>Última partida:</strong> {ultimaPartida}</span>
        </div>
      </div>
      <div className="hero-right">
        <div className="recorte">
          {["todos","casa","fora"].map(r => (
            <button key={r} className={recorte===r?"active":""} onClick={()=>setRecorte(r)}>{r}</button>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============ Summary Row ============
function SummaryRow({ resumo, saldoSeries, aproveitamentoSeries, allResults, allJogos, season }) {
  return (
    <section className="summary">
      <div>
        <div className="summary-label">Resultados ({resumo.total} jogos)</div>
        <div className="ved-row">
          <span><span className="v">{resumo.v}</span><span className="lbl">V</span></span>
          <span><span className="e">{resumo.e}</span><span className="lbl">E</span></span>
          <span><span className="d">{resumo.d}</span><span className="lbl">D</span></span>
        </div>
        <div className="spark">
          <StreakBars results={allResults} games={allJogos} width={920} height={34} />
        </div>
        <div className="summary-sub">cronológico · esquerda = 1ª rodada</div>
      </div>
      <div>
        <div className="summary-label">Gols (pró – contra)</div>
        <div className="summary-value">{resumo.gp}<span style={{color:"var(--ink-faint)", margin:"0 8px"}}>–</span>{resumo.gc}</div>
        <div className="spark">
          <Sparkline data={saldoSeries} width={260} height={32} color="#b21f2d" />
        </div>
        <div className="summary-sub">saldo acumulado <strong style={{color:"var(--ink)"}}>{resumo.saldo > 0 ? "+" : ""}{resumo.saldo}</strong></div>
      </div>
      <div>
        <div className="summary-label">Aproveitamento</div>
        <div className="summary-value">{resumo.aprov.toFixed(1)}<span style={{fontSize:"22px", color:"var(--ink-mute)"}}>%</span></div>
        <div className="spark">
          <AproveitamentoChart data={aproveitamentoSeries} width={260} height={32} />
        </div>
        <div className="summary-sub">linha de 50% pontilhada</div>
      </div>
      <div>
        <div className="summary-label">Médias e séries</div>
        <div style={{display:"flex", gap:"22px", alignItems:"baseline", marginTop:"2px"}}>
          <div>
            <div style={{fontFamily:"var(--ff-display)", fontSize:"28px", lineHeight:1}}>{(resumo.gp/Math.max(1,resumo.total)).toFixed(2)}</div>
            <div className="summary-sub" style={{marginTop:2}}>gols pró/jogo</div>
          </div>
          <div>
            <div style={{fontFamily:"var(--ff-display)", fontSize:"28px", lineHeight:1}}>{(resumo.gc/Math.max(1,resumo.total)).toFixed(2)}</div>
            <div className="summary-sub" style={{marginTop:2}}>gols contra/jogo</div>
          </div>
        </div>
        <div style={{marginTop:8, display:"flex", gap:"14px"}}>
          <div className="summary-sub" style={{margin:0}}><strong style={{color:"var(--r-v)"}}>{season.resumo.maior_invicta}j</strong> invicto · <strong style={{color:"var(--r-d)"}}>{season.resumo.maior_jejum}j</strong> sem vencer</div>
        </div>
      </div>
    </section>
  );
}

function ScoutSummaryStrip({ scouts, onOpenScouts }) {
  const metrics = [
    ["Jogos com scout", seasonScoutFormat("jogos", scouts.summary.jogosComScoutTime, "total")],
    ["Posse média", seasonScoutFormat("posse_bola", scouts.summary.posseMedia, "media")],
    ["Passes certos", seasonScoutFormat("passes_certos", scouts.summary.passesCertosTotal, "total")],
    ["Passes tentados", seasonScoutFormat("passes_tentados", scouts.summary.passesTentadosTotal, "total")],
    ["Finalizações", seasonScoutFormat("finalizacoes", scouts.summary.finalizacoesTotal, "total")],
    ["No gol", seasonScoutFormat("finalizacoes_no_gol", scouts.summary.finalizacoesNoGolTotal, "total")],
  ];

  return (
    <section className="season-scout-strip">
      <div className="season-scout-strip-metrics">
        {metrics.map(([label, value]) => (
          <div className="season-scout-strip-metric" key={label}>
            <span>{label}:</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
      <button className="summary-scout-btn" onClick={onOpenScouts}>Ver scouts</button>
    </section>
  );
}

function SeasonScoutsModal({ scouts, onClose }) {
  const [tab, setTab] = useState("vasco");
  const [selectedPlayer, setSelectedPlayer] = useState("");

  React.useEffect(() => {
    const onKey = (event) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const playerNames = useMemo(() => {
    const names = Array.from(new Set((scouts.playerRows || []).map(row => row.jogador).filter(Boolean)));
    const elencoOrder = new Map(
      (window.ELENCO_DATA || [])
        .filter(player => player && player.status !== "ex")
        .map((player, idx) => [String(player.nome || "").trim(), idx])
    );
    return names.sort((a, b) => {
      const ai = elencoOrder.has(a) ? elencoOrder.get(a) : 9999;
      const bi = elencoOrder.has(b) ? elencoOrder.get(b) : 9999;
      return ai - bi || a.localeCompare(b, "pt-BR");
    });
  }, [scouts]);

  React.useEffect(() => {
    if (tab !== "jogadores") return;
    if (!playerNames.length) {
      setSelectedPlayer("");
      return;
    }
    if (!selectedPlayer || !playerNames.includes(selectedPlayer)) {
      setSelectedPlayer(playerNames[0]);
    }
  }, [tab, playerNames, selectedPlayer]);

  const activePlayer = playerNames.includes(selectedPlayer) ? selectedPlayer : (playerNames[0] || "");
  const rows = tab === "vasco"
    ? scouts.teamRows
    : scouts.playerRows.filter(row => row.jogador === activePlayer);

  return (
    <div className="season-scout-modal" onClick={onClose}>
      <div className="season-scout-dialog" onClick={(event) => event.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Fechar">×</button>
        <div className="season-scout-head">
          <span className="modal-eyebrow">Temporada · recorte atual</span>
          <h3>Scouts consolidados</h3>
          <p>
            {scouts.summary.jogosComScoutTime} jogos com scout do Vasco · {scouts.summary.jogosComScoutJogadores} com scouts individuais
          </p>
        </div>
        <div className="season-scout-tabs">
          <button className={tab === "vasco" ? "active" : ""} onClick={() => setTab("vasco")}>Vasco</button>
          <button className={tab === "jogadores" ? "active" : ""} onClick={() => setTab("jogadores")}>Jogadores</button>
        </div>
        {tab === "jogadores" && playerNames.length > 0 && (
          <div className="season-scout-player-select">
            <label htmlFor="season-scout-player">Jogador</label>
            <select
              id="season-scout-player"
              value={activePlayer}
              onChange={(event) => setSelectedPlayer(event.target.value)}
            >
              {playerNames.map((name) => <option key={name} value={name}>{name}</option>)}
            </select>
          </div>
        )}
        {rows.length ? (
          <div className="season-scout-table-wrap">
            <table className="season-scout-table">
              <thead>
                <tr>
                  <th>Estatística</th>
                  <th>Total</th>
                  <th>Média</th>
                  <th>Jogos</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={`${row.jogador || "vasco"}-${row.key}`}>
                    <td>{row.estatistica}</td>
                    <td>{row.total}</td>
                    <td>{row.media}</td>
                    <td>{row.jogos}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="stats-empty">Sem scouts no recorte atual.</div>
        )}
      </div>
    </div>
  );
}

// ============ Toolbar ============
function Toolbar({ comps, compCounts, comp, setComp, view, setView, search, setSearch, total }) {
  return (
    <div className="toolbar">
      <div className="chips">
        <button className={"chip" + (comp==="todas"?" active":"")} onClick={()=>setComp("todas")}>
          Todas <span className="count">{Object.values(compCounts).reduce((a,b)=>a+b,0)}</span>
        </button>
        {comps.map(c => (
          <button key={c} className={"chip" + (comp===c?" active":"")} onClick={()=>setComp(c)}>
            {shortComp(c)} <span className="count">{compCounts[c]}</span>
          </button>
        ))}
      </div>
      <div className="toolbar-right">
        <div className="search">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="7" cy="7" r="5"/><path d="M14 14L11 11"/></svg>
          <input placeholder="filtrar adversário, placar…" value={search} onChange={(e)=>setSearch(e.target.value)} />
        </div>
        <div className="viewtoggle">
          <button className={view==="table"?"active":""} onClick={()=>setView("table")}>Tabela</button>
          <button className={view==="cards"?"active":""} onClick={()=>setView("cards")}>Cards</button>
        </div>
      </div>
    </div>
  );
}

// ============ Games Table ============
function GamesTable({ jogos, chronologicalResults, chronologicalJogos, onOpen }) {
  const chronologicalIndex = useMemo(() => {
    const map = new Map();
    chronologicalJogos.forEach((j, idx) => map.set(j.id, idx));
    return map;
  }, [chronologicalJogos]);
  return (
    <div className="table-wrap">
      <table className="tbl">
        <thead>
          <tr>
            <th style={{width:90}}>Data</th>
            <th style={{width:50}}></th>
            <th>Adversário</th>
            <th style={{width:130}}>Competição</th>
            <th style={{width:60}}>Local</th>
            <th style={{width:110}}>Placar</th>
            <th style={{width:80}}>Forma</th>
            <th>Técnico</th>
            <th style={{width:24}}></th>
          </tr>
        </thead>
        <tbody>
          {jogos.map((j) => {
            // forma = últimos 5 resultados terminando neste jogo, mantendo a ordem cronológica real.
            const idx = chronologicalIndex.get(j.id) ?? 0;
            const formaRes = lastN(chronologicalResults, 5, idx);
            const vasco = j.local === "casa";
            return (
              <tr key={j.id} className={"has-detail"} onClick={()=>onOpen(j)} title="ver detalhes da partida">
                <td className="date">{j.data}</td>
                <td className="result-cell"><span className={"result-dot " + j.resultado} /></td>
                <td className="opponent">
                  <Monogram club={j.adversario} />
                  {j.adversario}
                </td>
                <td className="competition">{shortComp(j.competicao)}</td>
                <td className="locale">{j.local}</td>
                <td className="score">
                  {vasco ? j.placar[0] : j.placar[1]}<span className="vs">×</span>{vasco ? j.placar[1] : j.placar[0]}
                </td>
                <td><MiniStreak results={formaRes} /></td>
                <td className="tecnico">{j.tecnico}</td>
                <td><span className="open-arrow">›</span></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// ============ Games Cards ============
function GamesCards({ jogos, onOpen }) {
  return (
    <div className="cards">
      {jogos.map((j) => {
        const vasco_h = j.local === "casa";
        return (
          <article key={j.id} className="card" onClick={()=>onOpen(j)}>
            <div className="card-top">
              <span className="date">{j.data}</span>
              <span>{shortComp(j.competicao)} · {j.local}</span>
            </div>
            <div className="card-mid">
              <div className="card-team">
                <Monogram club={vasco_h ? "Vasco" : j.adversario} vasco={vasco_h} size="lg" />
                <div className="name">{vasco_h ? "Vasco" : j.adversario}</div>
              </div>
              <div className="card-score">
                {vasco_h ? j.placar[0] : j.placar[1]}<span className="vs">×</span>{vasco_h ? j.placar[1] : j.placar[0]}
              </div>
              <div className="card-team" style={{justifyContent:"flex-end"}}>
                <div className="name" style={{textAlign:"right"}}>{vasco_h ? j.adversario : "Vasco"}</div>
                <Monogram club={vasco_h ? j.adversario : "Vasco"} vasco={!vasco_h} size="lg" />
              </div>
            </div>
            <div className="card-bot">
              <span className="card-result">
                <span className={"result-dot " + j.resultado} />
                {j.resultado==="V"?"Vitória":j.resultado==="E"?"Empate":"Derrota"}
              </span>
              <span>{j.estadio}</span>
            </div>
          </article>
        );
      })}
    </div>
  );
}

// ============ Side Panels (Artilheiros + Aproveitamento) ============
function SidePanels({ season, jogos }) {
  const artilheiros = useMemo(() => computeArtilheiros(jogos, season), [jogos, season]);
  const painelAproveitamentoSeries = useMemo(() => computeRollingStats(jogos).aproveitamentoSeries, [jogos]);
  const max = artilheiros[0]?.gols || 1;
  const totalGols = artilheiros.reduce((a,p)=>a+p.gols,0);
  return (
    <div className="side-grid">
      <section className="panel">
        <h3 className="panel-title">
          Artilheiros do recorte
          <small>{totalGols} gols computados</small>
        </h3>
        <div className="artilharia">
          {artilheiros.length
            ? artilheiros.map((p, i) => (
                <div className="art-row" key={p.nome}>
                  <span className="pos">{String(i+1).padStart(2,"0")}</span>
                  <span className="name">{p.nome}</span>
                  <span className="goals">{p.gols}</span>
                  <span className="bar"><i style={{width:`${(p.gols/max)*100}%`}}/></span>
                </div>
              ))
            : <div className="art-empty">Nenhum gol do Vasco neste recorte.</div>}
        </div>
      </section>
      <section className="panel">
        <h3 className="panel-title">
          Aproveitamento
          <small>ao longo do recorte</small>
        </h3>
        <div style={{padding:"6px 0"}}>
          <AproveitamentoChart data={painelAproveitamentoSeries} width={360} height={140} />
        </div>
        <div style={{display:"flex", justifyContent:"space-between", fontFamily:"var(--ff-mono)", fontSize:"10.5px", color:"var(--ink-mute)", marginTop:6}}>
          <span>1ª rodada</span>
          <span>linha 50%</span>
          <span>último jogo</span>
        </div>
      </section>
    </div>
  );
}

window.Temporadas = Temporadas;
