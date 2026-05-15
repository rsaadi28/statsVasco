// Acervo Vasco — abas Estádios e Árbitros

// ============ Estádios ============
function Estadios({ onOpenMatch }) {
  const all = window.ESTADIOS;
  const [busca, setBusca] = useState("");
  const [sel, setSel] = useState("São Januário");
  const [sort, setSort] = useState({ k:"jogos", dir:"desc" });
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const detailRef = React.useRef(null);

  function selectEstadio(nome) {
    setSel(nome);
    setPage(1);
    requestAnimationFrame(() => {
      const el = detailRef.current;
      if (!el) return;
      const top = el.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top, behavior: "smooth" });
    });
  }

  const filtered = useMemo(() => {
    let out = all.filter(e => !busca.trim() || e.nome.toLowerCase().includes(busca.trim().toLowerCase()));
    out = [...out].sort((a,b) => {
      const av = a[sort.k], bv = b[sort.k];
      if (typeof av === "string") return sort.dir==="asc" ? av.localeCompare(bv,"pt-BR") : bv.localeCompare(av,"pt-BR");
      return sort.dir==="asc" ? av - bv : bv - av;
    });
    return out;
  }, [all, busca, sort]);

  const jogos = (window.JOGOS_POR_ESTADIO?.[sel]) || [];
  const totalPages = Math.max(1, Math.ceil(jogos.length / pageSize));
  const curPage = Math.min(page, totalPages);
  const pagedJogos = jogos.slice((curPage-1)*pageSize, curPage*pageSize);

  function clickSort(k) {
    setSort(s => s.k === k ? { k, dir: s.dir==="asc"?"desc":"asc" } : { k, dir:"desc" });
  }

  return (
    <div className="main">
      <EAHero
        eyebrow="Acervo · Estádios"
        title="Estádios"
        sub="Resumo de todos os palcos em que o Vasco já jogou no acervo — clique numa linha para listar os jogos."
        right={(
          <div className="ea-search">
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="7" cy="7" r="5"/><path d="M14 14L11 11"/></svg>
            <input placeholder="buscar estádio…" value={busca} onChange={(e)=>setBusca(e.target.value)} />
          </div>
        )}
      />
      <div className="ea-grid">
        <div className="ea-master">
          <h3 className="ea-section-title">Lista de estádios <small>{filtered.length}</small></h3>
          <div className="table-wrap">
            <table className="tbl ea-tbl">
              <thead>
                <tr>
                  <SortTh k="nome"  cur={sort} onClick={clickSort} style={{minWidth:240}}>Estádio</SortTh>
                  <SortTh k="jogos" cur={sort} onClick={clickSort} numeric>Jogos</SortTh>
                  <SortTh k="v"     cur={sort} onClick={clickSort} numeric>V</SortTh>
                  <SortTh k="e"     cur={sort} onClick={clickSort} numeric>E</SortTh>
                  <SortTh k="d"     cur={sort} onClick={clickSort} numeric>D</SortTh>
                  <SortTh k="gp"    cur={sort} onClick={clickSort} numeric>GP</SortTh>
                  <SortTh k="gc"    cur={sort} onClick={clickSort} numeric>GC</SortTh>
                  <th className="num">Saldo</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(e => (
                  <tr key={e.nome} className={"has-detail" + (sel===e.nome?" is-sel":"")} onClick={()=> selectEstadio(e.nome)}>
                    <td className="opponent" style={{fontWeight:600}}>{e.nome}</td>
                    <td className="num">{fmtN(e.jogos)}</td>
                    <td className="num c-v">{e.v}</td>
                    <td className="num c-e">{e.e}</td>
                    <td className="num c-d">{e.d}</td>
                    <td className="num">{fmtN(e.gp)}</td>
                    <td className="num">{fmtN(e.gc)}</td>
                    <td className={"num " + (e.gp-e.gc>0?"c-v":(e.gp-e.gc<0?"c-d":""))}>{(e.gp-e.gc) > 0 ? "+" : ""}{e.gp-e.gc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="ea-detail" ref={detailRef}>
          <h3 className="ea-section-title">Jogos do Vasco em <span className="ea-sel">{sel}</span> <small>{jogos.length} registros</small></h3>
          {jogos.length === 0 ? (
            <div className="ea-empty">Sem jogos detalhados deste estádio no acervo web.</div>
          ) : (
            <>
              <Paginacao
                page={curPage} totalPages={totalPages} pageSize={pageSize}
                setPage={setPage} setPageSize={setPageSize}
                total={jogos.length}
              />
              <div className="table-wrap">
                <table className="tbl ea-tbl">
                  <thead>
                    <tr>
                      <th style={{width:90}}>Data</th>
                      <th style={{width:24}}></th>
                      <th style={{width:60}}>Local</th>
                      <th style={{width:170}}>Competição</th>
                      <th>Adversário</th>
                      <th style={{width:220}}>Placar</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pagedJogos.map((j,i) => (
                      <tr key={i} className="has-detail" onClick={()=> onOpenMatch && onOpenMatch({ data: j.data, adversario: j.adv })}>
                        <td className="date">{j.data}</td>
                        <td className="result-cell"><span className={"result-dot " + j.res}/></td>
                        <td className="locale">{j.local}</td>
                        <td className="competition">{shortCompEA(j.competicao)}</td>
                        <td className="opponent">
                          <Monogram club={j.adv}/>
                          <span>{j.adv}</span>
                        </td>
                        <td style={{fontFamily:"var(--ff-serif)", fontSize:14}}>{j.placar}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ============ Árbitros ============
function Arbitros({ onOpenMatch }) {
  const all = window.ARBITROS;
  const [busca, setBusca] = useState("");
  const [local, setLocal] = useState("todos");
  const [ano, setAno]     = useState("todos");
  const [sel, setSel]     = useState(null);
  const [sort, setSort]   = useState({ k:"jogos", dir:"desc" });
  const [page, setPage]   = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const detailRef = React.useRef(null);

  function selectArbitro(nome) {
    setSel(nome);
    setPage(1);
    requestAnimationFrame(() => {
      const el = detailRef.current;
      if (!el) return;
      const top = el.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top, behavior: "smooth" });
    });
  }

  const filteredArbs = useMemo(() => {
    let out = all.filter(a => !busca.trim() || a.nome.toLowerCase().includes(busca.trim().toLowerCase()));
    out = [...out].sort((a,b) => {
      const av = a[sort.k], bv = b[sort.k];
      if (typeof av === "string") return sort.dir==="asc" ? av.localeCompare(bv,"pt-BR") : bv.localeCompare(av,"pt-BR");
      return sort.dir==="asc" ? av - bv : bv - av;
    });
    return out;
  }, [all, busca, sort]);

  // resolve jogos do árbitro selecionado
  const jogos = useMemo(() => {
    if (!sel) return [];
    const lista = window.JOGOS_POR_ARBITRO?.[sel] || [];
    if (lista.length > 0) return lista;
    // monta a partir de primeiro/ultimo se necessário
    const arb = all.find(a => a.nome === sel);
    if (!arb) return [];
    if (arb.primeiro.data === arb.ultimo.data) {
      return [{ data: arb.primeiro.data, local: "—", competicao: "—", adv: extractAdv(arb.primeiro.placar), res: scoreRes(arb.primeiro.placar), placar: arb.primeiro.placar }];
    }
    return [
      { data: arb.primeiro.data, local: "—", competicao: "—", adv: extractAdv(arb.primeiro.placar), res: scoreRes(arb.primeiro.placar), placar: arb.primeiro.placar },
      { data: arb.ultimo.data,   local: "—", competicao: "—", adv: extractAdv(arb.ultimo.placar),   res: scoreRes(arb.ultimo.placar),   placar: arb.ultimo.placar },
    ];
  }, [sel, all]);

  const filteredJogos = jogos.filter(j => {
    if (local !== "todos" && j.local !== local) return false;
    if (ano !== "todos" && !j.data.endsWith(`/${ano}`)) return false;
    return true;
  });
  const totalPages = Math.max(1, Math.ceil(filteredJogos.length / pageSize));
  const curPage = Math.min(page, totalPages);
  const pagedJogos = filteredJogos.slice((curPage-1)*pageSize, curPage*pageSize);

  // anos disponíveis: todos do acervo (2000-2026), independentemente do árbitro
  const anosDisponiveis = useMemo(() => {
    const out = [];
    for (let y = 2026; y >= 2000; y--) out.push(String(y));
    return out;
  }, []);

  function clickSort(k) {
    setSort(s => s.k === k ? { k, dir: s.dir==="asc"?"desc":"asc" } : { k, dir:"desc" });
  }

  return (
    <div className="main">
      <EAHero
        eyebrow="Acervo · Árbitros"
        title="Árbitros"
        sub="Lista de árbitros principais que já apitaram jogos do Vasco no acervo. Clique numa linha para ver todos os jogos apitados."
        right={(
          <div className="ea-search">
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="7" cy="7" r="5"/><path d="M14 14L11 11"/></svg>
            <input placeholder="buscar árbitro…" value={busca} onChange={(e)=>setBusca(e.target.value)} />
          </div>
        )}
      />

      <div className="ea-grid">
        <div className="ea-master">
          <h3 className="ea-section-title">Árbitros <small>{filteredArbs.length}</small></h3>
          <div className="table-wrap">
            <table className="tbl ea-tbl arb-tbl">
              <thead>
                <tr>
                  <SortTh k="nome"  cur={sort} onClick={clickSort}>Árbitro</SortTh>
                  <SortTh k="jogos" cur={sort} onClick={clickSort} numeric>Jogos</SortTh>
                  <th>Primeiro Jogo</th>
                  <th>Último Jogo</th>
                  <SortTh k="v" cur={sort} onClick={clickSort} numeric>V</SortTh>
                  <SortTh k="e" cur={sort} onClick={clickSort} numeric>E</SortTh>
                  <SortTh k="d" cur={sort} onClick={clickSort} numeric>D</SortTh>
                  <SortTh k="gp" cur={sort} onClick={clickSort} numeric>GP</SortTh>
                  <SortTh k="gc" cur={sort} onClick={clickSort} numeric>GC</SortTh>
                  <th className="num">Saldo</th>
                </tr>
              </thead>
              <tbody>
                {filteredArbs.map(a => (
                  <tr key={a.nome} className={"has-detail" + (sel===a.nome?" is-sel":"")} onClick={()=> selectArbitro(a.nome)}>
                    <td className="opponent" style={{fontWeight:600, gap:8}}>{a.nome}</td>
                    <td className="num">{a.jogos}</td>
                    <td style={{fontFamily:"var(--ff-mono)", fontSize:11, color:"var(--ink-mute)"}}>{a.primeiro.data} <span style={{color:"var(--ink-faint)"}}>·</span> <span style={{color:"var(--ink-soft)"}}>{a.primeiro.placar}</span></td>
                    <td style={{fontFamily:"var(--ff-mono)", fontSize:11, color:"var(--ink-mute)"}}>{a.ultimo.data} <span style={{color:"var(--ink-faint)"}}>·</span> <span style={{color:"var(--ink-soft)"}}>{a.ultimo.placar}</span></td>
                    <td className="num c-v">{a.v}</td>
                    <td className="num c-e">{a.e}</td>
                    <td className="num c-d">{a.d}</td>
                    <td className="num">{a.gp}</td>
                    <td className="num">{a.gc}</td>
                    <td className={"num " + (a.gp-a.gc>0?"c-v":(a.gp-a.gc<0?"c-d":""))}>{(a.gp-a.gc) > 0 ? "+" : ""}{a.gp-a.gc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="ea-detail" ref={detailRef}>
          {!sel ? (
            <div className="ea-empty">Selecione um árbitro acima para ver os jogos apitados.</div>
          ) : (
            <>
              <h3 className="ea-section-title">Jogos apitados por <span className="ea-sel">{sel}</span> <small>{filteredJogos.length} de {jogos.length}</small></h3>
              <div className="arb-filtros">
                <div className="arb-rad">
                  <span className="lbl">Local</span>
                  {["todos","casa","fora"].map(k => (
                    <button key={k} className={local===k?"active":""} onClick={()=>{ setLocal(k); setPage(1); }}>{k}</button>
                  ))}
                </div>
                <div className="arb-rad">
                  <span className="lbl">Ano</span>
                  <button className={ano==="todos"?"active":""} onClick={()=>{ setAno("todos"); setPage(1); }}>todos</button>
                  <select
                    className="arb-ano-select"
                    value={ano==="todos" ? "" : ano}
                    onChange={(e)=>{ setAno(e.target.value || "todos"); setPage(1); }}
                  >
                    <option value="">selecione um ano…</option>
                    {anosDisponiveis.map(a => (
                      <option key={a} value={a}>{a}</option>
                    ))}
                  </select>
                  {ano !== "todos" && (
                    <button className="active" onClick={()=>{ setAno("todos"); setPage(1); }} title="limpar filtro">
                      {ano} ×
                    </button>
                  )}
                </div>
              </div>
              <Paginacao
                page={curPage} totalPages={totalPages} pageSize={pageSize}
                setPage={setPage} setPageSize={setPageSize}
                total={filteredJogos.length}
              />
              <div className="table-wrap">
                <table className="tbl ea-tbl">
                  <thead>
                    <tr>
                      <th style={{width:90}}>Data</th>
                      <th style={{width:24}}></th>
                      <th style={{width:60}}>Local</th>
                      <th style={{width:170}}>Competição</th>
                      <th>Adversário</th>
                      <th style={{width:220}}>Placar</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pagedJogos.map((j,i) => (
                      <tr key={i} className="has-detail" onClick={()=> onOpenMatch && onOpenMatch({ data: j.data, adversario: j.adv })}>
                        <td className="date">{j.data}</td>
                        <td className="result-cell"><span className={"result-dot " + j.res}/></td>
                        <td className="locale">{j.local}</td>
                        <td className="competition">{shortCompEA(j.competicao)}</td>
                        <td className="opponent">
                          <Monogram club={j.adv}/>
                          <span>{j.adv}</span>
                        </td>
                        <td style={{fontFamily:"var(--ff-serif)", fontSize:14}}>{j.placar}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ============ Helpers compartilhados ============
function EAHero({ eyebrow, title, sub, right }) {
  return (
    <section className="ea-hero">
      <div className="hero-eyebrow">{eyebrow}</div>
      <div className="ea-hero-line">
        <div>
          <h1 className="ea-title">{title}</h1>
          <p className="ea-sub">{sub}</p>
        </div>
        {right}
      </div>
    </section>
  );
}

function SortTh({ k, cur, onClick, children, numeric, style }) {
  const active = cur.k === k;
  const arrow = active ? (cur.dir==="asc" ? "▲" : "▼") : "";
  return (
    <th onClick={()=>onClick(k)} className={(numeric?"num ":"") + "sort-th" + (active?" is-active":"")} style={{cursor:"pointer", ...style}}>
      {children} {arrow && <span className="sort-arrow">{arrow}</span>}
    </th>
  );
}

function Paginacao({ page, totalPages, pageSize, setPage, setPageSize, total }) {
  return (
    <div className="ea-paginacao">
      <div className="ea-pag-left">
        <span className="lbl">Por página</span>
        {[10, 30, 100].map(n => (
          <button key={n} className={pageSize===n?"active":""} onClick={()=>{ setPageSize(n); setPage(1); }}>{n}</button>
        ))}
        <span className="ea-pag-info">{total} {total===1?"jogo":"jogos"}</span>
      </div>
      <div className="ea-pag-right">
        <button onClick={()=>setPage(p=>Math.max(1,p-1))} disabled={page<=1}>‹ anterior</button>
        <span className="ea-pag-curr">página {page} <span style={{color:"var(--ink-faint)"}}>de</span> {totalPages}</span>
        <button onClick={()=>setPage(p=>Math.min(totalPages,p+1))} disabled={page>=totalPages}>próxima ›</button>
      </div>
    </div>
  );
}

function shortCompEA(c) {
  return {
    "Campeonato Brasileiro Série A": "Brasileiro A",
    "Campeonato Brasileiro Série B": "Brasileiro B",
    "Campeonato Carioca": "Carioca",
    "Copa do Brasil": "Copa do Brasil",
    "Copa Sul-Americana": "Sul-Americana",
    "Copa Libertadores": "Libertadores",
    "Copa Mercosul": "Mercosul",
    "—": "—",
  }[c] || c;
}

function extractAdv(placar) {
  // "Vasco N x M Adversário"
  const m = placar.match(/Vasco \d+ x \d+ (.+)$/);
  return m ? m[1] : "—";
}
function scoreRes(placar) {
  const m = placar.match(/Vasco (\d+) x (\d+) /);
  if (!m) return "E";
  const a = +m[1], b = +m[2];
  if (a > b) return "V";
  if (a < b) return "D";
  return "E";
}

window.Estadios = Estadios;
window.Arbitros = Arbitros;
