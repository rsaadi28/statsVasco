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
  const [tab, setTab] = useState("arbitro");
  const [busca, setBusca] = useState("");
  const [local, setLocal] = useState("todos");
  const [ano, setAno]     = useState("todos");
  const [sel, setSel]     = useState(null);
  const [sort, setSort]   = useState({ k:"jogos", dir:"desc" });
  const [page, setPage]   = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [combPage, setCombPage] = useState(1);
  const detailRef = React.useRef(null);
  const combinacoesPageSize = 50;

  const configs = useMemo(() => arbitragemConfigs(), []);
  const cfg = configs[tab] || configs.arbitro;
  const all = cfg.rows || [];

  useEffect(() => {
    setSel(null);
    setPage(1);
    setCombPage(1);
    setLocal("todos");
    setAno("todos");
    setSort({ k:"jogos", dir:"desc" });
  }, [tab]);

  useEffect(() => {
    setCombPage(1);
  }, [busca, sort.k, sort.dir]);

  function selectRegistro(row) {
    setSel(cfg.key(row));
    setPage(1);
    requestAnimationFrame(() => {
      const el = detailRef.current;
      if (!el) return;
      const top = el.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top, behavior: "smooth" });
    });
  }

  const filteredRows = useMemo(() => {
    const termo = busca.trim().toLowerCase();
    let out = all.filter(row => !termo || cfg.searchText(row).toLowerCase().includes(termo));
    out = [...out].sort((a,b) => {
      const av = sortValueArbitragem(a, sort.k), bv = sortValueArbitragem(b, sort.k);
      if (typeof av === "string" || typeof bv === "string") {
        return sort.dir==="asc"
          ? String(av).localeCompare(String(bv),"pt-BR")
          : String(bv).localeCompare(String(av),"pt-BR");
      }
      return sort.dir==="asc" ? av - bv : bv - av;
    });
    return out;
  }, [all, busca, sort, cfg]);

  const selectedRow = useMemo(() => {
    if (!sel) return null;
    return all.find(row => cfg.key(row) === sel) || null;
  }, [all, cfg, sel]);

  const totalCombinacoesPages = Math.max(1, Math.ceil(filteredRows.length / combinacoesPageSize));
  const curCombinacoesPage = Math.min(combPage, totalCombinacoesPages);
  const rowsTabela = tab === "combinacoes"
    ? filteredRows.slice((curCombinacoesPage - 1) * combinacoesPageSize, curCombinacoesPage * combinacoesPageSize)
    : filteredRows;

  const jogos = useMemo(() => {
    if (!sel) return [];
    const lista = cfg.games?.[sel] || [];
    if (lista.length > 0) return lista;
    if (!selectedRow?.primeiro || !selectedRow?.ultimo) return [];
    if (selectedRow.primeiro.data === selectedRow.ultimo.data) {
      return [fallbackGameFromMarker(selectedRow.primeiro)];
    }
    return [fallbackGameFromMarker(selectedRow.primeiro), fallbackGameFromMarker(selectedRow.ultimo)];
  }, [cfg, sel, selectedRow]);

  const filteredJogos = jogos.filter(j => {
    if (local !== "todos" && String(j.local || "").toLowerCase() !== local) return false;
    if (ano !== "todos" && !j.data.endsWith(`/${ano}`)) return false;
    return true;
  });
  const totalPages = Math.max(1, Math.ceil(filteredJogos.length / pageSize));
  const curPage = Math.min(page, totalPages);
  const pagedJogos = filteredJogos.slice((curPage-1)*pageSize, curPage*pageSize);

  const anosDisponiveis = useMemo(() => {
    const set = new Set();
    Object.values(configs).forEach(c => {
      Object.values(c.games || {}).flat().forEach(j => {
        const ano = String(j.data || "").slice(-4);
        if (/^\d{4}$/.test(ano)) set.add(ano);
      });
    });
    if (!set.size) {
      for (let y = 2026; y >= 2000; y--) set.add(String(y));
    }
    return Array.from(set).sort((a,b) => Number(b) - Number(a));
  }, [configs]);

  function clickSort(k) {
    setSort(s => s.k === k ? { k, dir: s.dir==="asc"?"desc":"asc" } : { k, dir:"desc" });
  }

  return (
    <div className="main">
      <EAHero
        eyebrow="Acervo · Árbitros"
        title="Arbitragem"
        sub="Árbitros principais, auxiliares, VARs e combinações completas de arbitragem em jogos do Vasco."
        right={(
          <div className="ea-search">
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="7" cy="7" r="5"/><path d="M14 14L11 11"/></svg>
            <input placeholder={cfg.placeholder} value={busca} onChange={(e)=>setBusca(e.target.value)} />
          </div>
        )}
      />

      <nav className="ea-tabs">
        {Object.entries(configs).map(([key, item]) => (
          <button key={key} className={tab===key?"active":""} onClick={()=>setTab(key)}>
            {item.tab} <span>{item.rows.length}</span>
          </button>
        ))}
      </nav>

      <div className="ea-grid">
        <div className="ea-master">
          <h3 className="ea-section-title">{cfg.heading} <small>{filteredRows.length}</small></h3>
          {tab === "combinacoes" && (
            <PaginacaoLinhas
              page={curCombinacoesPage}
              totalPages={totalCombinacoesPages}
              pageSize={combinacoesPageSize}
              setPage={setCombPage}
              total={filteredRows.length}
            />
          )}
          <div className="table-wrap">
            <table className="tbl ea-tbl arb-tbl">
              {tab === "combinacoes"
                ? <TabelaCombinacoes rows={rowsTabela} selected={sel} onSelect={selectRegistro} sort={sort} clickSort={clickSort} />
                : <TabelaOficiais rows={rowsTabela} selected={sel} onSelect={selectRegistro} sort={sort} clickSort={clickSort} label={cfg.label} />}
            </table>
          </div>
        </div>

        <div className="ea-detail" ref={detailRef}>
          {!sel ? (
            <div className="ea-empty">Selecione um registro acima para ver os jogos.</div>
          ) : (
            <>
              <h3 className="ea-section-title">
                {cfg.detailTitle(selectedRow)}
                <small>{filteredJogos.length} de {jogos.length}</small>
              </h3>
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
                      <th style={{width:190}}>Árbitro</th>
                      <th style={{width:280}}>Auxiliares</th>
                      <th style={{width:180}}>VAR</th>
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
                        <td className="official-cell">{displayOfficial(j.arbitro)}</td>
                        <td className="official-cell">{displayOfficials(j.auxiliares)}</td>
                        <td className="official-cell">{displayOfficial(j.var)}</td>
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

function arbitragemConfigs() {
  return {
    arbitro: {
      tab: "Árbitros",
      heading: "Árbitros principais",
      label: "Árbitro",
      placeholder: "buscar árbitro…",
      rows: window.ARBITROS || [],
      games: window.JOGOS_POR_ARBITRO || {},
      key: row => row?.nome || "",
      searchText: row => row?.nome || "",
      detailTitle: row => <>Jogos com <span className="ea-sel">{row?.nome || "—"}</span> como árbitro</>,
    },
    auxiliar: {
      tab: "Auxiliares",
      heading: "Auxiliares",
      label: "Auxiliar",
      placeholder: "buscar auxiliar…",
      rows: window.AUXILIARES_ARBITRAGEM || [],
      games: window.JOGOS_POR_AUXILIAR || {},
      key: row => row?.nome || "",
      searchText: row => row?.nome || "",
      detailTitle: row => <>Jogos com <span className="ea-sel">{row?.nome || "—"}</span> como auxiliar</>,
    },
    var: {
      tab: "VARs",
      heading: "VARs",
      label: "VAR",
      placeholder: "buscar VAR…",
      rows: window.VARS_ARBITRAGEM || [],
      games: window.JOGOS_POR_VAR || {},
      key: row => row?.nome || "",
      searchText: row => row?.nome || "",
      detailTitle: row => <>Jogos com <span className="ea-sel">{row?.nome || "—"}</span> no VAR</>,
    },
    combinacoes: {
      tab: "Combinações",
      heading: "Combinações de arbitragem",
      label: "Combinação",
      placeholder: "buscar árbitro, auxiliar ou VAR…",
      rows: window.COMBINACOES_ARBITRAGEM || [],
      games: window.JOGOS_POR_COMBINACAO_ARBITRAGEM || {},
      key: row => row?.id || "",
      searchText: row => [row?.arbitro, ...(row?.auxiliares || []), row?.var].filter(Boolean).join(" "),
      detailTitle: row => <>Jogos desta <span className="ea-sel">combinação</span></>,
    },
  };
}

function TabelaOficiais({ rows, selected, onSelect, sort, clickSort, label }) {
  return (
    <>
      <thead>
        <tr>
          <SortTh k="nome"  cur={sort} onClick={clickSort}>{label}</SortTh>
          <SortTh k="jogos" cur={sort} onClick={clickSort} numeric>Jogos</SortTh>
          <SortTh k="primeiro" cur={sort} onClick={clickSort}>Primeiro Jogo</SortTh>
          <SortTh k="ultimo" cur={sort} onClick={clickSort}>Último Jogo</SortTh>
          <SortTh k="v" cur={sort} onClick={clickSort} numeric>V</SortTh>
          <SortTh k="e" cur={sort} onClick={clickSort} numeric>E</SortTh>
          <SortTh k="d" cur={sort} onClick={clickSort} numeric>D</SortTh>
          <SortTh k="gp" cur={sort} onClick={clickSort} numeric>GP</SortTh>
          <SortTh k="gc" cur={sort} onClick={clickSort} numeric>GC</SortTh>
          <SortTh k="saldo" cur={sort} onClick={clickSort} numeric>Saldo</SortTh>
        </tr>
      </thead>
      <tbody>
        {rows.map(row => (
          <tr key={row.nome} className={"has-detail" + (selected===row.nome?" is-sel":"")} onClick={()=> onSelect(row)}>
            <td className="opponent" style={{fontWeight:600, gap:8}}>{row.nome}</td>
            <td className="num">{row.jogos}</td>
            <td className="ea-match-marker">{row.primeiro?.data || "—"} <span>·</span> {row.primeiro?.placar || "—"}</td>
            <td className="ea-match-marker">{row.ultimo?.data || "—"} <span>·</span> {row.ultimo?.placar || "—"}</td>
            <td className="num c-v">{row.v}</td>
            <td className="num c-e">{row.e}</td>
            <td className="num c-d">{row.d}</td>
            <td className="num">{row.gp}</td>
            <td className="num">{row.gc}</td>
            <td className={"num " + (Number(row.saldo ?? row.gp-row.gc)>0?"c-v":(Number(row.saldo ?? row.gp-row.gc)<0?"c-d":""))}>{fmtSaldo(row.saldo ?? row.gp-row.gc)}</td>
          </tr>
        ))}
      </tbody>
    </>
  );
}

function TabelaCombinacoes({ rows, selected, onSelect, sort, clickSort }) {
  return (
    <>
      <thead>
        <tr>
          <SortTh k="arbitro" cur={sort} onClick={clickSort}>Árbitro</SortTh>
          <SortTh k="auxiliares" cur={sort} onClick={clickSort}>Auxiliares</SortTh>
          <SortTh k="var" cur={sort} onClick={clickSort}>VAR</SortTh>
          <SortTh k="jogos" cur={sort} onClick={clickSort} numeric>Jogos</SortTh>
          <SortTh k="primeiro" cur={sort} onClick={clickSort}>Primeiro Jogo</SortTh>
          <SortTh k="ultimo" cur={sort} onClick={clickSort}>Último Jogo</SortTh>
          <SortTh k="v" cur={sort} onClick={clickSort} numeric>V</SortTh>
          <SortTh k="e" cur={sort} onClick={clickSort} numeric>E</SortTh>
          <SortTh k="d" cur={sort} onClick={clickSort} numeric>D</SortTh>
          <SortTh k="saldo" cur={sort} onClick={clickSort} numeric>Saldo</SortTh>
        </tr>
      </thead>
      <tbody>
        {rows.map(row => (
          <tr key={row.id} className={"has-detail" + (selected===row.id?" is-sel":"")} onClick={()=> onSelect(row)}>
            <td className="official-cell strong">{displayOfficial(row.arbitro)}</td>
            <td className="official-cell">{displayOfficials(row.auxiliares)}</td>
            <td className="official-cell">{displayOfficial(row.var)}</td>
            <td className="num">{row.jogos}</td>
            <td className="ea-match-marker">{row.primeiro?.data || "—"} <span>·</span> {row.primeiro?.placar || "—"}</td>
            <td className="ea-match-marker">{row.ultimo?.data || "—"} <span>·</span> {row.ultimo?.placar || "—"}</td>
            <td className="num c-v">{row.v}</td>
            <td className="num c-e">{row.e}</td>
            <td className="num c-d">{row.d}</td>
            <td className={"num " + (Number(row.saldo ?? row.gp-row.gc)>0?"c-v":(Number(row.saldo ?? row.gp-row.gc)<0?"c-d":""))}>{fmtSaldo(row.saldo ?? row.gp-row.gc)}</td>
          </tr>
        ))}
      </tbody>
    </>
  );
}

function sortValueArbitragem(row, key) {
  if (key === "primeiro" || key === "ultimo") return dateSortEA(row[key]?.data);
  if (key === "auxiliares") return displayOfficials(row.auxiliares);
  if (key === "saldo") return Number(row.saldo ?? row.gp - row.gc);
  const value = row[key];
  return typeof value === "number" ? value : String(value || "");
}

function dateSortEA(data) {
  const parts = String(data || "").split("/");
  if (parts.length !== 3) return 0;
  return Number(`${parts[2]}${parts[1]}${parts[0]}`) || 0;
}

function fallbackGameFromMarker(marker) {
  return {
    data: marker?.data || "—",
    local: "—",
    competicao: "—",
    adv: extractAdv(marker?.placar || ""),
    res: scoreRes(marker?.placar || ""),
    placar: marker?.placar || "—",
    arbitro: "—",
    auxiliares: [],
    var: "—",
  };
}

function displayOfficial(value) {
  const txt = String(value || "").trim();
  return txt && txt !== "—" ? txt : "—";
}

function displayOfficials(values) {
  if (!Array.isArray(values)) return displayOfficial(values);
  const names = values.map(displayOfficial).filter(v => v !== "—");
  return names.length ? names.join(", ") : "—";
}

function fmtSaldo(value) {
  const n = Number(value || 0);
  return `${n > 0 ? "+" : ""}${n}`;
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

function PaginacaoLinhas({ page, totalPages, pageSize, setPage, total }) {
  const ini = total ? (page - 1) * pageSize + 1 : 0;
  const fim = Math.min(page * pageSize, total);
  return (
    <div className="ea-paginacao">
      <div className="ea-pag-left">
        <span className="ea-pag-info">linhas {ini}-{fim} de {total}</span>
        <span className="ea-pag-info">{pageSize} por página</span>
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
