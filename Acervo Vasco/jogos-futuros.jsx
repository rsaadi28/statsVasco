// Acervo Vasco — aba Jogos Futuros

function JogosFuturos({ onOpenRetro }) {
  const all = window.JOGOS_FUTUROS;
  const [comp, setComp] = useState("todas");
  const [hover, setHover] = useState(null);
  const [probMatch, setProbMatch] = useState(null);

  const competicoes = useMemo(() => {
    const set = new Set();
    all.forEach(j => set.add(j.competicao));
    return Array.from(set).sort();
  }, [all]);

  const compCounts = useMemo(() => {
    const m = {};
    all.forEach(j => { m[j.competicao] = (m[j.competicao]||0) + 1; });
    return m;
  }, [all]);

  const filtered = useMemo(() => all.filter(j => comp==="todas" || j.competicao===comp), [all, comp]);

  // próxima partida — primeira da lista
  const proxima = filtered[0];

  return (
    <div className="main">
      <JFHero proxima={proxima} totalAll={all.length} totalFiltered={filtered.length} />
      <div className="jf-toolbar">
        <div className="chips">
          <button className={"chip" + (comp==="todas"?" active":"")} onClick={()=>setComp("todas")}>
            Todas <span className="count">{all.length}</span>
          </button>
          {competicoes.map(c => (
            <button key={c} className={"chip" + (comp===c?" active":"")} onClick={()=>setComp(c)}>
              {shortCompJF(c)} <span className="count">{compCounts[c]}</span>
            </button>
          ))}
        </div>
        <div style={{fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)"}}>
          clique numa partida para ver o retrospecto contra o adversário
        </div>
      </div>

      <div className="table-wrap">
        <table className="tbl jf-tbl">
          <thead>
            <tr>
              <th style={{width:100}}>Data</th>
              <th style={{width:64}}>Hora</th>
              <th>Adversário</th>
              <th style={{width:60}}>Local</th>
              <th style={{width:200}}>Estádio</th>
              <th style={{width:170}}>Competição</th>
              <th style={{width:84}}>Prob.</th>
              <th style={{width:44}}></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((j, idx) => {
              const dias = diasAte(j.data);
              const isProx = idx === 0;
              return (
                <tr key={idx}
                    className={"has-detail" + (isProx?" is-next":"") + (hover===idx?" is-hover":"")}
                    onMouseEnter={()=>setHover(idx)}
                    onMouseLeave={()=>setHover(null)}
                    onClick={()=> onOpenRetro && onOpenRetro(j.adv)}
                    title={`Ver retrospecto contra ${j.adv}`}
                >
                  <td className="date">
                    {j.data}
                    {isProx && <span className="prox-tag">próximo</span>}
                    {!isProx && dias != null && dias < 30 && <span className="dias-tag">em {dias}d</span>}
                  </td>
                  <td style={{fontFamily:"var(--ff-mono)", fontSize:12, color: j.hora==="—" ? "var(--ink-faint)" : "var(--ink-soft)"}}>{j.hora}</td>
                  <td className="opponent">
                    <Monogram club={j.adv} />
                    <span>{j.adv}</span>
                    <span className="vs-tag">{j.local==="casa" ? "em casa" : "visitante"}</span>
                  </td>
                  <td className="locale">{j.local}</td>
                  <td style={{fontFamily:"var(--ff-serif)", fontSize:13.5, color: j.estadio==="—" ? "var(--ink-faint)" : "var(--ink-soft)"}}>{j.estadio}</td>
                  <td className="competition">{shortCompJF(j.competicao)}</td>
                  <td>
                    <button
                      type="button"
                      className="jf-prob-btn"
                      title={`Ver probabilidades contra ${j.adv}`}
                      onClick={(event) => {
                        event.stopPropagation();
                        setProbMatch(j);
                      }}
                    >
                      Ver
                    </button>
                  </td>
                  <td>
                    <span className="open-arrow">›</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {probMatch && <JFProbabilityModal match={probMatch} onClose={() => setProbMatch(null)} />}
    </div>
  );
}

function normalizeTeamName(name) {
  return String(name || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/-?(RJ|SP|MG|RS|PR|SC|BA|PE|CE|PA|GO|AL|RN|SE|MT|MS|ES|DF)$/i, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function getRetroData(adv) {
  const retros = window.RETROSPECTOS || {};
  if (retros[adv]) return retros[adv];
  const target = normalizeTeamName(adv);
  const key = Object.keys(retros).find(name => normalizeTeamName(name) === target);
  return key ? retros[key] : null;
}

function latestSeasonGames() {
  const seasons = window.ACERVO_SEASONS || {};
  const years = Object.keys(seasons).map(Number).filter(Number.isFinite).sort((a, b) => b - a);
  const season = seasons[String(years[0])] || null;
  return Array.isArray(season?.jogos) ? season.jogos : [];
}

function futureProbDateValue(dateText) {
  const parts = String(dateText || "").split("/").map(Number);
  return parts.length === 3 ? new Date(parts[2], parts[1] - 1, parts[0]).getTime() : 0;
}

function countVED(games, field = "res") {
  const counts = { v: 0, e: 0, d: 0, total: 0, gp: 0, gc: 0 };
  (games || []).forEach((game) => {
    const result = String(game?.[field] || "").toUpperCase();
    if (result === "V") counts.v += 1;
    else if (result === "E") counts.e += 1;
    else if (result === "D") counts.d += 1;
    else return;
    counts.total += 1;
    const placar = Array.isArray(game.placar) ? game.placar : [];
    counts.gp += Number(placar[0] || 0);
    counts.gc += Number(placar[1] || 0);
  });
  return counts;
}

function distributionFromCounts(counts) {
  const total = counts.total + 3;
  return {
    v: (counts.v + 1) / total,
    e: (counts.e + 1) / total,
    d: (counts.d + 1) / total,
  };
}

function formatProbPct(value) {
  return `${Math.round(value * 100)}%`;
}

function calcFutureProbability(match) {
  const retro = getRetroData(match.adv);
  const history = Array.isArray(retro?.jogos) ? retro.jogos : [];
  const chronologicalHistory = [...history].sort((a, b) => futureProbDateValue(a.data) - futureProbDateValue(b.data));
  const seasonGames = latestSeasonGames();
  const recentSeason = seasonGames.slice(-10).map(game => ({
    res: game.resultado,
    placar: game.placar,
    local: game.local,
  }));
  const sameVenueSeason = seasonGames
    .filter(game => game.local === match.local)
    .map(game => ({ res: game.resultado, placar: game.placar, local: game.local }));

  const pieces = [
    { key: "geral", label: "Retrospecto geral", weight: 0.3, counts: countVED(history) },
    { key: "mando", label: match.local === "casa" ? "Retrospecto em casa" : "Retrospecto fora", weight: 0.25, counts: countVED(history.filter(game => game.local === match.local)) },
    { key: "recentes", label: "Últimos 5 confrontos", weight: 0.2, counts: countVED(chronologicalHistory.slice(-5)) },
    { key: "forma", label: "Forma recente do Vasco", weight: 0.15, counts: countVED(recentSeason) },
    { key: "mando_temporada", label: match.local === "casa" ? "Vasco em casa na temporada" : "Vasco fora na temporada", weight: 0.1, counts: countVED(sameVenueSeason) },
  ].filter(piece => piece.counts.total > 0);

  const fallbackPieces = pieces.length ? pieces : [
    { key: "neutro", label: "Sem amostra no acervo", weight: 1, counts: { v: 0, e: 0, d: 0, total: 0, gp: 0, gc: 0 } },
  ];

  const weightTotal = fallbackPieces.reduce((sum, piece) => sum + piece.weight, 0) || 1;
  const probability = fallbackPieces.reduce((acc, piece) => {
    const dist = distributionFromCounts(piece.counts);
    const weight = piece.weight / weightTotal;
    acc.v += dist.v * weight;
    acc.e += dist.e * weight;
    acc.d += dist.d * weight;
    return acc;
  }, { v: 0, e: 0, d: 0 });

  const rawTotal = probability.v + probability.e + probability.d || 1;
  probability.v /= rawTotal;
  probability.e /= rawTotal;
  probability.d /= rawTotal;

  const general = countVED(history);
  const venue = countVED(history.filter(game => game.local === match.local));
  const confidence = general.total >= 20 && venue.total >= 8
    ? "alta"
    : general.total >= 8 || venue.total >= 5
      ? "média"
      : "baixa";

  const favorite = [
    ["Vitória", probability.v, "v"],
    ["Empate", probability.e, "e"],
    ["Derrota", probability.d, "d"],
  ].sort((a, b) => b[1] - a[1])[0];

  return {
    match,
    retroName: retro?.adversario || match.adv,
    probability,
    confidence,
    favorite,
    pieces: fallbackPieces,
    general,
    venue,
    recent: countVED(chronologicalHistory.slice(-5)),
    season: countVED(recentSeason),
    seasonVenue: countVED(sameVenueSeason),
  };
}

function JFProbabilityModal({ match, onClose }) {
  const analysis = useMemo(() => calcFutureProbability(match), [match]);

  useEffect(() => {
    const onKey = (event) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const rows = [
    ["Vitória", analysis.probability.v, "v"],
    ["Empate", analysis.probability.e, "e"],
    ["Derrota", analysis.probability.d, "d"],
  ];

  return (
    <div className="jf-prob-modal" role="dialog" aria-modal="true" aria-label={`Probabilidade contra ${match.adv}`} onClick={onClose}>
      <div className="jf-prob-dialog" onClick={(event) => event.stopPropagation()}>
        <button type="button" className="modal-close" onClick={onClose} aria-label="Fechar">×</button>
        <div className="jf-prob-head">
          <span className="modal-eyebrow">Probabilidade pelo acervo</span>
          <h3>Vasco × {match.adv}</h3>
          <p>{match.data} · {match.hora} · {match.local === "casa" ? "em casa" : "fora"} · {shortCompJF(match.competicao)}</p>
        </div>

        <div className="jf-prob-main">
          <div className="jf-prob-score">
            <span>Tendência</span>
            <strong className={`c-${analysis.favorite[2]}`}>{analysis.favorite[0]}</strong>
            <small>confiança {analysis.confidence}</small>
          </div>
          <div className="jf-prob-bars">
            {rows.map(([label, value, key]) => (
              <div className="jf-prob-row" key={key}>
                <div className="jf-prob-row-head">
                  <span>{label}</span>
                  <strong className={`c-${key}`}>{formatProbPct(value)}</strong>
                </div>
                <div className="jf-prob-track">
                  <div className={`jf-prob-fill c-${key}`} style={{width: formatProbPct(value)}} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="jf-prob-grid">
          <ProbBox title="Confronto geral" counts={analysis.general} />
          <ProbBox title={match.local === "casa" ? "Confronto em casa" : "Confronto fora"} counts={analysis.venue} />
          <ProbBox title="Últimos 5 confrontos" counts={analysis.recent} />
          <ProbBox title="Forma recente" counts={analysis.season} />
        </div>

        <div className="jf-prob-method">
          <h4>Base do cálculo</h4>
          <ul>
            {analysis.pieces.map(piece => (
              <li key={piece.key}>
                <span>{piece.label}</span>
                <strong>{Math.round((piece.weight / analysis.pieces.reduce((sum, item) => sum + item.weight, 0)) * 100)}%</strong>
                <em>{piece.counts.total} jogos</em>
              </li>
            ))}
          </ul>
          <p>
            Estimativa baseada somente no acervo: retrospecto contra {analysis.retroName}, mando da partida,
            confrontos recentes e forma do Vasco na temporada. Não usa odds nem dados externos.
          </p>
        </div>
      </div>
    </div>
  );
}

function ProbBox({ title, counts }) {
  return (
    <div className="jf-prob-box">
      <span>{title}</span>
      <strong><b className="c-v">{counts.v}</b>V · <b className="c-e">{counts.e}</b>E · <b className="c-d">{counts.d}</b>D</strong>
      <small>{counts.total} jogos · saldo {counts.gp - counts.gc >= 0 ? "+" : ""}{counts.gp - counts.gc}</small>
    </div>
  );
}

function shortCompJF(c) {
  return {
    "Campeonato Brasileiro Série A": "Brasileiro A",
    "Campeonato Carioca": "Carioca",
    "Copa do Brasil": "Copa do Brasil",
    "Copa Sul-Americana": "Sul-Americana",
    "Copa Libertadores": "Libertadores",
  }[c] || c;
}

function diasAte(data) {
  const [d,m,y] = data.split("/").map(Number);
  const alvo = new Date(y, m-1, d);
  // "hoje" = 15/05/2026 conforme system clock
  const hoje = new Date(2026, 4, 15);
  const ms = alvo - hoje;
  if (ms < 0) return null;
  return Math.round(ms / (24*3600*1000));
}

function JFHero({ proxima, totalAll, totalFiltered }) {
  return (
    <section className="jf-hero">
      <div className="hero-eyebrow">Acervo · Jogos Futuros</div>
      <div className="jf-hero-line">
        <div className="jf-hero-left">
          <h1 className="jf-title">{totalFiltered} <small>jogos confirmados</small></h1>
          <div className="jf-hero-sub">
            até <strong>{ultimaData()}</strong> · contando do calendário oficial publicado pelas competições
          </div>
        </div>
        {proxima && (
          <div className="jf-next">
            <div className="jf-next-label">Próximo jogo</div>
            <div className="jf-next-card">
              <div className="jf-next-date">
                <div className="jf-next-day">{proxima.data.slice(0,2)}</div>
                <div className="jf-next-month">{mesAbrev(proxima.data)}</div>
              </div>
              <div className="jf-next-info">
                <div className="jf-next-comp">{shortCompJF(proxima.competicao)} · {proxima.local}</div>
                <div className="jf-next-teams">
                  <Monogram club="Vasco" vasco size="lg"/>
                  <span className="jf-vs">×</span>
                  <Monogram club={proxima.adv} size="lg"/>
                </div>
                <div className="jf-next-names">
                  <span>Vasco</span>
                  <span className="jf-next-x">×</span>
                  <span>{proxima.adv}</span>
                </div>
                <div className="jf-next-foot">
                  {proxima.estadio !== "—" ? proxima.estadio : "estádio a confirmar"}
                  {proxima.hora !== "—" && <> · <strong>{proxima.hora}</strong></>}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function mesAbrev(data) {
  const m = Number(data.split("/")[1]);
  return ["JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"][m-1] || "";
}
function ultimaData() {
  const last = window.JOGOS_FUTUROS[window.JOGOS_FUTUROS.length-1];
  if (!last) return "—";
  const [d,m,y] = last.data.split("/");
  return `${d}/${m}/${y}`;
}

window.JogosFuturos = JogosFuturos;
