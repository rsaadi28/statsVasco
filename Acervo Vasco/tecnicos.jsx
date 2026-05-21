// Acervo Vasco — aba Técnicos

function Tecnicos({ onOpenPlayer, onOpenMatch }) {
  const all = window.TECNICOS;
  const [busca, setBusca] = useState("");
  const [sort, setSort]   = useState({ k:"jogos", dir:"desc" });
  const [selected, setSelected] = useState(null);

  const filtered = useMemo(() => {
    let out = all.filter(t => !busca.trim() || t.nome.toLowerCase().includes(busca.trim().toLowerCase()));
    out = [...out].sort((a,b) => {
      const av = a[sort.k], bv = b[sort.k];
      if (typeof av === "string") return sort.dir==="asc" ? av.localeCompare(bv,"pt-BR") : bv.localeCompare(av,"pt-BR");
      return sort.dir==="asc" ? av - bv : bv - av;
    });
    return out;
  }, [all, busca, sort]);

  function clickSort(k) {
    setSort(s => s.k === k ? { k, dir: s.dir==="asc"?"desc":"asc" } : { k, dir:"desc" });
  }

  if (selected) {
    return <TecnicoDetalhe nome={selected} onBack={()=>setSelected(null)} onOpenPlayer={onOpenPlayer} onOpenMatch={onOpenMatch} />;
  }

  return (
    <div className="main">
      <section className="ea-hero">
        <div className="hero-eyebrow">Acervo · Técnicos</div>
        <div className="ea-hero-line">
          <div>
            <h1 className="ea-title">Técnicos</h1>
            <p className="ea-sub">Todos os técnicos que comandaram o Vasco no acervo. Clique numa linha pra ver passagens e jogos detalhados.</p>
          </div>
          <div className="ea-search">
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="7" cy="7" r="5"/><path d="M14 14L11 11"/></svg>
            <input placeholder="buscar técnico…" value={busca} onChange={(e)=>setBusca(e.target.value)} />
          </div>
        </div>
      </section>

      <h3 className="ea-section-title">Lista de técnicos <small>{filtered.length}</small></h3>
      <div className="table-wrap">
        <table className="tbl ea-tbl tec-tbl">
          <thead>
            <tr>
              <SortTh k="nome"  cur={sort} onClick={clickSort}>Técnico</SortTh>
              <SortTh k="jogos" cur={sort} onClick={clickSort} numeric>Jogos</SortTh>
              <SortTh k="casa"  cur={sort} onClick={clickSort} numeric>Casa</SortTh>
              <SortTh k="fora"  cur={sort} onClick={clickSort} numeric>Fora</SortTh>
              <SortTh k="v"     cur={sort} onClick={clickSort} numeric>V</SortTh>
              <SortTh k="e"     cur={sort} onClick={clickSort} numeric>E</SortTh>
              <SortTh k="d"     cur={sort} onClick={clickSort} numeric>D</SortTh>
              <SortTh k="gp"    cur={sort} onClick={clickSort} numeric>GP</SortTh>
              <SortTh k="gc"    cur={sort} onClick={clickSort} numeric>GC</SortTh>
              <SortTh k="saldo" cur={sort} onClick={clickSort} numeric>Saldo</SortTh>
              <SortTh k="aprov" cur={sort} onClick={clickSort} numeric>Aprov.</SortTh>
              <th style={{minWidth:180}}>Maior Goleador</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(t => (
              <tr key={t.nome} className="has-detail" onClick={()=>setSelected(t.nome)}>
                <td className="opponent" style={{fontFamily:"var(--ff-serif)", fontSize:15, fontWeight:600}}>
                  <Monogram club={t.nome} />
                  {t.nome}
                </td>
                <td className="num"><strong>{t.jogos}</strong></td>
                <td className="num">{t.casa}</td>
                <td className="num">{t.fora}</td>
                <td className="num c-v">{t.v}</td>
                <td className="num c-e">{t.e}</td>
                <td className="num c-d">{t.d}</td>
                <td className="num">{t.gp}</td>
                <td className="num">{t.gc}</td>
                <td className={"num " + (t.saldo>0?"c-v":(t.saldo<0?"c-d":""))}>{t.saldo > 0 ? "+" : ""}{t.saldo}</td>
                <td className="num">{t.aprov.toFixed(1)}%</td>
                <td style={{fontFamily:"var(--ff-serif)", fontSize:14}}>
                  {t.maior_goleador ? <>{t.maior_goleador.nome} <span style={{fontFamily:"var(--ff-mono)", fontSize:11, color:"var(--ink-mute)"}}>({t.maior_goleador.gols})</span></> : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ============ Detalhe do técnico ============
function TecnicoDetalhe({ nome, onBack, onOpenPlayer, onOpenMatch }) {
  const tec = window.TECNICOS.find(t => t.nome === nome);
  const passagensData = window.PASSAGENS_TECNICOS?.[nome];
  const [passagemSel, setPassagemSel] = useState("todas");
  const jogosFiltrados = useMemo(() => {
    const jogos = passagensData?.jogos || [];
    if (passagemSel === "todas") return jogos;
    return jogos.filter(j => j.passagem === passagemSel);
  }, [passagensData, passagemSel]);
  const passagemLabel = passagemSel === "todas" ? "todas as passagens" : `${passagemSel}ª passagem`;
  const resumoTotal = passagensData?.resumo || {
    jogos: tec.jogos, v: tec.v, e: tec.e, d: tec.d, gp: tec.gp, gc: tec.gc,
    saldo: tec.saldo, aprov: tec.aprov, artilheiro: tec.maior_goleador,
  };

  return (
    <div className="main">
      <button className="detail-back" onClick={onBack}><span className="arrow">‹</span> Voltar para técnicos</button>

      <section className="tec-hero">
        <div className="hero-eyebrow">Acervo · Técnico</div>
        <h1 className="tec-name">{nome}</h1>
        <div className="tec-resumo">
          <span><strong>{resumoTotal.jogos}</strong> jogos somados</span>
          <span className="dot">·</span>
          <span><strong>{passagensData?.passagens?.length || 0}</strong> passagem{(passagensData?.passagens?.length || 0) === 1 ? "" : "ens"}</span>
          <span className="dot">·</span>
          <span><strong style={{color:"var(--r-v)"}}>{resumoTotal.v}</strong> V</span>
          <span className="dot">·</span>
          <span><strong style={{color:"var(--r-e)"}}>{resumoTotal.e}</strong> E</span>
          <span className="dot">·</span>
          <span><strong style={{color:"var(--r-d)"}}>{resumoTotal.d}</strong> D</span>
          <span className="dot">·</span>
          <span><strong>{resumoTotal.aprov.toFixed(1)}%</strong> aproveitamento</span>
          <span className="dot">·</span>
          <span>saldo <strong style={{color: resumoTotal.saldo>=0?"var(--r-v)":"var(--r-d)"}}>{resumoTotal.saldo>0?"+":""}{resumoTotal.saldo}</strong></span>
        </div>
      </section>

      {passagensData ? (
        <>
          <h3 className="ea-section-title">Passagens pelo Vasco <small>{passagensData.passagens.length}</small></h3>
          <div className="table-wrap">
            <table className="tbl ea-tbl">
              <thead>
                <tr>
                  <th style={{width:80}}>Passagem</th>
                  <th style={{width:120}}>Período</th>
                  <th className="num">Jogos</th>
                  <th className="num">V</th>
                  <th className="num">E</th>
                  <th className="num">D</th>
                  <th className="num">GP</th>
                  <th className="num">GC</th>
                  <th className="num">Saldo</th>
                  <th className="num">Aprov.</th>
                  <th>Artilheiro</th>
                </tr>
              </thead>
              <tbody>
                {passagensData.passagens.map(p => (
                  <tr key={p.idx} className={"has-detail" + (passagemSel===p.idx?" is-sel":"")} onClick={()=>setPassagemSel(p.idx)}>
                    <td><span className="pos-chip" style={{background:"var(--ink)", color:"var(--paper-light)", borderColor:"var(--ink)"}}>{p.idx}ª</span></td>
                    <td style={{fontFamily:"var(--ff-serif)", fontSize:13, fontStyle:"italic", color:"var(--ink-soft)"}}>{p.periodo}</td>
                    <td className="num"><strong>{p.jogos}</strong></td>
                    <td className="num c-v">{p.v}</td>
                    <td className="num c-e">{p.e}</td>
                    <td className="num c-d">{p.d}</td>
                    <td className="num">{p.gp}</td>
                    <td className="num">{p.gc}</td>
                    <td className={"num " + (p.saldo>0?"c-v":(p.saldo<0?"c-d":""))}>{p.saldo > 0 ? "+" : ""}{p.saldo}</td>
                    <td className="num">{p.aprov.toFixed(1)}%</td>
                    <td style={{fontFamily:"var(--ff-serif)", fontSize:14}}>
                      <button className="plink" onClick={(e)=>{ e.stopPropagation(); onOpenPlayer && onOpenPlayer(p.artilheiro.nome); }}>
                        {p.artilheiro.nome}
                      </button>
                      <span style={{fontFamily:"var(--ff-mono)", fontSize:11, color:"var(--ink-mute)", marginLeft:6}}>({p.artilheiro.gols})</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {passagensData.jogos && (
            <>
              <div className="toolbar" style={{marginTop:28, marginBottom:16}}>
                <div className="chips">
                  <button className={"chip" + (passagemSel === "todas" ? " active" : "")} onClick={()=>setPassagemSel("todas")}>
                    Todas <span className="count">{passagensData.jogos.length}</span>
                  </button>
                  {passagensData.passagens.map(p => (
                    <button key={p.idx} className={"chip" + (passagemSel === p.idx ? " active" : "")} onClick={()=>setPassagemSel(p.idx)}>
                      {p.idx}ª passagem <span className="count">{p.jogos}</span>
                    </button>
                  ))}
                </div>
              </div>

              <h3 className="ea-section-title" style={{marginTop:32}}>
                Jogos de <span className="ea-sel">{passagemLabel}</span>
                <small>{jogosFiltrados.length} registros</small>
              </h3>
              <div className="table-wrap">
                <table className="tbl ea-tbl">
                  <thead>
                    <tr>
                      <th style={{width:92}}>Passagem</th>
                      <th style={{width:90}}>Data</th>
                      <th style={{width:60}}>Local</th>
                      <th style={{width:170}}>Competição</th>
                      <th>Adversário</th>
                      <th style={{width:24}}></th>
                      <th style={{width:220}}>Placar</th>
                    </tr>
                  </thead>
                  <tbody>
                    {jogosFiltrados.map((j,i) => (
                      <tr key={i} className="has-detail" onClick={()=> onOpenMatch && onOpenMatch({ data: j.data, adversario: j.adv })}>
                        <td><span className="pos-chip">{j.passagem}ª</span></td>
                        <td className="date">{j.data}</td>
                        <td className="locale">{j.local}</td>
                        <td className="competition">{j.competicao}</td>
                        <td className="opponent"><Monogram club={j.adv}/>{j.adv}</td>
                        <td className="result-cell"><span className={"result-dot " + j.res}/></td>
                        <td style={{fontFamily:"var(--ff-serif)", fontSize:14}}>{j.placar}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </>
      ) : (
        <div className="ea-empty">
          Passagens detalhadas de <strong style={{color:"var(--ink)", fontStyle:"normal"}}>{nome}</strong> ainda não foram migradas para o acervo web.
        </div>
      )}
    </div>
  );
}

window.Tecnicos = Tecnicos;
