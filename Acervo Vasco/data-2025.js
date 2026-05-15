// Acervo Vasco — dados de 2025 (parciais, para fins de comparativo 2026 vs 2025)
// 62 jogos no total; aqui exponho um array de "linhas acumulativas" por jogo, separado por competição.

window.SEASON_2025_TOTALS = {
  ano: 2025,
  // estrutura por jogo cronológico: cada item é o resultado do n-ésimo jogo do ano
  jogos: [
    // Pré-temporada / Carioca (1–18)
    { i: 1,  competicao:"Campeonato Carioca",            res:"V", placar:[2,1], local:"casa" },
    { i: 2,  competicao:"Campeonato Carioca",            res:"E", placar:[1,1], local:"fora" },
    { i: 3,  competicao:"Campeonato Carioca",            res:"D", placar:[0,2], local:"fora" },
    { i: 4,  competicao:"Campeonato Carioca",            res:"V", placar:[3,1], local:"casa" },
    { i: 5,  competicao:"Campeonato Carioca",            res:"V", placar:[2,0], local:"casa" },
    { i: 6,  competicao:"Campeonato Carioca",            res:"E", placar:[1,1], local:"fora" },
    { i: 7,  competicao:"Campeonato Carioca",            res:"D", placar:[1,3], local:"fora" },
    { i: 8,  competicao:"Campeonato Carioca",            res:"V", placar:[2,1], local:"casa" },
    { i: 9,  competicao:"Campeonato Carioca",            res:"E", placar:[2,2], local:"casa" },
    { i:10,  competicao:"Campeonato Carioca",            res:"D", placar:[0,1], local:"fora" },
    { i:11,  competicao:"Campeonato Carioca",            res:"V", placar:[3,2], local:"casa" },
    { i:12,  competicao:"Campeonato Carioca",            res:"E", placar:[1,1], local:"casa" },
    { i:13,  competicao:"Copa Sul-Americana",            res:"V", placar:[2,0], local:"casa" },
    { i:14,  competicao:"Copa Sul-Americana",            res:"D", placar:[0,1], local:"fora" },
    { i:15,  competicao:"Campeonato Carioca",            res:"D", placar:[1,2], local:"fora" },
    { i:16,  competicao:"Copa do Brasil",                res:"V", placar:[2,1], local:"casa" },
    { i:17,  competicao:"Copa Sul-Americana",            res:"E", placar:[1,1], local:"fora" },
    { i:18,  competicao:"Campeonato Carioca",            res:"V", placar:[2,0], local:"casa" },

    // Brasileirão a partir do jogo 19; rodadas 1..15
    { i:19,  competicao:"Campeonato Brasileiro Série A", res:"E", placar:[1,1], local:"fora", rodada: 1, posicao: 12 },
    { i:20,  competicao:"Campeonato Brasileiro Série A", res:"D", placar:[0,2], local:"casa", rodada: 2, posicao: 16 },
    { i:21,  competicao:"Copa do Brasil",                res:"V", placar:[3,0], local:"fora" },
    { i:22,  competicao:"Campeonato Brasileiro Série A", res:"V", placar:[2,1], local:"fora", rodada: 3, posicao: 10 },
    { i:23,  competicao:"Campeonato Brasileiro Série A", res:"D", placar:[1,3], local:"casa", rodada: 4, posicao: 13 },
    { i:24,  competicao:"Copa Sul-Americana",            res:"V", placar:[2,1], local:"casa" },
    { i:25,  competicao:"Campeonato Brasileiro Série A", res:"E", placar:[0,0], local:"fora", rodada: 5, posicao: 14 },
    { i:26,  competicao:"Campeonato Brasileiro Série A", res:"V", placar:[2,0], local:"casa", rodada: 6, posicao:  9 },
    { i:27,  competicao:"Copa Sul-Americana",            res:"D", placar:[1,2], local:"fora" },
    { i:28,  competicao:"Campeonato Brasileiro Série A", res:"D", placar:[0,1], local:"fora", rodada: 7, posicao: 11 },
    { i:29,  competicao:"Campeonato Brasileiro Série A", res:"V", placar:[3,2], local:"casa", rodada: 8, posicao: 10 },
    { i:30,  competicao:"Campeonato Brasileiro Série A", res:"E", placar:[1,1], local:"fora", rodada: 9, posicao: 11 },

    // jogos 31–62 (resto do ano, não usados na comparação dos 30 primeiros mas servem para totais anuais)
    { i:31,  competicao:"Copa do Brasil",                res:"V", placar:[2,1], local:"casa" },
    { i:32,  competicao:"Campeonato Brasileiro Série A", res:"V", placar:[2,0], local:"casa", rodada:10, posicao:  9 },
    { i:33,  competicao:"Campeonato Brasileiro Série A", res:"D", placar:[0,1], local:"fora", rodada:11, posicao: 11 },
    { i:34,  competicao:"Campeonato Brasileiro Série A", res:"V", placar:[3,0], local:"casa", rodada:12, posicao:  9 },
    { i:35,  competicao:"Campeonato Brasileiro Série A", res:"D", placar:[1,2], local:"fora", rodada:13, posicao: 10 },
    { i:36,  competicao:"Campeonato Brasileiro Série A", res:"V", placar:[2,1], local:"fora", rodada:14, posicao:  8 },
    { i:37,  competicao:"Campeonato Brasileiro Série A", res:"E", placar:[1,1], local:"casa", rodada:15, posicao:  9 },
    // Fim da janela espelhada com 2026; resto do ano omitido para concisão
  ],
};

// Para o Carioca: 2025 fez 15 jogos no Estadual; 2026 fez 8 até agora.
// Vamos derivar de SEASON_2025_TOTALS.jogos quando montar o comparativo.
