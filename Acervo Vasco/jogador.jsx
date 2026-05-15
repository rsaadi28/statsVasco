// Acervo Vasco — detalhe de um jogador

function Jogador({ nome, onBack, onOpenMatch }) {
  const dados = window.JOGADORES[nome];
  if (!dados) {
    return (
      <div className="main">
        <button className="detail-back" onClick={onBack}><span className="arrow">‹</span> Voltar</button>
        <div style={{padding:60, textAlign:"center", fontFamily:"var(--ff-serif)", fontStyle:"italic", color:"var(--ink-mute)"}}>
          Jogador <strong style={{color:"var(--ink)"}}>{nome}</strong> ainda não foi importado para o acervo web.
        </div>
      </div>
    );
  }
  // aba "Geral" agrega todas as passagens; senão, mostra uma passagem específica
  const [aba, setAba] = useState("geral");
  const passagemAtiva = aba === "geral" ? null : dados.passagens.find(p => p.id === aba);
  const statsAgregadas = aba === "geral"
    ? agregaPassagens(dados.passagens)
    : passagemAtiva.stats;

  return (
    <div className="main">
      <button className="detail-back" onClick={onBack}><span className="arrow">‹</span> Voltar</button>
      <PlayerHero dados={dados} />
      <nav className="detail-tabs">
        <button className={aba==="geral"?"active":""} onClick={()=>setAba("geral")}>Geral</button>
        {dados.passagens.map(p => (
          <button key={p.id} className={aba===p.id?"active":""} onClick={()=>setAba(p.id)}>
            Passagem {p.idx} · {p.periodo}
          </button>
        ))}
      </nav>
      <PlayerBody stats={statsAgregadas} passagem={passagemAtiva || dados.passagens[0]} onOpenMatch={onOpenMatch} aba={aba} />
    </div>
  );
}

function agregaPassagens(passagens) {
  const agg = {
    jogos_participacao: 0, minutos: 0, media_minutos: 0,
    jogos_titular: 0, jogos_reserva: 0, nao_entrou: 0,
    nao_relacionado: 0, lesionado: 0, suspenso: 0, selecao: 0,
    gols: 0, jogos_capitao: 0, partidas_marcou: 0,
    gols_titular: 0, gols_banco: 0,
    media_gols: 0, amarelos: 0, vermelhos: 0,
    amarelos_acumulados: 0, suspensao_pendente: false,
    media_min_entre_gols: null,
    ved: { v: 0, e: 0, d: 0 },
  };
  passagens.forEach(p => {
    const s = p.stats;
    for (const k of Object.keys(agg)) {
      if (k === "ved") {
        agg.ved.v += s.ved.v; agg.ved.e += s.ved.e; agg.ved.d += s.ved.d;
      } else if (k === "media_minutos" || k === "media_gols" || k === "media_min_entre_gols" || k === "suspensao_pendente") {
        // calculado depois
      } else if (typeof s[k] === "number") {
        agg[k] += s[k];
      }
    }
  });
  agg.media_minutos = agg.jogos_participacao ? +(agg.minutos / agg.jogos_participacao).toFixed(2) : 0;
  agg.media_gols = agg.jogos_participacao ? +(agg.gols / agg.jogos_participacao).toFixed(2) : 0;
  agg.media_min_entre_gols = agg.gols > 0 ? Math.round(agg.minutos / agg.gols) : null;
  // pega o último amarelo_acumulado e suspensão pendente (sempre da passagem mais recente)
  const ult = passagens[passagens.length - 1].stats;
  agg.amarelos_acumulados = ult.amarelos_acumulados;
  agg.suspensao_pendente = ult.suspensao_pendente;
  return agg;
}

// ============ Hero do jogador ============
function PlayerHero({ dados }) {
  const idade = calcIdade(dados.nascimento);
  return (
    <section className="player-hero">
      <div className="player-portrait">
        <PlayerAvatar nome={dados.nome} numero={dados.numero} size="xl" />
      </div>
      <div className="player-hero-info">
        <div className="hero-eyebrow">Acervo · Jogador</div>
        <h1 className="player-name">
          {dados.nome}
          {dados.capitao_atual && <span className="cap-badge" title="Capitão atual">C</span>}
        </h1>
        <div className="player-sub">
          {dados.nome_completo && dados.nome_completo !== dados.nome && (
            <em>{dados.nome_completo}</em>
          )}
        </div>
        <div className="player-meta-grid">
          <div className="pm"><span className="k">Posição</span><span className="v">{dados.posicao}</span></div>
          <div className="pm"><span className="k">Camisa</span><span className="v">{dados.numero != null ? `#${String(dados.numero).padStart(2,"0")}` : "—"}</span></div>
          <div className="pm"><span className="k">Nasc.</span><span className="v">{dados.nascimento}{idade?` · ${idade}a`:""}</span></div>
          <div className="pm"><span className="k">Naturalidade</span><span className="v">{dados.naturalidade}</span></div>
          {dados.altura_cm && <div className="pm"><span className="k">Altura</span><span className="v">{(dados.altura_cm/100).toFixed(2)} m</span></div>}
          {dados.pe && dados.pe !== "—" && <div className="pm"><span className="k">Perna</span><span className="v">{dados.pe}</span></div>}
          <div className="pm"><span className="k">Passagens</span><span className="v">{dados.passagens.length}</span></div>
          <div className="pm"><span className="k">Contratado de</span><span className="v">{dados.contratado_de}</span></div>
        </div>
      </div>
    </section>
  );
}

function calcIdade(nasc) {
  if (!nasc || nasc === "—") return null;
  const [d,m,y] = nasc.split("/").map(Number);
  if (!d || !m || !y) return null;
  const hoje = new Date(2026, 4, 15);
  let a = hoje.getFullYear() - y;
  if (hoje.getMonth()+1 < m || (hoje.getMonth()+1===m && hoje.getDate()<d)) a--;
  return a;
}

// Avatar do jogador — iniciais + número, estilo monograma editorial
function PlayerAvatar({ nome, numero, size = "md" }) {
  const initials = nome.split(/\s+/).filter(Boolean).slice(0,2).map(w=>w[0]).join("").toUpperCase();
  const klass = size === "xl" ? "player-avatar xl" : size === "lg" ? "player-avatar lg" : "player-avatar";
  return (
    <div className={klass}>
      <div className="pa-init">{initials}</div>
      {numero != null && <div className="pa-num">#{String(numero).padStart(2,"0")}</div>}
    </div>
  );
}

// ============ Corpo: presença, produção, disciplina, V/E/D, partidas ============
function PlayerBody({ stats, passagem, onOpenMatch, aba }) {
  return (
    <div className="player-body">
      <PresencaPanel stats={stats} />
      <ProducaoPanel stats={stats} />
      <SidePanel>
        <DisciplinaPanel stats={stats} />
        <VEDPanel ved={stats.ved} />
      </SidePanel>
      <PartidasPanel passagem={passagem} aba={aba} onOpenMatch={onOpenMatch} />
      <MetricasTabela stats={stats} passagem={passagem} aba={aba} />
    </div>
  );
}

function SidePanel({ children }) {
  return <div className="player-sidegrid">{children}</div>;
}

// ----- Presença -----
function PresencaPanel({ stats }) {
  const total = stats.jogos_titular + stats.jogos_reserva + stats.nao_entrou + stats.nao_relacionado + stats.lesionado + stats.suspenso + stats.selecao;
  const segs = [
    { k:"titular",    label:"Titular",        n: stats.jogos_titular,    color:"var(--ink)" },
    { k:"reserva",    label:"Reserva",        n: stats.jogos_reserva,    color:"#6b3a1f" },
    { k:"ne",         label:"Não entrou",     n: stats.nao_entrou,       color:"#a89a7d" },
    { k:"nr",         label:"Não relacionado",n: stats.nao_relacionado,  color:"#d6c9a6" },
    { k:"les",        label:"Lesionado",      n: stats.lesionado,        color:"var(--r-d)" },
    { k:"sus",        label:"Suspenso",       n: stats.suspenso,         color:"var(--gold)" },
    { k:"sel",        label:"Seleção",        n: stats.selecao,          color:"var(--blue)" },
  ].filter(s => s.n > 0 || (s.k==="titular"||s.k==="reserva"));
  return (
    <section className="ppanel">
      <h3 className="ppanel-title">Presença</h3>
      <div className="ppanel-kpis">
        <KPI label="Jogos com participação" value={stats.jogos_participacao} />
        <KPI label="Minutos jogados" value={fmtN(stats.minutos)} unit="min" />
        <KPI label="Média de minutos" value={stats.media_minutos.toFixed(1)} unit="min/j" />
        <KPI label="Como capitão" value={stats.jogos_capitao} />
      </div>
      <div className="status-bar" aria-label="Distribuição de status por jogo">
        {segs.map(s => (
          <div key={s.k} className="status-seg" style={{ flex: s.n || 0, background: s.color }} title={`${s.label}: ${s.n}`}>
            {s.n >= Math.max(1, total*0.06) && <span className="seg-num">{s.n}</span>}
          </div>
        ))}
      </div>
      <div className="status-legend">
        {segs.map(s => (
          <span key={s.k} className="leg"><span className="dot" style={{background:s.color}}/>{s.label} <strong>{s.n}</strong></span>
        ))}
      </div>
    </section>
  );
}

// ----- Produção -----
function ProducaoPanel({ stats }) {
  return (
    <section className="ppanel">
      <h3 className="ppanel-title">Produção</h3>
      <div className="ppanel-kpis">
        <KPI label="Gols pelo Vasco" value={stats.gols} big />
        <KPI label="Partidas em que marcou" value={stats.partidas_marcou} />
        <KPI label="Média gols/jogo" value={stats.media_gols.toFixed(2)} />
        <KPI label="Min. entre gols" value={stats.media_min_entre_gols ?? "—"} unit={stats.media_min_entre_gols ? "min" : ""} />
      </div>
      <div className="split-bar">
        <div className="split-row">
          <span className="split-lbl">Como titular</span>
          <span className="split-bar-track">
            <span className="split-bar-fill" style={{ width: pct(stats.gols_titular, Math.max(1, stats.gols)) }}/>
          </span>
          <span className="split-val">{stats.gols_titular}</span>
        </div>
        <div className="split-row">
          <span className="split-lbl">Saindo do banco</span>
          <span className="split-bar-track">
            <span className="split-bar-fill alt" style={{ width: pct(stats.gols_banco, Math.max(1, stats.gols)) }}/>
          </span>
          <span className="split-val">{stats.gols_banco}</span>
        </div>
      </div>
    </section>
  );
}

function pct(n, total) { return `${(n/total)*100}%`; }

// ----- Disciplina -----
function DisciplinaPanel({ stats }) {
  return (
    <section className="ppanel">
      <h3 className="ppanel-title">Disciplina</h3>
      <div className="discipline-row">
        <div className="card-stat yellow">
          <div className="card-icon"/>
          <div className="card-info">
            <div className="card-val">{stats.amarelos}</div>
            <div className="card-lbl">amarelos</div>
          </div>
        </div>
        <div className="card-stat red">
          <div className="card-icon"/>
          <div className="card-info">
            <div className="card-val">{stats.vermelhos}</div>
            <div className="card-lbl">vermelhos</div>
          </div>
        </div>
      </div>
      <div className="acumulado">
        <div className="kv-line">
          <span>Suspensão pendente</span>
          <span className={"v " + (stats.suspensao_pendente?"pend":"")}>
            {stats.suspensao_pendente ? "Sim" : "Não"}
          </span>
        </div>
      </div>
    </section>
  );
}

// ----- V/E/D -----
function VEDPanel({ ved }) {
  const total = ved.v + ved.e + ved.d || 1;
  return (
    <section className="ppanel">
      <h3 className="ppanel-title">Participação V/E/D <small>quando esteve em campo</small></h3>
      <div className="ved-big">
        <div className="ved-num v"><span className="n">{ved.v}</span><span className="l">vitórias</span></div>
        <div className="ved-num e"><span className="n">{ved.e}</span><span className="l">empates</span></div>
        <div className="ved-num d"><span className="n">{ved.d}</span><span className="l">derrotas</span></div>
      </div>
      <div className="ved-bar">
        <div style={{ flex: ved.v, background: "var(--r-v)" }}/>
        <div style={{ flex: ved.e, background: "var(--r-e)" }}/>
        <div style={{ flex: ved.d, background: "var(--r-d)" }}/>
      </div>
      <div className="ved-meta">
        Aproveitamento individual <strong>{((ved.v*3 + ved.e) / (total*3) * 100).toFixed(1)}%</strong>
      </div>
    </section>
  );
}

// ----- Partidas (lista por linha) -----
function PartidasPanel({ passagem, onOpenMatch }) {
  const partidas = passagem.partidas || [];
  if (partidas.length === 0) {
    return (
      <section className="ppanel">
        <h3 className="ppanel-title">Partidas na passagem <small>{partidas.length} registros</small></h3>
        <div style={{padding:"30px 0", fontFamily:"var(--ff-serif)", fontStyle:"italic", color:"var(--ink-mute)", textAlign:"center"}}>
          Histórico partida-a-partida deste jogador ainda não foi migrado para o acervo web.
        </div>
      </section>
    );
  }
  return (
    <section className="ppanel">
      <h3 className="ppanel-title">Partidas na passagem <small>{partidas.length} registros</small></h3>
      <div className="table-wrap">
        <table className="tbl player-games">
          <thead>
            <tr>
              <th style={{width:90}}>Data</th>
              <th style={{width:28}}></th>
              <th>Adversário</th>
              <th style={{width:80}}>Placar</th>
              <th style={{width:90}}>Função</th>
              <th style={{width:70}}>Min.</th>
              <th style={{width:60}}>Gols</th>
              <th style={{width:80}}>Cartões</th>
            </tr>
          </thead>
          <tbody>
            {partidas.map((p,i) => (
              <tr key={i} onClick={()=>onOpenMatch && onOpenMatch({ data: p.data, adversario: p.adv })} className="has-detail">
                <td className="date">{p.data}</td>
                <td className="result-cell"><span className={"result-dot " + p.res}/></td>
                <td className="opponent">
                  <Monogram club={p.adv} />
                  {p.adv}
                </td>
                <td className="score">{p.placar.replace("x","×")}</td>
                <td className="tecnico">
                  {p.status ? <span style={{color:"var(--ink-faint)", fontStyle:"italic"}}>{p.status}</span>
                            : p.titular ? "titular" : "reserva"}
                </td>
                <td className="tecnico">{p.minutos || "—"}</td>
                <td className="tecnico" style={{textAlign:"center"}}>{p.gols || ""}</td>
                <td>
                  {p.amarelo && <span className="cardlet yellow"/>}
                  {p.vermelho && <span className="cardlet red"/>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

// ----- Tabela métrica/valor completa (paridade com o app antigo) -----
function MetricasTabela({ stats, passagem, aba }) {
  const linhas = [
    ["Data de estreia no Vasco", passagem.estreia],
    ["Data de saída",            passagem.saida],
    ["Passagens pelo Vasco",     aba==="geral" ? "todas" : `passagem ${passagem.idx}`],
    ["Jogos com participação",   stats.jogos_participacao],
    ["Minutos jogados",          fmtN(stats.minutos)],
    ["Média de minutos jogados", stats.media_minutos.toFixed(2)],
    ["Jogos como titular",       stats.jogos_titular],
    ["Jogos como reserva",       stats.jogos_reserva],
    ["Foi para o jogo e não entrou", stats.nao_entrou],
    ["Jogos como não relacionado", stats.nao_relacionado],
    ["Jogos como lesionado",     stats.lesionado],
    ["Jogos como suspenso",      stats.suspenso],
    ["Jogos servindo a seleção", stats.selecao],
    ["Gols pelo Vasco",          stats.gols],
    ["Jogos como capitão",       stats.jogos_capitao],
    ["Partidas em que marcou",   stats.partidas_marcou],
    ["Gols como titular",        stats.gols_titular],
    ["Gols saindo do banco",     stats.gols_banco],
    ["Média de gols por jogo",   stats.media_gols.toFixed(2)],
    ["Cartões amarelos",         stats.amarelos],
    ["Cartões vermelhos",        stats.vermelhos],
    ["Amarelos acumulados atuais", stats.amarelos_acumulados],
    ["Suspensão pendente",       stats.suspensao_pendente ? "Sim" : "Não"],
    ["Média de minutos entre gols", stats.media_min_entre_gols ?? "—"],
    ["Participação (V/E/D)",     `${stats.ved.v}/${stats.ved.e}/${stats.ved.d}`],
  ];
  return (
    <section className="ppanel collapse-tbl">
      <h3 className="ppanel-title">Métricas detalhadas <small>todas as 25 linhas do acervo</small></h3>
      <div className="metric-table">
        {linhas.map(([k,v]) => (
          <div key={k} className="metric-row">
            <span className="metric-k">{k}</span>
            <span className="metric-v">{v}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

// ============ helper KPI ============
function KPI({ label, value, unit, big }) {
  return (
    <div className={"kpi-cell" + (big ? " big" : "")}>
      <div className="kpi-cell-val">
        {value}
        {unit && <span className="kpi-cell-unit"> {unit}</span>}
      </div>
      <div className="kpi-cell-lbl">{label}</div>
    </div>
  );
}

window.Jogador = Jogador;
window.PlayerAvatar = PlayerAvatar;
