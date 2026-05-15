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

// ============ Temporadas Page ============
function Temporadas({ season, onOpenMatch }) {
  const [recorte, setRecorte] = useState("todos"); // todos | casa | fora
  const [view, setView] = useState("table"); // table | cards
  const [comp, setComp] = useState("todas");
  const [search, setSearch] = useState("");

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

  return (
    <div className="main">
      <Hero season={season} resumo={resumo} recorte={recorte} setRecorte={setRecorte} />
      <SummaryRow resumo={resumo} saldoSeries={saldoSeries} aproveitamentoSeries={aproveitamentoSeries} allResults={allResults} season={season} />
      <Toolbar
        comps={comps}
        compCounts={compCounts}
        comp={comp} setComp={setComp}
        view={view} setView={setView}
        search={search} setSearch={setSearch}
        total={filtered.length}
      />
      {view === "table"
        ? <GamesTable jogos={filtered} allResults={allResults} onOpen={onOpenMatch} />
        : <GamesCards jogos={filtered} onOpen={onOpenMatch} />}
      <SidePanels season={season} aproveitamentoSeries={aproveitamentoSeries} />
    </div>
  );
}

// ============ Hero ============
function Hero({ season, resumo, recorte, setRecorte }) {
  const tecnicos = season.tecnicos;
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
          <span><strong>Sequência atual:</strong> 4V 2E em 6 jogos</span>
          <span className="dot">·</span>
          <span><strong>Última partida:</strong> 13/05 · 2x2 Paysandu</span>
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
function SummaryRow({ resumo, saldoSeries, aproveitamentoSeries, allResults, season }) {
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
          <StreakBars results={allResults} width={420} height={32} />
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
function GamesTable({ jogos, allResults, onOpen }) {
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
          {jogos.map((j, idx) => {
            // forma = últimos 5 resultados terminando neste jogo (no array filtrado)
            const formaRes = lastN(allResults, 5, idx);
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
                <div className="name">{vasco_h ? "Vasco" : j.adversario}<small>{vasco_h ? "Casa" : "Visitante"}</small></div>
              </div>
              <div className="card-score">
                {vasco_h ? j.placar[0] : j.placar[1]}<span className="vs">×</span>{vasco_h ? j.placar[1] : j.placar[0]}
              </div>
              <div className="card-team" style={{justifyContent:"flex-end"}}>
                <div className="name" style={{textAlign:"right"}}>{vasco_h ? j.adversario : "Vasco"}<small>{vasco_h ? "Visitante" : "Casa"}</small></div>
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
function SidePanels({ season, aproveitamentoSeries }) {
  const max = season.artilheiros[0].gols;
  return (
    <div className="side-grid">
      <section className="panel">
        <h3 className="panel-title">
          Artilheiros do ano
          <small>{season.artilheiros.reduce((a,p)=>a+p.gols,0)} gols computados</small>
        </h3>
        <div className="artilharia">
          {season.artilheiros.map((p, i) => (
            <div className="art-row" key={p.nome}>
              <span className="pos">{String(i+1).padStart(2,"0")}</span>
              <span className="name">{p.nome}</span>
              <span className="goals">{p.gols}</span>
              <span className="bar"><i style={{width:`${(p.gols/max)*100}%`}}/></span>
            </div>
          ))}
        </div>
      </section>
      <section className="panel">
        <h3 className="panel-title">
          Aproveitamento
          <small>ao longo do ano</small>
        </h3>
        <div style={{padding:"6px 0"}}>
          <AproveitamentoChart data={aproveitamentoSeries} width={360} height={140} />
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
