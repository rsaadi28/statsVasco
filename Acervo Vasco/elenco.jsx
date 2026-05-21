// Acervo Vasco — aba Elenco Atual

const POS_ORDER_ELENCO = [
  "Goleiro","Lateral-Direito","Zagueiro","Lateral-Esquerdo",
  "Volante","Meio-Campista","Atacante"
];
const POS_LABEL = {
  "Goleiro":"GOL","Lateral-Direito":"LD","Zagueiro":"ZAG","Lateral-Esquerdo":"LE",
  "Volante":"VOL","Meio-Campista":"MEI","Atacante":"ATA",
};
const POS_SHORT_GROUP = {
  "Goleiro":"GOL","Lateral-Direito":"DEF","Zagueiro":"DEF","Lateral-Esquerdo":"DEF",
  "Volante":"VOL","Meio-Campista":"MEI","Atacante":"ATA",
};

function ElencoAtual({ onOpenPlayer }) {
  const p = window.PARTIDA_PAYSANDU;
  const emprestados = window.EMPRESTADOS;
  const e = p.escalacao;

  // monta lista plana com condição
  const lista = useMemo(() => {
    const out = [];

    // 1) Titulares (na ordem das posições)
    POS_ORDER_ELENCO.forEach(pos => {
      (e.titulares_por_posicao[pos] || []).forEach(nome => {
        out.push({ pos, nome, cond: "titular", capitao: nome === p.capitao });
      });
    });

    // 2) Reservas — usa info do jogadores stubs para posição
    e.reservas.forEach(nome => {
      const dados = window.JOGADORES[nome];
      const pos = dados?.posicao || "—";
      out.push({ pos, nome, cond: "reserva" });
    });

    // 3) Não relacionados
    e.nao_relacionados.forEach(nome => {
      const dados = window.JOGADORES[nome];
      const pos = dados?.posicao || posicaoStub(nome);
      out.push({ pos, nome, cond: "nao-rel" });
    });

    // 4) Lesionados
    e.lesionados.forEach(nome => {
      const dados = window.JOGADORES[nome];
      const pos = dados?.posicao || posicaoStub(nome);
      out.push({ pos, nome, cond: "lesionado" });
    });

    // 5) Suspensos
    e.suspensos.forEach(nome => {
      out.push({ pos: window.JOGADORES[nome]?.posicao || "—", nome, cond: "suspenso" });
    });

    // 6) Servindo seleção (vazio neste jogo)
    (e.servindo_selecao || []).forEach(nome => {
      out.push({ pos: window.JOGADORES[nome]?.posicao || "—", nome, cond: "selecao" });
    });

    // 7) Emprestados
    emprestados.forEach(ep => {
      out.push({ pos: ep.posicao, nome: ep.nome, cond: "emprestado", clube: ep.clube, ate: ep.ate });
    });

    return out;
  }, [p, e, emprestados]);

  // contagens
  const counts = useMemo(() => {
    const c = { titular:0, reserva:0, "nao-rel":0, lesionado:0, suspenso:0, selecao:0, emprestado:0 };
    lista.forEach(r => c[r.cond]++);
    return c;
  }, [lista]);

  const [filtro, setFiltro] = useState("todas");
  const filtered = filtro === "todas" ? lista : lista.filter(r => r.cond === filtro);

  return (
    <div className="main">
      <ElencoHero p={p} counts={counts} />
      <div className="elenco-filtro">
        <button className={"chip"+(filtro==="todas"?" active":"")}    onClick={()=>setFiltro("todas")}>Todos <span className="count">{lista.length}</span></button>
        <button className={"chip"+(filtro==="titular"?" active":"")}  onClick={()=>setFiltro("titular")}>Titulares <span className="count">{counts.titular}</span></button>
        <button className={"chip"+(filtro==="reserva"?" active":"")}  onClick={()=>setFiltro("reserva")}>Reservas <span className="count">{counts.reserva}</span></button>
        <button className={"chip"+(filtro==="nao-rel"?" active":"")}  onClick={()=>setFiltro("nao-rel")}>Não relacionados <span className="count">{counts["nao-rel"]}</span></button>
        <button className={"chip"+(filtro==="lesionado"?" active":"")}onClick={()=>setFiltro("lesionado")}>Lesionados <span className="count">{counts.lesionado}</span></button>
        <button className={"chip"+(filtro==="suspenso"?" active":"")} onClick={()=>setFiltro("suspenso")}>Suspensos <span className="count">{counts.suspenso}</span></button>
        <button className={"chip"+(filtro==="selecao"?" active":"")}  onClick={()=>setFiltro("selecao")}>Seleção <span className="count">{counts.selecao}</span></button>
        <button className={"chip"+(filtro==="emprestado"?" active":"")}onClick={()=>setFiltro("emprestado")}>Emprestados <span className="count">{counts.emprestado}</span></button>
      </div>

      <div className="elenco-grid">
        <ElencoTabela rows={filtered} onOpenPlayer={onOpenPlayer} />
        <ElencoCampo p={p} />
      </div>
    </div>
  );
}

function ElencoHero({ p, counts }) {
  return (
    <section className="elenco-hero">
      <div className="hero-eyebrow">Acervo · Elenco Atual</div>
      <div className="elenco-hero-line">
        <h1 className="elenco-title">Elenco Atual</h1>
        <div className="elenco-hero-meta">
          <div className="elenco-snapshot">
            <span className="lbl">Snapshot pós-jogo</span>
            <span className="val">{p.data} · vs {p.adversario}</span>
            <span className="sub">{p.competicao} · {p.estadio}</span>
          </div>
          <div className="elenco-stats">
            <Stat lbl="Titulares" v={counts.titular} cor="ink"/>
            <Stat lbl="Reservas" v={counts.reserva} cor="gold"/>
            <Stat lbl="Não rel." v={counts["nao-rel"]} cor="mute"/>
            <Stat lbl="Lesionados" v={counts.lesionado} cor="red"/>
            <Stat lbl="Suspensos" v={counts.suspenso} cor="mute"/>
            <Stat lbl="Seleção" v={counts.selecao} cor="mute"/>
            <Stat lbl="Empréstimo" v={counts.emprestado} cor="blue"/>
          </div>
        </div>
      </div>
    </section>
  );
}

function Stat({ lbl, v, cor }) {
  return (
    <div className={"elenco-stat cor-"+cor}>
      <div className="val">{v}</div>
      <div className="lbl">{lbl}</div>
    </div>
  );
}

function ElencoTabela({ rows, onOpenPlayer }) {
  return (
    <div className="elenco-tabela-wrap">
      <table className="tbl elenco-tbl">
        <thead>
          <tr>
            <th style={{width:80}}>Posição</th>
            <th>Jogador</th>
            <th style={{width:140}}>Condição</th>
            <th style={{width:160}}>Observação</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r,i) => (
            <tr key={i} className={"elenco-row cond-"+r.cond} onClick={()=> onOpenPlayer && onOpenPlayer(r.nome)}>
              <td><span className="pos-chip">{POS_LABEL[r.pos] || r.pos}</span></td>
              <td className="opponent">
                <span style={{fontFamily:"var(--ff-serif)", fontSize:15, fontWeight:600}}>
                  {r.nome}
                </span>
                {r.capitao && <span className="cap-tag">C</span>}
              </td>
              <td>
                <span className={"cond-tag tag-"+r.cond}>{condLabel(r.cond)}</span>
              </td>
              <td style={{fontFamily:"var(--ff-serif)", fontSize:13, color:"var(--ink-mute)"}}>
                {r.cond === "emprestado" && r.clube && <span>{r.clube} · até {r.ate}</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function condLabel(c) {
  return {
    "titular":"Titular","reserva":"Reserva","nao-rel":"Não relacionado",
    "lesionado":"Lesionado","suspenso":"Suspenso","selecao":"Seleção",
    "emprestado":"Emprestado",
  }[c] || c;
}

function posicaoStub(nome) {
  // tenta inferir do jogadores stubs ou retorna —
  return window.JOGADORES[nome]?.posicao || "—";
}

// Campo do elenco — reaproveita layout do PARTIDA com numeração 1,2,...
function ElencoCampo({ p }) {
  const tit = p.escalacao.titulares_por_posicao;
  const placed = [];
  Object.entries(tit).forEach(([pos, players]) => {
    const coords = pitchCoordsForElenco(pos, players.length);
    players.forEach((name, i) => {
      const c = coords[i] || [50, 50];
      placed.push({ name, pos, x: c[0], y: c[1], idx: i+1 });
    });
  });
  const isGK = (pos) => pos === "Goleiro";
  const isCaptain = (name) => name === p.capitao;
  return (
    <div className="elenco-pitch-wrap">
      <div className="elenco-pitch-head">
        Campinho <small>ordenação dos titulares</small>
      </div>
      <div className="pitch elenco-pitch">
        <div className="pitch-stripes"/>
        <div className="pitch-center"/>
        <div className="pitch-top-box"/>
        <div style={{position:"absolute", left:"18%", right:"18%", bottom:0, height:"18%", border:"1px solid rgba(255,255,255,0.45)", borderBottom:0}}/>
        {/* linhas de posição */}
        {["ATA","MEI","VOL","DEF","GOL"].map((lab,i) => (
          <div key={lab} className="pitch-row-label" style={{top: `${[16,36,56,76,90][i]}%`}}>{lab}</div>
        ))}
        {placed.map((pl, i) => (
          <div key={i} className={`player-dot ${isGK(pl.pos)?"gk":""} ${isCaptain(pl.name)?"cap":""}`} style={{ left: `${pl.x}%`, top: `${pl.y}%` }}>
            <div className="num">{pl.idx}</div>
            <div className="nm">{pl.name}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// usa as mesmas coordenadas do partida.jsx (Goleiro embaixo, ataque em cima)
const PITCH_POS_Y_ELENCO = {
  Goleiro: 90,
  "Lateral-Direito": 76,
  Zagueiro: 76,
  "Lateral-Esquerdo": 76,
  Volante: 56,
  "Meio-Campista": 36,
  Atacante: 16,
};

function pitchLineXsElenco(count, pos) {
  if (pos === "Goleiro") return [50];
  if (pos === "Lateral-Direito") return [85];
  if (pos === "Lateral-Esquerdo") return [15];
  if (count <= 1) return [50];
  if (pos === "Zagueiro") {
    if (count === 2) return [38, 62];
    if (count === 3) return [28, 50, 72];
  }
  if (count === 2) return [36, 64];
  if (pos === "Atacante" && count === 3) return [26, 74, 50];
  if (count === 3) return [26, 50, 74];
  if (count === 4) return [18, 39, 61, 82];
  const step = 68 / Math.max(1, count - 1);
  return Array.from({ length: count }, (_, i) => 16 + i * step);
}

function pitchCoordsForElenco(pos, count) {
  const y = PITCH_POS_Y_ELENCO[pos] ?? 50;
  return pitchLineXsElenco(count, pos).map((x) => [x, y]);
}

window.ElencoAtual = ElencoAtual;
