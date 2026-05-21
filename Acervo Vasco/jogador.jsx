// Acervo Vasco — detalhe de um jogador

function Jogador({ nome, onBack }) {
  const dados = window.JOGADORES[nome];
  if (!dados) {
    return (
      <div className="main">
        <button className="detail-back" onClick={onBack}><span className="arrow">‹</span> Voltar</button>
        <div style={{padding:60, textAlign:"center", fontFamily:"var(--ff-serif)", fontStyle:"italic", color:"var(--ink-mute)"}}>
          Jogador <strong style={{color:"var(--ink)"}}>{nome}</strong> ainda não foi importado para o acervo web.
        </div>
      </div>
    );
  }
  // aba "Geral" agrega todas as passagens; senão, mostra uma passagem específica
  const [aba, setAba] = useState("geral");
  const [partidaSelecionada, setPartidaSelecionada] = useState(null);
  const passagemAtiva = aba === "geral" ? null : dados.passagens.find(p => p.id === aba);
  const statsAgregadas = aba === "geral"
    ? agregaPassagens(dados.passagens)
    : passagemAtiva.stats;

  useEffect(() => {
    setPartidaSelecionada(null);
  }, [nome, aba]);

  return (
    <div className="main">
      <button className="detail-back" onClick={onBack}><span className="arrow">‹</span> Voltar</button>
      <PlayerHero dados={dados} />
      <nav className="detail-tabs">
        <button className={aba==="geral"?"active":""} onClick={()=>setAba("geral")}>Geral</button>
        {dados.passagens.map(p => (
          <button key={p.id} className={aba===p.id?"active":""} onClick={()=>setAba(p.id)}>
            Passagem {p.idx} · {p.periodo}
          </button>
        ))}
      </nav>
      <PlayerBody stats={statsAgregadas} passagem={passagemAtiva || dados.passagens[0]} jogadorNome={dados.nome} onOpenPlayerMatch={setPartidaSelecionada} aba={aba} />
      {partidaSelecionada && (
        <PlayerMatchModal
          nome={dados.nome}
          row={partidaSelecionada}
          onClose={() => setPartidaSelecionada(null)}
        />
      )}
    </div>
  );
}

const PLAYER_CONSOLIDATED_PERCENT_KEYS = new Set([
  "posse_bola", "precisao_passes", "precisao_cruzamentos", "precisao_lancamentos",
]);

const PLAYER_CONSOLIDATED_AVERAGE_KEYS = new Set([
  "nota", "nota_media", "nota_sofascore", "nota_sofascore_media",
  "posse_bola_media", "precisao_passes_media", "precisao_cruzamentos_media", "precisao_lancamentos_media",
]);

const PLAYER_CONSOLIDATED_STAT_ORDER = [
  "jogos_com_scout",
  "passes_certos", "passes_errados", "passes_tentados", "precisao_passes",
  "finalizacoes", "finalizacoes_no_gol", "finalizacoes_fora", "finalizacoes_bloqueadas", "chances_criadas",
  "desarmes", "interceptacoes", "duelos_ganhos", "duelos_aereos_ganhos",
  "faltas_cometidas", "faltas_recebidas",
  "defesas", "defesas_dificeis", "gols_sofridos",
  "cruzamentos_certos", "cruzamentos_errados", "cruzamentos_tentados", "precisao_cruzamentos",
  "lancamentos_certos", "lancamentos_errados", "lancamentos_tentados", "precisao_lancamentos",
  "nota_sofascore_media", "nota_media",
];

function agregaPassagens(passagens) {
  const agg = {
    jogos_participacao: 0, minutos: 0, media_minutos: 0,
    jogos_titular: 0, jogos_reserva: 0, nao_entrou: 0,
    nao_relacionado: 0, lesionado: 0, suspenso: 0, selecao: 0,
    gols: 0, assistencias: 0, participacoes_gol: 0, jogos_capitao: 0, partidas_marcou: 0, partidas_assistencia: 0,
    gols_titular: 0, gols_banco: 0,
    media_gols: 0, amarelos: 0, vermelhos: 0,
    amarelos_acumulados: 0, suspensao_pendente: false,
    media_min_entre_gols: null,
    ved: { v: 0, e: 0, d: 0 },
    jogos_com_scout: 0,
    estatisticas_avancadas: {},
  };
  passagens.forEach(p => {
    const s = p.stats;
    for (const k of Object.keys(agg)) {
      if (k === "ved") {
        agg.ved.v += s.ved.v; agg.ved.e += s.ved.e; agg.ved.d += s.ved.d;
      } else if (k === "media_minutos" || k === "media_gols" || k === "media_min_entre_gols" || k === "suspensao_pendente") {
        // calculado depois
      } else if (typeof s[k] === "number") {
        agg[k] += s[k];
      }
    }
  });
  agg.media_minutos = agg.jogos_participacao ? +(agg.minutos / agg.jogos_participacao).toFixed(2) : 0;
  agg.media_gols = agg.jogos_participacao ? +(agg.gols / agg.jogos_participacao).toFixed(2) : 0;
  agg.participacoes_gol = agg.gols + agg.assistencias;
  agg.media_min_entre_gols = agg.gols > 0 ? Math.round(agg.minutos / agg.gols) : null;
  const ult = passagens[passagens.length - 1]?.stats || {};
  agg.amarelos_acumulados = ult.amarelos_acumulados || 0;
  agg.suspensao_pendente = !!ult.suspensao_pendente;
  agg.estatisticas_avancadas = agregaEstatisticasAvancadas(passagens);
  agg.jogos_com_scout = Number(agg.estatisticas_avancadas.jogos_com_scout || agg.jogos_com_scout || 0);
  return agg;
}

function agregaEstatisticasAvancadas(passagens) {
  const totals = {};
  const weighted = {};
  let jogosComScout = 0;

  const addWeighted = (key, value, weight) => {
    const w = weight || 1;
    if (!weighted[key]) weighted[key] = { sum: 0, weight: 0 };
    weighted[key].sum += value * w;
    weighted[key].weight += w;
  };

  (passagens || []).forEach(p => {
    const stats = p?.stats || {};
    const source = stats.estatisticas_avancadas || {};
    const sourceKeys = Object.keys(source);
    const scoutGames = statNumber(stats.jogos_com_scout ?? source.jogos_com_scout) || 0;
    const weight = scoutGames || (sourceKeys.length ? 1 : 0);
    jogosComScout += scoutGames;

    Object.entries(source).forEach(([key, value]) => {
      if (key === "jogos_com_scout") return;
      const number = statNumber(value);
      if (number == null) return;
      const avgKey = normalizedAverageStatKey(key);
      if (avgKey || PLAYER_CONSOLIDATED_PERCENT_KEYS.has(key)) {
        addWeighted(avgKey || key, number, weight || 1);
        return;
      }
      totals[key] = (totals[key] || 0) + number;
    });
  });

  deriveAttempted(totals, "passes_tentados", "passes_certos", "passes_errados");
  deriveAttempted(totals, "cruzamentos_tentados", "cruzamentos_certos", "cruzamentos_errados");
  deriveAttempted(totals, "lancamentos_tentados", "lancamentos_certos", "lancamentos_errados");
  derivePrecision(totals, "precisao_passes", "passes_certos", "passes_tentados");
  derivePrecision(totals, "precisao_cruzamentos", "cruzamentos_certos", "cruzamentos_tentados");
  derivePrecision(totals, "precisao_lancamentos", "lancamentos_certos", "lancamentos_tentados");

  Object.entries(weighted).forEach(([key, item]) => {
    if (!item.weight) return;
    if (PLAYER_CONSOLIDATED_PERCENT_KEYS.has(key) && totals[key] != null) return;
    totals[key] = cleanStatNumber(item.sum / item.weight);
  });

  if (jogosComScout) totals.jogos_com_scout = cleanStatNumber(jogosComScout);
  return Object.fromEntries(
    Object.entries(totals).map(([key, value]) => [key, cleanStatNumber(value)])
  );
}

function normalizedAverageStatKey(key) {
  if (!PLAYER_CONSOLIDATED_AVERAGE_KEYS.has(key) && !String(key).endsWith("_media")) return null;
  if (key === "nota") return "nota_media";
  if (key === "nota_sofascore") return "nota_sofascore_media";
  if (String(key).endsWith("_media")) {
    const base = key.replace(/_media$/, "");
    if (PLAYER_CONSOLIDATED_PERCENT_KEYS.has(base)) return base;
  }
  return key;
}

function statNumber(value) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string") {
    const cleaned = value.trim().replace("%", "").replace(",", ".");
    if (!cleaned) return null;
    const number = Number(cleaned);
    return Number.isFinite(number) ? number : null;
  }
  return null;
}

function cleanStatNumber(value) {
  const number = statNumber(value);
  if (number == null) return value;
  const rounded = Math.round(number * 100) / 100;
  return Number.isInteger(rounded) ? rounded : rounded;
}

function deriveAttempted(totals, attemptedKey, madeKey, missedKey) {
  if (totals[attemptedKey] != null) return;
  const made = statNumber(totals[madeKey]);
  const missed = statNumber(totals[missedKey]);
  if (made != null && missed != null) totals[attemptedKey] = made + missed;
}

function derivePrecision(totals, outKey, madeKey, attemptedKey) {
  const made = statNumber(totals[madeKey]);
  const attempted = statNumber(totals[attemptedKey]);
  if (made != null && attempted) totals[outKey] = +(made / attempted * 100).toFixed(1);
}

function scoutConsolidadoRows(stats) {
  const scout = { ...(stats.estatisticas_avancadas || {}) };
  if (stats.jogos_com_scout && scout.jogos_com_scout == null) scout.jogos_com_scout = stats.jogos_com_scout;
  return Object.entries(scout)
    .filter(([, value]) => statNumber(value) != null)
    .map(([key, value]) => ({ key, value: cleanStatNumber(value) }))
    .sort((a, b) => {
      const ai = PLAYER_CONSOLIDATED_STAT_ORDER.indexOf(a.key);
      const bi = PLAYER_CONSOLIDATED_STAT_ORDER.indexOf(b.key);
      if (ai !== -1 || bi !== -1) return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
      return playerStatLabel(a.key).localeCompare(playerStatLabel(b.key), "pt-BR");
    });
}

// ============ Hero do jogador ============
function PlayerHero({ dados }) {
  const idade = calcIdade(dados.nascimento);
  return (
    <section className="player-hero">
      <div className="player-portrait">
        <PlayerAvatar nome={dados.nome} numero={dados.numero} size="xl" />
      </div>
      <div className="player-hero-info">
        <div className="hero-eyebrow">Acervo · Jogador</div>
        <h1 className="player-name">
          {dados.nome}
          {dados.capitao_atual && <span className="cap-badge" title="Capitão atual">C</span>}
        </h1>
        <div className="player-sub">
          {dados.nome_completo && dados.nome_completo !== dados.nome && (
            <em>{dados.nome_completo}</em>
          )}
        </div>
        <div className="player-meta-grid">
          <div className="pm"><span className="k">Posição</span><span className="v">{dados.posicao}</span></div>
          <div className="pm"><span className="k">Camisa</span><span className="v">{dados.numero != null ? `#${String(dados.numero).padStart(2,"0")}` : "—"}</span></div>
          <div className="pm"><span className="k">Nasc.</span><span className="v">{dados.nascimento}{idade?` · ${idade}a`:""}</span></div>
          <div className="pm"><span className="k">Naturalidade</span><span className="v">{dados.naturalidade}</span></div>
          {dados.altura_cm && <div className="pm"><span className="k">Altura</span><span className="v">{(dados.altura_cm/100).toFixed(2)} m</span></div>}
          {dados.pe && dados.pe !== "—" && <div className="pm"><span className="k">Perna</span><span className="v">{dados.pe}</span></div>}
          <div className="pm"><span className="k">Passagens</span><span className="v">{dados.passagens.length}</span></div>
          <div className="pm"><span className="k">Contratado de</span><span className="v">{dados.contratado_de}</span></div>
        </div>
      </div>
    </section>
  );
}

function calcIdade(nasc) {
  if (!nasc || nasc === "—") return null;
  const [d,m,y] = nasc.split("/").map(Number);
  if (!d || !m || !y) return null;
  const hoje = new Date(2026, 4, 15);
  let a = hoje.getFullYear() - y;
  if (hoje.getMonth()+1 < m || (hoje.getMonth()+1===m && hoje.getDate()<d)) a--;
  return a;
}

// Avatar do jogador — iniciais + número, estilo monograma editorial
function PlayerAvatar({ nome, numero, size = "md" }) {
  const initials = nome.split(/\s+/).filter(Boolean).slice(0,2).map(w=>w[0]).join("").toUpperCase();
  const klass = size === "xl" ? "player-avatar xl" : size === "lg" ? "player-avatar lg" : "player-avatar";
  return (
    <div className={klass}>
      <div className="pa-init">{initials}</div>
      {numero != null && <div className="pa-num">#{String(numero).padStart(2,"0")}</div>}
    </div>
  );
}

// ============ Corpo: presença, produção, disciplina, V/E/D, partidas ============
function PlayerBody({ stats, passagem, jogadorNome, onOpenPlayerMatch, aba }) {
  return (
    <div className="player-body">
      <PresencaPanel stats={stats} />
      <ProducaoPanel stats={stats} />
      <ScoutConsolidadoPanel stats={stats} />
      <SidePanel>
        <DisciplinaPanel stats={stats} />
        <VEDPanel ved={stats.ved} />
      </SidePanel>
      <PartidasPanel passagem={passagem} jogadorNome={jogadorNome} aba={aba} onOpenPlayerMatch={onOpenPlayerMatch} />
      <MetricasTabela stats={stats} passagem={passagem} aba={aba} />
    </div>
  );
}

function ScoutConsolidadoPanel({ stats }) {
  const rows = scoutConsolidadoRows(stats);
  if (!rows.length) return null;

  const featuredKeys = ["jogos_com_scout", "passes_certos", "passes_errados", "precisao_passes"];
  const featured = [
    ...featuredKeys.map(key => rows.find(row => row.key === key)).filter(Boolean),
    ...rows.filter(row => !featuredKeys.includes(row.key)),
  ].slice(0, 4);

  return (
    <section className="ppanel player-scout-panel">
      <h3 className="ppanel-title">Scout consolidado <small>soma das partidas com dados</small></h3>
      <div className="player-scout-kpis">
        {featured.map(row => (
          <div className="player-scout-kpi" key={row.key}>
            <span>{playerStatLabel(row.key)}</span>
            <strong>{formatPlayerStatValue(row.key, row.value)}</strong>
          </div>
        ))}
      </div>
      <div className="metric-table player-scout-table">
        {rows.map(row => (
          <div key={row.key} className="metric-row">
            <span className="metric-k">{playerStatLabel(row.key)}</span>
            <span className="metric-v">{formatPlayerStatValue(row.key, row.value)}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function SidePanel({ children }) {
  return <div className="player-sidegrid">{children}</div>;
}

// ----- Presença -----
function PresencaPanel({ stats }) {
  const total = stats.jogos_titular + stats.jogos_reserva + stats.nao_entrou + stats.nao_relacionado + stats.lesionado + stats.suspenso + stats.selecao;
  const segs = [
    { k:"titular",    label:"Titular",        n: stats.jogos_titular,    color:"var(--ink)" },
    { k:"reserva",    label:"Reserva",        n: stats.jogos_reserva,    color:"#6b3a1f" },
    { k:"ne",         label:"Não entrou",     n: stats.nao_entrou,       color:"#a89a7d" },
    { k:"nr",         label:"Não relacionado",n: stats.nao_relacionado,  color:"#d6c9a6" },
    { k:"les",        label:"Lesionado",      n: stats.lesionado,        color:"var(--r-d)" },
    { k:"sus",        label:"Suspenso",       n: stats.suspenso,         color:"var(--gold)" },
    { k:"sel",        label:"Seleção",        n: stats.selecao,          color:"var(--blue)" },
  ].filter(s => s.n > 0 || (s.k==="titular"||s.k==="reserva"));
  return (
    <section className="ppanel">
      <h3 className="ppanel-title">Presença</h3>
      <div className="ppanel-kpis">
        <KPI label="Jogos com participação" value={stats.jogos_participacao} />
        <KPI label="Minutos jogados" value={fmtN(stats.minutos)} unit="min" />
        <KPI label="Média de minutos" value={stats.media_minutos.toFixed(1)} unit="min/j" />
        <KPI label="Como capitão" value={stats.jogos_capitao} />
      </div>
      <div className="status-bar" aria-label="Distribuição de status por jogo">
        {segs.map(s => (
          <div key={s.k} className="status-seg" style={{ flex: s.n || 0, background: s.color }} title={`${s.label}: ${s.n}`}>
            {s.n >= Math.max(1, total*0.06) && <span className="seg-num">{s.n}</span>}
          </div>
        ))}
      </div>
      <div className="status-legend">
        {segs.map(s => (
          <span key={s.k} className="leg"><span className="dot" style={{background:s.color}}/>{s.label} <strong>{s.n}</strong></span>
        ))}
      </div>
    </section>
  );
}

// ----- Produção -----
function ProducaoPanel({ stats }) {
  return (
    <section className="ppanel">
      <h3 className="ppanel-title">Produção</h3>
      <div className="ppanel-kpis">
        <KPI label="Gols pelo Vasco" value={stats.gols} big />
        <KPI label="Assistências" value={stats.assistencias || 0} />
        <KPI label="Participações em gol" value={stats.participacoes_gol || ((stats.gols || 0) + (stats.assistencias || 0))} />
        <KPI label="Partidas em que marcou" value={stats.partidas_marcou} />
        <KPI label="Média gols/jogo" value={stats.media_gols.toFixed(2)} />
        <KPI label="Min. entre gols" value={stats.media_min_entre_gols ?? "—"} unit={stats.media_min_entre_gols ? "min" : ""} />
      </div>
      <div className="split-bar">
        <div className="split-row">
          <span className="split-lbl">Como titular</span>
          <span className="split-bar-track">
            <span className="split-bar-fill" style={{ width: pct(stats.gols_titular, Math.max(1, stats.gols)) }}/>
          </span>
          <span className="split-val">{stats.gols_titular}</span>
        </div>
        <div className="split-row">
          <span className="split-lbl">Saindo do banco</span>
          <span className="split-bar-track">
            <span className="split-bar-fill alt" style={{ width: pct(stats.gols_banco, Math.max(1, stats.gols)) }}/>
          </span>
          <span className="split-val">{stats.gols_banco}</span>
        </div>
      </div>
    </section>
  );
}

function pct(n, total) { return `${(n/total)*100}%`; }

// ----- Disciplina -----
function DisciplinaPanel({ stats }) {
  return (
    <section className="ppanel">
      <h3 className="ppanel-title">Disciplina</h3>
      <div className="discipline-row">
        <div className="card-stat yellow">
          <div className="card-icon"/>
          <div className="card-info">
            <div className="card-val">{stats.amarelos}</div>
            <div className="card-lbl">amarelos</div>
          </div>
        </div>
        <div className="card-stat red">
          <div className="card-icon"/>
          <div className="card-info">
            <div className="card-val">{stats.vermelhos}</div>
            <div className="card-lbl">vermelhos</div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ----- V/E/D -----
function VEDPanel({ ved }) {
  const total = ved.v + ved.e + ved.d || 1;
  return (
    <section className="ppanel">
      <h3 className="ppanel-title">Participação V/E/D <small>quando esteve em campo</small></h3>
      <div className="ved-big">
        <div className="ved-num v"><span className="n">{ved.v}</span><span className="l">vitórias</span></div>
        <div className="ved-num e"><span className="n">{ved.e}</span><span className="l">empates</span></div>
        <div className="ved-num d"><span className="n">{ved.d}</span><span className="l">derrotas</span></div>
      </div>
      <div className="ved-bar">
        <div style={{ flex: ved.v, background: "var(--r-v)" }}/>
        <div style={{ flex: ved.e, background: "var(--r-e)" }}/>
        <div style={{ flex: ved.d, background: "var(--r-d)" }}/>
      </div>
      <div className="ved-meta">
        Aproveitamento individual <strong>{((ved.v*3 + ved.e) / (total*3) * 100).toFixed(1)}%</strong>
      </div>
    </section>
  );
}

// ----- Partidas (lista por linha) -----
function PartidasPanel({ passagem, jogadorNome, onOpenPlayerMatch }) {
  const partidas = passagem.partidas || [];
  const [pageSize, setPageSize] = useState(10);
  const [page, setPage] = useState(1);

  useEffect(() => {
    setPage(1);
  }, [passagem?.id, pageSize]);

  const totalPages = Math.max(1, Math.ceil(partidas.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const start = (currentPage - 1) * pageSize;
  const pagePartidas = partidas.slice(start, start + pageSize);
  const firstRegistro = partidas.length ? start + 1 : 0;
  const lastRegistro = Math.min(partidas.length, start + pagePartidas.length);

  if (partidas.length === 0) {
    return (
      <section className="ppanel">
        <h3 className="ppanel-title">Partidas na passagem <small>{partidas.length} registros</small></h3>
        <div style={{padding:"30px 0", fontFamily:"var(--ff-serif)", fontStyle:"italic", color:"var(--ink-mute)", textAlign:"center"}}>
          Histórico partida-a-partida deste jogador ainda não foi migrado para o acervo web.
        </div>
      </section>
    );
  }
  return (
    <section className="ppanel">
      <div className="player-games-head">
        <h3 className="ppanel-title">Partidas na passagem <small>{partidas.length} registros</small></h3>
        <div className="player-games-pager">
          <span className="pager-range">{firstRegistro}-{lastRegistro} de {partidas.length}</span>
          <label>
            <span>por página</span>
            <select value={pageSize} onChange={(e)=>setPageSize(Number(e.target.value))}>
              {[10, 50, 100].map(n => <option key={n} value={n}>{n}</option>)}
            </select>
          </label>
          <button type="button" disabled={currentPage <= 1} onClick={()=>setPage(p => Math.max(1, p - 1))}>‹</button>
          <span className="pager-page">{currentPage}/{totalPages}</span>
          <button type="button" disabled={currentPage >= totalPages} onClick={()=>setPage(p => Math.min(totalPages, p + 1))}>›</button>
        </div>
      </div>
      <div className="table-wrap">
        <table className="tbl player-games">
          <thead>
            <tr>
              <th style={{width:90}}>Data</th>
              <th style={{width:28}}></th>
              <th>Adversário</th>
              <th style={{width:80}}>Placar</th>
              <th style={{width:90}}>Função</th>
              <th style={{width:70}}>Min.</th>
              <th style={{width:60}}>Gols</th>
              <th style={{width:80}}>Cartões</th>
            </tr>
          </thead>
          <tbody>
            {pagePartidas.map((p,i) => (
              <tr key={start + i} onClick={()=>onOpenPlayerMatch && onOpenPlayerMatch(p)} className="has-detail" title={`Ver detalhes de ${jogadorNome} nesta partida`}>
                <td className="date">{p.data}</td>
                <td className="result-cell"><span className={"result-dot " + p.res}/></td>
                <td className="opponent">
                  <Monogram club={p.adv} />
                  {p.adv}
                </td>
                <td className="score">{p.placar.replace("x","×")}</td>
                <td className="tecnico">
                  {p.status ? <span style={{color:"var(--ink-faint)", fontStyle:"italic"}}>{p.status}</span>
                            : p.titular ? "titular" : "reserva"}
                </td>
                <td className="tecnico">{p.minutos || "—"}</td>
                <td className="tecnico" style={{textAlign:"center"}}>{p.gols || ""}</td>
                <td>
                  {p.amarelo && <span className="cardlet yellow"/>}
                  {p.vermelho && <span className="cardlet red"/>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

// ----- Modal jogador x partida -----
const PLAYER_MATCH_BASE_KEYS = new Set([
  "id", "db_match_id", "data", "adv", "adversario", "competicao", "local",
  "placar", "res", "resultado", "titular", "minutos", "gols", "assistencias",
  "amarelo", "vermelho", "status", "passagem", "estatisticas", "stats",
]);

const PLAYER_MATCH_STAT_LABELS = {
  jogos_com_scout: "Jogos com scout",
  nota: "Nota",
  nota_media: "Nota média",
  nota_sofascore: "Nota SofaScore",
  nota_sofascore_media: "Nota SofaScore média",
  passes_certos: "Passes certos",
  passes_errados: "Passes errados",
  passes_tentados: "Passes tentados",
  precisao_passes: "Precisão de passes",
  posse_bola: "Posse de bola",
  finalizacoes: "Finalizações",
  finalizacoes_no_gol: "Finalizações no gol",
  finalizacoes_fora: "Finalizações fora",
  finalizacoes_bloqueadas: "Finalizações bloqueadas",
  chances_criadas: "Chances criadas",
  desarmes: "Desarmes",
  interceptacoes: "Interceptações",
  duelos_ganhos: "Duelos ganhos",
  duelos_aereos_ganhos: "Duelos aéreos ganhos",
  faltas_cometidas: "Faltas cometidas",
  faltas_recebidas: "Faltas recebidas",
  defesas: "Defesas",
  defesas_dificeis: "Defesas difíceis",
  gols_sofridos: "Gols sofridos",
  cruzamentos_certos: "Cruzamentos certos",
  cruzamentos_errados: "Cruzamentos errados",
  cruzamentos_tentados: "Cruzamentos tentados",
  precisao_cruzamentos: "Precisão de cruzamentos",
  lancamentos_certos: "Lançamentos certos",
  lancamentos_errados: "Lançamentos errados",
  lancamentos_tentados: "Lançamentos tentados",
  precisao_lancamentos: "Precisão de lançamentos",
};

const PLAYER_MATCH_STAT_ORDER = [
  "nota", "nota_sofascore",
  "passes_certos", "passes_errados", "passes_tentados", "precisao_passes",
  "finalizacoes", "finalizacoes_no_gol", "finalizacoes_fora", "finalizacoes_bloqueadas", "chances_criadas",
  "desarmes", "interceptacoes", "duelos_ganhos", "duelos_aereos_ganhos",
  "faltas_cometidas", "faltas_recebidas",
  "defesas", "defesas_dificeis", "gols_sofridos",
  "cruzamentos_certos", "cruzamentos_errados", "cruzamentos_tentados", "precisao_cruzamentos",
  "lancamentos_certos", "lancamentos_errados", "lancamentos_tentados", "precisao_lancamentos",
];

function PlayerMatchModal({ nome, row, onClose }) {
  useEffect(() => {
    const onKey = (event) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const partida = resolvePlayerMatchDetail(row);
  const scout = playerAdvancedStats(nome, row, partida);
  const scoutGroups = groupPlayerStats(scout);
  const funcao = playerMatchRole(row);
  const posicao = playerMatchPosition(nome, partida);
  const gols = playerGoalsInMatch(nome, row, partida);
  const assistencias = playerAssistsInMatch(nome, row, partida);
  const amarelos = playerYellowCardsInMatch(nome, row, partida);
  const vermelhos = playerRedCardsInMatch(nome, row, partida);
  const substituicoes = playerSubstitutions(nome, partida);
  const resultado = row.res || resultFromDetail(partida);
  const placar = playerMatchScore(row, partida);
  const capitao = namesEqual(partida.capitao, nome);

  return (
    <div className="player-match-backdrop" onClick={onClose}>
      <article className="player-match-modal" role="dialog" aria-modal="true" aria-label={`Detalhes de ${nome} na partida`} onClick={(e)=>e.stopPropagation()}>
        <button type="button" className="player-match-close" onClick={onClose} aria-label="Fechar">×</button>
        <header className="player-match-header">
          <div>
            <div className="hero-eyebrow">Jogador · partida</div>
            <h2>{nome}</h2>
            <div className="player-match-sub">
              {partida.data} · {partida.competicao || "—"} · {partida.estadio || "—"}
            </div>
          </div>
          <div className="player-match-score">
            <Monogram club="Vasco" vasco />
            <span>{placar}</span>
            <Monogram club={partida.adversario || row.adv || "Adversário"} />
          </div>
        </header>

        <div className="player-match-summary">
          <PlayerMatchStat label="Resultado" value={RESULT_LABELS[resultado] || resultado || "—"} tone={resultado} />
          <PlayerMatchStat label="Função" value={funcao} />
          <PlayerMatchStat label="Posição" value={posicao || "—"} />
          <PlayerMatchStat label="Minutos" value={row.minutos || 0} />
          <PlayerMatchStat label="Capitão" value={capitao ? "Sim" : "Não"} />
        </div>

        <section className="player-match-section">
          <h3>Participação direta</h3>
          <div className="player-match-summary compact">
            <PlayerMatchStat label="Gols" value={gols.length || Number(row.gols || 0)} />
            <PlayerMatchStat label="Assistências" value={assistencias.length || Number(row.assistencias || 0)} />
            <PlayerMatchStat label="Amarelos" value={amarelos.length || (row.amarelo ? 1 : 0)} />
            <PlayerMatchStat label="Vermelhos" value={vermelhos.length || (row.vermelho ? 1 : 0)} />
          </div>
          <PlayerMatchEventList
            gols={gols}
            assistencias={assistencias}
            amarelos={amarelos}
            vermelhos={vermelhos}
            substituicoes={substituicoes}
            capitao={capitao}
          />
        </section>

        <section className="player-match-section">
          <h3>Scout detalhado</h3>
          {scoutGroups.length ? (
            <div className="player-match-stat-groups">
              {scoutGroups.map(group => (
                <div className="player-match-stat-group" key={group.title}>
                  <h4>{group.title}</h4>
                  <div className="player-match-stat-grid">
                    {group.items.map(([key, value]) => (
                      <div className="player-match-scout" key={key}>
                        <span>{playerStatLabel(key)}</span>
                        <strong>{formatPlayerStatValue(key, value)}</strong>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="player-match-empty">
              Scout individual avançado ainda não informado para este jogador nesta partida.
            </div>
          )}
        </section>

        <section className="player-match-context">
          <div><span>Técnico</span><strong>{partida.tecnico || "—"}</strong></div>
          <div><span>Capitão do jogo</span><strong>{partida.capitao || "—"}</strong></div>
          <div><span>Adversário</span><strong>{partida.adversario || row.adv || "—"}</strong></div>
          <div><span>Local</span><strong>{partida.local === "fora" ? "Visitante" : "Casa"}</strong></div>
        </section>
      </article>
    </div>
  );
}

function PlayerMatchStat({ label, value, tone }) {
  return (
    <div className={"player-match-mini" + (tone ? ` tone-${tone}` : "")}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

const RESULT_LABELS = { V: "Vitória", E: "Empate", D: "Derrota" };

function PlayerMatchEventList({ gols, assistencias, amarelos, vermelhos, substituicoes, capitao }) {
  const items = [
    ...gols.map(g => ({ icon: "G", label: "Gol", detail: playerEventDetail(g) })),
    ...assistencias.map(g => ({ icon: "A", label: "Assistência", detail: playerEventDetail(g, `gol de ${g.nome}`) })),
    ...amarelos.map(c => ({ icon: "", cls: "yellow", label: "Cartão amarelo", detail: playerEventDetail(c) })),
    ...vermelhos.map(c => ({ icon: "", cls: "red", label: "Cartão vermelho", detail: playerEventDetail(c) })),
    ...substituicoes.map(s => ({ icon: "↔", label: s.label, detail: s.detail })),
    ...(capitao ? [{ icon: "C", label: "Capitão", detail: "Iniciou ou foi registrado como capitão da partida" }] : []),
  ];
  if (!items.length) {
    return <div className="player-match-empty small">Sem eventos individuais registrados.</div>;
  }
  return (
    <div className="player-match-events">
      {items.map((item, index) => (
        <div className="player-match-event" key={index}>
          <span className={"player-match-event-icon " + (item.cls || "")}>{item.icon}</span>
          <span>
            <strong>{item.label}</strong>
            <small>{item.detail || "Sem minuto informado"}</small>
          </span>
        </div>
      ))}
    </div>
  );
}

function resolvePlayerMatchDetail(row) {
  const detalhes = window.PARTIDAS_DETALHES || {};
  const idKey = row?.id != null ? String(row.id) : row?.db_match_id != null ? String(row.db_match_id) : "";
  const adv = row?.adv || row?.adversario || "";
  return (idKey && detalhes[idKey])
    || detalhes[`${row?.data || ""}|${adv}`]
    || buildPlayerMatchStub(row);
}

function buildPlayerMatchStub(row) {
  const [v, a] = scoreFromRow(row);
  return {
    id: row?.id,
    data: row?.data || "—",
    adversario: row?.adv || row?.adversario || "Adversário",
    competicao: row?.competicao || "—",
    local: row?.local || "casa",
    estadio: "—",
    horario: "—",
    tecnico: "—",
    capitao: "—",
    placar: { vasco: v, adversario: a },
    gols_vasco: [],
    cartoes_amarelos_vasco: [],
    cartoes_vermelhos_vasco: [],
    estatisticas_jogadores_vasco: [],
    escalacao: { titulares_por_posicao: {}, substituicoes: [] },
  };
}

function scoreFromRow(row) {
  const raw = String(row?.placar || "");
  const found = raw.match(/(\d+)\D+(\d+)/);
  return found ? [Number(found[1]), Number(found[2])] : [0, 0];
}

function playerMatchScore(row, partida) {
  if (partida?.placar && typeof partida.placar === "object") {
    return `Vasco ${Number(partida.placar.vasco || 0)} × ${Number(partida.placar.adversario || 0)} ${partida.adversario || row.adv || ""}`.trim();
  }
  return String(row.placar || "—").replace(/x/g, "×");
}

function resultFromDetail(partida) {
  const v = Number(partida?.placar?.vasco || 0);
  const a = Number(partida?.placar?.adversario || 0);
  return v > a ? "V" : v < a ? "D" : "E";
}

function normalizePlayerName(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s*\(contra\)\s*$/i, "")
    .replace(/[^\w\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function namesEqual(a, b) {
  return normalizePlayerName(a) === normalizePlayerName(b);
}

function playerMatchRole(row) {
  if (row.status) return capitalizeStatus(row.status);
  if (row.titular) return "Titular";
  if (Number(row.minutos || 0) > 0) return "Entrou do banco";
  return "Reserva";
}

function capitalizeStatus(value) {
  const txt = String(value || "").trim();
  return txt ? txt.charAt(0).toUpperCase() + txt.slice(1) : "—";
}

function playerMatchPosition(nome, partida) {
  const titulares = partida?.escalacao?.titulares_por_posicao || {};
  for (const [pos, nomes] of Object.entries(titulares)) {
    if (Array.isArray(nomes) && nomes.some(n => namesEqual(n, nome))) return pos;
  }
  return window.JOGADORES?.[nome]?.posicao || "—";
}

function playerSubstitutions(nome, partida) {
  const subs = partida?.escalacao?.substituicoes || [];
  return subs
    .filter(s => namesEqual(s.sai || s.jogador_saiu, nome) || namesEqual(s.entra || s.jogador_entrou, nome))
    .map(s => {
      const saiu = s.sai || s.jogador_saiu || "";
      const entrou = s.entra || s.jogador_entrou || "";
      const minuto = playerEventMinute(s);
      if (namesEqual(entrou, nome)) {
        return { label: "Entrou", detail: `${minuto}${saiu ? ` no lugar de ${saiu}` : ""}` };
      }
      return { label: "Saiu", detail: `${minuto}${entrou ? ` para entrada de ${entrou}` : ""}` };
    });
}

function playerGoalsInMatch(nome, row, partida) {
  const goals = (partida?.gols_vasco || []).filter(g => namesEqual(g.nome, nome));
  if (goals.length) return goals;
  return Number(row.gols || 0) > 0 ? Array.from({ length: Number(row.gols) }, () => ({ nome })) : [];
}

function playerAssistsInMatch(nome, row, partida) {
  const assists = (partida?.gols_vasco || []).filter(g => namesEqual(g.assistencia, nome));
  if (assists.length) return assists;
  return Number(row.assistencias || 0) > 0 ? Array.from({ length: Number(row.assistencias) }, () => ({ assistencia: nome })) : [];
}

function playerYellowCardsInMatch(nome, row, partida) {
  const cards = (partida?.cartoes_amarelos_vasco || []).filter(c => namesEqual(cardName(c), nome));
  if (cards.length) return cards;
  return row.amarelo ? [{ nome }] : [];
}

function playerRedCardsInMatch(nome, row, partida) {
  const cards = (partida?.cartoes_vermelhos_vasco || []).filter(c => namesEqual(cardName(c), nome));
  if (cards.length) return cards;
  return row.vermelho ? [{ nome }] : [];
}

function cardName(card) {
  return typeof card === "string" ? card : card?.nome;
}

function playerEventMinute(event) {
  if (event?.minuto == null || event.minuto === "") return "Sem minuto";
  return `${event.minuto}'${event.periodo ? `/${event.periodo}` : ""}`;
}

function playerEventDetail(event, fallback) {
  const min = playerEventMinute(event);
  return fallback ? `${min} · ${fallback}` : min;
}

function playerAdvancedStats(nome, row, partida) {
  const merged = {};
  if (row.stats && typeof row.stats === "object") Object.assign(merged, row.stats);
  if (row.estatisticas && typeof row.estatisticas === "object") Object.assign(merged, row.estatisticas);
  Object.entries(row || {}).forEach(([key, value]) => {
    if (!PLAYER_MATCH_BASE_KEYS.has(key) && hasStatValue(value) && (typeof value !== "object" || Array.isArray(value))) {
      merged[key] = value;
    }
  });
  Object.assign(merged, playerAdvancedStatsFromDetail(nome, partida));
  delete merged.nome;
  return Object.fromEntries(Object.entries(merged).filter(([, value]) => hasStatValue(value)));
}

function playerAdvancedStatsFromDetail(nome, partida) {
  const raw = partida?.estatisticas_jogadores_vasco;
  if (Array.isArray(raw)) {
    const found = raw.find(item => item && typeof item === "object" && namesEqual(item.nome, nome));
    return found ? { ...found } : {};
  }
  if (raw && typeof raw === "object") {
    const entry = Object.entries(raw).find(([key]) => namesEqual(key, nome));
    return entry && entry[1] && typeof entry[1] === "object" ? { ...entry[1], nome: entry[0] } : {};
  }
  return {};
}

function hasStatValue(value) {
  if (value == null || value === "") return false;
  if (Array.isArray(value)) return value.length > 0;
  return true;
}

function groupPlayerStats(stats) {
  const entries = Object.entries(stats).sort(([a], [b]) => {
    const ai = PLAYER_MATCH_STAT_ORDER.indexOf(a);
    const bi = PLAYER_MATCH_STAT_ORDER.indexOf(b);
    if (ai !== -1 || bi !== -1) return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
    return playerStatLabel(a).localeCompare(playerStatLabel(b), "pt-BR");
  });
  const groups = [
    ["Passe", ([key]) => /passe|passes|cruzamento|lancamento|lançamento/.test(key)],
    ["Ataque", ([key]) => /finalizacao|finalização|chances|gol|assist/.test(key)],
    ["Defesa", ([key]) => /desarme|intercept|duelo|falta|defesa|gols_sofridos/.test(key)],
  ];
  const used = new Set();
  const out = groups.map(([title, test]) => {
    const items = entries.filter(entry => !used.has(entry[0]) && test(entry));
    items.forEach(([key]) => used.add(key));
    return { title, items };
  }).filter(group => group.items.length);
  const other = entries.filter(([key]) => !used.has(key));
  if (other.length) out.push({ title: "Outros", items: other });
  return out;
}

function playerStatLabel(key) {
  if (PLAYER_MATCH_STAT_LABELS[key]) return PLAYER_MATCH_STAT_LABELS[key];
  return String(key || "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, ch => ch.toUpperCase());
}

function formatPlayerStatValue(key, value) {
  if (typeof value === "boolean") return value ? "Sim" : "Não";
  if (typeof value === "number") {
    const suffix = /precisao|precisão|pct|percent/.test(key) ? "%" : "";
    return `${value.toLocaleString("pt-BR")}${suffix}`;
  }
  if (Array.isArray(value)) return value.join(", ");
  if (value && typeof value === "object") return JSON.stringify(value);
  return String(value);
}

// ----- Tabela métrica/valor completa (paridade com o app antigo) -----
function MetricasTabela({ stats, passagem, aba }) {
  const scoutLinhas = scoutConsolidadoRows(stats).map(row => [
    `Scout · ${playerStatLabel(row.key)}`,
    formatPlayerStatValue(row.key, row.value),
  ]);
  const linhas = [
    ["Data de estreia no Vasco", passagem.estreia],
    ["Data de saída",            passagem.saida],
    ["Passagens pelo Vasco",     aba==="geral" ? "todas" : `passagem ${passagem.idx}`],
    ["Jogos com participação",   stats.jogos_participacao],
    ["Minutos jogados",          fmtN(stats.minutos)],
    ["Média de minutos jogados", stats.media_minutos.toFixed(2)],
    ["Jogos como titular",       stats.jogos_titular],
    ["Jogos como reserva",       stats.jogos_reserva],
    ["Foi para o jogo e não entrou", stats.nao_entrou],
    ["Jogos como não relacionado", stats.nao_relacionado],
    ["Jogos como lesionado",     stats.lesionado],
    ["Jogos como suspenso",      stats.suspenso],
    ["Jogos servindo a seleção", stats.selecao],
    ["Gols pelo Vasco",          stats.gols],
    ["Assistências",             stats.assistencias || 0],
    ["Participações em gol",     stats.participacoes_gol || ((stats.gols || 0) + (stats.assistencias || 0))],
    ["Jogos como capitão",       stats.jogos_capitao],
    ["Partidas em que marcou",   stats.partidas_marcou],
    ["Partidas com assistência", stats.partidas_assistencia || 0],
    ["Gols como titular",        stats.gols_titular],
    ["Gols saindo do banco",     stats.gols_banco],
    ["Média de gols por jogo",   stats.media_gols.toFixed(2)],
    ["Cartões amarelos",         stats.amarelos],
    ["Cartões vermelhos",        stats.vermelhos],
    ["Média de minutos entre gols", stats.media_min_entre_gols ?? "—"],
    ["Participação (V/E/D)",     `${stats.ved.v}/${stats.ved.e}/${stats.ved.d}`],
    ...scoutLinhas,
  ];
  return (
    <section className="ppanel collapse-tbl">
      <h3 className="ppanel-title">Métricas detalhadas <small>todas as linhas do acervo</small></h3>
      <div className="metric-table">
        {linhas.map(([k,v]) => (
          <div key={k} className="metric-row">
            <span className="metric-k">{k}</span>
            <span className="metric-v">{v}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

// ============ helper KPI ============
function KPI({ label, value, unit, big }) {
  return (
    <div className={"kpi-cell" + (big ? " big" : "")}>
      <div className="kpi-cell-val">
        {value}
        {unit && <span className="kpi-cell-unit"> {unit}</span>}
      </div>
      <div className="kpi-cell-lbl">{label}</div>
    </div>
  );
}

window.Jogador = Jogador;
window.PlayerAvatar = PlayerAvatar;
