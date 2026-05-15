// Acervo Vasco — aba Títulos

const CAT_LABEL = {
  continental: "Internacional",
  nacional: "Nacional",
  estadual: "Estadual",
};
const CAT_COLOR = {
  continental: "var(--red)",
  nacional: "var(--ink)",
  estadual: "var(--gold)",
};

function Titulos({ onOpenPlayer }) {
  const all = window.TITULOS;
  const [cat, setCat] = useState("todos");

  // Agrupa por campeonato
  const grupos = useMemo(() => {
    const m = {};
    all.forEach(t => {
      if (!m[t.campeonato]) m[t.campeonato] = { titulos:[], categoria: t.categoria };
      m[t.campeonato].titulos.push(t);
    });
    return Object.entries(m)
      .map(([nome, g]) => ({ nome, ...g, anos: g.titulos.map(t=>t.ano).sort((a,b)=>a-b) }))
      .sort((a,b) => {
        // ordem: continental, nacional, estadual; e dentro de cada, mais títulos primeiro
        const catOrder = { continental:0, nacional:1, estadual:2 };
        if (catOrder[a.categoria] !== catOrder[b.categoria]) return catOrder[a.categoria] - catOrder[b.categoria];
        return b.titulos.length - a.titulos.length;
      });
  }, [all]);

  const totalPorCat = useMemo(() => {
    const m = { continental:0, nacional:0, estadual:0 };
    all.forEach(t => m[t.categoria]++);
    return m;
  }, [all]);

  const visible = cat === "todos" ? grupos : grupos.filter(g => g.categoria === cat);
  const totalVisible = visible.reduce((acc, g) => acc + g.titulos.length, 0);

  return (
    <div className="main">
      <section className="tit-hero">
        <div className="hero-eyebrow">Acervo · Títulos</div>
        <div className="tit-hero-line">
          <div>
            <h1 className="tit-title">Títulos do Vasco</h1>
            <p className="tit-sub">Campanhas vitoriosas registradas no acervo desde 1998.</p>
          </div>
          <div className="tit-stats">
            <div className="tit-stat"><div className="val">{all.length}</div><div className="lbl">Títulos totais</div></div>
            <div className="tit-stat cont"><div className="val">{totalPorCat.continental}</div><div className="lbl">Internacionais</div></div>
            <div className="tit-stat nac"><div className="val">{totalPorCat.nacional}</div><div className="lbl">Nacionais</div></div>
            <div className="tit-stat est"><div className="val">{totalPorCat.estadual}</div><div className="lbl">Estaduais</div></div>
          </div>
        </div>
      </section>

      <div className="tit-filter">
        <button className={"chip"+(cat==="todos"?" active":"")} onClick={()=>setCat("todos")}>Todos <span className="count">{all.length}</span></button>
        <button className={"chip"+(cat==="continental"?" active":"")} onClick={()=>setCat("continental")}>Internacionais <span className="count">{totalPorCat.continental}</span></button>
        <button className={"chip"+(cat==="nacional"?" active":"")} onClick={()=>setCat("nacional")}>Nacionais <span className="count">{totalPorCat.nacional}</span></button>
        <button className={"chip"+(cat==="estadual"?" active":"")} onClick={()=>setCat("estadual")}>Estaduais <span className="count">{totalPorCat.estadual}</span></button>
      </div>

      <div className="tit-galeria">
        {visible.map(grp => (
          <TituloGrupo key={grp.nome} grupo={grp} onOpenPlayer={onOpenPlayer} />
        ))}
      </div>

      <section style={{marginTop:36}}>
        <h3 className="ea-section-title">Campanhas detalhadas <small>{totalVisible} títulos</small></h3>
        <p style={{fontFamily:"var(--ff-serif)", fontSize:14, fontStyle:"italic", color:"var(--ink-mute)", margin:"0 0 14px"}}>
          Números das campanhas campeãs: vitórias, empates, derrotas e artilheiro do Vasco em cada conquista.
        </p>
        <div className="table-wrap">
          <table className="tbl ea-tbl">
            <thead>
              <tr>
                <th style={{width:30}}></th>
                <th>Campeonato</th>
                <th style={{width:80}} className="num">Ano</th>
                <th style={{width:80}} className="num">Vitórias</th>
                <th style={{width:80}} className="num">Empates</th>
                <th style={{width:80}} className="num">Derrotas</th>
                <th>Artilheiro do Vasco</th>
              </tr>
            </thead>
            <tbody>
              {[...all]
                .filter(t => cat==="todos" || t.categoria===cat)
                .sort((a,b) => a.ano - b.ano)
                .map((t,i) => (
                <tr key={i}>
                  <td><span className="tit-dot" style={{background:CAT_COLOR[t.categoria]}}/></td>
                  <td style={{fontFamily:"var(--ff-serif)", fontSize:15, fontWeight:600}}>{t.campeonato}</td>
                  <td className="num"><strong>{t.ano}</strong></td>
                  <td className="num c-v">{t.v ?? <em style={{color:"var(--ink-faint)", fontFamily:"var(--ff-serif)"}}>sem registro</em>}</td>
                  <td className="num c-e">{t.e ?? <em style={{color:"var(--ink-faint)", fontFamily:"var(--ff-serif)"}}>—</em>}</td>
                  <td className="num c-d">{t.d ?? <em style={{color:"var(--ink-faint)", fontFamily:"var(--ff-serif)"}}>—</em>}</td>
                  <td style={{fontFamily:"var(--ff-serif)", fontSize:14}}>
                    {t.artilheiro
                      ? <>
                          <button className="plink" onClick={()=> onOpenPlayer && onOpenPlayer(t.artilheiro.nome)}>{t.artilheiro.nome}</button>
                          <span style={{fontFamily:"var(--ff-mono)", fontSize:11, color:"var(--ink-mute)", marginLeft:6}}>({t.artilheiro.gols})</span>
                        </>
                      : <em style={{color:"var(--ink-faint)"}}>sem registro</em>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function TituloGrupo({ grupo, onOpenPlayer }) {
  return (
    <section className={"tit-grupo cat-"+grupo.categoria}>
      <div className="tit-grupo-head">
        <div className="tit-grupo-cat">{CAT_LABEL[grupo.categoria]}</div>
        <div className="tit-grupo-count">{grupo.titulos.length}{grupo.titulos.length>1 ? <small>×</small> : ""}</div>
      </div>
      <h3 className="tit-grupo-nome">{grupo.nome}</h3>
      <div className="tit-grupo-anos">
        {grupo.titulos.sort((a,b)=>a.ano-b.ano).map(t => (
          <div key={t.ano} className="tit-card">
            <TrofeuSVG categoria={grupo.categoria} />
            <div className="tit-card-ano">{t.ano}</div>
            {t.v != null ? (
              <div className="tit-card-stats">
                <span className="c-v">{t.v}V</span> · <span className="c-e">{t.e}E</span> · <span className="c-d">{t.d}D</span>
              </div>
            ) : (
              <div className="tit-card-stats" style={{color:"var(--ink-faint)", fontStyle:"italic"}}>campanha não migrada</div>
            )}
            {t.artilheiro && (
              <div className="tit-card-art">
                Artilheiro · <button className="plink" onClick={()=> onOpenPlayer && onOpenPlayer(t.artilheiro.nome)}>{t.artilheiro.nome}</button>
                <span className="g"> ({t.artilheiro.gols})</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

function TrofeuSVG({ categoria }) {
  const cor = CAT_COLOR[categoria] || "var(--ink)";
  return (
    <svg className="trofeu" viewBox="0 0 80 100" aria-hidden="true">
      <defs>
        <linearGradient id="tg" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={cor} stopOpacity="1"/>
          <stop offset="100%" stopColor={cor} stopOpacity="0.6"/>
        </linearGradient>
      </defs>
      {/* base */}
      <rect x="22" y="86" width="36" height="8" fill="var(--ink)"/>
      <rect x="30" y="74" width="20" height="14" fill="var(--ink)"/>
      {/* taça */}
      <path d="M22 18 L58 18 L56 50 Q56 64 40 68 Q24 64 24 50 Z" fill="url(#tg)" stroke="var(--ink)" strokeWidth="1.5"/>
      {/* alças */}
      <path d="M22 22 Q10 22 12 38 Q14 50 24 48" fill="none" stroke="var(--ink)" strokeWidth="2"/>
      <path d="M58 22 Q70 22 68 38 Q66 50 56 48" fill="none" stroke="var(--ink)" strokeWidth="2"/>
      {/* topo */}
      <rect x="20" y="14" width="40" height="6" fill="var(--ink)"/>
      {/* estrela central */}
      <path d="M40 30 L43 38 L51 38 L44 43 L47 51 L40 46 L33 51 L36 43 L29 38 L37 38 Z" fill="var(--paper-card)" stroke="var(--ink)" strokeWidth="0.5"/>
    </svg>
  );
}

window.Titulos = Titulos;
