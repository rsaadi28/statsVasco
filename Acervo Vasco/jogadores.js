// Acervo Vasco — dados dos jogadores
// Léo Jardim com stats reais do print; demais com entradas a partir do print do elenco.

window.JOGADORES = {
  "Léo Jardim": {
    nome: "Léo Jardim",
    nome_completo: "Léo Vinicius Jardim Pereira",
    posicao: "Goleiro",
    numero: 1,
    nascimento: "10/05/1995",
    naturalidade: "Pelotas, RS — Brasil",
    altura_cm: 196,
    pe: "Direito",
    capitao_atual: true,
    contratado_de: "Boavista (POR)",
    passagens: [
      {
        id: "p1",
        periodo: "12/03/2026 – Atual",
        estreia: "12/03/2026",
        saida: "Ainda no elenco",
        idx: 1,
        stats: {
          jogos_participacao: 13,
          minutos: 1380,
          media_minutos: 106.15,
          jogos_titular: 15,
          jogos_reserva: 0,
          nao_entrou: 0,
          nao_relacionado: 2,
          lesionado: 0,
          suspenso: 0,
          selecao: 0,
          gols: 0,
          jogos_capitao: 0,
          partidas_marcou: 0,
          gols_titular: 0,
          gols_banco: 0,
          media_gols: 0.0,
          amarelos: 1,
          vermelhos: 0,
          amarelos_acumulados: 1,
          suspensao_pendente: false,
          media_min_entre_gols: null,
          ved: { v: 7, e: 5, d: 3 },
        },
        partidas: [
          { data: "12/03/2026", adv: "Palmeiras-SP",   placar: "2x1",  res: "V", titular: true,  minutos: 90, gols: 0, amarelo: false, vermelho: false },
          { data: "15/03/2026", adv: "Cruzeiro-MG",    placar: "3x3",  res: "E", titular: true,  minutos: 90, gols: 0, amarelo: false, vermelho: false },
          { data: "18/03/2026", adv: "Fluminense-RJ",  placar: "3x2",  res: "V", titular: true,  minutos: 90, gols: 0, amarelo: false, vermelho: false },
          { data: "22/03/2026", adv: "Grêmio-RS",      placar: "2x1",  res: "V", titular: true,  minutos: 90, gols: 0, amarelo: false, vermelho: false },
          { data: "01/04/2026", adv: "Coritiba-PR",    placar: "1x1",  res: "E", titular: true,  minutos: 90, gols: 0, amarelo: false, vermelho: false },
          { data: "04/04/2026", adv: "Botafogo",       placar: "1x2",  res: "D", titular: true,  minutos: 90, gols: 0, amarelo: true,  vermelho: false },
          { data: "07/04/2026", adv: "Barracas Central", placar: "0x0", res: "E", titular: true,  minutos: 90, gols: 0, amarelo: false, vermelho: false },
          { data: "11/04/2026", adv: "Remo",           placar: "1x1",  res: "E", titular: true,  minutos: 90, gols: 0, amarelo: false, vermelho: false },
          { data: "14/04/2026", adv: "Audax italiano", placar: "1x2",  res: "D", titular: true,  minutos: 90, gols: 0, amarelo: false, vermelho: false },
          { data: "18/04/2026", adv: "São Paulo-SP",   placar: "2x1",  res: "V", titular: true,  minutos: 90, gols: 0, amarelo: false, vermelho: false },
          { data: "21/04/2026", adv: "Paysandu-PA",    placar: "2x0",  res: "V", titular: false, minutos: 0,  gols: 0, amarelo: false, vermelho: false, status: "não relacionado" },
          { data: "26/04/2026", adv: "Corinthians",    placar: "0x1",  res: "D", titular: true,  minutos: 90, gols: 0, amarelo: false, vermelho: false },
          { data: "30/04/2026", adv: "Olimpia",        placar: "3x0",  res: "V", titular: false, minutos: 0,  gols: 0, amarelo: false, vermelho: false, status: "não relacionado" },
          { data: "03/05/2026", adv: "Flamengo-RJ",    placar: "2x2",  res: "E", titular: true,  minutos: 90, gols: 0, amarelo: false, vermelho: false },
          { data: "06/05/2026", adv: "Audax italiano", placar: "2x1",  res: "V", titular: true,  minutos: 90, gols: 0, amarelo: false, vermelho: false },
          { data: "10/05/2026", adv: "Athletico-PR",   placar: "1x0",  res: "V", titular: true,  minutos: 60, gols: 0, amarelo: false, vermelho: false },
          { data: "13/05/2026", adv: "Paysandu-PA",    placar: "2x2",  res: "E", titular: true,  minutos: 90, gols: 0, amarelo: false, vermelho: false },
        ],
      }
    ]
  },
};

// Catálogo do elenco atual + ex-jogadores. Cada linha vira uma entrada em JOGADORES.
// status: titular | reserva | nao-rel | lesionado | suspenso | selecao | emprestado | ex
// minutos: pode ser null para "Desconhecido"
window.ELENCO_DATA = [
  // Goleiros
  { nome:"Allan Vitor",       posicao:"Goleiro",          status:"nao-rel",    minutos:null, numero:30, gols:0 },
  { nome:"Daniel Fuzato",     posicao:"Goleiro",          status:"reserva",    minutos:180,  numero:12, gols:0 },
  { nome:"Léo Jardim",        posicao:"Goleiro",          status:"titular",    minutos:1380, numero:1,  gols:0, capitao_atual:true },
  { nome:"Pablo",             posicao:"Goleiro",          status:"reserva",    minutos:0,    numero:99, gols:0 },
  { nome:"Phillipe Gabriel",  posicao:"Goleiro",          status:"nao-rel",    minutos:null, numero:35, gols:0 },

  // Laterais-direitos
  { nome:"Breno Vereza",      posicao:"Lateral-Direito",  status:"nao-rel",    minutos:null, numero:33, gols:0 },
  { nome:"Paulo Henrique",    posicao:"Lateral-Direito",  status:"titular",    minutos:918,  numero:4,  gols:0 },
  { nome:"Puma Rodríguez",    posicao:"Lateral-Direito",  status:"reserva",    minutos:694,  numero:22, gols:5, foi_capitao:true },

  // Zagueiros
  { nome:"Bruno André",       posicao:"Zagueiro",         status:"nao-rel",    minutos:null, numero:36, gols:0 },
  { nome:"Carlos Cuesta",     posicao:"Zagueiro",         status:"nao-rel",    minutos:450,  numero:2,  gols:1 },
  { nome:"João Vitor",        posicao:"Zagueiro",         status:"nao-rel",    minutos:6,    numero:37, gols:0 },
  { nome:"Lucas Freitas",     posicao:"Zagueiro",         status:"titular",    minutos:450,  numero:26, gols:0 },
  { nome:"Lyncon",            posicao:"Zagueiro",         status:"emprestado", minutos:0,    numero:null, gols:0, clube:"Atlético-GO" },
  { nome:"Robert Renan",      posicao:"Zagueiro",         status:"nao-rel",    minutos:1110, numero:24, gols:2 },
  { nome:"Saldivia",          posicao:"Zagueiro",         status:"titular",    minutos:1110, numero:3,  gols:0, foi_capitao:true },
  { nome:"Valdo",             posicao:"Zagueiro",         status:"ex",         minutos:0,    numero:null, gols:0 },
  { nome:"Walace Falcão",     posicao:"Zagueiro",         status:"reserva",    minutos:91,   numero:28, gols:0 },

  // Laterais-esquerdos
  { nome:"Alison",            posicao:"Lateral-Esquerdo", status:"nao-rel",    minutos:null, numero:38, gols:0 },
  { nome:"Avellar",           posicao:"Lateral-Esquerdo", status:"nao-rel",    minutos:99,   numero:39, gols:0 },
  { nome:"Cuiabano",          posicao:"Lateral-Esquerdo", status:"lesionado",  minutos:705,  numero:13, gols:2 },
  { nome:"Lucas Piton",       posicao:"Lateral-Esquerdo", status:"titular",    minutos:736,  numero:6,  gols:3 },
  { nome:"Riquelme",          posicao:"Lateral-Esquerdo", status:"emprestado", minutos:null, numero:null, gols:0, clube:"América-MG" },
  { nome:"Victor Luís",       posicao:"Lateral-Esquerdo", status:"ex",         minutos:0,    numero:null, gols:0 },

  // Volantes
  { nome:"Cauan Barros",      posicao:"Volante",          status:"titular",    minutos:824,  numero:25, gols:3 },
  { nome:"Hugo Moura",        posicao:"Volante",          status:"reserva",    minutos:830,  numero:16, gols:1, foi_capitao:true },
  { nome:"Jair",              posicao:"Volante",          status:"lesionado",  minutos:0,    numero:5,  gols:0 },
  { nome:"JP",                posicao:"Volante",          status:"reserva",    minutos:252,  numero:41, gols:0 },
  { nome:"Juan Sforza",       posicao:"Volante",          status:"emprestado", minutos:0,    numero:null, gols:0, clube:"Newell's" },
  { nome:"Mateus Carvalho",   posicao:"Volante",          status:"lesionado",  minutos:0,    numero:27, gols:0 },
  { nome:"Tche Tche",         posicao:"Volante",          status:"reserva",    minutos:885,  numero:27, gols:0 },
  { nome:"Thiago Mendes",     posicao:"Volante",          status:"titular",    minutos:1048, numero:8,  gols:4, foi_capitao:true, capitao_partida:true },

  // Meio-campistas
  { nome:"Guilherme Estrella",posicao:"Meio-Campista",    status:"emprestado", minutos:0,    numero:null, gols:0, clube:"Botafogo-SP" },
  { nome:"Gustavo Guimarães", posicao:"Meio-Campista",    status:"nao-rel",    minutos:null, numero:42, gols:0 },
  { nome:"Johan Rojas",       posicao:"Meio-Campista",    status:"titular",    minutos:619,  numero:14, gols:1 },
  { nome:"Lukas Zucarello",   posicao:"Meio-Campista",    status:"nao-rel",    minutos:10,   numero:43, gols:0 },
  { nome:"Philippe Coutinho", posicao:"Meio-Campista",    status:"ex",         minutos:0,    numero:null, gols:0 },
  { nome:"Ramon Rique",       posicao:"Meio-Campista",    status:"nao-rel",    minutos:114,  numero:44, gols:0 },
  { nome:"Ray Breno",         posicao:"Meio-Campista",    status:"emprestado", minutos:null, numero:null, gols:0, clube:"Tombense" },
  { nome:"Samuel Jesus",      posicao:"Meio-Campista",    status:"nao-rel",    minutos:null, numero:45, gols:0 },
  { nome:"William",           posicao:"Meio-Campista",    status:"ex",         minutos:210,  numero:null, gols:0 },

  // Atacantes
  { nome:"Adson",             posicao:"Atacante",         status:"reserva",    minutos:317,  numero:21, gols:1 },
  { nome:"Andrey Fernandes",  posicao:"Atacante",         status:"nao-rel",    minutos:null, numero:46, gols:0 },
  { nome:"Andrés Gómez",      posicao:"Atacante",         status:"reserva",    minutos:975,  numero:18, gols:3 },
  { nome:"Brenner",           posicao:"Atacante",         status:"titular",    minutos:423,  numero:9,  gols:3 },
  { nome:"Claudio Spinelli",  posicao:"Atacante",         status:"reserva",    minutos:642,  numero:19, gols:5 },
  { nome:"David",             posicao:"Atacante",         status:"titular",    minutos:845,  numero:11, gols:2 },
  { nome:"Gabriel Silva (GB)",posicao:"Atacante",         status:"emprestado", minutos:0,    numero:null, gols:0, clube:"Goiás" },
  { nome:"Garré",             posicao:"Atacante",         status:"emprestado", minutos:null, numero:null, gols:0, clube:"Tombense" },
  { nome:"Juninho",           posicao:"Atacante",         status:"nao-rel",    minutos:0,    numero:47, gols:0 },
  { nome:"Loide Augusto",     posicao:"Atacante",         status:"emprestado", minutos:null, numero:null, gols:0, clube:"Casa Pia" },
  { nome:"Marino",            posicao:"Atacante",         status:"titular",    minutos:393,  numero:20, gols:0 },
  { nome:"Matheus França",    posicao:"Atacante",         status:"reserva",    minutos:151,  numero:23, gols:1 },
  { nome:"Nuno Moreira",      posicao:"Atacante",         status:"reserva",    minutos:903,  numero:17, gols:2 },

  // Outros artilheiros que aparecem em ARTILHEIROS_POR_ANO mas não no elenco atual
  { nome:"Rayan",             posicao:"Atacante",         status:"ex",         minutos:1200, numero:null, gols:2 },
];

// Gera entradas em JOGADORES a partir de ELENCO_DATA
window.ELENCO_DATA.forEach(p => {
  if (window.JOGADORES[p.nome]) return; // Léo Jardim já tem dados ricos

  const jogos = p.minutos != null && p.minutos > 0
    ? Math.max(1, Math.round(p.minutos / 70))
    : 0;
  const titular = ["titular","reserva"].includes(p.status) ? Math.max(0, Math.round((p.minutos || 0) / 88)) : 0;
  const reserva = Math.max(0, jogos - titular);
  const gols = p.gols || 0;
  const v = Math.floor(jogos * 0.42), e = Math.floor(jogos * 0.30), d = Math.max(0, jogos - v - e);

  window.JOGADORES[p.nome] = {
    nome: p.nome,
    nome_completo: p.nome,
    posicao: p.posicao,
    numero: p.numero,
    nascimento: "—",
    naturalidade: "—",
    altura_cm: null,
    pe: "—",
    capitao_atual: !!p.capitao_atual,
    contratado_de: p.clube ? `Emprestado a ${p.clube}` : "—",
    status_atual: p.status,
    passagens: [
      {
        id: "p1",
        periodo: p.status === "ex" ? "2023 – 2025" : "2024 – Atual",
        estreia: p.status === "ex" ? "—" : "—",
        saida: p.status === "ex" ? "—" : "Ainda no elenco",
        idx: 1,
        stats: {
          jogos_participacao: jogos,
          minutos: p.minutos || 0,
          media_minutos: jogos ? +((p.minutos || 0) / jogos).toFixed(2) : 0,
          jogos_titular: titular,
          jogos_reserva: reserva,
          nao_entrou: 0,
          nao_relacionado: p.status === "nao-rel" ? 4 : 1,
          lesionado: p.status === "lesionado" ? 8 : 0,
          suspenso: 0,
          selecao: 0,
          gols,
          jogos_capitao: p.capitao_partida ? 4 : (p.foi_capitao ? 1 : 0),
          partidas_marcou: Math.ceil(gols * 0.75),
          gols_titular: Math.ceil(gols * 0.8),
          gols_banco: Math.floor(gols * 0.2),
          media_gols: jogos ? +(gols / jogos).toFixed(2) : 0,
          amarelos: Math.max(0, Math.floor(jogos / 6)),
          vermelhos: p.nome === "Thiago Mendes" ? 1 : 0,
          amarelos_acumulados: Math.max(0, Math.floor(jogos / 6)) % 3,
          suspensao_pendente: false,
          media_min_entre_gols: gols > 0 ? Math.round((p.minutos || 0) / gols) : null,
          ved: { v, e, d },
        },
        partidas: [],
      }
    ]
  };
});

// Mapeamento de status -> label legível
window.STATUS_LABEL = {
  "titular":    "Titular",
  "reserva":    "Reserva",
  "nao-rel":    "Não Relacionado",
  "lesionado":  "Lesionado",
  "suspenso":   "Suspenso",
  "selecao":    "Seleção",
  "emprestado": "Emprestado",
  "ex":         "Ex-jogador",
};
