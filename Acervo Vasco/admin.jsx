// Acervo Vasco — aba Admin (registro manual de jogos via JSON)
// Só visível quando o app é aberto com ?admin=1

const SAMPLE_JOGO = {
  data: "20/05/2026",
  hora: "19:00",
  local: "fora",
  competicao: "Copa Sul-Americana",
  fase: "Fase de grupos — 4ª rodada",
  adversario: "Olimpia",
  estadio: "Manuel Ferreira",
  tecnico: "Renato Gaúcho",
  capitao: "Léo Jardim",
  placar: { vasco: 1, adversario: 1 },
  gols_vasco: [
    { nome: "Brenner", minuto: 22, periodo: "1T" },
  ],
  gols_adversario: [
    { nome: "Pedro Sarabia", minuto: 71, periodo: "2T" },
  ],
  cartoes_amarelos_vasco: ["Saldivia", "Hugo Moura"],
  cartoes_vermelhos_vasco: [],
  publico_pagante: 18200,
  publico_presente: 19400,
  renda: 421000.00,
  arbitragem: {
    arbitro: "Felipe González (CHI)",
    auxiliares: ["Christian Schiemann", "Claudio Urrutia"],
    var: "Jhon Ospina (COL)",
  },
  escalacao: {
    formacao: "4-4-2",
    titulares_por_posicao: {
      Goleiro:           ["Léo Jardim"],
      "Lateral-Direito": ["Puma Rodríguez"],
      Zagueiro:          ["Saldivia", "Lucas Freitas"],
      "Lateral-Esquerdo":["Lucas Piton"],
      Volante:           ["Cauan Barros", "Thiago Mendes"],
      "Meio-Campista":   ["Johan Rojas", "Marino"],
      Atacante:          ["David", "Brenner"],
    },
    reservas: ["Daniel Fuzato","Walace Falcão","Tche Tche","Adson","Andrés Gómez","Nuno Moreira"],
    substituicoes: [],
    nao_relacionados: [],
    lesionados: ["Jair","Mateus Carvalho","Cuiabano"],
    suspensos: [],
    servindo_selecao: [],
  },
  observacao: "Empate na altura, fora de casa.",
};

function Admin() {
  const [raw, setRaw] = useState("");
  const [erro, setErro] = useState(null);
  const [previa, setPrevia] = useState(null);
  const [adicionados, setAdicionados] = useState(window.__JOGOS_ADICIONADOS || []);

  function tentarParsear(text) {
    setErro(null);
    setPrevia(null);
    if (!text.trim()) return;
    try {
      const obj = JSON.parse(text);
      validar(obj);
      setPrevia(obj);
    } catch (e) {
      setErro(e.message);
    }
  }

  function validar(o) {
    const req = ["data","local","competicao","adversario","placar"];
    for (const k of req) {
      if (o[k] === undefined) throw new Error(`Campo obrigatório ausente: "${k}"`);
    }
    if (!/^\d{2}\/\d{2}\/\d{4}$/.test(o.data)) throw new Error(`Data inválida (use DD/MM/AAAA): "${o.data}"`);
    if (!["casa","fora"].includes(o.local)) throw new Error(`local deve ser "casa" ou "fora"`);
    if (!o.placar || typeof o.placar.vasco !== "number" || typeof o.placar.adversario !== "number") {
      throw new Error(`placar deve conter { vasco: número, adversario: número }`);
    }
  }

  function handleChange(e) {
    setRaw(e.target.value);
    tentarParsear(e.target.value);
  }

  function handleAdicionar() {
    if (!previa) return;
    // converte para o formato do SEASON_2026.jogos
    const v = previa.placar.vasco;
    const a = previa.placar.adversario;
    const resultado = v > a ? "V" : v < a ? "D" : "E";
    const novoJogo = {
      id: 10000 + adicionados.length + 1,
      data: previa.data,
      local: previa.local,
      competicao: previa.competicao,
      adversario: previa.adversario,
      resultado,
      placar: previa.local === "casa" ? [v, a] : [v, a],
      tecnico: previa.tecnico || "—",
      estadio: previa.estadio || "—",
      publico: previa.publico_presente || 0,
      _adminAdicionado: true,
    };
    window.SEASON_2026.jogos.push(novoJogo);
    const lista = [...adicionados, { ...previa, _at: new Date().toISOString() }];
    window.__JOGOS_ADICIONADOS = lista;
    setAdicionados(lista);
    setRaw("");
    setPrevia(null);
  }

  function handleCarregarExemplo() {
    const txt = JSON.stringify(SAMPLE_JOGO, null, 2);
    setRaw(txt);
    tentarParsear(txt);
  }

  function handleLimpar() {
    setRaw("");
    setPrevia(null);
    setErro(null);
  }

  return (
    <div className="main">
      <section className="admin-hero">
        <div className="hero-eyebrow">Acervo · Painel do Admin</div>
        <div className="admin-hero-line">
          <h1 className="admin-title">Registrar Jogo</h1>
          <div className="admin-warn">
            <span className="lock">●</span>
            Modo administrador <strong>ativo</strong> · saia da query string <code>?admin=1</code> pra ocultar essa aba.
          </div>
        </div>
      </section>

      <div className="admin-grid">
        <div className="admin-editor">
          <div className="admin-editor-head">
            <h3 className="admin-section-title">Cole o JSON do jogo</h3>
            <div className="admin-actions">
              <button className="btn-ghost" onClick={handleCarregarExemplo}>Carregar exemplo</button>
              <button className="btn-ghost" onClick={handleLimpar}>Limpar</button>
            </div>
          </div>
          <textarea
            className="admin-textarea"
            placeholder='Cole aqui o JSON do jogo no formato do acervo…'
            value={raw}
            onChange={handleChange}
            spellCheck={false}
          />
          {erro && (
            <div className="admin-erro">
              <strong>Erro de validação:</strong> {erro}
            </div>
          )}
          {previa && !erro && (
            <div className="admin-ok">
              <strong>JSON válido.</strong> {resumirPrevia(previa)}
            </div>
          )}
          <div className="admin-submit-row">
            <button className="btn-primary" disabled={!previa || erro} onClick={handleAdicionar}>
              ▸ Adicionar ao acervo
            </button>
            <span className="admin-hint">
              {previa
                ? "Pré-visualização à direita confere os dados antes de salvar."
                : "Cole um JSON válido para habilitar."}
            </span>
          </div>
        </div>

        <div className="admin-preview">
          <h3 className="admin-section-title">Pré-visualização</h3>
          {!previa ? (
            <div className="admin-empty">
              Cole um JSON no editor para ver a partida renderizada aqui no mesmo formato do acervo.
            </div>
          ) : (
            <AdminPreview p={previa} />
          )}
        </div>
      </div>

      {adicionados.length > 0 && (
        <section className="admin-historico">
          <h3 className="admin-section-title">Adicionados nesta sessão <small>{adicionados.length}</small></h3>
          <div className="table-wrap">
            <table className="tbl">
              <thead>
                <tr>
                  <th style={{width:90}}>Data</th>
                  <th>Adversário</th>
                  <th style={{width:80}}>Placar</th>
                  <th style={{width:170}}>Competição</th>
                  <th style={{width:60}}>Local</th>
                  <th style={{width:180}}>Inserido</th>
                </tr>
              </thead>
              <tbody>
                {adicionados.map((j,i) => (
                  <tr key={i}>
                    <td className="date">{j.data}</td>
                    <td className="opponent"><Monogram club={j.adversario}/>{j.adversario}</td>
                    <td className="score">{j.placar.vasco}<span className="vs">×</span>{j.placar.adversario}</td>
                    <td className="competition">{j.competicao}</td>
                    <td className="locale">{j.local}</td>
                    <td style={{fontFamily:"var(--ff-mono)", fontSize:11, color:"var(--ink-mute)"}}>{fmtAt(j._at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{marginTop:10, fontFamily:"var(--ff-sans)", fontSize:10, letterSpacing:"0.18em", textTransform:"uppercase", color:"var(--ink-mute)"}}>
            Nota: registros adicionados aqui ficam em memória até a página ser recarregada.
          </div>
        </section>
      )}
    </div>
  );
}

function resumirPrevia(p) {
  return `${p.data} · Vasco ${p.placar.vasco}×${p.placar.adversario} ${p.adversario} (${p.competicao}, ${p.local})`;
}

function fmtAt(iso) {
  const d = new Date(iso);
  return d.toLocaleString("pt-BR", { hour12: false });
}

function AdminPreview({ p }) {
  const v = p.placar.vasco, a = p.placar.adversario;
  const res = v > a ? "Vitória" : v < a ? "Derrota" : "Empate";
  return (
    <div className="adminprev">
      <div className="adminprev-head">
        <div className="adminprev-meta">
          <strong>{p.competicao || "—"}</strong>
          {p.fase && <> · {p.fase}</>}
          <span className="dot"> · </span>
          {p.data}{p.hora && p.hora !== "—" ? <> <strong>{p.hora}</strong></> : null}
        </div>
        <div className="adminprev-scoreline">
          <div className="adminprev-team">
            <Monogram club="Vasco" vasco size="lg"/>
            <span className="adminprev-name">Vasco</span>
          </div>
          <div className="adminprev-score">{v}<span className="x">×</span>{a}</div>
          <div className="adminprev-team">
            <span className="adminprev-name">{p.adversario}</span>
            <Monogram club={p.adversario} size="lg"/>
          </div>
        </div>
        <div className="adminprev-meta" style={{marginTop:6}}>
          <strong>{p.estadio || "estádio a confirmar"}</strong> · {p.local}
          {p.tecnico && <> · técnico {p.tecnico}</>}
          {p.capitao && <> · capitão {p.capitao}</>}
        </div>
        <div className="adminprev-meta">
          Resultado: <strong style={{color: res==="Vitória"?"var(--r-v)":res==="Derrota"?"var(--r-d)":"var(--r-e)"}}>{res}</strong>
        </div>
      </div>

      <div className="adminprev-grid">
        <div>
          <h5>Gols do Vasco</h5>
          {(p.gols_vasco || []).length === 0
            ? <em>nenhum gol</em>
            : <ul>{p.gols_vasco.map((g,i) => <li key={i}>{g.nome} <span className="min">{g.minuto}'/{g.periodo}{g.penalti ? " · pen" : ""}</span></li>)}</ul>}
        </div>
        <div>
          <h5>Gols do {p.adversario}</h5>
          {(p.gols_adversario || []).length === 0
            ? <em>nenhum gol</em>
            : <ul>{p.gols_adversario.map((g,i) => <li key={i}>{g.nome}{g.contra ? " (contra)" : ""} <span className="min">{g.minuto}'/{g.periodo}</span></li>)}</ul>}
        </div>
        <div>
          <h5>Amarelos · {(p.cartoes_amarelos_vasco||[]).length}</h5>
          {(p.cartoes_amarelos_vasco||[]).length === 0 ? <em>—</em> : <ul>{p.cartoes_amarelos_vasco.map(n => <li key={n}>{n}</li>)}</ul>}
        </div>
        <div>
          <h5>Vermelhos · {(p.cartoes_vermelhos_vasco||[]).length}</h5>
          {(p.cartoes_vermelhos_vasco||[]).length === 0 ? <em>—</em> : <ul>{p.cartoes_vermelhos_vasco.map((c,i) => <li key={i}>{c.nome} <span className="min">{c.minuto}'/{c.periodo}</span></li>)}</ul>}
        </div>
        <div>
          <h5>Bilheteria</h5>
          {p.publico_pagante != null
            ? <ul><li>Pagantes: {fmtN(p.publico_pagante)}</li><li>Presente: {fmtN(p.publico_presente)}</li>{p.renda != null && <li>Renda: R$ {p.renda.toLocaleString("pt-BR", {minimumFractionDigits:2})}</li>}</ul>
            : <em>—</em>}
        </div>
        <div>
          <h5>Arbitragem</h5>
          {p.arbitragem
            ? <ul><li>Árbitro: <strong>{p.arbitragem.arbitro}</strong></li>{p.arbitragem.var && <li>VAR: {p.arbitragem.var}</li>}{p.arbitragem.auxiliares && <li>Auxiliares: {p.arbitragem.auxiliares.join(", ")}</li>}</ul>
            : <em>—</em>}
        </div>
      </div>
    </div>
  );
}

window.Admin = Admin;
