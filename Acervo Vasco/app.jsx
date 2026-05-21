// Acervo Vasco — shell e roteamento simples

const NAV_TABS_PUBLIC = [
  "Jogos Futuros", "Retrospecto", "Geral",
  "Temporadas", "Comparativo", "Evolução",
  "Elenco Atual", "Técnicos", "Árbitros", "Jogadores",
  "Estádios", "Títulos",
];
const NAV_TABS = NAV_TABS_PUBLIC;

const YEARS = (() => {
  if (window.ACERVO_SEASONS) {
    return Object.keys(window.ACERVO_SEASONS).map(Number).sort((a,b) => b - a);
  }
  const arr = [];
  for (let y = 2026; y >= 2000; y--) arr.push(y);
  return arr;
})();

// estatística sintética por ano (placeholder pros anos antigos — só pro hover do sidebar)
const YEAR_HINTS = {
  2026: "30j · 11V 11E 8D · 48.9%",
  2025: "62j · 28V 18E 16D · 58.1%",
  2024: "61j · 27V 16E 18D · 56.0%",
  2023: "58j · 24V 14E 20D · 49.4%",
  2022: "53j · 23V 16E 14D · 53.5%",
  2021: "58j · 22V 17E 19D · 47.7%",
  2020: "47j · 20V 13E 14D · 51.8%",
  2011: "67j · 38V 16E 13D · 64.2%",
  2000: "63j · 38V 14E 11D · 67.7%",
  ...(window.ACERVO_YEAR_HINTS || {}),
};

function App() {
  const [activeTab, setActiveTab] = useState("Temporadas");
  const [year, setYear] = useState(YEARS[0] || 2026);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [retroAdv, setRetroAdv] = useState(null);

  const seasons = window.ACERVO_SEASONS || { 2026: window.SEASON_2026 };
  const season = seasons[year] || window.SEASON_2026;
  const topbarMeta = season
    ? `v0.1 · ${season.resumo?.jogos || season.jogos?.length || 0} jogos · ${season.ano}`
    : "v0.1 · acervo";

  function handleOpenMatch(jogo) {
    setSelectedPlayer(null);
    setSelectedMatch(resolveMatchDetail(jogo));
    window.scrollTo({ top: 0, behavior: "instant" });
  }

  function handleOpenPlayer(nome) {
    setSelectedPlayer(nome);
    window.scrollTo({ top: 0, behavior: "instant" });
  }

  function handleOpenRetro(advNome) {
    setRetroAdv(advNome);
    setActiveTab("Retrospecto");
    setSelectedMatch(null);
    setSelectedPlayer(null);
    window.scrollTo({ top: 0, behavior: "instant" });
  }

  function handleTabChange(tab) {
    setActiveTab(tab);
    setSelectedMatch(null);
    setSelectedPlayer(null);
    if (tab !== "Retrospecto") setRetroAdv(null);
    window.scrollTo({ top: 0, behavior: "instant" });
  }

  function handleBack() {
    if (selectedPlayer) { setSelectedPlayer(null); return; }
    setSelectedMatch(null);
  }

  return (
    <div className="app">
      <TopBar tabs={NAV_TABS} active={activeTab} onChange={handleTabChange} meta={topbarMeta} />
      <div className={"page" + (activeTab === "Temporadas" && !selectedMatch && !selectedPlayer ? "" : " page-no-sidebar")}>
        {activeTab === "Temporadas" && !selectedMatch && !selectedPlayer && (
          <YearsSidebar year={year} setYear={(y)=>{ setYear(y); setSelectedMatch(null); }} />
        )}
        {selectedPlayer
          ? <Jogador nome={selectedPlayer} onBack={handleBack} onOpenMatch={handleOpenMatch} />
          : selectedMatch
            ? <Partida partida={selectedMatch} onBack={handleBack} onOpenPlayer={handleOpenPlayer} />
            : (function () {
                switch (activeTab) {
                  case "Retrospecto":    return <Retrospecto initial={retroAdv || "Botafogo-RJ"} onOpenPlayer={handleOpenPlayer} onOpenMatch={handleOpenMatch} />;
                  case "Jogos Futuros":  return <JogosFuturos onOpenRetro={handleOpenRetro} />;
                  case "Elenco Atual":   return <ElencoAtual onOpenPlayer={handleOpenPlayer} />;
                  case "Jogadores":      return <Jogadores onOpenPlayer={handleOpenPlayer} />;
                  case "Estádios":       return <Estadios onOpenMatch={handleOpenMatch} />;
                  case "Árbitros":       return <Arbitros onOpenMatch={handleOpenMatch} />;
                  case "Geral":          return <Geral onOpenPlayer={handleOpenPlayer} />;
                  case "Técnicos":       return <Tecnicos onOpenPlayer={handleOpenPlayer} onOpenMatch={handleOpenMatch} />;
                  case "Títulos":        return <Titulos onOpenPlayer={handleOpenPlayer} />;
                  case "Comparativo":    return <Comparativo />;
                  case "Evolução":       return <Evolucao onOpenPlayer={handleOpenPlayer} />;
                  case "Temporadas":     return season ? <Temporadas season={season} onOpenMatch={handleOpenMatch} /> : <YearPlaceholder year={year} />;
                  default:               return <TabPlaceholder tab={activeTab} />;
                }
              })()
        }
      </div>
    </div>
  );
}

function TopBar({ tabs, active, onChange, meta }) {
  return (
    <header className="topbar">
      <div className="topbar-inner">
        <div className="brand">
          <div className="brand-eyebrow">Acervo · desde 2000</div>
          <div className="brand-title">VASCO<em>·</em>DA<em>·</em>GAMA</div>
        </div>
        <nav className="mainnav">
          {tabs.map(t => (
            <button key={t} className={active===t?"active":""} onClick={()=>onChange(t)}>
              {t}
            </button>
          ))}
        </nav>
        <div className="topbar-meta">
          <span>{meta}</span>
        </div>
      </div>
    </header>
  );
}

function YearsSidebar({ year, setYear }) {
  return (
    <aside className="years">
      <div className="years-label">Temporadas</div>
      <div className="years-list">
        {YEARS.map(y => (
          <button key={y} className={"year-btn" + (y===year?" active":"")} onClick={()=>setYear(y)}>
            <span>{y}</span>
            <span className="year-stat">{YEAR_HINTS[y] || ""}</span>
          </button>
        ))}
        <div className="years-section">Décadas</div>
        <button className="year-btn" style={{fontSize:14, paddingTop:8}}>Anos 90 · arquivo</button>
        <button className="year-btn" style={{fontSize:14}}>Anos 80 · arquivo</button>
      </div>
    </aside>
  );
}

function TabPlaceholder({ tab }) {
  return (
    <div className="main">
      <section className="hero">
        <div className="hero-left">
          <div className="hero-eyebrow">Acervo Vasco</div>
          <h1 className="hero-year" style={{fontSize:96}}>{tab}</h1>
          <div className="hero-meta">
            <span>Esta seção ainda não foi migrada para a versão web do acervo.</span>
          </div>
        </div>
      </section>
    </div>
  );
}

function YearPlaceholder({ year }) {
  return (
    <div className="main">
      <section className="hero">
        <div className="hero-left">
          <div className="hero-eyebrow">Temporada · Acervo Vasco</div>
          <h1 className="hero-year">{year}</h1>
          <div className="hero-sub">
            Importação pendente. Os dados de {year} estão no acervo local em formato de planilha e ainda não foram migrados para esta vista web.
          </div>
          <div className="hero-meta">
            <span><strong>Resumo provável:</strong> {YEAR_HINTS[year] || "dados em consolidação"}</span>
          </div>
        </div>
      </section>
      <div style={{padding:"60px 0", textAlign:"center", border:"1px dashed var(--rule)", background:"var(--paper-card)", fontFamily:"var(--ff-serif)", fontSize:17, fontStyle:"italic", color:"var(--ink-mute)"}}>
        Selecione <strong style={{color:"var(--ink)", fontStyle:"normal"}}>2026</strong> na lateral para navegar pela temporada já migrada.
      </div>
    </div>
  );
}

function matchKey(jogo) {
  return `${jogo?.data || ""}|${jogo?.adversario || ""}`;
}

function resolveMatchDetail(jogo) {
  const detalhes = window.PARTIDAS_DETALHES || {};
  const idKey = jogo?.id != null ? String(jogo.id) : "";
  return detalhes[idKey]
    || detalhes[matchKey(jogo)]
    || (jogo?.id === 30 ? window.PARTIDA_PAYSANDU : null)
    || buildStubPartida(jogo);
}

// stub pra partidas que ainda não têm detalhe completo
function buildStubPartida(j) {
  const placar = Array.isArray(j?.placar) ? j.placar : [0, 0];
  const vasco_casa = j?.local !== "fora";
  return {
    id: j?.id,
    data: j?.data || "—",
    adversario: j?.adversario || j?.adv || "Adversário",
    competicao: j?.competicao || "—",
    fase: "—",
    local: j?.local || "casa",
    estadio: j?.estadio || "—",
    horario: "—",
    tecnico: j?.tecnico || "—",
    capitao: "—",
    placar: {
      vasco: vasco_casa ? placar[0] : placar[1],
      adversario: vasco_casa ? placar[1] : placar[0],
    },
    agregado: null,
    gols_vasco: [],
    gols_adversario: [],
    cartoes_amarelos_vasco: [],
    cartoes_vermelhos_vasco: [],
    estatisticas_vasco: {},
    estatisticas_jogadores_vasco: [],
    publico_pagante: j?.publico || 0,
    publico_presente: j?.publico ? Math.round(j.publico * 1.05) : 0,
    renda: (j?.publico || 0) * 65,
    arbitragem: { arbitro: "—", auxiliares: ["—","—"], var: "—" },
    escalacao: {
      formacao: "—",
      titulares_por_posicao: {},
      reservas: [],
      substituicoes: [],
      nao_relacionados: [],
      lesionados: [],
      suspensos: [],
      servindo_selecao: [],
    },
    observacao: `Detalhe completo desta partida ainda não foi migrado para o acervo web. Estrutura abaixo já está pronta para receber os dados. Clique em "Voltar" e selecione a partida de 13/05 (Paysandu) para ver um exemplo completo.`,
  };
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
