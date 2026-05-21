// Acervo Vasco — componentes reutilizáveis

const { useState, useEffect, useMemo, useRef } = React;

// ============ helpers ============
const fmtN = (n) => Number(n || 0).toLocaleString("pt-BR");
const fmtBRL = (n) => "R$ " + Number(n || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// monograma estilizado dos clubes — 3 letras + cor estável por nome
const CLUB_COLORS = [
  ["#1a1a1a", "#e7d9b5"], // preto / creme
  ["#8b1620", "#f0e2c4"], // vinho / creme
  ["#1f3b6b", "#f0e2c4"], // azul / creme
  ["#3a4a2a", "#f0e2c4"], // verde-musgo / creme
  ["#5a4a2a", "#f0e2c4"], // marrom / creme
  ["#6b3a1f", "#f0e2c4"], // terracota / creme
  ["#1a1a1a", "#c8a85a"], // preto / dourado
  ["#3a3225", "#f0e2c4"], // tinta / creme
];

function clubHash(name) {
  let h = 0;
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) >>> 0;
  return h;
}
function clubInitials(name) {
  // remove sufixo -UF
  const clean = name.replace(/-[A-Z]{2}$/, "").trim();
  const words = clean.split(/\s+/).filter(Boolean);
  if (words.length === 1) {
    return clean.slice(0, 3).toUpperCase();
  }
  // pegue 1ª de cada palavra, até 3
  const ini = words.slice(0, 3).map((w) => w[0]).join("");
  return ini.toUpperCase();
}
function clubBg(name) {
  return CLUB_COLORS[clubHash(name) % CLUB_COLORS.length];
}

function Monogram({ club, size = "md", vasco = false }) {
  const cls = size === "huge" ? "monogram huge"
            : size === "xl"   ? "monogram xl"
            : size === "lg"   ? "monogram lg"
            : "monogram";
  if (vasco) {
    return (
      <div className={cls + " vasco"} title="Vasco da Gama">
        <svg viewBox="0 0 100 100" width="100%" height="100%" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
          <path d="M50 2 L62 38 L98 50 L62 62 L50 98 L38 62 L2 50 L38 38 Z" fill="#b21f2d"/>
          <circle cx="50" cy="50" r="8" fill="#15110b"/>
        </svg>
      </div>
    );
  }
  const [bg, fg] = clubBg(club);
  return (
    <div className={cls} style={{ background: bg, color: fg }} title={club}>
      {clubInitials(club)}
    </div>
  );
}

// ============ Sparkline (saldo de gols cumulativo) ============
function Sparkline({ data, width = 320, height = 56, color = "#b21f2d" }) {
  if (!data || data.length === 0) return null;
  const min = Math.min(0, ...data);
  const max = Math.max(0, ...data);
  const range = max - min || 1;
  const pad = 4;
  const w = width - pad * 2;
  const h = height - pad * 2;
  const step = w / Math.max(1, data.length - 1);
  const pts = data.map((d, i) => [pad + i * step, pad + h - ((d - min) / range) * h]);
  const zeroY = pad + h - ((0 - min) / range) * h;
  const path = pts.map((p, i) => (i === 0 ? `M${p[0]},${p[1]}` : `L${p[0]},${p[1]}`)).join(" ");
  const last = pts[pts.length - 1];
  return (
    <svg width={width} height={height} style={{ display: "block" }}>
      <line x1={pad} x2={pad + w} y1={zeroY} y2={zeroY} stroke="#d6c9a6" strokeWidth="1" strokeDasharray="2 3" />
      <path d={path} fill="none" stroke={color} strokeWidth="1.6" strokeLinejoin="round" strokeLinecap="round" />
      {pts.map((p, i) => (
        <circle key={i} cx={p[0]} cy={p[1]} r="1.6" fill={color} />
      ))}
      <circle cx={last[0]} cy={last[1]} r="3.2" fill={color} />
    </svg>
  );
}

// ============ Aproveitamento line chart (% rolling) ============
function AproveitamentoChart({ data, width = 320, height = 56 }) {
  // data: array de % acumulado (0-100)
  if (!data || data.length === 0) return null;
  const pad = 4;
  const w = width - pad * 2;
  const h = height - pad * 2;
  const step = w / Math.max(1, data.length - 1);
  const pts = data.map((d, i) => [pad + i * step, pad + h - (d / 100) * h]);
  const path = pts.map((p, i) => (i === 0 ? `M${p[0]},${p[1]}` : `L${p[0]},${p[1]}`)).join(" ");
  const area = path + ` L${pts[pts.length-1][0]},${pad+h} L${pts[0][0]},${pad+h} Z`;
  const y50 = pad + h - (50 / 100) * h;
  return (
    <svg width={width} height={height} style={{ display: "block" }}>
      <line x1={pad} x2={pad + w} y1={y50} y2={y50} stroke="#d6c9a6" strokeWidth="1" strokeDasharray="2 3" />
      <path d={area} fill="#b21f2d" fillOpacity="0.08" />
      <path d={path} fill="none" stroke="#15110b" strokeWidth="1.6" strokeLinejoin="round" />
    </svg>
  );
}

// ============ V/E/D streak bars (sequência de resultados) ============
function formatMatchScore(jogo) {
  if (!jogo || !Array.isArray(jogo.placar)) return "Placar não informado";
  if (jogo.local === "fora") {
    return `${jogo.adversario} ${jogo.placar[1]} × ${jogo.placar[0]} Vasco`;
  }
  return `Vasco ${jogo.placar[0]} × ${jogo.placar[1]} ${jogo.adversario}`;
}

function scorePair(jogo) {
  if (Array.isArray(jogo?.placar)) return jogo.placar.map((n) => Number(n || 0));
  if (jogo?.placar && typeof jogo.placar === "object") {
    return [Number(jogo.placar.vasco || 0), Number(jogo.placar.adversario || 0)];
  }
  return null;
}

function streakBarHeight(result, game, height) {
  const inner = Math.max(1, height - 8);
  const pair = scorePair(game);
  if (!pair) {
    const fallback = result === "E" ? 0.32 : result === "D" ? 0.46 : 0.64;
    return inner * fallback;
  }
  const [gp, gc] = pair;
  if (result === "E") {
    const drawGoals = Math.min(4, Math.max(0, gp));
    return inner * (0.22 + drawGoals * 0.12);
  }
  const diff = Math.min(4, Math.max(1, Math.abs(gp - gc)));
  return inner * (0.32 + diff * 0.16);
}

function StreakBars({ results, games = [], width = 320, height = 56 }) {
  // results: ["V","E","D",...]
  const n = results.length;
  const [hover, setHover] = useState(null);
  if (!n) return null;
  const pad = 2;
  const barW = (width - pad * (n + 1)) / n;
  const COLORS = { V: "#4d6b2a", E: "#b48415", D: "#a8341f" };
  const RESULT_LABELS = { V: "Vitória", E: "Empate", D: "Derrota" };
  const tooltipGame = hover ? games[hover.index] : null;
  const tooltipHalf = 110;
  const tooltipLeft = hover ? Math.max(tooltipHalf, Math.min(width - tooltipHalf, hover.left)) : 0;
  return (
    <span className="streak-bars-wrap" style={{ width, height }}>
      <svg width={width} height={height} className="streak-bars-svg" aria-label="Sequência de resultados">
        {results.map((r, i) => {
          const x = pad + i * (barW + pad);
          const game = games[i];
          const h = streakBarHeight(r, game, height);
          const y = r === "E" ? (height - h) / 2 : height - 4 - h;
          return (
            <rect
              key={i}
              className="streak-bars-hit"
              x={x}
              y={y}
              width={barW}
              height={h}
              fill={COLORS[r]}
              onMouseEnter={() => game && setHover({ index: i, left: x + barW / 2 })}
              onMouseMove={() => game && setHover({ index: i, left: x + barW / 2 })}
              onMouseLeave={() => setHover(null)}
            />
          );
        })}
      </svg>
      {tooltipGame && (
        <span
          className={"streak-tooltip " + tooltipGame.resultado}
          style={{ left: tooltipLeft, bottom: height + 8 }}
        >
          <span className="streak-tooltip-kicker">
            {tooltipGame.data} · {RESULT_LABELS[tooltipGame.resultado] || tooltipGame.resultado}
          </span>
          <span className="streak-tooltip-main">{tooltipGame.adversario}</span>
          <span className="streak-tooltip-score">{formatMatchScore(tooltipGame)}</span>
          <span className="streak-tooltip-comp">{tooltipGame.competicao}</span>
        </span>
      )}
    </span>
  );
}

// ============ Mini V/E/D streak (na tabela) ============
function MiniStreak({ results }) {
  return (
    <span className="streak">
      {results.map((r, i) => <span key={i} className={r} />)}
    </span>
  );
}

Object.assign(window, {
  fmtN, fmtBRL,
  Monogram, clubInitials, clubBg,
  formatMatchScore,
  Sparkline, AproveitamentoChart, StreakBars, MiniStreak,
});
