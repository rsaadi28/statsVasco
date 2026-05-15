// Acervo Vasco — aba Jogos Futuros

function JogosFuturos({ onOpenRetro }) {
  const all = window.JOGOS_FUTUROS;
  const [comp, setComp] = useState("todas");
  const [hover, setHover] = useState(null);

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
              <th style={{width:60}}></th>
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
                    <span className="open-arrow">›</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
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
