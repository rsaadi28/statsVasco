// Acervo Vasco — aba Retrospecto

function Retrospecto({ initial = "", onOpenPlayer, onOpenMatch }) {
  const adversarios = Object.keys(window.RETROSPECTOS || {}).sort();
  const [advNome, setAdvNome] = useState(initial || "");
  const [open, setOpen] = useState(false);
  const [busca, setBusca] = useState("");
  const data = advNome ? (window.RETROSPECTOS || {})[advNome] : null;

  const calc = useMemo(() => calcular(data), [data]);

  useEffect(() => {
    setAdvNome(initial || "");
  }, [initial]);

  return (
    <div className="main">
      <RetrospectoHero advNome={advNome} adversarios={adversarios} setAdv={setAdvNome} open={open} setOpen={setOpen} busca={busca} setBusca={setBusca} calc={calc} hasSelection={Boolean(data)} />
      {data ? (
        <div className="retro-grid">
          <RetroGames jogos={data.jogos} onOpenMatch={onOpenMatch} />
          <RetroAside data={data} calc={calc} onOpenPlayer={onOpenPlayer} />
        </div>
      ) : (
        <div className="retro-empty-state">Selecione um time para ver o retrospecto.</div>
      )}
    </div>
  );
}

function calcular(data) {
  const jogos = data?.jogos || [];
  let v=0,e=0,d=0, gp=0, gc=0;
  jogos.forEach(j => {
    if (j.res==="V") v++;
    else if (j.res==="E") e++;
    else d++;
    gp += j.placar[0];
    gc += j.placar[1];
  });
  const total = jogos.length;
  const aprov = total ? ((v*3 + e) / (total*3)) * 100 : 0;

  // placares elásticos
  let elasticoVasco = null, elasticoAdv = null;
  jogos.forEach(j => {
    const sV = j.placar[0] - j.placar[1];
    if (j.res === "V") {
      if (!elasticoVasco || sV > elasticoVasco.saldo) elasticoVasco = { jogo: j, saldo: sV };
    }
    if (j.res === "D") {
      const sA = j.placar[1] - j.placar[0];
      if (!elasticoAdv || sA > elasticoAdv.saldo) elasticoAdv = { jogo: j, saldo: sA };
    }
  });

  // maiores jejuns por data
  // ordenar por data ASC
  const ord = [...jogos].sort((a,b)=> toDate(a.data) - toDate(b.data));
  const advSemVencer = longestRun(ord, j => j.res !== "D"); // adv não venceu
  const vascoSemVencer = longestRun(ord, j => j.res !== "V"); // vasco não venceu

  // artilheiros
  const artVasco = countScorers(jogos.flatMap(j => j.gols_vasco || []));
  const artAdv = countScorers(jogos.flatMap(j => j.gols_adv || []));

  return { v,e,d, total, aprov, gp, gc, elasticoVasco, elasticoAdv, advSemVencer, vascoSemVencer, artVasco, artAdv };
}

function toDate(dt) {
  const [d,m,y] = dt.split("/").map(Number);
  return new Date(y, m-1, d).getTime();
}
function longestRun(arr, predicate) {
  let best = null, current = [];
  arr.forEach(j => {
    if (predicate(j)) current.push(j);
    else {
      if (!best || current.length > best.length) best = [...current];
      current = [];
    }
  });
  if (!best || current.length > best.length) best = [...current];
  if (!best || best.length === 0) return null;
  return {
    length: best.length,
    inicio: best[0].data,
    fim: best[best.length-1].data,
  };
}
function countScorers(list) {
  const map = {};
  list.forEach(n => {
    if (!n || n === "—") return;
    map[n] = (map[n] || 0) + 1;
  });
  return Object.entries(map).map(([nome, gols]) => ({ nome, gols })).sort((a,b)=> b.gols - a.gols);
}

// ============ Hero ============
function RetrospectoHero({ advNome, adversarios, setAdv, open, setOpen, busca, setBusca, calc, hasSelection }) {
  const filtered = adversarios.filter(a => a.toLowerCase().includes(busca.toLowerCase()));
  return (
    <section className="retro-hero">
      <div className="retro-hero-left">
        <div className="hero-eyebrow">Acervo · Retrospecto</div>
        <div className="retro-vs">
          <div className="retro-team retro-team-vasco">
            <Monogram club="Vasco" vasco size="huge" />
            <span className="retro-team-name">Vasco</span>
          </div>
          {hasSelection ? (
            <div className="retro-score">
              <div className="retro-score-num">{calc.gp}</div>
              <div className="retro-score-x">×</div>
              <div className="retro-score-num">{calc.gc}</div>
            </div>
          ) : (
            <div className="retro-score retro-score-empty">×</div>
          )}
          <div className="retro-team retro-team-adv">
            <RetroAdvPicker advNome={advNome} adversarios={filtered} setAdv={setAdv} open={open} setOpen={setOpen} busca={busca} setBusca={setBusca} />
          </div>
        </div>
        <div className="retro-hero-foot">
          {hasSelection ? (
            <>
              <span><strong>{calc.total}</strong> jogos no acervo</span>
              <span className="dot">·</span>
              <span><strong>{calc.aprov.toFixed(1)}%</strong> de aproveitamento</span>
              <span className="dot">·</span>
              <span>saldo <strong style={{color: calc.gp - calc.gc >= 0 ? "var(--r-v)" : "var(--r-d)"}}>{calc.gp - calc.gc >= 0 ? "+" : ""}{calc.gp - calc.gc}</strong></span>
            </>
          ) : (
            <span>Selecione um time para ver o retrospecto.</span>
          )}
        </div>
      </div>
    </section>
  );
}

function RetroAdvPicker({ advNome, adversarios, setAdv, open, setOpen, busca, setBusca }) {
  const ref = React.useRef(null);
  const label = advNome || "Selecione um time";
  useEffect(() => {
    function close(e) { if (ref.current && !ref.current.contains(e.target)) setOpen(false); }
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, [setOpen]);
  return (
    <div className="adv-picker" ref={ref}>
      <button type="button" className={"adv-picker-btn" + (open ? " open" : "") + (!advNome ? " empty" : "")} onClick={()=>setOpen(o=>!o)}>
        {advNome && <Monogram club={advNome} size="huge" />}
        <span className="adv-picker-name">{label}</span>
        <span className="adv-picker-chev">▾</span>
      </button>
      {open && (
        <div className="adv-picker-menu">
          <div className="adv-picker-search">
            <input autoFocus placeholder="buscar adversário…" value={busca} onChange={(e)=>setBusca(e.target.value)} />
          </div>
          <ul>
            {adversarios.map(a => (
              <li key={a} className={a===advNome?"sel":""} onClick={()=>{ setAdv(a); setOpen(false); setBusca(""); }}>
                <Monogram club={a} /> {a}
                <span className="adv-cnt">{window.RETROSPECTOS[a].jogos.length}j</span>
              </li>
            ))}
            {adversarios.length === 0 && <li className="empty">nenhum encontrado</li>}
          </ul>
        </div>
      )}
    </div>
  );
}

// ============ Tabela de jogos ============
function RetroGames({ jogos, onOpenMatch }) {
  return (
    <div>
      <h3 className="retro-section-title">Confrontos no acervo</h3>
      <div className="table-wrap">
        <table className="tbl retro-tbl">
          <thead>
            <tr>
              <th style={{width:90}}>Data</th>
              <th style={{width:28}}></th>
              <th>Competição</th>
              <th style={{width:60}}>Local</th>
              <th style={{width:90}}>Placar</th>
              <th>Gols do Vasco</th>
            </tr>
          </thead>
          <tbody>
            {jogos.map((j,i) => (
              <tr key={i} className="has-detail" onClick={()=> onOpenMatch && onOpenMatch({ data: j.data, adversario: jogos.adv })}>
                <td className="date">{j.data}</td>
                <td className="result-cell"><span className={"result-dot " + j.res}/></td>
                <td className="competition">{j.competicao.replace("Campeonato ","")}</td>
                <td className="locale">{j.local}</td>
                <td className="score">{j.placar[0]}<span className="vs">×</span>{j.placar[1]}</td>
                <td style={{fontFamily:"var(--ff-serif)", fontSize:13.5}}>
                  {j.gols_vasco.length === 0 ? <span style={{color:"var(--ink-faint)"}}>—</span> : j.gols_vasco.join(", ")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ============ Aside ============
function RetroAside({ data, calc, onOpenPlayer }) {
  return (
    <aside className="retro-aside">
      <h3 className="retro-section-title">Resumo do retrospecto</h3>
      <RetroKPIs calc={calc} />
      <RetroElasticos elastico={calc} adversario={data.adversario} />
      <RetroJejuns jejum={calc} adversario={data.adversario} />
      <RetroArtilheiros art={calc.artVasco} titulo="Artilheiros do Vasco" onOpenPlayer={onOpenPlayer} />
      <RetroArtilheiros art={calc.artAdv} titulo={`Artilheiros do ${data.adversario}`} adv />
    </aside>
  );
}

function RetroKPIs({ calc }) {
  return (
    <div className="retro-kpis">
      <div className="rkpi" style={{gridColumn:"span 2"}}>
        <div className="rkpi-lbl">Jogos</div>
        <div className="rkpi-val">{calc.total}</div>
      </div>
      <div className="rkpi rkpi-ap" style={{gridColumn:"span 2"}}>
        <div className="rkpi-lbl">Aproveitamento</div>
        <div className="rkpi-val red">{calc.aprov.toFixed(1)}<small>%</small></div>
      </div>
      <div className="rkpi rkpi-v">
        <div className="rkpi-lbl">V</div>
        <div className="rkpi-val">{calc.v}</div>
      </div>
      <div className="rkpi rkpi-e">
        <div className="rkpi-lbl">E</div>
        <div className="rkpi-val">{calc.e}</div>
      </div>
      <div className="rkpi rkpi-d">
        <div className="rkpi-lbl">D</div>
        <div className="rkpi-val">{calc.d}</div>
      </div>
      <div className="rkpi rkpi-bar" style={{gridColumn:"span 4", marginTop:-2}}>
        <div className="rkpi-bar-track">
          <div style={{flex: calc.v, background:"var(--r-v)"}}/>
          <div style={{flex: calc.e, background:"var(--r-e)"}}/>
          <div style={{flex: calc.d, background:"var(--r-d)"}}/>
        </div>
      </div>
    </div>
  );
}

function RetroElasticos({ elastico, adversario }) {
  return (
    <div className="retro-block">
      <h4 className="retro-block-title">Placares mais elásticos</h4>
      <div className="retro-elasticos">
        <ElasticoCard label="Para o Vasco" jogo={elastico.elasticoVasco?.jogo} forVasco />
        <ElasticoCard label={`Para o ${adversario}`} jogo={elastico.elasticoAdv?.jogo} />
      </div>
    </div>
  );
}

function ElasticoCard({ label, jogo, forVasco }) {
  if (!jogo) {
    return (
      <div className={"el-card " + (forVasco ? "el-vasco" : "el-adv")}>
        <div className="el-label">{label}</div>
        <div className="el-empty">sem registro</div>
      </div>
    );
  }
  return (
    <div className={"el-card " + (forVasco ? "el-vasco" : "el-adv")}>
      <div className="el-label">{label}</div>
      <div className="el-score">{jogo.placar[0]}<span className="el-x">×</span>{jogo.placar[1]}</div>
      <div className="el-date">{jogo.data} · {jogo.local}</div>
    </div>
  );
}

function RetroJejuns({ jejum, adversario }) {
  return (
    <div className="retro-block">
      <h4 className="retro-block-title">Maiores jejuns</h4>
      <div className="retro-jejuns">
        <JejumCard label={`${adversario} sem vencer`} jejum={jejum.advSemVencer} />
        <JejumCard label="Vasco sem vencer" jejum={jejum.vascoSemVencer} alt />
      </div>
    </div>
  );
}
function JejumCard({ label, jejum, alt }) {
  return (
    <div className={"j-card " + (alt ? "j-alt" : "")}>
      <div className="j-label">{label}</div>
      {jejum ? (
        <>
          <div className="j-num">{jejum.length}<small>jogo{jejum.length===1?"":"s"}</small></div>
          <div className="j-range">{jejum.inicio} <span className="j-arrow">→</span> {jejum.fim}</div>
        </>
      ) : (
        <div className="el-empty">sem jejum</div>
      )}
    </div>
  );
}

function RetroArtilheiros({ art, titulo, onOpenPlayer, adv }) {
  if (!art || art.length === 0) {
    return (
      <div className="retro-block">
        <h4 className="retro-block-title">{titulo}</h4>
        <div className="el-empty" style={{padding:"6px 0"}}>—</div>
      </div>
    );
  }
  const max = art[0].gols;
  return (
    <div className="retro-block">
      <h4 className="retro-block-title">{titulo}</h4>
      <div className="retro-art">
        {art.map((p, i) => (
          <div key={p.nome} className="art-row">
            <span className="pos">{String(i+1).padStart(2,"0")}</span>
            <span className="name">
              {adv || !onOpenPlayer ? p.nome : (
                <button className="plink" onClick={()=>onOpenPlayer(p.nome)}>{p.nome}</button>
              )}
            </span>
            <span className="goals">{p.gols}</span>
            <span className="bar"><i style={{width:`${(p.gols/max)*100}%`}}/></span>
          </div>
        ))}
      </div>
    </div>
  );
}

window.Retrospecto = Retrospecto;
