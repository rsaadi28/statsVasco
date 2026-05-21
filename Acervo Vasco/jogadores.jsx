// Acervo Vasco — aba Jogadores (todos que já passaram, incluindo elenco atual)

const POS_ORDER_JOG = [
  "Goleiro","Lateral-Direito","Zagueiro","Lateral-Esquerdo",
  "Volante","Meio-Campista","Atacante"
];

function Jogadores({ onOpenPlayer }) {
  const all = window.ELENCO_DATA;
  const [busca, setBusca] = useState("");
  const [filtro, setFiltro] = useState("todos"); // status
  const [sort, setSort]   = useState("posicao"); // posicao | minutos | gols | assistencias | participacoes

  const filtered = useMemo(() => {
    let out = all.filter(p => {
      if (filtro !== "todos" && p.status !== filtro) return false;
      if (busca.trim()) {
        const s = busca.trim().toLowerCase();
        if (!p.nome.toLowerCase().includes(s) && !p.posicao.toLowerCase().includes(s)) return false;
      }
      return true;
    });
    if (sort === "posicao") {
      out = [...out].sort((a,b) => {
        const ai = POS_ORDER_JOG.indexOf(a.posicao);
        const bi = POS_ORDER_JOG.indexOf(b.posicao);
        if (ai !== bi) return ai - bi;
        return a.nome.localeCompare(b.nome, "pt-BR");
      });
    } else if (sort === "minutos") {
      out = [...out].sort((a,b) => (b.minutos || 0) - (a.minutos || 0));
    } else if (sort === "gols") {
      out = [...out].sort((a,b) => (b.gols || 0) - (a.gols || 0));
    } else if (sort === "assistencias") {
      out = [...out].sort((a,b) => (b.assistencias || 0) - (a.assistencias || 0));
    } else if (sort === "participacoes") {
      out = [...out].sort((a,b) => (b.participacoes_gol || 0) - (a.participacoes_gol || 0));
    }
    return out;
  }, [all, busca, filtro, sort]);

  const counts = useMemo(() => {
    const c = { todos: all.length };
    all.forEach(p => { c[p.status] = (c[p.status] || 0) + 1; });
    return c;
  }, [all]);

  return (
    <div className="main">
      <JogHero total={all.length} filtrados={filtered.length} />

      <div className="jog-toolbar">
        <div className="jog-search">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="7" cy="7" r="5"/><path d="M14 14L11 11"/></svg>
          <input placeholder="buscar jogador ou posição…" value={busca} onChange={(e)=>setBusca(e.target.value)} />
        </div>
        <div className="jog-filters">
          {[
            ["todos","Todos"],
            ["titular","Titulares"],
            ["reserva","Reservas"],
            ["nao-rel","Não Relacionado"],
            ["lesionado","Lesionados"],
            ["emprestado","Emprestados"],
            ["ex","Ex-jogadores"],
          ].map(([k,lbl]) => (
            <button key={k} className={"chip"+(filtro===k?" active":"")} onClick={()=>setFiltro(k)}>
              {lbl} <span className="count">{counts[k] || 0}</span>
            </button>
          ))}
        </div>
        <div className="jog-sort">
          <span className="lbl">Ordenar:</span>
          <button className={sort==="posicao"?"active":""} onClick={()=>setSort("posicao")}>Posição</button>
          <button className={sort==="minutos"?"active":""} onClick={()=>setSort("minutos")}>Mais minutos</button>
          <button className={sort==="gols"?"active":""}    onClick={()=>setSort("gols")}>Mais gols</button>
          <button className={sort==="assistencias"?"active":""} onClick={()=>setSort("assistencias")}>Mais assist.</button>
          <button className={sort==="participacoes"?"active":""} onClick={()=>setSort("participacoes")}>G+A</button>
        </div>
      </div>

      <div className="table-wrap">
        <table className="tbl jog-tbl">
          <thead>
            <tr>
              <th style={{width:90}}>Posição</th>
              <th>Jogador</th>
              <th style={{width:140}}>Status</th>
              <th style={{width:90}}>Minutos</th>
              <th style={{width:80}}>Gols</th>
              <th style={{width:80}}>Assist.</th>
              <th style={{width:80}}>G+A</th>
              <th style={{width:60}}>Capitão</th>
              <th style={{width:40}}></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((p,i) => (
              <tr key={p.nome} className={"has-detail jog-row status-"+p.status} onClick={()=> onOpenPlayer(p.nome)}>
                <td><span className="pos-chip">{p.posicao}</span></td>
                <td className="opponent">
                  <PlayerAvatar nome={p.nome} numero={p.numero} size="lg" />
                  <div style={{display:"flex", flexDirection:"column", gap:2}}>
                    <span style={{fontFamily:"var(--ff-serif)", fontSize:15, fontWeight:600}}>{p.nome}</span>
                    {p.clube && <span style={{fontFamily:"var(--ff-mono)", fontSize:10, color:"var(--ink-mute)"}}>{p.clube}</span>}
                  </div>
                </td>
                <td><span className={"cond-tag tag-"+p.status}>{window.STATUS_LABEL[p.status]}</span></td>
                <td style={{fontFamily:"var(--ff-mono)", fontSize:13}}>
                  {p.minutos == null ? <span style={{color:"var(--ink-faint)", fontStyle:"italic"}}>—</span>
                                      : fmtN(p.minutos)}
                </td>
                <td style={{fontFamily:"var(--ff-display)", fontSize:18, color: (p.gols||0) > 0 ? "var(--ink)" : "var(--ink-faint)"}}>
                  {p.gols || 0}
                </td>
                <td style={{fontFamily:"var(--ff-display)", fontSize:18, color: (p.assistencias||0) > 0 ? "var(--ink)" : "var(--ink-faint)"}}>
                  {p.assistencias || 0}
                </td>
                <td style={{fontFamily:"var(--ff-display)", fontSize:18, color: (p.participacoes_gol||0) > 0 ? "var(--ink)" : "var(--ink-faint)"}}>
                  {p.participacoes_gol || ((p.gols || 0) + (p.assistencias || 0))}
                </td>
                <td>
                  {(p.foi_capitao || p.capitao_atual || p.capitao_partida) && (
                    <span title="Já vestiu a braçadeira" style={{display:"inline-flex", alignItems:"center", justifyContent:"center", width:22, height:22, background:"var(--red)", color:"var(--paper-light)", fontFamily:"var(--ff-display)", fontSize:13, borderRadius:"50%"}}>C</span>
                  )}
                </td>
                <td><span className="open-arrow">›</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function JogHero({ total, filtrados }) {
  return (
    <section className="jog-hero">
      <div className="hero-eyebrow">Acervo · Jogadores</div>
      <div className="jog-hero-line">
        <h1 className="jog-title">
          {filtrados}{filtrados !== total && <small> de {total}</small>}
          <span className="jog-title-sub"> {filtrados === 1 ? "jogador" : "jogadores"}</span>
        </h1>
        <div className="jog-hero-sub">
          Todos os atletas que já passaram pelo Vasco no acervo — elenco atual, lesionados, emprestados e ex-jogadores. Clique numa linha pra ver a ficha completa.
        </div>
      </div>
    </section>
  );
}

window.Jogadores = Jogadores;
