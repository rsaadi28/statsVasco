// Acervo Vasco — aba Evolução

function Evolucao({ onOpenPlayer }) {
  const [topTab, setTopTab] = useState("resumo");
  const [innerTab, setInnerTab] = useState("artilheiros");

  const yearsAvailable = window.YEARLY.map(y => y.ano).sort((a,b)=>a-b);
  // Mostra na barra: Resumo Anual | Geral | Mais | últimos 7 anos
  const yearTabs = yearsAvailable.slice(-7);
  const yearsInMais = yearsAvailable.filter(y => !yearTabs.includes(y)).sort((a,b)=>b-a);

  // "Mais" está selecionado quando topTab é um ano antigo
  const isMaisActive = topTab !== "resumo" && topTab !== "geral" && !yearTabs.includes(Number(topTab));
  const maisYear = isMaisActive ? Number(topTab) : null;

  return (
    <div className="main">
      <EvoHero topTab={topTab} />
      <EvoTopTabs
        topTab={topTab} setTopTab={setTopTab}
        yearTabs={yearTabs}
        yearsInMais={yearsInMais}
        isMaisActive={isMaisActive}
        maisYear={maisYear}
      />
      {topTab === "resumo" ? (
        <EvoResumo />
      ) : (
        <>
          <EvoInnerTabs innerTab={innerTab} setInnerTab={setInnerTab} />
          <EvoInnerContent topTab={topTab} innerTab={innerTab} onOpenPlayer={onOpenPlayer} />
        </>
      )}
    </div>
  );
}

function EvoHero({ topTab }) {
  const t = window.YEARLY_TOTAIS;
  const label = topTab === "resumo" ? "Visão Anual"
              : topTab === "geral"  ? "Histórico Geral · 2000–2026"
              : `Temporada · ${topTab}`;
  return (
    <section className="evo-hero">
      <div className="hero-eyebrow">Acervo · Evolução</div>
      <div className="evo-hero-line">
        <h1 className="evo-title">{label}</h1>
        <div className="evo-hero-totais">
          <div className="ehv"><span className="lbl">Jogos</span><span className="val">{fmtN(t.jogos)}</span></div>
          <div className="ehv"><span className="lbl">V</span><span className="val v">{t.v}</span></div>
          <div className="ehv"><span className="lbl">E</span><span className="val e">{t.e}</span></div>
          <div className="ehv"><span className="lbl">D</span><span className="val d">{t.d}</span></div>
          <div className="ehv"><span className="lbl">Saldo</span><span className="val red">{(t.gp-t.gc) >= 0 ? "+" : ""}{t.gp-t.gc}</span></div>
        </div>
      </div>
    </section>
  );
}

function EvoTopTabs({ topTab, setTopTab, yearTabs, yearsInMais, isMaisActive, maisYear }) {
  const [openMais, setOpenMais] = useState(false);
  const ref = React.useRef(null);
  useEffect(() => {
    function close(e) { if (ref.current && !ref.current.contains(e.target)) setOpenMais(false); }
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);
  return (
    <nav className="evo-tabs">
      <button className={topTab==="resumo"?"active":""} onClick={()=>setTopTab("resumo")}>Resumo Anual</button>
      <button className={topTab==="geral"?"active":""}  onClick={()=>setTopTab("geral")}>Geral</button>
      <div className="evo-mais" ref={ref}>
        <button
          className={(isMaisActive?"active":"") + (openMais?" open":"")}
          onClick={()=>setOpenMais(o=>!o)}
        >
          Mais{maisYear ? <> · <strong>{maisYear}</strong></> : null}
          <span className="evo-mais-chev">▾</span>
        </button>
        {openMais && (
          <div className="evo-mais-menu">
            <div className="evo-mais-menu-head">Temporadas anteriores</div>
            <div className="evo-mais-menu-grid">
              {yearsInMais.map(y => (
                <button
                  key={y}
                  className={maisYear===y?"sel":""}
                  onClick={()=>{ setTopTab(String(y)); setOpenMais(false); }}
                >{y}</button>
              ))}
            </div>
          </div>
        )}
      </div>
      <span className="evo-tabs-sep"/>
      {yearTabs.map(y => (
        <button key={y} className={topTab===String(y)?"active":""} onClick={()=>setTopTab(String(y))}>{y}</button>
      ))}
    </nav>
  );
}

function EvoInnerTabs({ innerTab, setInnerTab }) {
  return (
    <nav className="evo-inner-tabs">
      <button className={innerTab==="artilheiros"?"active":""} onClick={()=>setInnerTab("artilheiros")}>Artilheiros</button>
      <button className={innerTab==="gols"?"active":""}       onClick={()=>setInnerTab("gols")}>Gols (Acum.)</button>
      <button className={innerTab==="saldo"?"active":""}      onClick={()=>setInnerTab("saldo")}>Saldo</button>
      <button className={innerTab==="ved"?"active":""}        onClick={()=>setInnerTab("ved")}>V/E/D (Totais)</button>
    </nav>
  );
}

// ============ Resumo Anual ============
function EvoResumo() {
  const years = [...window.YEARLY].sort((a,b)=>b.ano-a.ano); // 2026 em cima
  const maxGP = Math.max(...years.map(y=>y.gp));
  const maxGC = Math.max(...years.map(y=>y.gc));
  const maxV  = Math.max(...years.map(y=>y.v));
  const maxE  = Math.max(...years.map(y=>y.e));
  const maxD  = Math.max(...years.map(y=>y.d));
  const saldos = years.map(y=>y.gp-y.gc);
  return (
    <div className="evo-resumo-grid">
      <YearBars title="Gols pró por ano"     unit="gols pró"     data={years.map(y=>({label:y.ano, value:y.gp, max:maxGP}))} color="var(--r-v)" />
      <YearBars title="Gols contra por ano"  unit="gols contra"  data={years.map(y=>({label:y.ano, value:y.gc, max:maxGC}))} color="var(--r-d)" />
      <YearBars title="Saldo por ano"        unit="saldo"        data={years.map((y,i)=>({label:y.ano, value:saldos[i], max:Math.max(...saldos.map(Math.abs))}))} color="var(--ink)" signed />
      <YearBars title="Vitórias por ano"     unit="vitórias"     data={years.map(y=>({label:y.ano, value:y.v, max:maxV}))} color="var(--r-v)" />
      <YearBars title="Empates por ano"      unit="empates"      data={years.map(y=>({label:y.ano, value:y.e, max:maxE}))} color="var(--r-e)" />
      <YearBars title="Derrotas por ano"     unit="derrotas"     data={years.map(y=>({label:y.ano, value:y.d, max:maxD}))} color="var(--r-d)" />
    </div>
  );
}

function YearBars({ title, unit, data, color, signed }) {
  const rowH = 18;
  const labelW = 44;
  const maxAbs = Math.max(...data.map(d => Math.abs(d.value)), 1);
  const trackW = 400;
  const W = labelW + trackW + 50;
  const H = data.length * rowH + 36;
  return (
    <section className="evo-panel">
      <h3 className="evo-panel-title">{title}<small>{unit}</small></h3>
      <svg viewBox={`0 0 ${W} ${H}`} className="evo-svg" preserveAspectRatio="xMidYMid meet">
        {/* eixo vertical de zero (para saldo) */}
        {signed && (
          <line x1={labelW + trackW/2} x2={labelW + trackW/2} y1={4} y2={H-12} stroke="#15110b" strokeWidth="0.8"/>
        )}
        {data.map((d, i) => {
          const y = 4 + i * rowH;
          let barX, barW, val = d.value;
          if (signed) {
            const center = labelW + trackW/2;
            const w = (Math.abs(val) / maxAbs) * (trackW/2);
            if (val >= 0) { barX = center; barW = w; }
            else { barX = center - w; barW = w; }
          } else {
            barX = labelW;
            barW = (Math.abs(val) / maxAbs) * trackW;
          }
          const barColor = signed && val < 0 ? "var(--r-d)" : color;
          return (
            <g key={d.label}>
              <text x={labelW - 8} y={y + 11} textAnchor="end" fontFamily="JetBrains Mono" fontSize="10" fill="#3a3225">{d.label}</text>
              <rect x={barX} y={y+3} width={Math.max(0.5, barW)} height={rowH-7} fill={barColor}/>
              <text x={signed ? (val >= 0 ? barX + barW + 4 : barX - 4) : (barX + barW + 4)}
                    y={y + 11}
                    textAnchor={signed && val < 0 ? "end" : "start"}
                    fontFamily="Archivo" fontSize="10" fontWeight="600" fill="#15110b">
                {signed ? (val > 0 ? "+" + val : val) : val}
              </text>
            </g>
          );
        })}
        {/* gridline base */}
        <line x1={labelW} x2={labelW + trackW} y1={H-12} y2={H-12} stroke="#d6c9a6" strokeWidth="0.6"/>
      </svg>
    </section>
  );
}

// ============ Inner content (Artilheiros/Gols/Saldo/VED) ============
function EvoInnerContent({ topTab, innerTab, onOpenPlayer }) {
  if (innerTab === "artilheiros") return <InnerArtilheiros topTab={topTab} onOpenPlayer={onOpenPlayer} />;
  if (innerTab === "gols")        return <InnerGolsAcum topTab={topTab} />;
  if (innerTab === "saldo")       return <InnerSaldo topTab={topTab} />;
  if (innerTab === "ved")         return <InnerVED topTab={topTab} />;
  return null;
}

function InnerArtilheiros({ topTab, onOpenPlayer }) {
  let lista;
  let titulo;
  if (topTab === "geral") {
    lista = window.ARTILHEIROS_GERAL;
    titulo = "Artilheiros · todos os anos";
  } else {
    const ano = Number(topTab);
    lista = window.ARTILHEIROS_POR_ANO[ano] || [];
    titulo = `Artilheiros ${ano}`;
  }
  if (lista.length === 0) {
    return (
      <section className="evo-panel">
        <h3 className="evo-panel-title">{titulo}<small>sem registros</small></h3>
        <div style={{padding:"30px 0", textAlign:"center", fontFamily:"var(--ff-serif)", fontStyle:"italic", color:"var(--ink-mute)"}}>
          Artilharia desta temporada ainda não foi migrada para o acervo web.
        </div>
      </section>
    );
  }
  const max = lista[0].gols;
  return (
    <section className="evo-panel">
      <h3 className="evo-panel-title">{titulo}<small>{lista.reduce((a,p)=>a+p.gols,0)} gols computados</small></h3>
      <div className="evo-artilharia">
        {lista.map((p, i) => (
          <div className="art-row" key={p.nome + i}>
            <span className="pos">{String(i+1).padStart(2,"0")}</span>
            <span className="name">
              {onOpenPlayer
                ? <button className="plink" onClick={()=>onOpenPlayer(p.nome)}>{p.nome}</button>
                : p.nome}
            </span>
            <span className="goals">{p.gols}</span>
            <span className="bar"><i style={{width:`${(p.gols/max)*100}%`}}/></span>
          </div>
        ))}
      </div>
    </section>
  );
}

function InnerGolsAcum({ topTab }) {
  const isGeral = topTab === "geral";
  const series = isGeral ? window.gameSeriesGeral() : window.gameSeriesForYear(Number(topTab));
  if (series.length === 0) return <EmptyState/>;
  const acc = accCumulative(series, ["gp","gc"]);
  // Comparação com ano anterior (só para anos específicos com prev existindo)
  let acc25 = null;
  if (!isGeral) {
    const anoPrev = Number(topTab) - 1;
    const prev = window.gameSeriesForYear(anoPrev);
    if (prev && prev.length > 0) acc25 = accCumulative(prev, ["gp","gc"]);
  }
  return (
    <section className="evo-panel">
      <h3 className="evo-panel-title">
        Gols acumulados
        <small>{isGeral ? "todos os anos · cada ponto = um jogo" : `temporada ${topTab}`}</small>
      </h3>
      <LineMulti
        series={acc}
        series2={acc25}
        labelPrev={!isGeral ? `${Number(topTab)-1}` : null}
        metrics={[
          { key:"gp", label:"Gols pró",    color:"var(--r-v)", color2:"#9bb978" },
          { key:"gc", label:"Gols contra", color:"var(--r-d)", color2:"#d49e8f" },
        ]}
      />
    </section>
  );
}

function InnerSaldo({ topTab }) {
  const isGeral = topTab === "geral";
  const series = isGeral ? window.gameSeriesGeral() : window.gameSeriesForYear(Number(topTab));
  if (series.length === 0) return <EmptyState/>;
  // saldo acumulado
  const acc = [];
  let saldo = 0;
  series.forEach((s,i) => {
    saldo += s.gp - s.gc;
    acc.push({ i: i+1, saldo });
  });
  let acc25 = null;
  if (!isGeral) {
    const prev = window.gameSeriesForYear(Number(topTab) - 1);
    if (prev && prev.length > 0) {
      acc25 = [];
      let s2 = 0;
      prev.forEach((s,i) => { s2 += s.gp - s.gc; acc25.push({ i: i+1, saldo: s2 }); });
    }
  }
  return (
    <section className="evo-panel">
      <h3 className="evo-panel-title">
        Saldo de gols acumulado
        <small>{isGeral ? "todos os anos" : `temporada ${topTab}`}</small>
      </h3>
      <LineMulti
        series={acc}
        series2={acc25}
        labelPrev={!isGeral ? `${Number(topTab)-1}` : null}
        zeroLine
        metrics={[
          { key:"saldo", label:"Saldo", color:"var(--ink)", color2:"var(--ink-faint)" },
        ]}
      />
    </section>
  );
}

function InnerVED({ topTab }) {
  let v, e, d, titulo;
  if (topTab === "geral") {
    const t = window.YEARLY_TOTAIS;
    v = t.v; e = t.e; d = t.d;
    titulo = "V/E/D · todos os anos";
  } else {
    const y = window.YEARLY.find(y => y.ano === Number(topTab));
    if (!y) return <EmptyState/>;
    v = y.v; e = y.e; d = y.d;
    titulo = `V/E/D · ${topTab}`;
  }
  const max = Math.max(v, e, d) || 1;
  const total = v + e + d;
  return (
    <section className="evo-panel">
      <h3 className="evo-panel-title">
        {titulo}
        <small>{total} jogos · aproveitamento {((v*3+e)/(total*3)*100).toFixed(1)}%</small>
      </h3>
      <div className="evo-ved-stage">
        <VEDBar label="Vitórias" val={v} max={max} color="var(--r-v)" total={total}/>
        <VEDBar label="Empates"  val={e} max={max} color="var(--r-e)" total={total}/>
        <VEDBar label="Derrotas" val={d} max={max} color="var(--r-d)" total={total}/>
      </div>
    </section>
  );
}

function VEDBar({ label, val, max, color, total }) {
  const pct = total ? ((val/total)*100).toFixed(1) : 0;
  return (
    <div className="evo-ved-col">
      <div className="evo-ved-num">{val}</div>
      <div className="evo-ved-pct">{pct}%</div>
      <div className="evo-ved-bar-wrap">
        <div className="evo-ved-bar" style={{ height: `${(val/max)*100}%`, background: color }}/>
      </div>
      <div className="evo-ved-lbl">{label}</div>
    </div>
  );
}

// ============ Charts utilitários ============
function accCumulative(series, keys) {
  const out = [];
  const acc = {};
  keys.forEach(k => acc[k] = 0);
  series.forEach((s, idx) => {
    keys.forEach(k => acc[k] += s[k] || 0);
    out.push({ i: idx+1, ...acc });
  });
  return out;
}

function LineMulti({ series, series2, labelPrev, metrics, zeroLine }) {
  const W = 1080, H = 380, padX = 50, padY = 30;
  if (!series || series.length === 0) return null;
  const n = Math.max(series.length, series2 ? series2.length : 0);

  const all = [];
  metrics.forEach(m => {
    series.forEach(s => all.push(s[m.key]));
    if (series2) series2.forEach(s => all.push(s[m.key]));
  });
  let yMin = Math.min(0, ...all);
  let yMax = Math.max(1, ...all);
  if (zeroLine) { yMin = Math.min(yMin, 0); yMax = Math.max(yMax, 0); }
  const yPad = (yMax - yMin) * 0.06 || 1;
  yMin -= yPad; yMax += yPad;
  const yRange = yMax - yMin || 1;

  function x(i) { return padX + ((i-1) / Math.max(1, n-1)) * (W - padX*2); }
  function y(v) { return padY + (H - padY*2) - ((v - yMin) / yRange) * (H - padY*2); }

  function pathFor(arr, key) {
    return arr.map((s, idx) => (idx===0?"M":"L") + x(s.i).toFixed(1) + "," + y(s[key]).toFixed(1)).join(" ");
  }

  const yTicks = niceTicksEvo(yMin, yMax, 5);
  const xTicksArr = xTicksEvo(n);

  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} className="cmp-svg" preserveAspectRatio="xMidYMid meet" style={{maxHeight:380}}>
        {/* grid */}
        {yTicks.map((t,i) => (
          <g key={i}>
            <line x1={padX} x2={W-padX} y1={y(t)} y2={y(t)} stroke="#d6c9a6" strokeWidth="0.6" strokeDasharray="2 3"/>
            <text x={padX-8} y={y(t)+4} textAnchor="end" fontFamily="JetBrains Mono" fontSize="11" fill="#7a6f59">{t}</text>
          </g>
        ))}
        {zeroLine && <line x1={padX} x2={W-padX} y1={y(0)} y2={y(0)} stroke="#15110b" strokeWidth="0.8"/>}
        {/* x labels */}
        {xTicksArr.map((i, k) => (
          <text key={k} x={x(i)} y={H-padY+16} textAnchor="middle" fontFamily="JetBrains Mono" fontSize="11" fill="#7a6f59">{i}</text>
        ))}
        {/* prev */}
        {series2 && metrics.map(m => (
          <path key={"p"+m.key} d={pathFor(series2, m.key)} stroke={m.color2} strokeWidth="1.6" strokeDasharray="4 3" fill="none" strokeLinejoin="round" strokeLinecap="round" />
        ))}
        {/* current */}
        {metrics.map(m => (
          <path key={"c"+m.key} d={pathFor(series, m.key)} stroke={m.color} strokeWidth="2.2" fill="none" strokeLinejoin="round" strokeLinecap="round" />
        ))}
        {/* dot final */}
        {metrics.map(m => {
          const last = series[series.length-1];
          return <circle key={"l"+m.key} cx={x(last.i)} cy={y(last[m.key])} r="3.4" fill={m.color}/>;
        })}
      </svg>
      <div className="cmp-legend" style={{marginTop:8}}>
        {metrics.map(m => (
          <span key={m.key} className="cmp-leg">
            <span className="leg-line solid" style={{background:m.color}}/>
            <span className="leg-label">{m.label}</span>
            {series2 && (<>
              <span className="leg-line dashed" style={{borderColor:m.color2}}/>
              <span className="leg-label faded">{labelPrev} · {m.label}</span>
            </>)}
          </span>
        ))}
      </div>
    </div>
  );
}

function niceTicksEvo(min, max, n) {
  const range = max - min;
  const step = Math.pow(10, Math.floor(Math.log10(range / n)));
  const err = (n / range) * step;
  let s;
  if (err <= 0.15) s = step * 10;
  else if (err <= 0.35) s = step * 5;
  else if (err <= 0.75) s = step * 2;
  else s = step;
  const ticks = [];
  let v = Math.ceil(min / s) * s;
  while (v <= max) { ticks.push(Number.isInteger(s) ? Math.round(v) : +v.toFixed(2)); v += s; }
  return ticks;
}
function xTicksEvo(n) {
  const target = 8;
  const step = Math.max(1, Math.ceil(n / target));
  const out = [];
  for (let i = 1; i <= n; i += step) out.push(i);
  if (out[out.length-1] !== n) out.push(n);
  return out;
}

function EmptyState() {
  return (
    <div style={{padding:"60px 0", textAlign:"center", fontFamily:"var(--ff-serif)", fontStyle:"italic", color:"var(--ink-mute)"}}>
      Dados não disponíveis para este recorte.
    </div>
  );
}

window.Evolucao = Evolucao;
