// Acervo Vasco — detalhe de uma partida

const PlayerOpenCtx = React.createContext(null);

function Plink({ name, children, style }) {
  const open = React.useContext(PlayerOpenCtx);
  if (!open || !name) return <span style={style}>{children || name}</span>;
  return (
    <button className="plink" onClick={(e)=>{ e.stopPropagation(); open(name); }} style={style}>
      {children || name}
    </button>
  );
}

// converte período+minuto em "minuto absoluto" pra ordenação
function absMin(min, periodo) {
  if (min == null || min === "" || !periodo) return 9999;
  if (periodo === "1T") return Math.min(min, 45);
  // 2T: minuto 1 = 46, minuto 45 = 90
  return 45 + min;
}
function fmtMin(min, periodo) {
  if (min == null || min === "" || !periodo) return "s/min";
  return `${min}'/${periodo}`;
}

function Partida({ partida, onBack, onOpenPlayer }) {
  const [tab, setTab] = useState("resumo");
  return (
    <PlayerOpenCtx.Provider value={onOpenPlayer}>
    <div className="main">
      <button className="detail-back" onClick={onBack}>
        <span className="arrow">‹</span> Voltar para temporada 2026
      </button>
      <DetailHero p={partida} />
      <nav className="detail-tabs">
        {[
          ["resumo","Resumo"],
          ["escalacao","Escalação"],
          ["eventos","Eventos"],
          ["arbitragem","Arbitragem"],
          ["bilheteria","Bilheteria"],
        ].map(([k,l]) => (
          <button key={k} className={tab===k?"active":""} onClick={()=>setTab(k)}>{l}</button>
        ))}
      </nav>
      {tab==="resumo"     && <TabResumo p={partida} />}
      {tab==="escalacao"  && <TabEscalacao p={partida} />}
      {tab==="eventos"    && <TabEventos p={partida} />}
      {tab==="arbitragem" && <TabArbitragem p={partida} />}
      {tab==="bilheteria" && <TabBilheteria p={partida} />}
    </div>
    </PlayerOpenCtx.Provider>
  );
}

// ============ Hero do detalhe ============
function DetailHero({ p }) {
  const vasco_casa = p.local === "casa";
  return (
    <section className="detail-hero">
      <div className="detail-meta">
        <span><strong>{p.competicao}</strong></span>
        <span className="dot">·</span>
        <span>{p.fase}</span>
        <span className="dot">·</span>
        <span>{p.data} <strong>{p.horario}</strong></span>
        <span className="dot">·</span>
        <span><strong>{p.estadio}</strong> · {vasco_casa ? "Casa" : "Visitante"}</span>
        <span className="dot">·</span>
        <span>Técnico: <strong>{p.tecnico}</strong></span>
        <span className="dot">·</span>
        <span>Capitão: <strong>{p.capitao}</strong></span>
      </div>
      <div className="detail-scoreline">
        <div className="team-block">
          <div className="team-header">
            <Monogram club="Vasco" vasco size="lg" />
            <div className="name">Vasco</div>
          </div>
          {p.gols_vasco.length > 0 && (
            <div className="scorers">
              {p.gols_vasco.map((g, i) => (
                <div key={i}>
                  <span className="who"><Plink name={g.nome}/>{g.penalti ? " (pen)" : ""}</span>
                  <span className="min">{fmtMin(g.minuto, g.periodo)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="detail-score">
          {p.placar.vasco}<span className="x">×</span>{p.placar.adversario}
        </div>
        <div className="team-block away">
          <div className="team-header">
            <div className="name" style={{textAlign:"right"}}>{p.adversario}</div>
            <Monogram club={p.adversario} size="lg" />
          </div>
          {p.gols_adversario.length > 0 && (
            <div className="scorers">
              {p.gols_adversario.map((g, i) => (
                <div key={i}>
                  <span className="min">{fmtMin(g.minuto, g.periodo)}</span>
                  <span className="who">{g.nome}{g.contra ? " (contra)" : ""}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      {p.agregado && (
        <div className="detail-aggregate">
          Agregado <strong>{p.agregado.vasco} × {p.agregado.adversario}</strong> · <strong>{p.agregado.classificado}</strong> classificado para as oitavas
        </div>
      )}
    </section>
  );
}

// ============ Resumo ============
function TabResumo({ p }) {
  const v = p.placar.vasco, a = p.placar.adversario;
  const result = v > a ? "Vitória" : v < a ? "Derrota" : "Empate";
  return (
    <div className="resumo-grid">
      <div>
        <p className="resumo-text">{p.observacao}</p>
      </div>
      <div className="resumo-side">
        <div className="kv"><span className="k">Resultado</span><span className="v">{result}</span></div>
        <div className="kv"><span className="k">Placar</span><span className="v">{v} × {a}</span></div>
        {p.agregado && (
          <div className="kv"><span className="k">Agregado</span><span className="v">{p.agregado.vasco} × {p.agregado.adversario}</span></div>
        )}
        <div className="kv"><span className="k">Estádio</span><span className="v">{p.estadio}</span></div>
        <div className="kv"><span className="k">Horário</span><span className="v">{p.horario}</span></div>
        <div className="kv"><span className="k">Competição</span><span className="v">{p.competicao}</span></div>
        <div className="kv"><span className="k">Técnico</span><span className="v">{p.tecnico}</span></div>
        <div className="kv"><span className="k">Capitão</span><span className="v"><Plink name={p.capitao}/></span></div>
        <div className="kv"><span className="k">Formação</span><span className="v">{p.escalacao.formacao}</span></div>
        <div className="kv"><span className="k">Cartões amarelos</span><span className="v">{p.cartoes_amarelos_vasco.length}</span></div>
        <div className="kv"><span className="k">Cartão vermelho</span><span className="v">{p.cartoes_vermelhos_vasco.length}</span></div>
        <div className="kv"><span className="k">Substituições</span><span className="v">{p.escalacao.substituicoes.length}</span></div>
      </div>
    </div>
  );
}

// ============ Escalação ============
// Posições no campo para 4-2-2-2 (Vasco atacando pra cima)
// Eixo Y de baixo (0) pra cima (100); X de esquerda (0) à direita (100)
const PITCH_POS_442 = {
  Goleiro:           [[50, 90]],
  "Lateral-Direito": [[85, 72]],
  Zagueiro:          [[37, 76], [63, 76]],
  "Lateral-Esquerdo":[[15, 72]],
  Volante:           [[35, 54], [65, 54]],
  "Meio-Campista":   [[28, 33], [72, 33]],
  Atacante:          [[38, 14], [62, 14]],
};

function playerInitials(name) {
  const parts = name.split(/\s+/).filter(Boolean);
  if (parts.length === 1) return parts[0].slice(0,2).toUpperCase();
  return (parts[0][0] + parts[parts.length-1][0]).toUpperCase();
}

function TabEscalacao({ p }) {
  const [mode, setMode] = useState("campo"); // campo | lista
  const tit = p.escalacao.titulares_por_posicao;
  return (
    <div>
      <div className="lineup-toggle">
        <button className={mode==="campo"?"active":""} onClick={()=>setMode("campo")}>Campo</button>
        <button className={mode==="lista"?"active":""} onClick={()=>setMode("lista")}>Por posição</button>
      </div>
      {mode==="campo" ? <LineupPitch p={p} /> : <LineupList p={p} />}
      <BenchAndOuts p={p} />
    </div>
  );
}

function LineupPitch({ p }) {
  const tit = p.escalacao.titulares_por_posicao;
  const placed = [];
  Object.entries(tit).forEach(([pos, players]) => {
    const coords = PITCH_POS_442[pos] || [];
    players.forEach((name, i) => {
      const c = coords[i] || [50, 50];
      placed.push({ name, pos, x: c[0], y: c[1] /* GK em baixo, ataque em cima */ });
    });
  });
  const isCaptain = (name) => name === p.capitao;
  const isGK = (pos) => pos === "Goleiro";
  return (
    <div className="lineup-grid">
      <div className="pitch">
        <div className="pitch-stripes"/>
        <div className="pitch-center"/>
        <div className="pitch-top-box"/>
        {/* área inferior */}
        <div style={{position:"absolute", left:"18%", right:"18%", bottom:0, height:"18%", border:"1px solid rgba(255,255,255,0.45)", borderBottom:0}}/>
        {placed.map((pl, i) => (
          <div key={i} className={`player-dot ${isGK(pl.pos)?"gk":""} ${isCaptain(pl.name)?"cap":""}`} style={{ left: `${pl.x}%`, top: `${pl.y}%` }}>
            <div className="num">{playerInitials(pl.name)}</div>
            <div className="nm"><Plink name={pl.name}/></div>
          </div>
        ))}
      </div>
      <div className="lineup-side">
        <h4>Reservas no banco · {p.escalacao.reservas.length}</h4>
        <ul>{p.escalacao.reservas.map(n => <li key={n}><Plink name={n}/></li>)}</ul>
        <h4>Substituições</h4>
        <ul style={{gridTemplateColumns:"1fr", display:"block", fontSize:13.5}}>
          {p.escalacao.substituicoes.map((s, i) => (
            <li key={i} style={{padding:"5px 0", display:"flex", justifyContent:"space-between", borderBottom:"1px dotted var(--rule)"}}>
              <span><span style={{color:"var(--r-d)"}}>−</span> <Plink name={s.sai}/> <span style={{color:"var(--ink-mute)", fontFamily:"var(--ff-mono)", fontSize:11}}>›</span> <span style={{color:"var(--r-v)"}}>+</span> <Plink name={s.entra}/></span>
              <span style={{fontFamily:"var(--ff-mono)", fontSize:11, color:"var(--ink-mute)"}}>{s.minuto}'/{s.periodo}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function LineupList({ p }) {
  const tit = p.escalacao.titulares_por_posicao;
  const isCaptain = (name) => name === p.capitao;
  const POS_ORDER = ["Goleiro","Lateral-Direito","Zagueiro","Lateral-Esquerdo","Volante","Meio-Campista","Atacante"];
  return (
    <div className="lineup-list-only">
      {POS_ORDER.map(pos => (
        <div className="pos-group" key={pos}>
          <h5>{pos}</h5>
          {(tit[pos]||[]).map(n => (
            <div className="pl" key={n}>
              <span><Plink name={n}/>{isCaptain(n) && <span style={{color:"var(--red)", marginLeft:6, fontFamily:"var(--ff-display)", fontSize:11}}>(C)</span>}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function BenchAndOuts({ p }) {
  return (
    <div style={{marginTop:32, display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:32, borderTop:"1px solid var(--rule)", paddingTop:20}}>
      <div>
        <h4 style={{fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)", margin:"0 0 8px"}}>Não relacionados · {p.escalacao.nao_relacionados.length}</h4>
        <ul style={{listStyle:"none", padding:0, margin:0, fontFamily:"var(--ff-serif)", fontSize:13.5, columns:2, columnGap:24}}>
          {p.escalacao.nao_relacionados.map(n => <li key={n} style={{padding:"3px 0", breakInside:"avoid"}}><Plink name={n}/></li>)}
        </ul>
      </div>
      <div>
        <h4 style={{fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)", margin:"0 0 8px"}}>Lesionados · {p.escalacao.lesionados.length}</h4>
        <ul style={{listStyle:"none", padding:0, margin:0, fontFamily:"var(--ff-serif)", fontSize:13.5}}>
          {p.escalacao.lesionados.map(n => <li key={n} style={{padding:"3px 0", color:"var(--r-d)"}}><Plink name={n}/></li>)}
        </ul>
      </div>
      <div>
        <h4 style={{fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)", margin:"0 0 8px"}}>Suspensos · {p.escalacao.suspensos.length}</h4>
        <ul style={{listStyle:"none", padding:0, margin:0, fontFamily:"var(--ff-serif)", fontSize:13.5, color:"var(--ink-mute)"}}>
          {p.escalacao.suspensos.length===0 ? <li style={{fontStyle:"italic"}}>nenhum</li> : p.escalacao.suspensos.map(n => <li key={n} style={{padding:"3px 0"}}><Plink name={n}/></li>)}
        </ul>
      </div>
    </div>
  );
}

// ============ Eventos ============
function TabEventos({ p }) {
  // monta lista de eventos lado-a-lado
  const events = [];
  p.gols_vasco.forEach(g => events.push({
    side: "vasco", kind: g.penalti ? "pen" : "goal",
    name: g.nome, label: g.penalti ? "Gol (pênalti)" : "Gol",
    minuto: g.minuto, periodo: g.periodo, abs: absMin(g.minuto, g.periodo),
  }));
  p.gols_adversario.forEach(g => events.push({
    side: "adv", kind: g.contra ? "og" : "goal",
    name: g.nome, label: g.contra ? "Gol contra · Saldivia" : "Gol",
    minuto: g.minuto, periodo: g.periodo, abs: absMin(g.minuto, g.periodo),
  }));
  p.cartoes_amarelos_vasco.forEach(n => events.push({
    side: "vasco", kind: "yellow", name: n, label: "Amarelo",
    minuto: null, periodo: null, abs: 9999, // sem minuto conhecido → ao final
  }));
  p.cartoes_vermelhos_vasco.forEach(c => events.push({
    side: "vasco", kind: "red", name: c.nome, label: `Vermelho · ${c.motivo}`,
    minuto: c.minuto, periodo: c.periodo, abs: absMin(c.minuto, c.periodo),
  }));
  p.escalacao.substituicoes.forEach(s => events.push({
    side: "vasco", kind: "sub", name: `${s.entra}`, label: `entra por ${s.sai}`,
    minuto: s.minuto, periodo: s.periodo, abs: absMin(s.minuto, s.periodo),
  }));
  events.sort((a,b)=>a.abs-b.abs);

  // separa por período pra inserir marker do intervalo
  const firstHalf = events.filter(e => (e.periodo==="1T") || (e.abs<=45 && e.minuto!=null));
  const secondHalf = events.filter(e => e.periodo==="2T");
  const unknown = events.filter(e => e.minuto==null);

  return (
    <div className="timeline">
      <div className="timeline-side left">
        <EventRow label={<span style={{fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)"}}>Vasco</span>} kind="header" />
        {firstHalf.map((e, i) => e.side==="vasco" ? <EventRow key={"f"+i} {...e} /> : <EventRow key={"fe"+i} empty />)}
        <EventRow kind="halfTime" />
        {secondHalf.map((e, i) => e.side==="vasco" ? <EventRow key={"s"+i} {...e} /> : <EventRow key={"se"+i} empty />)}
        {unknown.length > 0 && (
          <>
            <EventRow kind="indet" />
            {unknown.map((e, i) => e.side==="vasco" ? <EventRow key={"u"+i} {...e} /> : <EventRow key={"ue"+i} empty />)}
          </>
        )}
      </div>
      <div className="timeline-mid">
        <div className="timeline-min" style={{fontSize:9, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)"}}>Min.</div>
        {firstHalf.map((e, i) => (
          <div key={"m"+i} className="timeline-min">{e.minuto}'</div>
        ))}
        <div className="timeline-min half">Intervalo</div>
        {secondHalf.map((e, i) => (
          <div key={"sm"+i} className="timeline-min">{e.minuto}'</div>
        ))}
        {unknown.length > 0 && (
          <>
            <div className="timeline-min half">—</div>
            {unknown.map((_, i) => <div key={"um"+i} className="timeline-min">?</div>)}
          </>
        )}
      </div>
      <div className="timeline-side right">
        <EventRow label={<span style={{fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)"}}>{p.adversario}</span>} kind="header" />
        {firstHalf.map((e, i) => e.side==="adv" ? <EventRow key={"af"+i} {...e} /> : <EventRow key={"afe"+i} empty />)}
        <EventRow kind="halfTime" />
        {secondHalf.map((e, i) => e.side==="adv" ? <EventRow key={"as"+i} {...e} /> : <EventRow key={"ase"+i} empty />)}
        {unknown.length > 0 && (
          <>
            <EventRow kind="indet" />
            {unknown.map((e, i) => e.side==="adv" ? <EventRow key={"au"+i} {...e} /> : <EventRow key={"aue"+i} empty />)}
          </>
        )}
      </div>
    </div>
  );
}

function EventRow({ kind, name, label, minuto, periodo, empty }) {
  if (empty) return <div className="evt empty" />;
  if (kind === "halfTime") return <div className="evt" style={{minHeight:35, background:"var(--paper-deep)", fontFamily:"var(--ff-sans)", fontSize:9, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink)", fontWeight:600, padding:"8px 18px"}}>Intervalo</div>;
  if (kind === "indet") return <div className="evt" style={{minHeight:35, background:"var(--paper-deep)", fontFamily:"var(--ff-sans)", fontSize:9, letterSpacing:"0.22em", textTransform:"uppercase", color:"var(--ink-mute)", padding:"8px 18px"}}>Sem minuto registrado</div>;
  if (kind === "header") return <div className="evt" style={{minHeight:30, background:"var(--paper-deep)", padding:"6px 18px"}}>{label}</div>;
  const iconChar = kind==="goal" ? "⚽" : kind==="pen" ? "P" : kind==="og" ? "OG" : kind==="sub" ? "⇄" : "";
  return (
    <div className="evt">
      <span className={"icon " + kind}>{iconChar}</span>
      <span className="label">
        <strong style={{fontFamily:"var(--ff-serif)", fontWeight:700}}><Plink name={name}/></strong>
        <small>{label}</small>
      </span>
    </div>
  );
}

// ============ Arbitragem ============
function TabArbitragem({ p }) {
  return (
    <div className="arb-list">
      <div className="arb-card">
        <h4>Árbitro principal</h4>
        <div className="nm">{p.arbitragem.arbitro}</div>
        <div style={{fontFamily:"var(--ff-sans)", fontSize:10.5, color:"var(--ink-mute)", letterSpacing:"0.08em", marginTop:6}}>
          Estreia no nosso banco · cadastrar antes de importar
        </div>
      </div>
      <div className="arb-card">
        <h4>VAR</h4>
        <div className="nm">{p.arbitragem.var}</div>
      </div>
      <div className="arb-card" style={{gridColumn:"1 / -1"}}>
        <h4>Auxiliares</h4>
        <ul>
          {p.arbitragem.auxiliares.map(n => <li key={n}>{n}</li>)}
        </ul>
      </div>
    </div>
  );
}

// ============ Bilheteria ============
function TabBilheteria({ p }) {
  const publicoPagante = Number(p.publico_pagante || 0);
  const publicoPresente = Number(p.publico_presente || 0);
  const renda = Number(p.renda || 0);
  const naoPagantes = Math.max(0, publicoPresente - publicoPagante);
  const mediaTicket = publicoPagante ? renda / publicoPagante : 0;
  return (
    <div>
      <div className="kpi-grid">
        <div>
          <div className="kpi-label">Público pagante</div>
          <div className="kpi-value">{fmtN(publicoPagante)}</div>
          <div className="kpi-sub">torcedores com ingresso</div>
        </div>
        <div>
          <div className="kpi-label">Público presente</div>
          <div className="kpi-value">{fmtN(publicoPresente)}</div>
          <div className="kpi-sub">+{fmtN(naoPagantes)} não-pagantes (sócios, cortesias)</div>
        </div>
        <div>
          <div className="kpi-label">Renda</div>
          <div className="kpi-value" style={{fontSize:32}}>{fmtBRL(renda)}</div>
          <div className="kpi-sub">ticket médio {fmtBRL(mediaTicket)}</div>
        </div>
      </div>
      <div style={{marginTop:32, display:"grid", gridTemplateColumns:"2fr 1fr", gap:36}}>
        <div>
          <h4 style={{fontFamily:"var(--ff-display)", fontSize:22, letterSpacing:"0.04em", margin:"0 0 12px"}}>Ocupação do estádio</h4>
          <div style={{background:"var(--paper-card)", border:"1px solid var(--rule)", padding:20}}>
            <div style={{display:"flex", justifyContent:"space-between", fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.18em", textTransform:"uppercase", color:"var(--ink-mute)", marginBottom:10}}>
              <span>São Januário</span>
              <span>capacidade ≈ 21.880</span>
            </div>
            <div style={{height:24, background:"var(--paper-deep)", position:"relative", border:"1px solid var(--rule)"}}>
              <div style={{height:"100%", width:`${(publicoPagante/21880)*100}%`, background:"var(--ink)"}}/>
              <div style={{height:"100%", width:`${((publicoPresente-publicoPagante)/21880)*100}%`, background:"var(--red)", position:"absolute", left:`${(publicoPagante/21880)*100}%`, top:0, opacity:0.85}}/>
            </div>
            <div style={{display:"flex", gap:18, marginTop:12, fontFamily:"var(--ff-sans)", fontSize:11}}>
              <span style={{display:"flex", alignItems:"center", gap:6}}><span style={{width:12,height:10,background:"var(--ink)"}}/>Pagantes</span>
              <span style={{display:"flex", alignItems:"center", gap:6}}><span style={{width:12,height:10,background:"var(--red)"}}/>Não-pagantes</span>
              <span style={{color:"var(--ink-mute)", marginLeft:"auto"}}>{((publicoPresente/21880)*100).toFixed(1)}% de ocupação</span>
            </div>
          </div>
        </div>
        <div>
          <h4 style={{fontFamily:"var(--ff-display)", fontSize:22, letterSpacing:"0.04em", margin:"0 0 12px"}}>Notas</h4>
          <p style={{fontFamily:"var(--ff-serif)", fontSize:14, lineHeight:1.5, color:"var(--ink-soft)", fontStyle:"italic"}}>
            Boletim financeiro confirmado por imagem da súmula CBF enviada pelo usuário. Renda bruta sem deduções de borderô.
          </p>
        </div>
      </div>
    </div>
  );
}

window.Partida = Partida;
