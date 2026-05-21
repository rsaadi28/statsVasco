// Acervo Vasco — Comparativo: temporada atual vs ano anterior (mesmo nº de jogos)

const COMP_TABS = [
  { id: "totais",      label: "Totais",                         competicao: null },
  { id: "brasileiro",  label: "Brasileirão",                    competicao: "Campeonato Brasileiro Série A", isLeague: true },
  { id: "carioca",     label: "Carioca",                        competicao: "Campeonato Carioca" },
  { id: "copabr",      label: "Copa do Brasil",                 competicao: "Copa do Brasil" },
  { id: "sulam",       label: "Sul-Americana",                  competicao: "Copa Sul-Americana" },
];

function normalizeCompeticaoName(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function competicaoKey(value) {
  const norm = normalizeCompeticaoName(value);
  if (!norm) return "";
  if (norm.includes("campeonato brasileiro") && norm.includes("serie a")) return "brasileiro-a";
  if (norm.includes("campeonato brasileiro") && norm.includes("serie b")) return "brasileiro-b";
  if (norm.includes("campeonato carioca")) return "carioca";
  if (norm.includes("copa do brasil")) return "copa-do-brasil";
  if (norm.includes("sul americana")) return "sul-americana";
  return norm;
}

function sameCompeticao(value, target) {
  return !target || competicaoKey(value) === competicaoKey(target);
}

function Comparativo() {
  const [tab, setTab] = useState("totais");
  const [anoComp, setAnoComp] = useState(2025);
  const ativo = COMP_TABS.find(c => c.id === tab);

  const series = useMemo(
    () => buildSeries(window.SEASON_2026, window.SEASON_2025_TOTALS, ativo.competicao, anoComp),
    [ativo, anoComp]
  );

  return (
    <div className="main">
      <CmpHero ativo={ativo} series={series} anoComp={anoComp} setAnoComp={setAnoComp} />
      <CmpSubtabs tab={tab} setTab={setTab} />
      <CmpBody ativo={ativo} series={series} anoComp={anoComp} />
    </div>
  );
}

// Constrói as séries acumulativas filtradas por competição
function buildSeries(season26, season25, competicao, anoComparacao) {
  // 2026 — pega do SEASON_2026.jogos (ordem cronológica) e normaliza o campo de resultado
  const jogos26 = season26.jogos
    .filter(j => sameCompeticao(j.competicao, competicao))
    .map(j => ({
      placar: j.placar,
      res: j.resultado,
      rodada: j.rodada,
      posicao: j.posicao,
      competicao: j.competicao,
    }));

  // Ano anterior — usa data-2025 quando é 2025, senão gera de YEARLY totals
  let jogosPrev = [];
  if (anoComparacao === 2025 && season25?.jogos) {
    jogosPrev = season25.jogos
      .filter(j => sameCompeticao(j.competicao, competicao))
      .map(j => ({
        placar: j.placar, res: j.res, rodada: j.rodada, posicao: j.posicao, competicao: j.competicao,
      }));
  } else if (window.gameSeriesForYear) {
    // gera série sintética a partir de YEARLY
    const ser = window.gameSeriesForYear(anoComparacao) || [];
    jogosPrev = ser.map(s => ({
      placar: [s.gp, s.gc],
      res: s.res,
      rodada: null,
      posicao: null,
      competicao: null,
    }));
    if (competicao) jogosPrev = []; // sem dados por competição em anos antigos
  }

  // recorte do mesmo número de jogos
  const n = jogos26.length;
  const jogosPrevCut = jogosPrev.slice(0, n);

  return {
    competicao,
    anoComparacao,
    n_atual: n,
    jogos26,
    jogos25: jogosPrevCut,
    jogos25_full: jogosPrev,
    acc26: accumulate(jogos26),
    acc25: accumulate(jogosPrevCut),
    totals26: totals(jogos26),
    totals25: totals(jogosPrevCut),
  };
}

function accumulate(jogos) {
  let v=0,e=0,d=0,gp=0,gc=0,pts=0;
  const series = jogos.map((j, idx) => {
    if (j.res==="V"){ v++; pts+=3; }
    else if (j.res==="E"){ e++; pts+=1; }
    else d++;
    gp += j.placar[0]; gc += j.placar[1];
    return {
      i: idx + 1,
      v, e, d, gp, gc, pts, saldo: gp - gc,
      posicao: j.posicao ?? null, // só Brasileirão
      rodada:  j.rodada  ?? null,
    };
  });
  return series;
}

function totals(jogos) {
  const t = { jogos: jogos.length, v:0, e:0, d:0, gp:0, gc:0, pts:0 };
  jogos.forEach(j => {
    if (j.res==="V"){ t.v++; t.pts+=3; }
    else if (j.res==="E"){ t.e++; t.pts+=1; }
    else t.d++;
    t.gp += j.placar[0]; t.gc += j.placar[1];
  });
  t.saldo = t.gp - t.gc;
  t.aprov = t.jogos ? ((t.v*3 + t.e) / (t.jogos*3)) * 100 : 0;
  t.media_gp = t.jogos ? t.gp / t.jogos : 0;
  t.media_gc = t.jogos ? t.gc / t.jogos : 0;
  return t;
}

// ============ Hero ============
function CmpHero({ ativo, series, anoComp, setAnoComp }) {
  const t26 = series.totals26;
  const t25 = series.totals25;
  // anos selecionáveis: todos os do acervo menos o atual
  const anosSel = useMemo(() => {
    const out = [];
    for (let y = 2025; y >= 2000; y--) out.push(y);
    return out;
  }, []);
  return (
    <section className="cmp-hero">
      <div className="hero-eyebrow">Acervo · Comparativo</div>
      <div className="cmp-hero-line">
        <div className="cmp-hero-years">
          <span className="cmp-y26">2026</span>
          <span className="cmp-vs">vs</span>
          <span className="cmp-year-picker">
            <select value={anoComp} onChange={(e)=>setAnoComp(Number(e.target.value))}>
              {anosSel.map(y => <option key={y} value={y}>{y}</option>)}
            </select>
            <span className="cmp-y25">{anoComp}</span>
          </span>
        </div>
        <div className="cmp-hero-meta">
          <div className="cmp-pill">
            {ativo.id === "totais"
              ? <><strong>{series.n_atual}</strong> jogos comparados aos primeiros <strong>{series.n_atual}</strong> de {anoComp}</>
              : ativo.isLeague
                ? <>Rodada <strong>{series.n_atual}</strong> registrada no Brasileirão · mesma rodada em {anoComp}</>
                : <><strong>{series.n_atual}</strong> jogo(s) em <strong>{ativo.label}</strong> · mesmo recorte em {anoComp}</>
            }
          </div>
          {ativo.isLeague && <PosicaoBadges series={series} anoComp={anoComp} />}
        </div>
      </div>
    </section>
  );
}

function PosicaoBadges({ series, anoComp }) {
  const lastWithPos = [...series.acc26].reverse().find(s => s.posicao != null);
  const pos26 = lastWithPos?.posicao ?? null;
  const rodada = lastWithPos?.rodada ?? series.n_atual;
  const sameRodada25 = series.acc25.find(s => s.rodada === rodada);
  const pos25 = sameRodada25?.posicao ?? null;
  const delta = (pos26 != null && pos25 != null) ? pos25 - pos26 : null; // positivo = subiu
  return (
    <div className="cmp-pos">
      <div className="cmp-pos-cell now">
        <div className="cmp-pos-lbl">Posição atual</div>
        <div className="cmp-pos-val">{pos26 ?? "—"}</div>
      </div>
      <div className="cmp-pos-cell prev">
        <div className="cmp-pos-lbl">Rod. {rodada} · {anoComp}</div>
        <div className="cmp-pos-val">{pos25 ?? "—"}</div>
      </div>
      {delta != null && (
        <div className={"cmp-pos-cell delta " + (delta > 0 ? "up" : delta < 0 ? "down" : "even")}>
          <div className="cmp-pos-lbl">Variação</div>
          <div className="cmp-pos-val">{delta > 0 ? `▲ ${delta}` : delta < 0 ? `▼ ${Math.abs(delta)}` : "—"}</div>
        </div>
      )}
    </div>
  );
}

// ============ Subtabs ============
function CmpSubtabs({ tab, setTab }) {
  return (
    <nav className="cmp-tabs">
      {COMP_TABS.map(c => (
        <button key={c.id} className={tab===c.id?"active":""} onClick={()=>setTab(c.id)}>
          {c.label}
        </button>
      ))}
    </nav>
  );
}

// ============ Body ============
function CmpBody({ ativo, series, anoComp }) {
  const t26 = series.totals26;
  const t25 = series.totals25;
  if (series.n_atual === 0) {
    return (
      <div style={{padding:"60px 0", textAlign:"center", border:"1px dashed var(--rule)", background:"var(--paper-card)", fontFamily:"var(--ff-serif)", fontSize:17, fontStyle:"italic", color:"var(--ink-mute)"}}>
        Sem jogos registrados em <strong style={{color:"var(--ink)", fontStyle:"normal"}}>{ativo.label}</strong> em 2026 ainda.
      </div>
    );
  }
  return (
    <div className="cmp-body">
      <CmpDuelGrid t26={t26} t25={t25} isLeague={ativo.isLeague} anoComp={anoComp} />
      <div className="cmp-charts">
        <CmpChart
          title="Evolução de gols"
          subtitle="acumulado a cada jogo"
          series={series}
          metrics={[
            { key:"gp", label:"Gols pró",   color26:"var(--r-v)", color25:"#9bb978" },
            { key:"gc", label:"Gols contra",color26:"var(--r-d)", color25:"#d49e8f" },
          ]}
        />
        <CmpChart
          title="Saldo de gols"
          subtitle="acumulado"
          series={series}
          metrics={[
            { key:"saldo", label:"Saldo", color26:"var(--ink)", color25:"var(--ink-faint)" },
          ]}
          zeroLine
        />
        <CmpChart
          title="Vitórias acumuladas"
          subtitle="V por jogo"
          series={series}
          metrics={[
            { key:"v", label:"Vitórias", color26:"var(--r-v)", color25:"#9bb978" },
          ]}
        />
        <CmpChart
          title="Empates × Derrotas"
          subtitle="acumulado"
          series={series}
          metrics={[
            { key:"e", label:"Empates",  color26:"var(--r-e)", color25:"#d6c089" },
            { key:"d", label:"Derrotas", color26:"var(--r-d)", color25:"#d49e8f" },
          ]}
        />
        {ativo.isLeague && (
          <CmpPosicaoChart series={series} />
        )}
      </div>
    </div>
  );
}

// ============ Duel grid ============
function CmpDuelGrid({ t26, t25, isLeague, anoComp }) {
  // métricas no estilo da imagem original, com a tipografia editorial
  const baseRows = [
    { k:"jogos", label:"Jogos",            v26:t26.jogos, v25:t25.jogos, kind:"int", invert:false, isCount:true },
    ...(isLeague ? [{ k:"pts", label:"Pontos", v26:t26.pts, v25:t25.pts, kind:"int", invert:false }] : []),
    { k:"v",     label:"Vitórias",         v26:t26.v,     v25:t25.v,     kind:"int", invert:false },
    { k:"e",     label:"Empates",          v26:t26.e,     v25:t25.e,     kind:"int", invert:false },
    { k:"d",     label:"Derrotas",         v26:t26.d,     v25:t25.d,     kind:"int", invert:true },
    { k:"gp",    label:"Gols pró",         v26:t26.gp,    v25:t25.gp,    kind:"int", invert:false },
    { k:"gc",    label:"Gols contra",      v26:t26.gc,    v25:t25.gc,    kind:"int", invert:true },
    { k:"saldo", label:"Saldo",            v26:t26.saldo, v25:t25.saldo, kind:"signed", invert:false },
    { k:"aprov", label:"Aproveitamento",   v26:t26.aprov, v25:t25.aprov, kind:"pct", invert:false },
    { k:"mgp",   label:"Média gols pró",   v26:t26.media_gp, v25:t25.media_gp, kind:"dec2", invert:false },
    { k:"mgc",   label:"Média gols contra",v26:t26.media_gc, v25:t25.media_gc, kind:"dec2", invert:true },
  ];

  return (
    <section className="cmp-duel">
      <div className="cmp-duel-head">
        <div className="cmp-duel-th label">Métrica</div>
        <div className="cmp-duel-th y25">{anoComp || 2025}</div>
        <div className="cmp-duel-th y26">2026</div>
        <div className="cmp-duel-th delta">Diferença</div>
      </div>
      {baseRows.map(r => <CmpDuelRow key={r.k} row={r} />)}
    </section>
  );
}

function fmtVal(v, kind) {
  if (v == null) return "—";
  if (kind === "pct")  return v.toFixed(1) + "%";
  if (kind === "dec2") return v.toFixed(2);
  if (kind === "signed") return (v > 0 ? "+" : "") + v;
  return Math.round(v);
}
function CmpDuelRow({ row }) {
  const diff = row.v26 - row.v25;
  let direction = "even";
  if (diff !== 0) {
    if (row.isCount) direction = "even"; // jogos: contagem é igual no recorte; sem cor
    else direction = (diff > 0) !== row.invert ? "up" : "down";
  }
  const arrow = diff > 0 ? "▲" : diff < 0 ? "▼" : "—";
  return (
    <div className={"cmp-duel-row dir-" + direction}>
      <div className="cmp-duel-cell label">{row.label}</div>
      <div className="cmp-duel-cell y25">{fmtVal(row.v25, row.kind)}</div>
      <div className="cmp-duel-cell y26">{fmtVal(row.v26, row.kind)}</div>
      <div className="cmp-duel-cell delta">
        <span className="cmp-arrow">{arrow}</span>
        <span className="cmp-delta-num">{diff === 0 ? "0" : fmtVal(diff, row.kind === "pct" ? "pct" : row.kind === "dec2" ? "dec2" : "signed")}</span>
      </div>
    </div>
  );
}

// ============ Linhas comparativas (cumulativas) ============
function CmpChart({ title, subtitle, series, metrics, zeroLine }) {
  const W = 560, H = 220, padX = 36, padY = 22;
  const n = Math.max(series.acc26.length, series.acc25.length);
  if (n === 0) return null;

  const allValues = [];
  metrics.forEach(m => {
    series.acc26.forEach(s => allValues.push(s[m.key]));
    series.acc25.forEach(s => allValues.push(s[m.key]));
  });
  let yMin = Math.min(0, ...allValues);
  let yMax = Math.max(1, ...allValues);
  if (zeroLine) { yMin = Math.min(yMin, 0); yMax = Math.max(yMax, 0); }
  const yPad = (yMax - yMin) * 0.08 || 1;
  yMin -= yPad; yMax += yPad;
  const yRange = yMax - yMin || 1;

  function x(i) { return padX + ((i-1) / Math.max(1, n-1)) * (W - padX*2); }
  function y(v) { return padY + (H - padY*2) - ((v - yMin) / yRange) * (H - padY*2); }

  function pathFor(seriesArr, key) {
    if (!seriesArr || seriesArr.length === 0) return "";
    return seriesArr.map((s, idx) => {
      const px = x(s.i);
      const py = y(s[key]);
      return (idx === 0 ? "M" : "L") + px.toFixed(1) + "," + py.toFixed(1);
    }).join(" ");
  }

  const yTicks = niceTicks(yMin, yMax, 4);

  return (
    <section className="cmp-chart">
      <div className="cmp-chart-head">
        <h4>{title}</h4>
        <small>{subtitle}</small>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="cmp-svg" preserveAspectRatio="xMidYMid meet">
        {/* gridlines */}
        {yTicks.map((t,i) => (
          <g key={i}>
            <line x1={padX} x2={W-padX} y1={y(t)} y2={y(t)} stroke="#d6c9a6" strokeWidth="0.6" strokeDasharray="2 3"/>
            <text x={padX-6} y={y(t)+3.5} textAnchor="end" fontFamily="JetBrains Mono" fontSize="9" fill="#7a6f59">{t}</text>
          </g>
        ))}
        {zeroLine && (
          <line x1={padX} x2={W-padX} y1={y(0)} y2={y(0)} stroke="#15110b" strokeWidth="0.8" />
        )}
        {/* x axis labels */}
        {xTicks(n).map((i, k) => (
          <text key={k} x={x(i)} y={H-padY+12} textAnchor="middle" fontFamily="JetBrains Mono" fontSize="9" fill="#7a6f59">{i}</text>
        ))}
        {/* 2025 dashed (background) */}
        {metrics.map(m => (
          <path key={"25"+m.key} d={pathFor(series.acc25, m.key)} stroke={m.color25} strokeWidth="1.6" strokeDasharray="4 3" fill="none" strokeLinejoin="round" strokeLinecap="round" />
        ))}
        {/* 2026 solid */}
        {metrics.map(m => (
          <path key={"26"+m.key} d={pathFor(series.acc26, m.key)} stroke={m.color26} strokeWidth="2.2" fill="none" strokeLinejoin="round" strokeLinecap="round" />
        ))}
        {/* dots no último ponto 2026 */}
        {metrics.map(m => {
          const last = series.acc26[series.acc26.length-1];
          if (!last) return null;
          return <circle key={"l"+m.key} cx={x(last.i)} cy={y(last[m.key])} r="3.2" fill={m.color26} />;
        })}
      </svg>
      <div className="cmp-legend">
        {metrics.map(m => (
          <span key={m.key} className="cmp-leg">
            <span className="leg-line solid" style={{background:m.color26}}/>
            <span className="leg-label">2026 · {m.label}</span>
            <span className="leg-line dashed" style={{borderColor:m.color25}}/>
            <span className="leg-label faded">2025 · {m.label}</span>
          </span>
        ))}
      </div>
    </section>
  );
}

function niceTicks(min, max, n) {
  const range = max - min;
  const step = Math.pow(10, Math.floor(Math.log10(range / n)));
  const err = (n / range) * step;
  let stepFinal;
  if (err <= 0.15) stepFinal = step * 10;
  else if (err <= 0.35) stepFinal = step * 5;
  else if (err <= 0.75) stepFinal = step * 2;
  else stepFinal = step;
  const ticks = [];
  let v = Math.ceil(min / stepFinal) * stepFinal;
  while (v <= max) { ticks.push(Number.isInteger(stepFinal) ? Math.round(v) : +v.toFixed(2)); v += stepFinal; }
  return ticks;
}
function xTicks(n) {
  const target = 6;
  const step = Math.max(1, Math.ceil(n / target));
  const out = [];
  for (let i = 1; i <= n; i += step) out.push(i);
  if (out[out.length-1] !== n) out.push(n);
  return out;
}

// ============ Chart de posição na tabela ============
function CmpPosicaoChart({ series }) {
  // só pontos com rodada definida
  const ser26 = series.acc26.filter(s => s.rodada != null);
  const ser25 = series.acc25.filter(s => s.rodada != null);
  if (ser26.length === 0) return null;

  const W = 560, H = 240, padX = 36, padY = 22;
  const maxRodada = Math.max(
    ...ser26.map(s => s.rodada),
    ...ser25.map(s => s.rodada),
    1,
  );
  const allPos = [...ser26.map(s=>s.posicao), ...ser25.map(s=>s.posicao)].filter(p=>p!=null);
  const minP = 1;
  const maxP = Math.max(20, ...allPos);

  // Y invertido: posição 1 em cima
  function x(r) { return padX + ((r-1) / Math.max(1, maxRodada-1)) * (W - padX*2); }
  function y(p) { return padY + ((p - minP) / (maxP - minP)) * (H - padY*2); }

  function pathFor(arr) {
    return arr.filter(s=>s.posicao!=null).map((s, idx) =>
      (idx === 0 ? "M" : "L") + x(s.rodada).toFixed(1) + "," + y(s.posicao).toFixed(1)
    ).join(" ");
  }

  const yTicks = [1, 4, 7, 10, 13, 16, 20];

  return (
    <section className="cmp-chart cmp-chart-pos">
      <div className="cmp-chart-head">
        <h4>Posição na tabela</h4>
        <small>menor é melhor · zonas Libertadores/Sul-Am/Rebaixamento</small>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="cmp-svg" preserveAspectRatio="xMidYMid meet">
        {/* zonas */}
        <rect x={padX} y={y(1)} width={W-padX*2} height={y(6)-y(1)} fill="#4d6b2a" fillOpacity="0.08"/>
        <rect x={padX} y={y(7)} width={W-padX*2} height={y(12)-y(7)} fill="#b48415" fillOpacity="0.07"/>
        <rect x={padX} y={y(17)} width={W-padX*2} height={y(maxP)-y(17)} fill="#a8341f" fillOpacity="0.07"/>
        {/* gridlines */}
        {yTicks.map((t,i) => (
          <g key={i}>
            <line x1={padX} x2={W-padX} y1={y(t)} y2={y(t)} stroke="#d6c9a6" strokeWidth="0.6" strokeDasharray="2 3"/>
            <text x={padX-6} y={y(t)+3.5} textAnchor="end" fontFamily="JetBrains Mono" fontSize="9" fill="#7a6f59">{t}º</text>
          </g>
        ))}
        {/* labels x */}
        {xTicks(maxRodada).map((i, k) => (
          <text key={k} x={x(i)} y={H-padY+12} textAnchor="middle" fontFamily="JetBrains Mono" fontSize="9" fill="#7a6f59">R{i}</text>
        ))}
        {/* 2025 dashed */}
        <path d={pathFor(ser25)} stroke="var(--ink-faint)" strokeWidth="1.6" strokeDasharray="4 3" fill="none" strokeLinejoin="round" strokeLinecap="round"/>
        {/* 2026 solid */}
        <path d={pathFor(ser26)} stroke="var(--red)" strokeWidth="2.4" fill="none" strokeLinejoin="round" strokeLinecap="round"/>
        {/* pontos 2026 */}
        {ser26.map((s,i) => s.posicao != null && (
          <circle key={i} cx={x(s.rodada)} cy={y(s.posicao)} r="3" fill="var(--red)"/>
        ))}
      </svg>
      <div className="cmp-legend">
        <span className="cmp-leg">
          <span className="leg-line solid" style={{background:"var(--red)"}}/>
          <span className="leg-label">2026</span>
          <span className="leg-line dashed" style={{borderColor:"var(--ink-faint)"}}/>
          <span className="leg-label faded">2025</span>
        </span>
        <span style={{marginLeft:"auto", display:"flex", gap:14, fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.14em", textTransform:"uppercase", color:"var(--ink-mute)"}}>
          <span style={{display:"flex", alignItems:"center", gap:6}}><span style={{width:10, height:10, background:"#4d6b2a", opacity:0.4}}/>G6</span>
          <span style={{display:"flex", alignItems:"center", gap:6}}><span style={{width:10, height:10, background:"#b48415", opacity:0.4}}/>G12</span>
          <span style={{display:"flex", alignItems:"center", gap:6}}><span style={{width:10, height:10, background:"#a8341f", opacity:0.4}}/>Z4</span>
        </span>
      </div>
    </section>
  );
}

window.Comparativo = Comparativo;
