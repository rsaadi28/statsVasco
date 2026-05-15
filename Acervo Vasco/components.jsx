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
function StreakBars({ results, width = 320, height = 56 }) {
  // results: ["V","E","D",...]
  const n = results.length;
  const pad = 2;
  const barW = (width - pad * (n + 1)) / n;
  const COLORS = { V: "#4d6b2a", E: "#b48415", D: "#a8341f" };
  return (
    <svg width={width} height={height} style={{ display: "block" }}>
      {results.map((r, i) => (
        <rect
          key={i}
          x={pad + i * (barW + pad)}
          y={r === "V" ? 4 : r === "E" ? height / 2 - height / 8 : height - 4 - height * 0.6}
          width={barW}
          height={r === "V" ? height - 8 : r === "E" ? height / 4 : height * 0.6}
          fill={COLORS[r]}
        />
      ))}
    </svg>
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
  Sparkline, AproveitamentoChart, StreakBars, MiniStreak,
});
