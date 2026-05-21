// Acervo Vasco — dados de estádios e árbitros

// ============ ESTÁDIOS ============
// Reproduz o print: poucos estádios "conhecidos" do recorte recente + grande "Não informado"
// que representa a maior parte do acervo (1.737 jogos sem estádio carimbado).
window.ESTADIOS = [
  { nome:"Couto Pereira",                                  jogos: 1, v:0, e:1, d:0, gp:1,    gc:1    },
  { nome:"Estadio Bicentenario Municipal de La Florida",   jogos: 1, v:1, e:0, d:0, gp:2,    gc:1    },
  { nome:"Florencio Sola",                                 jogos: 1, v:0, e:1, d:0, gp:0,    gc:0    },
  { nome:"Mangueirão",                                     jogos: 2, v:1, e:1, d:0, gp:3,    gc:1    },
  { nome:"Maracanã",                                       jogos: 3, v:1, e:1, d:1, gp:6,    gc:6    },
  { nome:"Mineirão",                                       jogos: 1, v:0, e:1, d:0, gp:3,    gc:3    },
  { nome:"Morumbi",                                        jogos: 1, v:0, e:0, d:1, gp:0,    gc:4    },
  { nome:"Neo Química Arena",                              jogos: 1, v:0, e:0, d:1, gp:0,    gc:1    },
  { nome:"Nou Camp",                                       jogos: 1, v:0, e:0, d:1, gp:3,    gc:0    },
  { nome:"Não informado",                                  jogos: 1737, v:758, e:463, d:516, gp:2639, gc:2116 },
  { nome:"São Januário",                                   jogos: 9, v:6, e:1, d:2, gp:18,   gc:9    },
  { nome:"Universitário",                                  jogos: 1, v:0, e:1, d:0, gp:2,    gc:2    },
];

// jogos por estádio (sample real para os relevantes do acervo 2026)
window.JOGOS_POR_ESTADIO = {
  "São Januário": [
    { data:"20/11/2005", local:"casa", competicao:"Campeonato Brasileiro Série A", adv:"Paysandu-PA",      res:"V", placar:"Vasco 4 x 0 Paysandu-PA" },
    { data:"12/03/2026", local:"casa", competicao:"Campeonato Brasileiro Série A", adv:"Palmeiras-SP",     res:"V", placar:"Vasco 2 x 1 Palmeiras-SP" },
    { data:"22/03/2026", local:"casa", competicao:"Campeonato Brasileiro Série A", adv:"Grêmio-RS",        res:"V", placar:"Vasco 2 x 1 Grêmio-RS" },
    { data:"04/04/2026", local:"casa", competicao:"Campeonato Brasileiro Série A", adv:"Botafogo",         res:"D", placar:"Vasco 1 x 2 Botafogo" },
    { data:"14/04/2026", local:"casa", competicao:"Copa Sul-Americana",            adv:"Audax italiano",   res:"D", placar:"Vasco 1 x 2 Audax italiano" },
    { data:"18/04/2026", local:"casa", competicao:"Campeonato Brasileiro Série A", adv:"São Paulo-SP",     res:"V", placar:"Vasco 2 x 1 São Paulo-SP" },
    { data:"30/04/2026", local:"casa", competicao:"Copa Sul-Americana",            adv:"Olimpia",          res:"V", placar:"Vasco 3 x 0 Olimpia" },
    { data:"10/05/2026", local:"casa", competicao:"Campeonato Brasileiro Série A", adv:"Athletico-PR",     res:"V", placar:"Vasco 1 x 0 Athletico-PR" },
    { data:"13/05/2026", local:"casa", competicao:"Copa do Brasil",                adv:"Paysandu-PA",      res:"E", placar:"Vasco 2 x 2 Paysandu-PA" },
  ],
  "Maracanã": [
    { data:"21/01/2026", local:"fora", competicao:"Campeonato Carioca",            adv:"Flamengo-RJ",      res:"D", placar:"Vasco 0 x 1 Flamengo-RJ" },
    { data:"22/02/2026", local:"casa", competicao:"Campeonato Carioca",            adv:"Fluminense-RJ",    res:"D", placar:"Vasco 0 x 1 Fluminense-RJ" },
    { data:"18/03/2026", local:"casa", competicao:"Campeonato Brasileiro Série A", adv:"Fluminense-RJ",    res:"V", placar:"Vasco 3 x 2 Fluminense-RJ" },
    { data:"01/03/2026", local:"fora", competicao:"Campeonato Carioca",            adv:"Fluminense-RJ",    res:"E", placar:"Vasco 1 x 1 Fluminense-RJ" },
    { data:"04/04/2026", local:"casa", competicao:"Campeonato Brasileiro Série A", adv:"Botafogo",         res:"D", placar:"Vasco 1 x 2 Botafogo" },
    { data:"03/05/2026", local:"fora", competicao:"Campeonato Brasileiro Série A", adv:"Flamengo-RJ",      res:"E", placar:"Vasco 2 x 2 Flamengo-RJ" },
  ],
  "Mangueirão": [
    { data:"21/04/2026", local:"fora", competicao:"Copa do Brasil",                adv:"Paysandu-PA",      res:"V", placar:"Vasco 2 x 0 Paysandu-PA" },
    { data:"11/04/2026", local:"fora", competicao:"Campeonato Brasileiro Série A", adv:"Remo",             res:"E", placar:"Vasco 1 x 1 Remo" },
  ],
  "Couto Pereira": [
    { data:"01/04/2026", local:"fora", competicao:"Campeonato Brasileiro Série A", adv:"Coritiba-PR",      res:"E", placar:"Vasco 1 x 1 Coritiba-PR" },
  ],
  "Mineirão": [
    { data:"15/03/2026", local:"fora", competicao:"Campeonato Brasileiro Série A", adv:"Cruzeiro-MG",      res:"E", placar:"Vasco 3 x 3 Cruzeiro-MG" },
  ],
  "Morumbi": [
    { data:"07/08/2011", local:"fora", competicao:"Campeonato Brasileiro Série A", adv:"Botafogo",         res:"D", placar:"Vasco 0 x 4 Botafogo" },
  ],
  "Neo Química Arena": [
    { data:"26/04/2026", local:"fora", competicao:"Campeonato Brasileiro Série A", adv:"Corinthians",      res:"D", placar:"Vasco 0 x 1 Corinthians" },
  ],
  "Nou Camp": [
    { data:"06/05/2026", local:"fora", competicao:"Copa Sul-Americana",            adv:"Audax italiano",   res:"V", placar:"Vasco 2 x 1 Audax italiano" },
  ],
  "Estadio Bicentenario Municipal de La Florida": [
    { data:"06/05/2026", local:"fora", competicao:"Copa Sul-Americana",            adv:"Audax italiano",   res:"V", placar:"Vasco 2 x 1 Audax italiano" },
  ],
  "Florencio Sola": [
    { data:"07/04/2026", local:"fora", competicao:"Copa Sul-Americana",            adv:"Barracas Central", res:"E", placar:"Vasco 0 x 0 Barracas Central" },
  ],
  "Universitário": [
    { data:"30/04/2026", local:"fora", competicao:"Copa Sul-Americana",            adv:"Olimpia",          res:"E", placar:"Vasco 2 x 2 Olimpia" },
  ],
  "Não informado": [
    // amostra representativa — o resto não tem estádio cadastrado
    { data:"03/05/2000", local:"fora", competicao:"Campeonato Brasileiro Série A", adv:"Cruzeiro-MG",      res:"V", placar:"Vasco 3 x 1 Cruzeiro-MG" },
    { data:"12/07/2001", local:"casa", competicao:"Copa Mercosul",                 adv:"Cerro Porteño",    res:"V", placar:"Vasco 4 x 2 Cerro Porteño" },
    { data:"30/06/2002", local:"fora", competicao:"Campeonato Brasileiro Série A", adv:"Santos",           res:"E", placar:"Vasco 1 x 1 Santos" },
    { data:"15/09/2009", local:"casa", competicao:"Campeonato Brasileiro Série B", adv:"Ponte Preta",      res:"V", placar:"Vasco 2 x 0 Ponte Preta" },
    { data:"22/05/2011", local:"casa", competicao:"Copa do Brasil",                adv:"Coritiba-PR",      res:"V", placar:"Vasco 1 x 0 Coritiba-PR" },
  ],
};

// ============ ÁRBITROS ============
window.ARBITROS = [
  { nome:"Ramon Abatti Abel",          jogos:2, primeiro:{data:"01/04/2026", placar:"Vasco 1 x 1 Coritiba-PR"},   ultimo:{data:"21/04/2026", placar:"Vasco 2 x 0 Paysandu-PA"}, v:1, e:1, d:0, gp:3, gc:1 },
  { nome:"Davi de Oliveira Lacerda",   jogos:2, primeiro:{data:"22/03/2026", placar:"Vasco 2 x 1 Grêmio-RS"},     ultimo:{data:"26/04/2026", placar:"Vasco 0 x 1 Corinthians"}, v:1, e:0, d:1, gp:2, gc:2 },
  { nome:"Wilton Pereira Sampaio",     jogos:1, primeiro:{data:"03/05/2026", placar:"Vasco 2 x 2 Flamengo-RJ"},   ultimo:{data:"03/05/2026", placar:"Vasco 2 x 2 Flamengo-RJ"}, v:0, e:1, d:0, gp:2, gc:2 },
  { nome:"Wagner do Nascimento Magalhães", jogos:1, primeiro:{data:"04/04/2026", placar:"Vasco 1 x 2 Botafogo"},  ultimo:{data:"04/04/2026", placar:"Vasco 1 x 2 Botafogo"},   v:0, e:0, d:1, gp:1, gc:2 },
  { nome:"Savio Pereira Sampaio",      jogos:1, primeiro:{data:"18/04/2026", placar:"Vasco 2 x 1 São Paulo-SP"},  ultimo:{data:"18/04/2026", placar:"Vasco 2 x 1 São Paulo-SP"},v:1, e:0, d:0, gp:2, gc:1 },
  { nome:"Rodrigo José Pereira De Lima", jogos:1, primeiro:{data:"11/04/2026", placar:"Vasco 1 x 1 Remo"},        ultimo:{data:"11/04/2026", placar:"Vasco 1 x 1 Remo"},        v:0, e:1, d:0, gp:1, gc:1 },
  { nome:"Raphael Claus",              jogos:1, primeiro:{data:"10/05/2026", placar:"Vasco 1 x 0 Athletico-PR"},  ultimo:{data:"10/05/2026", placar:"Vasco 1 x 0 Athletico-PR"},v:1, e:0, d:0, gp:1, gc:0 },
  { nome:"Jorge Travassos dos Santos", jogos:1, primeiro:{data:"01/03/2000", placar:"Vasco 0 x 4 Palmeiras-SP"},  ultimo:{data:"01/03/2000", placar:"Vasco 0 x 4 Palmeiras-SP"},v:0, e:0, d:1, gp:0, gc:4 },
  { nome:"Jhon Ospina (COL)",          jogos:1, primeiro:{data:"06/05/2026", placar:"Vasco 2 x 1 Audax italiano"},ultimo:{data:"06/05/2026", placar:"Vasco 2 x 1 Audax italiano"},v:1, e:0, d:0, gp:2, gc:1 },
  { nome:"Jesús Valenzuela",           jogos:1, primeiro:{data:"30/04/2026", placar:"Vasco 3 x 0 Olimpia"},       ultimo:{data:"30/04/2026", placar:"Vasco 3 x 0 Olimpia"},     v:1, e:0, d:0, gp:3, gc:0 },
  { nome:"Hernán Heras",               jogos:1, primeiro:{data:"14/04/2026", placar:"Vasco 1 x 2 Audax italiano"},ultimo:{data:"14/04/2026", placar:"Vasco 1 x 2 Audax italiano"},v:0, e:0, d:1, gp:1, gc:2 },
  { nome:"Germán Arredondo",           jogos:1, primeiro:{data:"08/07/2001", placar:"Vasco 3 x 1 León"},          ultimo:{data:"08/07/2001", placar:"Vasco 3 x 1 León"},        v:1, e:0, d:0, gp:3, gc:1 },
  { nome:"Eduardo Brizio Carter",      jogos:1, primeiro:{data:"10/07/2001", placar:"Vasco 2 x 2 Tigres"},        ultimo:{data:"10/07/2001", placar:"Vasco 2 x 2 Tigres"},      v:0, e:1, d:0, gp:2, gc:2 },
  { nome:"Carlos Bentancur (COL)",     jogos:1, primeiro:{data:"07/04/2026", placar:"Vasco 0 x 0 Barracas Central"}, ultimo:{data:"07/04/2026", placar:"Vasco 0 x 0 Barracas Central"}, v:0, e:1, d:0, gp:0, gc:0 },
  { nome:"Braulio da Silva Machado",   jogos:1, primeiro:{data:"13/05/2026", placar:"Vasco 2 x 2 Paysandu-PA"},   ultimo:{data:"13/05/2026", placar:"Vasco 2 x 2 Paysandu-PA"}, v:0, e:1, d:0, gp:2, gc:2 },
];

// jogos apitados por árbitro
window.JOGOS_POR_ARBITRO = {
  "Ramon Abatti Abel": [
    { data:"01/04/2026", local:"fora", competicao:"Campeonato Brasileiro Série A", adv:"Coritiba-PR", res:"E", placar:"Vasco 1 x 1 Coritiba-PR" },
    { data:"21/04/2026", local:"fora", competicao:"Copa do Brasil",                adv:"Paysandu-PA", res:"V", placar:"Vasco 2 x 0 Paysandu-PA" },
  ],
  "Davi de Oliveira Lacerda": [
    { data:"22/03/2026", local:"casa", competicao:"Campeonato Brasileiro Série A", adv:"Grêmio-RS",   res:"V", placar:"Vasco 2 x 1 Grêmio-RS" },
    { data:"26/04/2026", local:"fora", competicao:"Campeonato Brasileiro Série A", adv:"Corinthians", res:"D", placar:"Vasco 0 x 1 Corinthians" },
  ],
  // demais árbitros — só 1 jogo cada, derivado de "primeiro" e "ultimo"
};

window.AUXILIARES_ARBITRAGEM = window.AUXILIARES_ARBITRAGEM || [];
window.JOGOS_POR_AUXILIAR = window.JOGOS_POR_AUXILIAR || {};
window.VARS_ARBITRAGEM = window.VARS_ARBITRAGEM || [];
window.JOGOS_POR_VAR = window.JOGOS_POR_VAR || {};
window.COMBINACOES_ARBITRAGEM = window.COMBINACOES_ARBITRAGEM || [];
window.JOGOS_POR_COMBINACAO_ARBITRAGEM = window.JOGOS_POR_COMBINACAO_ARBITRAGEM || {};
