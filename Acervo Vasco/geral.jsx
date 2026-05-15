// Acervo Vasco — aba Geral: KPIs gerais + Artilheiros + Carrascos

function Geral({ onOpenPlayer }) {
  const t = window.GERAL_TOTAIS;
  const [buscaArt, setBuscaArt] = useState("");
  const [buscaCar, setBuscaCar] = useState("");

  const filteredArt = useMemo(() => filtraGoleadores(window.ARTILHEIROS_VASCO, buscaArt), [buscaArt]);
  const filteredCar = useMemo(() => filtraGoleadores(window.CARRASCOS, buscaCar), [buscaCar]);

  const maxArt = window.ARTILHEIROS_VASCO[0]?.gols || 1;
  const maxCar = window.CARRASCOS[0]?.gols || 1;

  return (
    <div className="main">
      <section className="geral-hero">
        <div className="hero-eyebrow">Acervo · Geral</div>
        <h1 className="geral-title">Histórico Total</h1>
        <p className="geral-sub">Tudo o que está registrado no acervo desde 2000 — agregados, artilheiros e carrascos.</p>
      </section>

      <section className="geral-kpis">
        <KpiCell lbl="Jogos"       v={fmtN(t.jogos)} />
        <KpiCell lbl="Vitórias"    v={fmtN(t.vitorias)} cor="v" />
        <KpiCell lbl="Empates"     v={fmtN(t.empates)}  cor="e" />
        <KpiCell lbl="Derrotas"    v={fmtN(t.derrotas)} cor="d" />
        <KpiCell lbl="Gols pró"    v={fmtN(t.gp)} />
        <KpiCell lbl="Gols contra" v={fmtN(t.gc)} />
        <KpiCell lbl="Saldo"       v={(t.saldo>0?"+":"") + t.saldo} cor="red" />
        <KpiCell lbl="Aproveitamento" v={t.aprov.toFixed(1) + "%"} cor="red" />
        <KpiCell lbl="Média gols pró"    v={t.media_gp.toFixed(2)} />
        <KpiCell lbl="Média gols contra" v={t.media_gc.toFixed(2)} />
        <KpiCell lbl="Maior sequência invicta"  v={t.maior_invicta} cor="v" />
        <KpiCell lbl="Maior sequência derrotas" v={t.maior_derrotas} cor="d" />
      </section>

      <div className="geral-grid">
        <GoleadoresPanel
          title="Artilheiros do Vasco"
          subtitle={`${window.ARTILHEIROS_VASCO.length} jogadores marcaram pelo Vasco`}
          lista={filteredArt}
          totalLista={window.ARTILHEIROS_VASCO}
          busca={buscaArt}
          setBusca={setBuscaArt}
          max={maxArt}
          accent="red"
          onClickName={onOpenPlayer}
        />
        <GoleadoresPanel
          title="Carrascos (gols contra o Vasco)"
          subtitle={`${window.CARRASCOS.length} jogadores adversários marcaram`}
          lista={filteredCar}
          totalLista={window.CARRASCOS}
          busca={buscaCar}
          setBusca={setBuscaCar}
          max={maxCar}
          accent="ink"
        />
      </div>
    </div>
  );
}

function filtraGoleadores(arr, busca) {
  if (!busca.trim()) return arr;
  const s = busca.trim().toLowerCase();
  return arr.filter(p => p.nome.toLowerCase().includes(s));
}

function KpiCell({ lbl, v, cor }) {
  return (
    <div className={"geral-kpi" + (cor ? " cor-"+cor : "")}>
      <div className="lbl">{lbl}</div>
      <div className="val">{v}</div>
    </div>
  );
}

function GoleadoresPanel({ title, subtitle, lista, totalLista, busca, setBusca, max, accent, onClickName }) {
  return (
    <section className="geral-panel">
      <div className="geral-panel-head">
        <h3 className="ppanel-title">{title}<small>{subtitle}</small></h3>
        <div className="geral-search">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="7" cy="7" r="5"/><path d="M14 14L11 11"/></svg>
          <input placeholder="buscar…" value={busca} onChange={(e)=>setBusca(e.target.value)} />
          {busca && <button className="clear" onClick={()=>setBusca("")}>×</button>}
        </div>
      </div>
      <div className="goleadores-list">
        {lista.length === 0 ? (
          <div className="goleadores-empty">Nenhum jogador encontrado.</div>
        ) : lista.map((p,i) => (
          <div className="goleadores-row" key={p.nome}>
            <span className="pos">{String(totalLista.indexOf(p)+1).padStart(3,"0")}</span>
            <span className="name">
              {onClickName && !p.nome.includes("(contra)") && !p.nome.includes("Gol contra")
                ? <button className="plink" onClick={()=>onClickName(p.nome)}>{p.nome}</button>
                : p.nome}
            </span>
            <span className="goals">{p.gols}</span>
            <span className="bar"><i style={{width: `${(p.gols/max)*100}%`, background: accent==="red"?"var(--red)":"var(--ink)"}}/></span>
          </div>
        ))}
      </div>
    </section>
  );
}

window.Geral = Geral;
