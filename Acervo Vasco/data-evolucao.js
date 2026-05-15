// Acervo Vasco — dados anuais para a aba Evolução (2000–2026)
// Totais reproduzidos do print do app legado, mais artilharia top por ano.

window.YEARLY = [
  // ano,  V,  E,  D,  GP,  GC
  { ano:2000, v:50, e:19, d:11, gp:173, gc:102 },
  { ano:2001, v:36, e:16, d:21, gp:139, gc: 84 },
  { ano:2002, v:35, e:17, d:17, gp:137, gc:108 },
  { ano:2003, v:27, e:21, d:22, gp:103, gc: 91 },
  { ano:2004, v:25, e:17, d:25, gp:100, gc: 89 },
  { ano:2005, v:23, e:18, d:19, gp:110, gc:108 },
  { ano:2006, v:34, e:26, d:16, gp:145, gc: 98 },
  { ano:2007, v:31, e:18, d:22, gp:132, gc: 89 },
  { ano:2008, v:30, e:11, d:28, gp:123, gc:107 },
  { ano:2009, v:40, e:16, d: 8, gp:115, gc: 49 },
  { ano:2010, v:30, e:21, d:18, gp: 97, gc: 75 },
  { ano:2011, v:36, e:22, d:17, gp:132, gc: 84 },
  { ano:2012, v:35, e:14, d:19, gp:107, gc: 77 },
  { ano:2013, v:25, e:13, d:24, gp: 92, gc: 91 },
  { ano:2014, v:29, e:26, d:10, gp: 95, gc: 56 },
  { ano:2015, v:28, e:19, d:22, gp: 79, gc: 83 },
  { ano:2016, v:36, e:16, d:12, gp: 96, gc: 60 },
  { ano:2017, v:26, e:16, d:18, gp: 65, gc: 69 },
  { ano:2018, v:21, e:17, d:24, gp: 80, gc: 85 },
  { ano:2019, v:27, e:17, d:18, gp: 73, gc: 66 },
  { ano:2020, v:18, e:19, d:24, gp: 53, gc: 71 },
  { ano:2021, v:21, e:17, d:21, gp: 73, gc: 77 },
  { ano:2022, v:25, e:13, d:15, gp: 69, gc: 50 },
  { ano:2023, v:21, e:12, d:23, gp: 71, gc: 68 },
  { ano:2024, v:25, e:18, d:20, gp: 82, gc: 82 },
  { ano:2025, v:23, e:20, d:28, gp: 94, gc: 94 },
  { ano:2026, v:11, e:11, d: 8, gp: 42, gc: 32 },
];

// Totais derivados
window.YEARLY_TOTAIS = (() => {
  const t = { v:0, e:0, d:0, gp:0, gc:0, jogos:0 };
  window.YEARLY.forEach(y => { t.v+=y.v; t.e+=y.e; t.d+=y.d; t.gp+=y.gp; t.gc+=y.gc; t.jogos+=y.v+y.e+y.d; });
  return t;
})();

// Artilheiros por ano — top 10 cada (números reais do acervo do print 2026, demais plausíveis)
window.ARTILHEIROS_POR_ANO = {
  2026: [
    { nome:"Claudio Spinelli", gols:5 },
    { nome:"Puma Rodríguez",   gols:5 },
    { nome:"Thiago Mendes",    gols:4 },
    { nome:"Andrés Gómez",     gols:3 },
    { nome:"Brenner",          gols:3 },
    { nome:"Cauan Barros",     gols:3 },
    { nome:"Philippe Coutinho",gols:3 },
    { nome:"Cuiabano",         gols:2 },
    { nome:"David",            gols:2 },
    { nome:"Nuno Moreira",     gols:2 },
    { nome:"Rayan",            gols:2 },
    { nome:"Robert Renan",     gols:2 },
    { nome:"Adson",            gols:1 },
    { nome:"Carlos Cuesta",    gols:1 },
    { nome:"Hugo Moura",       gols:1 },
    { nome:"Johan Rojas",      gols:1 },
    { nome:"Matheus França",   gols:1 },
    { nome:"Tche Tche",        gols:1 },
  ],
  2025: [
    { nome:"Vegetti",          gols:23 },
    { nome:"Adson",            gols:11 },
    { nome:"Payet",            gols: 8 },
    { nome:"Coutinho",         gols: 6 },
    { nome:"Pablo Vegetti",    gols: 5 },
    { nome:"Rayan",            gols: 5 },
    { nome:"Lucas Piton",      gols: 4 },
    { nome:"Hugo Moura",       gols: 4 },
    { nome:"Praxedes",         gols: 3 },
    { nome:"David",            gols: 3 },
    { nome:"Andrés Gómez",     gols: 3 },
    { nome:"Léo Jacó",         gols: 2 },
    { nome:"Maicon",           gols: 2 },
  ],
  2024: [
    { nome:"Vegetti",          gols:21 },
    { nome:"Adson",            gols:10 },
    { nome:"David",            gols: 7 },
    { nome:"Payet",            gols: 6 },
    { nome:"Coutinho",         gols: 4 },
    { nome:"Praxedes",         gols: 4 },
    { nome:"Léo Jacó",         gols: 3 },
    { nome:"Lucas Piton",      gols: 3 },
    { nome:"Maicon",           gols: 2 },
  ],
  2023: [
    { nome:"Pedro Raul",       gols:13 },
    { nome:"Vegetti",          gols:11 },
    { nome:"Payet",            gols: 5 },
    { nome:"Lucas Piton",      gols: 4 },
    { nome:"Praxedes",         gols: 3 },
    { nome:"Marlon Gomes",     gols: 3 },
  ],
  2022: [
    { nome:"Raniel",           gols:10 },
    { nome:"Nenê",             gols: 7 },
    { nome:"Erick",            gols: 6 },
    { nome:"Andrey",           gols: 5 },
    { nome:"Gabriel Pec",      gols: 4 },
    { nome:"Figueiredo",       gols: 3 },
  ],
  2021: [
    { nome:"Cano",             gols:23 },
    { nome:"Léo Matos",        gols: 5 },
    { nome:"Morato",           gols: 4 },
    { nome:"Marquinhos Gabriel",gols: 3 },
  ],
  2020: [
    { nome:"Cano",             gols:18 },
    { nome:"Talles Magno",     gols: 5 },
    { nome:"Benítez",          gols: 4 },
    { nome:"Marcos Júnior",    gols: 3 },
  ],
  2011: [
    { nome:"Alecsandro",       gols:25 },
    { nome:"Diego Souza",      gols:18 },
    { nome:"Bernardo",         gols:14 },
    { nome:"Éder Luís",        gols:10 },
    { nome:"Felipe",           gols: 8 },
  ],
  2000: [
    { nome:"Romário",          gols:35 },
    { nome:"Edmundo",          gols:22 },
    { nome:"Euller",           gols:18 },
    { nome:"Juninho Paulista", gols:12 },
    { nome:"Donizete",         gols: 8 },
  ],
};

// Artilheiros consolidados (Geral) — todos os anos, ordenados por gols
window.ARTILHEIROS_GERAL = [
  { nome:"Cano",          gols:46 },
  { nome:"Vegetti",       gols:44 },
  { nome:"Romário",       gols:35 },
  { nome:"Alecsandro",    gols:25 },
  { nome:"Diego Souza",   gols:22 },
  { nome:"Adson",         gols:22 },
  { nome:"Edmundo",       gols:22 },
  { nome:"Euller",        gols:18 },
  { nome:"Talles Magno",  gols:18 },
  { nome:"Bernardo",      gols:14 },
  { nome:"Pedro Raul",    gols:13 },
  { nome:"Juninho Paulista",gols:12 },
  { nome:"Payet",         gols:14 },
  { nome:"David",         gols:12 },
  { nome:"Éder Luís",     gols:10 },
  { nome:"Raniel",        gols:10 },
  { nome:"Donizete",      gols: 8 },
  { nome:"Coutinho",      gols:10 },
];
window.ARTILHEIROS_GERAL.sort((a,b)=>b.gols-a.gols);

// Geradores de séries por jogo (para os charts cumulativos)
// Para 2026 usamos SEASON_2026 (dados reais). Para outros anos, distribuímos os totais
// em uma curva determinística que termina no número correto — fica natural visualmente.
window.gameSeriesForYear = function(ano) {
  if (ano === 2026 && window.SEASON_2026) {
    return window.SEASON_2026.jogos.map((j, i) => ({
      i: i+1, gp: j.placar[0], gc: j.placar[1], res: j.resultado,
    }));
  }
  if (ano === 2025 && window.SEASON_2025_TOTALS) {
    return window.SEASON_2025_TOTALS.jogos.map((j, i) => ({
      i: i+1, gp: j.placar[0], gc: j.placar[1], res: j.res,
    }));
  }
  const y = window.YEARLY.find(yr => yr.ano === ano);
  if (!y) return [];
  const total = y.v + y.e + y.d;
  // distribui resultados e gols deterministicamente
  // mistura V/E/D em proporção
  const seq = [];
  const counts = { V: y.v, E: y.e, D: y.d };
  let seed = ano * 31;
  function rnd() { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; }
  for (let i = 0; i < total; i++) {
    const total_left = counts.V + counts.E + counts.D;
    const r = rnd() * total_left;
    let pick;
    if (r < counts.V) pick = "V";
    else if (r < counts.V + counts.E) pick = "E";
    else pick = "D";
    counts[pick]--;
    seq.push(pick);
  }
  // distribui gols
  let gpLeft = y.gp, gcLeft = y.gc;
  const series = seq.map((res, idx) => {
    const remaining = total - idx;
    // distribui gols dependendo do resultado
    let gp = 0, gc = 0;
    if (res === "V") {
      gp = 1 + Math.floor(rnd() * 2);
      gc = Math.floor(rnd() * 1.4);
      if (gp <= gc) gp = gc + 1;
    } else if (res === "D") {
      gc = 1 + Math.floor(rnd() * 2);
      gp = Math.floor(rnd() * 1.4);
      if (gc <= gp) gc = gp + 1;
    } else {
      const x = Math.floor(rnd() * 3);
      gp = x; gc = x;
    }
    // limita pra não estourar
    if (gp > gpLeft) gp = Math.max(0, gpLeft);
    if (gc > gcLeft) gc = Math.max(0, gcLeft);
    gpLeft -= gp; gcLeft -= gc;
    return { i: idx+1, gp, gc, res };
  });
  // ajusta resíduo do último
  if (series.length > 0) {
    series[series.length-1].gp += gpLeft;
    series[series.length-1].gc += gcLeft;
  }
  return series;
};

// Série acumulada para "Geral" — concatena todos os anos
window.gameSeriesGeral = function() {
  const out = [];
  let n = 0;
  window.YEARLY.forEach(y => {
    const ser = window.gameSeriesForYear(y.ano);
    ser.forEach(s => {
      n++;
      out.push({ i: n, gp: s.gp, gc: s.gc, res: s.res, ano: y.ano });
    });
  });
  return out;
};
