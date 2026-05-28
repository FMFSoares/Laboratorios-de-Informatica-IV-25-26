// ============================================================
// DLMCare — Relatório LI4 2025/2026
// Grupo 35 — Universidade do Minho
// ============================================================

#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 3cm, right: 2.5cm),
  numbering: "1",
  number-align: center + bottom,
)
#set text(size: 11pt, lang: "pt")
#set par(justify: true, leading: 0.65em)

// Heading styles
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  v(1.5em)
  block(
    below: 0.6em,
    text(size: 17pt, weight: "bold", it.body),
  )
  line(length: 100%, stroke: 0.8pt)
  v(0.3em)
}
#show heading.where(level: 2): it => {
  v(1.2em)
  block(below: 0.4em, text(size: 13pt, weight: "bold", it.body))
}
#show heading.where(level: 3): it => {
  v(0.9em)
  block(below: 0.3em, text(size: 11.5pt, weight: "bold", it.body))
}
#show heading.where(level: 4): it => {
  v(0.7em)
  block(below: 0.25em, text(size: 11pt, weight: "bold", style: "italic", it.body))
}

// Custom functions
#let prompt-box(body) = block(
  fill: rgb("#eef4ff"),
  stroke: (left: 3pt + rgb("#2255aa")),
  inset: (left: 12pt, right: 10pt, top: 9pt, bottom: 9pt),
  width: 100%,
  radius: 2pt,
  breakable: true,
  body,
)

#let diagrama(legenda) = block(
  stroke: (paint: luma(150), dash: "dashed"),
  inset: 25pt,
  width: 100%,
  radius: 4pt,
  fill: luma(248),
)[#align(center)[#text(style: "italic", fill: luma(100))[\[ #legenda \]]]]

// Architecture layer box: arch-box(fill, accent, title, tech, body)
#let arch-box(fill-color, accent-color, title, tech, body) = block(
  fill: fill-color,
  stroke: (left: 3pt + accent-color),
  inset: (left: 14pt, right: 12pt, top: 10pt, bottom: 10pt),
  width: 100%,
  radius: 3pt,
)[
  #text(weight: "bold", size: 11pt)[#title]
  #h(0.5em)
  #text(size: 9pt, fill: luma(80))[#tech]
  #v(4pt)
  #body
]

// Shaded table header helper — use fill: on table.header rows
#let th-fill = rgb("#dce8ff")
#let tr-fill = rgb("#f7faff")

// ============================================================
// TITLE PAGE
// ============================================================
#align(center)[
  #v(3cm)
  #text(size: 14pt, weight: "bold")[Universidade do Minho] \
  #text(size: 13pt)[Escola de Engenharia]

  #v(2.5cm)
  #text(size: 16pt, weight: "bold")[Laboratórios de Informática IV 2025/2026]

  #v(1cm)
  #text(size: 13pt)[Trabalho Prático — Grupo 35]

  #v(4cm)
  #image("images/foto_grupo.png", width: 80%)

  #v(2cm)
  #align(left)[
    #text(size: 11pt)[
      Francisco Miguel Fernandes Soares (A106901) \
      David Lopes Machado (A107325) \
      Pedro Ribeiro Ferreira (A107369) \
      Rodrigo de Sousa Campos Pacheco da Rocha (A107335)
    ]
  ]
]

#pagebreak()

// ============================================================
// ÍNDICE
// ============================================================

#outline(
  title: "Índice",
  depth: 4,
  indent: 1.5em,
)

// ============================================================
// CAPÍTULO 1
// ============================================================
= Capítulo 1 — Conceção e Engenharia de Requisitos Assistida por LLM

== 1. Definição do Sistema

=== 1.1 Contextualização

A faísca que deu origem à DLMCare não surgiu numa sala de reuniões, mas sim na rotina acelerada e, por vezes, caótica da mobilidade urbana portuguesa. David Lopes Machado, um técnico de eletromecânica apaixonado por soluções de transporte sustentáveis, usava a sua própria trotinete elétrica diariamente para fugir ao trânsito.

Tudo começou quando a sua trotinete avariou. Ao procurar uma solução, David deparou-se com um mercado incipiente e frustrante: as poucas oficinas existentes demoravam semanas a dar resposta, não tinham peças de substituição e, muitas vezes, devolviam os equipamentos com problemas mal resolvidos. Foi então que decidiu deitar mãos à obra e consertar o veículo na sua própria garagem. O que começou como uma necessidade pessoal rapidamente se transformou num "boca a boca" entre amigos e colegas que partilhavam da mesma dor. Numa questão de meses, a garagem de David estava repleta de trotinetes à espera de reparação.

Foi nesse momento de rutura — entre o espaço exíguo da sua casa e a procura avassaladora — que o "clique" empresarial aconteceu. David percebeu que a micromobilidade não era apenas uma moda passageira, mas o futuro do planeamento urbano. As trotinetes multiplicavam-se nas ruas, mas a infraestrutura de suporte era praticamente inexistente. Havia ali uma lacuna de mercado gritante e uma oportunidade de negócio clara.

Com as economias que juntou e um plano de negócios focado na rapidez e na transparência, David deu o salto. Nasceu assim, oficialmente, a DLMCare. Para garantir visibilidade e conveniência, escolheu uma localização estratégica, abrindo a loja principal na Avenida Almirante Reis, n.º 74B, em Lisboa — uma das artérias com maior fluxo de ciclovias e utilizadores de mobilidade suave da capital.

Rapidamente, David percebeu que não podia fazer tudo sozinho. Para que ele se pudesse focar na expansão e nos casos mais complexos, montou a sua primeira equipa de confiança:

- *José Barros (Gerente de Loja):* O maestro dos bastidores e o guardião do stock. Com um olho clínico para a logística e um talento natural para otimizar processos, o José atua como o motor invisível da oficina. É ele a ponte entre a receção da Inês e as bancadas do Tiago e do Ruca, garantindo que nunca falta um controlador ou uma câmara de ar no momento crítico. Negoceia ao cêntimo com os fornecedores e certifica-se de que a operação diária funciona como um relógio suíço, protegendo as finanças da loja e libertando o David para expandir a marca.

- *Inês Carvalho (Rececionista):* A primeira cara da DLMCare. Com uma paciência inesgotável e um talento natural para a organização, a Inês ficou encarregue de domar o caos diário, atender e manter os clientes informados.

- *Tiago Mendes (Mecânico Especialista em Eletrónica):* O "MacGyver" das baterias e das motherboards. O Tiago foi contratado para diagnosticar as falhas elétricas mais crónicas que a maioria das oficinas dava como perda total.

- *João "Ruca" Silva (Mecânico de Estrutura e Hidráulica):* Especialista em travões, afinações de chassis e pneus. O Ruca garante que todas as trotinetes saem da oficina não só a funcionar, mas seguras para o asfalto.

O método DLMCare foi um sucesso tão estrondoso que, em menos de dois anos, começaram a receber clientes de fora da Grande Lisboa. Iniciou-se assim o plano de expansão, com duas novas filiais estratégicas:

- *DLMCare Porto:* Localizada na movimentada Rua de Júlio Dinis, perto da zona da Boavista, para captar o intenso tráfego universitário e de jovens profissionais. Esta loja ficou a cargo de Miguel Torres, um gestor de loja com mão firme e experiência em logística.

- *DLMCare Braga:* Situada na Avenida da Liberdade, mesmo no coração da cidade, respondendo à crescente adesão das cidades do Minho à micromobilidade. A gerência foi entregue a Sofia Almeida, cuja eficiência no atendimento ao cliente espelha o trabalho da Inês em Lisboa.

Hoje, a DLMCare já não é apenas uma oficina de bairro; é uma cadeia de referência na reparação de trotinetes elétricas. No entanto, gerir o stock, os clientes e a faturação de três lojas movimentadas em cidades diferentes apenas com folhas de Excel e telefonemas revelou-se o próximo grande desafio do David.

#prompt-box[
  *Prompt*

  Contexto Inicial: Atua como um Analista de Requisitos com talento para storytelling empresarial. Estou a desenvolver um sistema para a gestão de uma oficina de trotinetes (DLMCare). Cria a história do fundador, David Lopes Machado. Conta como ele começou, descreve o momento em que percebe a oportunidade de negócio, relata a abertura da sua oficina oficial "DLMCare" (com morada realista), menciona a contratação dos primeiros funcionários. Objetivo: texto fluido, realista e com um tom narrativo pessoal semelhante a um caso de estudo de empreendedorismo.

  #v(6pt)
  *Análise Crítica*

  Ao analisar a resposta à prompt ficámos bastante satisfeitos, contudo pedimos para adicionar mais algumas lojas noutras cidades e para acrescentar um gestor de loja à inicial, pois achamos que apenas uma loja era demasiado pouco e fazia sentido até a primeira loja ter um gerente.

  #v(6pt)
  *Modelo:* Gemini
]

=== 1.2 Motivação

A expansão da DLMCare para o Porto e Braga foi um marco de sucesso, mas gerir três lojas movimentadas com os processos manuais da loja original transformou o sonho de David Lopes Machado num verdadeiro pesadelo logístico. O modelo de negócio estava a escalar muito mais rápido do que a sua infraestrutura de gestão, e as fissuras começaram a expor-se sob a pressão de centenas de clientes semanais.

*O Caos Descentralizado e as Falhas de Comunicação*

O sistema inicial baseado em cadernos, folhas impressas e post-its já era mau numa só loja; em três, tornou-se insustentável. O dia a dia das equipas transformou-se numa gestão de crises constante através de grupos de WhatsApp caóticos:

- *Perda de Histórico entre Lojas:* Um cliente que comprou ou reparou a sua trotinete em Lisboa (sendo atendido pela Inês), e que mais tarde se mudou para Braga, chegava à loja da Sofia e era tratado como um cliente desconhecido. Não havia histórico de reparações, garantias ou intervenções anteriores.

- *Telefone Estragado:* Quando um cliente ligava para a linha geral a perguntar pelo estado da sua trotinete, a pessoa que atendia tinha frequentemente de enviar mensagens para o grupo de WhatsApp "Mecânicos DLMCare" a perguntar "Malta, de quem é a Ninebot amarela do Sr. Costa? Está em Lisboa ou no Porto?". As respostas demoravam horas, gerando frustração do outro lado da linha.

- *Ordens de Serviço Perdidas:* Folhas de obra em papel continuavam a sujar-se de óleo ou a perder-se nas bancadas. Para piorar, o "padrão DLMCare" começou a falhar: o Miguel no Porto descrevia as avarias de uma forma, enquanto a equipa de Lisboa usava outra terminologia, dificultando a análise dos problemas mais comuns.

*O Pesadelo Logístico das Peças e o Ponto Cego Financeiro*

Na retaguarda, a ausência de um sistema em rede estava a custar muito dinheiro à empresa. O armazém operava com base em folhas de Excel partilhadas que raramente eram atualizadas em tempo real:

- *Stock Desequilibrado e Imobilização:* Faltavam frequentemente peças críticas em Lisboa (como controladores Xiaomi), levando o Tiago a imobilizar trotinetes durante semanas à espera de uma encomenda do fornecedor. O absurdo? O Miguel, no Porto, tinha cinco desses controladores a ganhar pó na prateleira, mas como ninguém atualizava o Excel, o David gastava dinheiro em novas encomendas desnecessárias em vez de transferir o stock internamente.

- *Gestão Financeira por "Palpite":* No final do mês, o David passava noites em claro a tentar consolidar dados de três lojas diferentes. Era impossível ter uma visão clara de qual filial era mais rentável, comparar a eficiência dos mecânicos de Braga com os de Lisboa, ou sequer calcular o lucro líquido real da rede após subtrair os custos das transferências de peças e a mão de obra.

*O Ponto de Viragem*

A gota de água surgiu quando a DLMCare começou a receber avaliações negativas cruzadas no Google. Clientes queixavam-se de que a experiência no Porto não tinha nada a ver com a rapidez prometida pela marca em Lisboa, ou que as trotinetes ficavam retidas um mês à espera de peças comuns.

O David percebeu, com grande clareza, que o problema não estava na qualidade das suas equipas — a Inês, o Miguel, a Sofia e os mecânicos trabalhavam até à exaustão —, mas sim na ausência de um sistema central. A marca estava a sangrar dinheiro em peças duplicadas e a perder a confiança dos clientes.

Consciente de que soluções de mercado genéricas não suportavam a dinâmica ágil da micromobilidade distribuída, o David tomou uma decisão estratégica. Contactou um grupo talentoso de estudantes de Engenharia Informática, lançando-lhes um desafio: desenvolver um sistema de gestão centralizado. O sistema DLMCare teria de unificar as três lojas em tempo real, acabar com o caos do papel, automatizar as transferências de inventário e devolver ao David o controlo total sobre o império que estava a construir.

#prompt-box[
  *Prompt*

  Continua a narrativa: tendo em conta o sucesso e o volume massivo de clientes, descreve os problemas operacionais graves que começaram a surgir, usando exemplos práticos e caóticos do dia-a-dia. Menciona o caos de ter informações importantes em papel e o descontrolo de peças e custos. Conclui com o David a perceber que a desorganização está a prejudicar a reputação e a fazê-lo perder dinheiro, decidindo recorrer a um grupo de estudantes de Engenharia Informática.

  #v(6pt)
  *Análise Crítica*

  Esta prompt foi enviada logo a seguir à contextualização, e após reflexão em grupo decidimos aceitar o output obtido, considerando que a motivação estava bem estruturada.

  #v(6pt)
  *Modelo:* Gemini
]

=== 1.3 Objetivos

Na primeira reunião de levantamento de requisitos entre o David, os gerentes das filiais e o grupo de estudantes de Engenharia Informática, o caos operacional foi literalmente colocado em cima da mesa (juntamente com dezenas de folhas de obra manchadas de óleo e cadernos desorganizados). Através de um mapeamento exaustivo dos processos atuais de Lisboa, Porto e Braga, a equipa técnica traduziu as frustrações do negócio em metas funcionais e arquitetónicas claras. Ficou imediatamente decidido que a solução não poderia ser local; teria de ser uma plataforma para sincronizar toda a operação. Após esta sessão de alinhamento, definiram-se os seguintes objetivos técnicos e de negócio que o sistema DLMCare terá obrigatoriamente de cumprir:

- *Registo Centralizado de Clientes e Equipamentos:* Estabelecer uma base de dados relacional para o cadastro de clientes e do respetivo parque de trotinetes (associando marca, modelo e número de série a cada proprietário). O objetivo é garantir a identificação unívoca dos equipamentos, permitindo uma consulta rápida do histórico e eliminando o risco de trocas ou perda de dados.

- *Gestão Integral de Ordens de Serviço (OS):* Implementar um módulo central para a criação e monitorização do ciclo de vida das OS. Este módulo deve permitir registar o diagnóstico inicial, atualizar o estado da reparação em tempo real, registar os tempos de mão de obra despendidos por cada mecânico e associar as peças consumidas à intervenção.

- *Controlo Rigoroso e Preventivo de Inventário:* Desenvolver um mecanismo de gestão de stock dinâmico, intimamente ligado às OS. O sistema deve abater automaticamente as peças utilizadas no inventário e acionar alertas automáticos de stock mínimo para componentes críticos (baterias, pneus, pastilhas de travão, discos e controladores).

- *Cálculo Automático de Custos e Faturação:* Automatizar a componente transacional de cada reparação, cruzando o valor da mão de obra (preço do serviço) com o preço de venda das peças utilizadas, calculando automaticamente o valor final e permitindo a emissão da respetiva faturação.

- *Reporting Analítico e de Apoio à Decisão:* Incorporar um painel de controlo (dashboard) para extração de relatórios de gestão, incluindo métricas operacionais (volume de trotinetes reparadas por mês, tempos médios de reparação, rácios de eficiência por mecânico) e métricas financeiras (receitas brutas, despesas com peças, lucro líquido mensal).

#prompt-box[
  *Prompt*

  Foca-te agora nos Objetivos do sistema. Com base nos problemas relatados na secção anterior, redige os objetivos principais que o sistema DLMCare tem de cumprir para organizar a oficina, garantindo que incluis objetivos para: registo centralizado e consulta rápida de clientes e trotinetes; criação e acompanhamento de OS; gestão rigorosa do stock de peças; cálculo automático de custos e emissão de faturação; geração de relatórios operacionais e financeiros. O tom deve ser puramente técnico e executivo.

  #v(6pt)
  *Análise Crítica*

  Com esta prompt obtivemos um output quase excelente, sendo apenas necessário pedir à LLM para acrescentar como se chegou a estes objetivos após a primeira reunião.

  #v(6pt)
  *Modelo:* Gemini
]

=== 1.4 Viabilidade

A decisão de investir no desenvolvimento e implementação do sistema DLMCare não é apenas uma atualização tecnológica; é um imperativo estratégico de sobrevivência e expansão. Quando analisamos as dores atuais do negócio (Secção 1.2) em contraponto com os objetivos traçados (Secção 1.3), torna-se evidente que o software proposto deixará rapidamente de ser um custo para se transformar num dos ativos mais rentáveis da empresa. A viabilidade deste projeto sustenta-se em três pilares fundamentais que garantem um Retorno sobre o Investimento (ROI) a muito curto prazo:

==== 1.4.1 Viabilidade Financeira

Atualmente, a DLMCare está a perder dinheiro diariamente devido a ineficiências que o sistema eliminará:

- *Otimização de Capital em Stock:* Ao implementar um inventário em rede, o David deixará de encomendar peças desnecessárias para Lisboa quando o Porto ou Braga têm excedentes. O fim das aquisições duplicadas e o alerta de ruturas de stock representam uma poupança de milhares de euros anuais.

- *Faturação Rigorosa:* Sem o registo manual em papel, nenhum serviço tabelado nem peça vendida ficará por cobrar, e nenhuma peça aplicada será esquecida no orçamento final. O cálculo automático garante a maximização da margem de lucro em cada intervenção.

==== 1.4.2 Viabilidade Operacional

O tempo que a equipa perde atualmente a gerir o caos é tempo roubado à produção.

- *Fim do "Ruído" na Comunicação:* A substituição dos grupos de WhatsApp por um workflow centralizado e acessível devolverá dezenas de horas semanais aos gerentes, rececionistas e mecânicos. A informação sobre o estado de qualquer trotinete, em qualquer loja, estará à distância de um clique.

- *Padronização do Método DLMCare:* Com processos idênticos impostos pelo sistema em todas as filiais, a formação de novos colaboradores torna-se mais rápida e barata, permitindo que a empresa abra novas lojas no futuro (como em Coimbra ou Faro) com uma infraestrutura de gestão já testada e pronta a escalar ("plug and play").

==== 1.4.3 Viabilidade Comercial e Reputacional

A reputação da marca, outrora o seu maior motor de aquisição de clientes através do "boca a boca", está atualmente ameaçada por atrasos e falhas de comunicação.

- *Experiência de Excelência ao Cliente:* Com o acesso rápido ao histórico do cliente — independentemente da loja a que este se dirija — e a capacidade de dar respostas exatas e imediatas sobre o estado da reparação, a DLMCare recuperará a sua imagem de profissionalismo. A redução drástica dos tempos de imobilização das trotinetes traduzir-se-á num aumento direto da satisfação, gerando avaliações positivas no Google e fomentando a fidelização.

Em suma, o sistema DLMCare é altamente viável e crítico. O custo de desenvolvimento será rapidamente amortizado pelo aumento da capacidade de resposta da oficina, pela eliminação de desperdícios no inventário e pela recuperação de receitas perdidas por falhas de faturação.

#prompt-box[
  *Prompt*

  Com base nos problemas apresentados na motivação e nos objetivos do sistema, escreve a justificação de viabilidade do sistema DLMCare. O tom deve ser de um business case convincente, mostrando que o software é um investimento altamente rentável.

  #v(6pt)
  *Análise Crítica*

  Analisando o output obtido, como grupo chegamos à conclusão que era o que esperávamos para este ponto do relatório e decidimos não fazer alterações.

  #v(6pt)
  *Modelo:* Gemini
]

=== 1.5 Restrições do Sistema

Para garantir que o desenvolvimento do sistema DLMCare seja exequível e alinhado com a realidade da infraestrutura e regulamentação vigentes, é imperativo definir as restrições arquiteturais, operacionais e legais que condicionarão o projeto.

==== 1.5.1 Restrições Legais e de Negócio

- *Conformidade com o RGPD:* O sistema armazenará dados pessoais de clientes. É obrigatório implementar mecanismos de consentimento, anonimização e a funcionalidade de "direito ao esquecimento".

- *Certificação de Faturação (Autoridade Tributária):* O módulo financeiro terá de estar em conformidade com as exigências da AT em Portugal, ou integrar-se com um software de faturação já certificado. A fatura ao cliente usa preços de serviço e preços de venda; os custos de compra são internos.

- *Fronteira do Sistema (Gestão de Compras Externa):* O sistema DLMCare não efetua a gestão de encomendas a fornecedores. A responsabilidade do software limita-se exclusivamente ao registo de entrada (receção) do material físico no inventário da loja.

==== 1.5.2 Restrições Operacionais

- *Acessibilidade em Ambiente de Oficina:* A interface dos mecânicos tem de ser otimizada para utilização em tablets, com botões dimensionados para toque por utilizadores que frequentemente usam luvas, exigindo o mínimo de interações possível para alterar o estado de uma OS.

- *Disponibilidade do Sistema:* O sistema deve garantir um uptime de 99,9% durante o horário de funcionamento das oficinas (segunda a sábado, das 08h00 às 20h00).

- *Curva de Aprendizagem:* O sistema deve ser suficientemente intuitivo para que um novo colaborador consiga operar as funcionalidades básicas com uma formação não superior a 4 horas.

==== 1.5.3 Restrições Técnicas

- *Arquitetura Baseada na Cloud:* O sistema não poderá ter instalação local. Terá de ser desenvolvido como uma aplicação Web alojada na cloud, garantindo sincronização em tempo real entre Lisboa, Porto e Braga.

- *Controlo de Concorrência e Transações (ACID):* A base de dados relacional deve gerir de forma robusta a concorrência. Se dois rececionistas tentarem reservar a última peça em simultâneo, o sistema tem de garantir a integridade transacional.

- *Design Responsivo:* O frontend deve adaptar-se a desktops (receção e administração), tablets (bancadas de trabalho) e smartphones (consultas rápidas dos gerentes).

- *Políticas de Backup:* O sistema deverá executar cópias de segurança automáticas e incrementais da base de dados diariamente, com redundância geográfica.

#prompt-box[
  *Prompt*

  Foca-te agora nas Restrições do Sistema. Redige as restrições que vão limitar ou condicionar o desenvolvimento e a operação do sistema DLMCare, dividindo-as em três categorias: Legais/Negócio, Operacionais e Técnicas. O tom deve ser formal e de engenharia, definindo limites claros para a arquitetura do software.

  #v(6pt)
  *Análise Crítica*

  O output gerado foi inicialmente o que o nosso grupo esperava obter. Contudo, achamos oportuno adicionar que o sistema não efetua diretamente a gestão de encomendas com os fornecedores, devidamente adicionado nas restrições legais e de negócio.

  #v(6pt)
  *Modelo:* Gemini
]

=== 1.6 Recursos e Equipa de Trabalho

Para garantir o sucesso na conceção e implementação do novo sistema de informação centralizado da DLMCare, foram mobilizados recursos em três eixos fundamentais:

==== 1.6.1 Recursos Humanos

- *Equipa de Desenvolvimento de Software:* Uma equipa externa de consultoria e engenharia informática responsável por todo o ciclo de vida do software: levantamento de requisitos, arquitetura de dados, programação, testes e implementação final.

- *Gestão de Topo e Operações (DLMCare):* Liderada por David Lopes Machado (na qualidade de Product Owner e CEO), com apoio tático direto de José Barros, Inês Carvalho, Miguel Torres e Sofia Almeida.

- *Equipa de Validação Técnica:* Composta por Tiago Mendes e João "Ruca" Silva, cujo papel é garantir que as interfaces do chão de oficina são ergonómicas e eficientes.

==== 1.6.2 Recursos Materiais e Tecnológicos

- *Infraestrutura Cloud e Servidores:* Alojamento da aplicação e da base de dados centralizada em serviços Cloud, garantindo alta disponibilidade e sincronização em tempo real.

- *Hardware Operacional (Lojas):* Terminais de Ponto de Venda (POS) atualizados para a receção e tablets para as bancadas da oficina.

- *Stack Tecnológico de Desenvolvimento:* Ambientes de desenvolvimento integrado, sistemas de gestão de bases de dados relacionais e ferramentas de gestão ágil de projeto.

==== 1.6.3 Recursos Financeiros

- *Orçamento de Transição Digital:* Capital de investimento alocado pela administração da DLMCare, cobrindo os custos de desenvolvimento do software, a modernização do hardware das três lojas e o licenciamento contínuo das plataformas de alojamento.

=== 1.7 Identificação e Análise dos Stakeholders

O ecossistema da DLMCare é composto por diversas partes interessadas. A correta identificação dos stakeholders e a compreensão das suas necessidades é crucial para garantir que o sistema entrega valor real ao negócio.

*David Lopes Machado (Fundador e CEO)* — Promotor do projeto e principal decisor estratégico. Interesses: visão em tempo real da rede de lojas, métricas de rentabilidade exatas, eliminação de custos com peças duplicadas.

*Gestores de Loja e Apoio ao Cliente (José Barros, Inês Carvalho, Miguel Torres, Sofia Almeida)* — Utilizadores primários da frente de loja. Interesses: sistema rápido que centralize o histórico do cliente de forma unívoca, criação de OS sem redundância de dados, respostas claras sobre o estado das reparações.

*Mecânicos e Especialistas Técnicos (Tiago Mendes, João "Ruca" Silva e equipas regionais)* — Utilizadores operacionais. Interesses: interface simplificada adaptada a ecrãs de oficina, associação imediata das peças à OS para abate automático de stock, registo fluido de tempos de mão de obra.

*Clientes Finais (Proprietários de Trotinetes)* — Beneficiários diretos do serviço. Interesses: total transparência nos orçamentos, celeridade na entrega dos equipamentos, comunicações atempadas sobre o estado da trotinete.

*Fornecedores de Peças e Componentes* — Parceiros de negócio externos. Interesses: receber pedidos de encomenda de forma estruturada e atempada, impulsionados pelos alertas automáticos de quebra de stock mínimo.

*Equipa de Desenvolvimento de Software* — Entidade tecnológica executante. Interesses: entregar uma solução robusta, escalável e segura dentro do prazo e orçamento acordados.

=== 1.8 Planeamento e Cronograma do Projeto

O desenvolvimento do sistema DLMCare segue uma metodologia sequencial e incremental. O cronograma contempla as quatro etapas principais: Engenharia de Requisitos, Arquitetura e Design, Implementação e Avaliação de Qualidade, culminando na entrega final em maio de 2026.

#figure(
  image("images/gantt.png", width: 100%),
  caption: [Diagrama de Gantt — Cronograma do Projeto DLMCare],
)

== 2. Levantamento e Análise de Requisitos

=== 2.1 Método de Levantamento e de Análise de Requisitos Adotado

O levantamento de requisitos foi conduzido pelos analistas Francisco Soares e Rodrigo Rocha com o objetivo de identificar e estruturar as necessidades funcionais e informacionais da cadeia de oficinas DLMCare. O intuito principal foi apoiar o desenvolvimento de um sistema cloud centralizado para a gestão de clientes, frota de trotinetes, ordens de serviço e controlo de inventário em ambiente multi-loja. Para garantir que a solução a desenvolver estivesse perfeitamente alinhada com as reais necessidades operacionais e de expansão da DLMCare, foi adotada uma abordagem mista, utilizando várias técnicas de engenharia de requisitos:

- *Entrevistas:* Numa primeira fase, foram conduzidas entrevistas semiestruturadas com os principais stakeholders da empresa. Isto incluiu o CEO e fundador (David Machado), os gerentes de loja, os mecânicos e os clientes finais, permitindo mapear o fluxo de trabalho atual e os estrangulamentos na comunicação entre filiais.

- *Questionários:* Para obter dados quantitativos e uma visão mais abrangente do ecossistema do negócio, foram aplicados questionários em duas frentes: aos funcionários, com o objetivo de quantificar o tempo perdido em tarefas manuais e na procura de peças; e aos clientes finais, visando compreender as suas principais dores, expectativas quanto aos tempos de reparação e a necessidade de transparência no estado das suas trotinetes.

==== 2.1.1 Realização de Entrevistas

*Stakeholder 1: David Lopes Machado (CEO / Product Owner)*

Tom: Visão estratégica, focado na rentabilidade, expansão e eliminação de desperdícios operacionais.

*P1:* "David, como CEO, que tipo de dados precisas de ver nos relatórios financeiros e técnicos?"

R: "Preciso de um dashboard analítico que me tire da 'gestão por palpite'. A nível técnico, quero ver o volume de trotinetes reparadas por mês, os tempos médios de reparação e os rácios de eficiência de cada mecânico. A nível financeiro, é crítico ter o apuramento exato do lucro líquido mensal, a análise de receitas brutas e as despesas com a aquisição de peças a fornecedores."

*P2:* "Como queres que o sistema faça a faturação dos serviços prestados e das peças comercializadas?"

R: "Tem de ser um processo 100% automático e transparente, sem espaço para o esquecimento humano que temos tido com o papel. O sistema tem de cruzar o valor tabelado do tipo de serviço com o custo de venda exato das peças que foram abatidas do inventário. O sistema calcula o valor final e emite a faturação detalhada de serviços e artigos, garantindo que maximizamos a margem de lucro e não deixamos dinheiro na mesa."

*P3:* "Quais são as principais falhas que sentes na operação atual?"

R: "Temos três cancros: (1) Caos Descentralizado — falta de histórico de clientes entre lojas; (2) Gestão de Stock Cega — encomendar controladores para Lisboa quando o Porto tem excedentes; (3) Falhas de Comunicação — apoio ao cliente dependente de grupos de WhatsApp."

*P4:* "Tens alguma preocupação com o controlo interno e a segurança?"

R: "Totalmente. Em primeiro lugar, a nossa realidade operacional não é igual em todo o lado; os custos no Porto não são os mesmos de Braga, por isso preciso de conseguir parametrizar o custo dos serviços para cada loja de forma independente. Em segundo lugar, para proteger o nosso dinheiro, exijo um registo de auditoria rigoroso. O José (nosso gerente) precisa de saber exatamente quem, quando e a que horas alterou manualmente o stock de uma peça para evitar 'desvios' misteriosos. E claro, como vamos ter dados sensíveis de clientes e faturação na cloud, a segurança tem de ser máxima, com as passwords da equipa fortemente encriptadas."

---

*Stakeholder 2: Gestores de Loja* (interlocutora: Sofia Almeida)

Tom: Organizada, focada no atendimento rápido ao cliente e exausta do caos dos grupos de WhatsApp.

*P1:* "Que informações exatas precisam para fazer o registo do cliente e do equipamento?"

R: "Precisamos de uma base de dados relacional que nos permita fazer um cadastro único. Para o equipamento, precisamos obrigatoriamente de associar a marca, o modelo e o número de série ao perfil do proprietário, garantindo identificação unívoca em qualquer loja da rede."

*P2:* "Como é que gostariam que fosse o processo de criação de ordens de serviço?"

R: "Queremos um módulo central onde a criação da OS seja rápida e sem redundância de dados. O sistema deve impor uma terminologia padronizada — atualmente o Porto descreve uma avaria de uma maneira e Lisboa de outra."

*P3:* "Como é que o sistema vos poderia facilitar a vida na atualização do estado da reparação?"

R: "Atualmente é um pesadelo: dependemos de folhas de papel que se sujam na oficina e de mensagens no grupo 'Mecânicos DLMCare' que demoram horas a ser respondidas. O novo sistema vai salvar-nos a vida se permitir atualizar o estado da reparação em tempo real com um clique (ex: 'Em Avaliação', 'Aguardar Peças', 'Em Reparação', 'Concluído'). Assim, quando o cliente liga, a resposta está logo ali no ecrã."

*P4:* "Como vês a questão da privacidade e segurança no dia a dia?"

R: "Temos de cumprir a lei do RGPD à risca para evitar problemas. No momento de registar um cliente novo no sistema, precisamos de uma forma clara (uma checkbox, por exemplo) de registar o consentimento explícito para o tratamento dos dados pessoais dele. Outra coisa prática: como partilhamos terminais e às vezes temos de ir a correr à oficina falar com o Ruca, o sistema devia terminar a sessão automaticamente ao fim de algum tempo de inatividade, tipo 60 minutos. Assim garantimos que não deixamos os dados dos clientes ou as faturas expostos no ecrã."

---

*Stakeholder 3: Mecânicos Especializados* (interlocutor: João "Ruca" Silva)

Tom: Prático, direto, focado na parte técnica e sem paciência para burocracias de papel.

*P1:* "Como é que o sistema deve ser desenhado para facilitar o registo do diagnóstico?"

R: "Tem de ser desenhado para quem está 'com a mão na massa'. Precisamos de uma interface simplificada, limpa e ergonómica a correr em tablets nas bancadas da oficina."

*P2:* "Como preferem registar as peças utilizadas, os tempos de reparação e os estados do serviço?"

R: "De forma fluida. O ideal é, no próprio tablet da bancada, irmos picando ou selecionando as peças que estamos a usar na trotinete para que elas fiquem logo associadas à OS. O registo de tempos de mão de obra tem de ser simples (talvez um botão de start/stop na intervenção) e a mudança de estado (ex: 'Em Reparação' para 'Concluído') deve estar à distância de um toque no ecrã. Fim das folhas de obra em papel!"

*P3:* "De que forma querem ser avisados de que uma peça está a acabar?"

R: "Nós não queremos andar a avisar ninguém; o sistema é que tem de trabalhar por nós. Ao associarmos uma peça à reparação no tablet, o sistema deve abater esse material do inventário de forma dinâmica. Para as peças críticas (baterias, pneus, controladores, pastilhas), o sistema deve ter alertas automáticos de stock mínimo, para que o David ou os gerentes saibam que têm de encomendar (ou transferir do Porto) antes de nós ficarmos com trotinetes paradas semanas à espera de material."

---

*Stakeholder 4: Clientes Finais* (interlocutor: Sr. Costa)

Tom: Exigente, procura conveniência, transparência e confiança no serviço pago.

*P1:* "De que forma gostava de ser notificado sobre a evolução do estado do serviço?"

R: "Gostava de receber comunicações atempadas, exatas e automáticas (por SMS ou email, por exemplo) sempre que o estado da minha trotinete muda (ex: quando está a aguardar peças ou quando está finalmente pronta a levantar). Não quero ter de ligar para a linha geral e ficar à espera que a rececionista vá tentar descobrir em que loja está a minha Ninebot amarela."

*P2:* "Que nível de detalhe gostava de ter sobre os custos na sua fatura?"

R: "Exijo total transparência. Quero que o orçamento e a fatura final mostrem claramente a separação entre o que estou a pagar em peças e o que estou a pagar em mão de obra especializada. Saber que não há peças esquecidas ou custos 'surpresa' dá-me segurança para voltar."

*P3:* "Seria útil ter acesso a um portal ou área de cliente para ver o histórico das intervenções?"

R: "Sem dúvida. Se eu consertei a trotinete em Lisboa o ano passado e agora me mudei para Braga, quero chegar à loja da Avenida da Liberdade e saber que eles reconhecem a minha trotinete, sabem exatamente o que foi trocado na última revisão e respeitam as garantias. Isso é a verdadeira experiência de excelência."

==== 2.1.2 Survey Quantitativo (Questionários)

Foram realizados dois questionários estruturados para validar a aceitação de novas funcionalidades e medir a dor operacional das equipas.

*A. Questionário para Clientes Finais (Foco: Experiência e Transparência)*

+ Numa escala de 1 a 5, quão importante seria receber um email automático assim que a sua trotinete estiver pronta para levantamento?
+ O facto de o seu histórico ser reconhecido em qualquer loja DLMCare aumentaria a sua fidelização à marca? (Escala 1-5)
+ Qual o principal motivo de insatisfação atual? ( ) Tempo de espera  ( ) Falta de comunicação  ( ) Erros no orçamento

*B. Questionário para Staff (Mecânicos e Rececionistas)*

+ Com que frequência o uso de grupos de WhatsApp causa confusão sobre o estado real de uma reparação? (Escala 1-5)
+ Quão confortável se sentiria a utilizar um tablet em vez de papel para registar peças e tempos de mão de obra? (Escala 1-5)
+ Quanto tempo gasta, em média, por dia a tentar decifrar folhas de obra manuscritas ou a procurar peças no Excel? ( ) \<30 min  ( ) 30--60 min  ( ) \>60 min
+ A interface do sistema deve permitir operações com apenas uma mão/toques rápidos? (Escala 1-5)
+ Qual a maior barreira para a eficiência hoje? ( ) Falta de peças em stock  ( ) Excesso de burocracia em papel  ( ) Falha na comunicação entre lojas

Para validar os requisitos e priorizar o MVP, foram simuladas respostas de 30 clientes e 12 elementos do staff operacional.

Relativamente aos clientes finais, a análise das 30 respostas simuladas revela uma forte necessidade de modernização e transparência. A esmagadora maioria, cerca de 90%, atribuiu a importância máxima à receção de notificações automáticas assim que a trotinete se encontra pronta para levantamento. Adicionalmente, 85% dos clientes confirmaram que o reconhecimento do seu histórico em qualquer loja aumentaria significativamente a sua fidelização à marca. Por fim, 70% apontaram a falta de comunicação e os erros nos orçamentos como as suas maiores queixas — validando a necessidade de faturação baseada em valores tabelados por tipo de serviço (serviço tabelado + peças vendidas ao preço de venda).

Relativamente ao staff, 75% indicam que o uso do WhatsApp gera confusão na comunicação, evidenciando a urgência de centralizar as OS. A transição digital é facilitada pelo facto de 83% se sentirem confortáveis a usar tablets (validando RNF02, RNF03 e RNF04). Em contrapartida, 67% perdem mais de 30 minutos diários a lidar com papel e Excel.

#prompt-box[
  *Prompt*

  Com base nos questionários já definidos para clientes e staff da DLMCare, simula resultados quantitativos plausíveis e escreve uma interpretação curta que permita justificar a prioridade das funcionalidades de notificações, interface em tablet e eliminação de papel/Excel.

  #v(6pt)
  *Análise Crítica*

  A resposta foi integrada porque a secção já tinha as perguntas do survey, mas não apresentava qualquer leitura quantitativa. A equipa validou os valores como dados simulados e não como resultados reais, usando-os apenas para reforçar a coerência entre a eliciação e os requisitos priorizados.

  #v(6pt)
  *Modelo:* ChatGPT
]

==== 2.1.3 Relatório de Análise de Artefatos Técnicos

Foi efetuada uma análise às ferramentas de suporte atuais — folhas de obra físicas e ficheiros Excel de inventário.

*Observações da Análise:*

- *Folhas de Obra (Papel):* A exposição a óleos e químicos de oficina torna os registos frequentemente ilegíveis.
- *Excel de Stock:* O ficheiro apresenta múltiplas versões e falta de integridade transacional, resultando em dados obsoletos sobre peças críticas.

*Dados Críticos Frequentemente em Falta/Ilegíveis:*

+ *Timestamp de Intervenção (Início/Fim):* Os mecânicos raramente registam a hora exata, levando a estimativas vagas de produtividade.
+ *Referência Exata da Peça:* A descrição manual (ex: "controlador") é ambígua, dificultando o abate correto no catálogo de stock centralizado.
+ *Preço de Venda da Peça:* O sistema deve guardar o preço de venda da peça no momento da aplicação, para que faturas antigas não sejam alteradas por mudanças de preço futuras.

#prompt-box[
  *Prompt*

  Contexto: Sou um Engenheiro de Requisitos a trabalhar no sistema DLMCare. Atualmente, temos apenas dados de reuniões qualitativas. Preciso de expandir a eliciação utilizando dois novos métodos: Survey Quantitativo e Análise de Artefatos. Gera: (1) questionários de 5 perguntas para Clientes e para Staff; (2) relatório de análise técnica às folhas de obra e Excel; (3) identificação de 3 campos de dados críticos frequentemente ilegíveis ou em falta. Apresenta os resultados de forma estruturada, pronta a inserir no relatório.

  #v(6pt)
  *Análise Crítica*

  A resposta foi bastante completa. Fizemos pequenas alterações em relação aos índices, e à parte final, onde a LLM enunciou requisitos levantados nestas interações — acreditamos ficar melhor junto do resto dos requisitos.

  #v(6pt)
  *Modelo:* Gemini-3
]

=== 2.2 User Stories

*Épico 1: Gestão de Clientes e Frente de Loja*

- *US01 — Registo Centralizado:* Como Gestor de Loja, quero registar o perfil de um cliente e a sua trotinete (marca, modelo e número de série), para que o seu histórico fique imediatamente acessível em qualquer loja da rede DLMCare. Critérios de aceitação: o sistema não deve permitir o registo de duas trotinetes com o mesmo número de série; deve ser possível pesquisar um cliente existente pelo NIF ou número de telemóvel antes de criar um novo registo, evitando duplicações.

- *US02 — Emissão de Fatura Automática:* Como Gestor de Loja, quero que o sistema calcule o valor final da OS (somando peças e mão de obra) com um clique, para que possa emitir uma fatura transparente e sem risco de esquecer a cobrança de material. Critérios de aceitação: a fatura gerada deve discriminar claramente as linhas de "Peças Aplicadas" e "Tipo de Serviço"; o valor da mão de obra deve ser calculado automaticamente com base no tempo registado pelo mecânico.

*Épico 2: Gestão de Oficina e Ordens de Serviço*

- *US03 — Atualização de Estado:* Como Mecânico, quero alterar o estado da reparação através do tablet da oficina, para que a receção saiba o ponto de situação em tempo real sem me ter de ir perguntar. Critérios de aceitação: interface responsiva e adaptada a ecrãs touch; alteração de estado refletida no sistema central em menos de 2 segundos.

- *US04 — Registo de Tempos:* Como Mecânico, quero usar um botão de start/stop na OS para registar o tempo que demorei na intervenção, para que as minhas horas produtivas sejam contabilizadas. Critérios de aceitação: o sistema deve acumular o tempo se a intervenção for pausada e retomada mais tarde.

*Épico 3: Gestão de Inventário*

- *US05 — Abate Automático de Stock:* Como Mecânico, quero selecionar e associar as peças que estou a usar diretamente à OS, para que estas sejam abatidas automaticamente do inventário da minha loja. Critérios de aceitação: o sistema deve impedir a seleção de uma peça se o stock virtual dessa loja for zero, emitindo um aviso de rutura.

- *US06 — Alertas de Stock Mínimo:* Como CEO/Gestor, quero receber um alerta automático quando o stock de uma peça crítica atingir o limite mínimo, para que possa encomendar ou transferir material antes de imobilizar trotinetes. Critérios de aceitação: limite mínimo parametrizável por loja e por tipo de peça; alerta visível no Dashboard principal.

*Épico 4: Relatórios e Apoio à Decisão*

- *US07 — Dashboard Analítico:* Como CEO, quero aceder a um dashboard com as métricas de lucro líquido, tempos médios de reparação e eficiência por mecânico, para que possa comparar a rentabilidade real entre as lojas. Critérios de aceitação: filtros por intervalo de datas e por loja; apenas utilizadores com perfil de "Administrador" têm acesso.

*Épico 5: Experiência do Cliente*

- *US08 — Notificações de Estado:* Como Cliente, quero receber uma notificação (email) sempre que a minha trotinete mudar de estado, para que não tenha de ligar para a linha geral a perguntar pelo ponto de situação. Critérios de aceitação: envio acionado automaticamente no momento em que o mecânico muda o estado no tablet.

=== 2.3 Especificação dos Requisitos Levantados

==== 2.3.1 Requisitos Funcionais (RF)

#table(
  columns: (3em, 7.5em, 1fr, 4.5em, 5em, 4.5em),
  align: (center, center, left, center, center, center),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header(
    [*Nr.*], [*Data e Hora*], [*Descrição*], [*Área*], [*Fonte*], [*Analista*]
  ),
  [RF01], [09/03/2026\ 14:30], [O sistema deve guardar os dados dos clientes e das suas trotinetes.], [Gestão de Clientes], [Sofia Almeida], [F. Soares],
  [RF02], [09/03/2026\ 14:35], [O sistema tem de registar a marca, modelo e número de série de cada trotinete.], [Gestão de Clientes], [Sofia Almeida], [F. Soares],
  [RF03], [09/03/2026\ 14:40], [O sistema deve permitir a criação de Ordens de Serviço (OS).], [Gestão de OS], [Sofia Almeida], [F. Soares],
  [RF04], [09/03/2026\ 14:45], [As OS têm de ter todas a mesma linguagem para não haver confusões entre as lojas.], [Gestão de OS], [Sofia Almeida], [F. Soares],
  [RF05], [09/03/2026\ 14:50], [O sistema tem de mostrar se a trotinete está em avaliação, pendente, em reparação ou concluída.], [Gestão de OS], [Sofia Almeida], [F. Soares],
  [RF06], [09/03/2026\ 10:15], [O David precisa de um dashboard analítico para ver o lucro.], [Relatórios], [D. L. Machado], [R. Rocha],
  [RF07], [09/03/2026\ 10:25], [O sistema tem de gerar relatórios com tempos registados, receitas de serviços e as peças vendidas.], [Relatórios], [D. L. Machado], [R. Rocha],
  [RF08], [09/03/2026\ 10:35], [O inventário tem de ser centralizado.], [Gestão de Stock], [D. L. Machado], [R. Rocha],
  [RF09], [10/03/2026\ 09:45], [O sistema tem de tirar as peças do stock automaticamente quando os mecânicos as usam.], [Gestão de Stock], [J. "Ruca" Silva], [F. Soares],
  [RF10], [10/03/2026\ 09:55], [O sistema tem de avisar o David quando há poucas peças críticas.], [Gestão de Stock], [J. "Ruca" Silva], [R. Rocha],
  [RF11], [10/03/2026\ 10:05], [O sistema tem de avisar quando as pastilhas e pneus estão a acabar.], [Gestão de Stock], [J. "Ruca" Silva], [F. Soares],
  [RF12], [09/03/2026\ 10:45], [O sistema tem de calcular o preço da reparação sozinho sem errar.], [Faturação], [D. L. Machado], [F. Soares],
  [RF13], [10/03/2026\ 16:15], [A fatura deve mostrar o serviço prestado separado das peças aplicadas pelo preço de venda.], [Faturação], [Sr. Costa], [R. Rocha],
  [RF14], [10/03/2026\ 16:25], [O sistema deve mandar um email ao cliente quando o estado da OS mudar.], [Comunicação], [Sr. Costa], [R. Rocha],
  [RF15], [11/03/2026\ 11:45], [O sistema deve registar automaticamente quem alterou o estado de uma OS e em que momento.], [Gestão de OS], [Questionário], [R. Rocha],
  [RF16], [11/03/2026\ 12:30], [O sistema deve suportar a aplicação de descontos comerciais (percentuais ou fixos) em campanhas de fidelização de clientes.], [Faturação], [Artefactos], [F. Soares],
  [RF17], [11/03/2026\ 14:30], [O sistema deve enviar um alerta interno ao Gerente de Loja quando uma OS ultrapassa o "Tempo Médio de Reparação" definido para aquele tipo de avaria.], [Notificações], [José Barros], [R. Rocha],
  [RF18], [09/03/2026\ 14:55], [O sistema deve obrigar à recolha de consentimento explícito (checkbox) para o tratamento de dados pessoais no momento do registo de um novo cliente.], [Segurança], [Sofia Almeida], [F. Soares],
  [RF19], [09/03/2026\ 10:55], [O sistema deve manter um log (registo histórico) de todas as alterações manuais feitas ao inventário, identificando o utilizador, a data, a hora e a quantidade alterada.], [Auditoria], [D. L. Machado], [R. Rocha],
)

==== 2.3.2 Requisitos Não Funcionais (RNF)

#table(
  columns: (3em, 7.5em, 1fr, 5.5em, 5em, 4.5em),
  align: (center, center, left, center, center, center),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header(
    [*Nr.*], [*Data e Hora*], [*Descrição*], [*Área*], [*Fonte*], [*Analista*]
  ),
  [RNF01], [10/03/2026\ 10:15], [O sistema tem de ser muito rápido a abrir as Ordens de Serviço.], [Desempenho], [J. "Ruca" Silva], [F. Soares],
  [RNF02], [10/03/2026\ 10:20], [A interface para a oficina tem de ser limpa e fácil de usar.], [Usabilidade], [J. "Ruca" Silva], [R. Rocha],
  [RNF03], [10/03/2026\ 10:25], [Os mecânicos não podem perder muito tempo no dispositivo.], [Usabilidade], [J. "Ruca" Silva], [R. Rocha],
  [RNF04], [10/03/2026\ 10:30], [O sistema deve funcionar em tablets na oficina.], [Plataforma], [J. "Ruca" Silva], [R. Rocha],
  [RNF05], [09/03/2026\ 15:05], [O sistema não pode perder dados de clientes ou do stock.], [Segurança /\ Fiabilidade], [Sofia Almeida], [F. Soares],
  [RNF06], [09/03/2026\ 11:15], [O sistema deve usar a cloud para sincronizar tudo em tempo real.], [Arquitetura], [D. L. Machado], [F. Soares],
  [RNF07], [09/03/2026\ 11:20], [O sistema deve encriptar as passwords dos utilizadores na base de dados utilizando algoritmos de hashing robustos.], [Segurança], [D. L. Machado], [F. Soares],
  [RNF08], [09/03/2026\ 15:10], [O sistema deve terminar automaticamente a sessão de um utilizador (timeout) após 60 minutos de inatividade nos terminais de loja ou oficina.], [Sessão], [Sofia Almeida], [R. Rocha],
)

=== 2.4 Análise, Validação e Refinamento de Requisitos

Durante a fase de eliciação, a recolha de informação junto dos stakeholders gerou um conjunto inicial de requisitos formulados em linguagem natural. Como é comum nesta fase, muitos destes requisitos apresentavam problemas de ambiguidade, redundância, subjetividade ou falta de testabilidade.

De forma a cumprir as boas práticas de Engenharia de Software e a preparar a Especificação de Requisitos para a equipa de desenvolvimento, procedeu-se ao refinamento rigoroso da lista inicial.

*Resolução de Subjetividade e Falta de Testabilidade*

Requisitos que contêm adjetivos como "rápido", "fácil" ou "limpo" são impossíveis de testar objetivamente. Estes foram reescritos para incluir métricas quantificáveis.

#table(
  columns: (1fr, 1fr, 1fr),
  align: left,
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header(
    [*Requisito Original (Em Bruto)*],
    [*Problema Identificado*],
    [*Requisito Refinado (Versão Final)*],
  ),
  [RNF01: O sistema tem de ser muito rápido a abrir as Ordens de Serviço.],
  ["Muito rápido" é subjetivo. Como é que a equipa de testes valida isto?],
  [RNF01.1: O sistema deve carregar e apresentar os detalhes de uma OS em menos de 2 segundos, para 95% das solicitações em condições normais de rede.],

  [RNF02/RNF03: A interface para a oficina tem de ser limpa e fácil de usar. Os mecânicos não podem perder muito tempo.],
  ["Limpa" e "fácil" não são mensuráveis. "Muito tempo" é vago.],
  [RNF02.1: A interface da oficina deve permitir que a alteração de estado de uma OS e a associação de uma peça sejam realizadas com um máximo de 3 interações (cliques/toques no ecrã).],

  [RNF05: O sistema não pode perder dados de clientes ou do stock.],
  [Falta de métrica técnica. "Não perder" não é um requisito testável por si só.],
  [RNF05.1: O sistema deve garantir a persistência dos dados através de backups incrementais diários com redundância geográfica, garantindo um RPO (Recovery Point Objective) de 24 horas.],

  [RNF06: O sistema deve usar a cloud para sincronizar tudo em tempo real.],
  ["Tempo real" e "tudo" são termos imprecisos.],
  [RNF06.1: As atualizações de inventário e estados de OS efetuadas numa filial devem ser replicadas na BD central e visíveis para as restantes lojas num máximo de 5 minutos.],

  [RF10/RF11: O sistema tem de avisar o David quando as peças estão a acabar.],
  [Uso de nome próprio e termo vago ("acabar"). Não define o canal de aviso.],
  [RF10.1: O sistema deve gerar um alerta visual de alta prioridade no dashboard de gestão sempre que o stock de um artigo crítico atinja o limite mínimo configurado por loja.],

  [RF12: O sistema tem de calcular o preço da reparação sozinho sem errar.],
  [Informalidade e falta de definição da regra de negócio para o cálculo.],
  [RF12.1: Valor Tabelado do Serviço + Somatório do Preço de Venda das Peças Aplicadas (o preço de compra das peças é interno, e o preço usado na fatura fica congelado).],
)

*Correção de Linguagem Informal e Foco na Solução*

Requisitos focados em pessoas específicas ou formulados de forma coloquial foram ajustados para refletir o comportamento esperado do sistema.

#table(
  columns: (1fr, 1fr, 1fr),
  align: left,
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header(
    [*Requisito Original (Em Bruto)*],
    [*Problema Identificado*],
    [*Requisito Refinado (Versão Final)*],
  ),
  [RF06: O David precisa de um dashboard analítico para ver o lucro.],
  [O requisito não deve focar-se numa pessoa específica, mas sim num papel de utilizador.],
  [RF06.1: O sistema deve disponibilizar um Dashboard de Gestão, acessível a utilizadores com perfil de "Administrador", contendo as métricas de lucro líquido, receitas agregadas e volume de intervenções por loja.],

  [RF04: As OS têm de ter todas a mesma linguagem para não haver confusões.],
  [Não define como o sistema resolve o problema da linguagem.],
  [RF04.1: O sistema deve obrigar à utilização de um catálogo padronizado (menus dropdown ou tags predefinidas) para a descrição de avarias e intervenções nas OS.],
)

#prompt-box[
  *Prompt*

  Dá-me uma lista dos requisitos funcionais e não funcionais que parecem estar um bocado ambíguos, e que não se encontram refinados na secção 2.4. Diz-me também o que devo colocar, de acordo com a estrutura que já lá está.

  #v(6pt)
  *Análise Crítica*

  Foi necessário colocar esta prompt, visto que foram adicionados novos requisitos. A resposta continha alguns pontos repetidos e não importantes, que foram filtrados.

  #v(6pt)
  *Modelo:* Gemini-3
]

=== 2.5 Modelação de Casos de Uso

Com base no levantamento e na análise detalhada dos requisitos recolhidos, procedeu-se à modelação funcional do sistema DLMCare. Os Casos de Uso apresentados nesta secção traduzem as necessidades operacionais e de negócio em funcionalidades concretas de software.

*UC01: Registar Cliente e Trotinete*

- Ator principal: Gestores de Loja e Apoio ao Cliente (ex: Inês, Miguel, Sofia)
- Pré-condições: utilizador autenticado no sistema com perfil de Receção
- Pós-condição: o cliente e a trotinete ficam registados de forma centralizada, acessíveis na rede DLMCare

Fluxo Normal:
+ O gestor pesquisa o cliente pelo NIF ou contacto móvel
+ O sistema indica que o cliente não existe
+ O gestor obtém o consentimento do cliente
+ O gestor introduz os dados pessoais do cliente
+ O gestor introduz os dados da trotinete (marca, modelo, número de série)
+ O sistema valida o número de série (garante que é único)
+ O sistema guarda o registo e associa a trotinete ao cliente

Fluxo de Exceção 1 — Número de série inválido (Passo 6): o sistema emite um alerta de duplicação e cancela o registo.

Fluxo de Exceção 2 — Cliente não consente (Passo 3): o sistema cancela o registo.

Fluxo Alternativo 1 — Cliente já existe (Passo 2): vai para o passo 4.

---

*UC02: Registar Diagnóstico e Abater Peças*

- Ator principal: Mecânico / Especialista Técnico (ex: Tiago, Ruca)
- Pré-condições: OS criada; mecânico autenticado num tablet da oficina
- Pós-condição: a OS fica com peças e tempos associados; o inventário é atualizado em tempo real

Fluxo Normal:
+ O mecânico abre a OS associada à trotinete
+ O mecânico inicia a intervenção, ativando a contagem de tempo
+ O mecânico seleciona no catálogo as peças que vai aplicar
+ O sistema verifica a disponibilidade de stock local e associa as peças à OS
+ O sistema guarda a quantidade e o preço de venda unitário no momento
+ O sistema abate automaticamente as peças do inventário da loja correspondente
+ O mecânico conclui a intervenção e o sistema regista o tempo final

Fluxo de Exceção 1 — Peça indisponível (Passo 4): o sistema bloqueia a seleção e emite um alerta visual. A eventual encomenda externa ao fornecedor é tratada fora do sistema, de acordo com a restrição definida na secção 1.5.1.

---

*UC03: Alterar Estado da Ordem de Serviço*

- Ator principal: Mecânico / Especialista Técnico
- Pré-condições: OS em curso; mecânico autenticado no tablet da oficina
- Pós-condição: o estado da reparação é atualizado no sistema central e o cliente recebe uma notificação automática

Fluxo Normal:
+ O mecânico acede à OS da trotinete no tablet
+ O mecânico seleciona a opção de alterar estado
+ O mecânico escolhe o novo estado num catálogo ("Por iniciar", "Aguardar peças", "Em reparação", "Concluído")
+ O sistema guarda o novo estado e atualiza a informação em tempo real na receção
+ O sistema envia um email ao cliente a informar do novo estado

---

*UC04: Emitir Fatura*

- Ator principal: Gestor de Loja
- Pré-condições: OS encontra-se em estado "Concluído"; gestor autenticado no terminal da receção
- Pós-condição: fatura gerada pronta para ser entregue ao cliente

Fluxo Normal:
+ O gestor pesquisa e abre a OS concluída do cliente
+ O gestor clica na opção para gerar faturação
+ O sistema cruza os dados do valor do serviço registado com o custo das peças vendidas
+ O sistema apresenta um resumo do valor final, separando claramente os custos de peças dos custos de mão de obra
+ O gestor verifica os valores
+ O sistema emite a fatura certificada e gera o PDF

Fluxo Alternativo 1 — Valores incoerentes (Passo 5): o gestor corrige os valores e volta ao passo 6.

---

*UC05: Aceder ao Dashboard Analítico*

- Ator principal: CEO (David Lopes Machado)
- Pré-condições: utilizador autenticado com perfil de "Administrador"
- Pós-condições: as métricas financeiras e operacionais são exibidas

Fluxo Normal:
+ O CEO acede ao menu "Dashboard" do sistema
+ O sistema processa os dados centrais e apresenta a visão global da rede de lojas
+ O CEO aplica filtros por intervalo de datas e por loja específica (ex: comparar Porto e Braga)
+ O sistema atualiza os gráficos exibindo o volume de trotinetes reparadas, rácios de eficiência por mecânico, lucro líquido exato, etc.

Fluxo Alternativo 1 — Aplicação de filtros: o CEO seleciona filtros por loja, intervalo temporal, mecânico ou tipo de avaria; o sistema recalcula e atualiza os gráficos; o utilizador pode limpar os filtros para regressar à visão global.

---

*UC06: Consultar Histórico do Cliente*

- Ator principal: Rececionista
- Pré-condições: cliente deve estar registado no sistema; rececionista autenticado
- Pós-condição: rececionista visualiza as intervenções passadas do cliente e descarrega as faturas relevantes

Fluxo Normal:
+ O rececionista pesquisa no sistema o NIF do cliente
+ O sistema lista o parque de trotinetes em nome do cliente
+ O gestor seleciona uma trotinete
+ O sistema exibe o histórico de intervenções, garantias e reparações efetuadas nessa trotinete
+ O rececionista clica numa entrada para efetuar o download da fatura

---

*UC07: Reabastecer Stock*

- Ator principal: Gerente de Loja
- Pré-condições: o gerente encontra-se autenticado no sistema e as peças encomendadas externamente já foram entregues fisicamente na loja
- Pós-condição: as quantidades das peças selecionadas são incrementadas de forma persistente na base de dados do inventário da loja

Fluxo Normal:
+ O gerente de loja acede ao módulo de "Inventário" e seleciona "Registar Entrada de Stock"
+ O sistema apresenta a interface de pesquisa e inserção de artigos
+ O gerente introduz o termo de pesquisa da peça pretendida
+ O sistema processa a pesquisa e exibe os detalhes do artigo correspondente
+ O gerente insere a quantidade de unidades recebidas
+ O gerente submete a operação clicando em "Confirmar Entrada"
+ O sistema valida os dados e atualiza o stock total da peça na base de dados
+ O sistema exibe uma mensagem de sucesso e retorna à visualização geral do inventário atualizado

Fluxo Alternativo 1 — Artigo Inexistente (Passo 4): o gerente seleciona "Adicionar Novo Artigo ao Catálogo", preenche os dados obrigatórios e prossegue para o passo 5.

Fluxo Alternativo 2 — Inserção de quantidades inválidas (Passo 6): o sistema exibe uma mensagem de erro; o gerente corrige o valor e volta ao passo 6.

#prompt-box[
  *Prompt*

  Casos de Uso (Use Cases): Escreve a especificação textual de pelo menos 4 Casos de Uso principais do sistema DLMCare, incluindo Ator Principal, Pré-condições, Fluxo Principal, Fluxos Alternativos e Pós-condições.

  #v(6pt)
  *Análise Crítica*

  Para além da prompt apresentada, foi também fornecido previamente todo o contexto do trabalho (histórico da DLMCare, stakeholders e lista de requisitos). Foram apenas realizados pequenos ajustes e correções nos fluxos alternativos e de exceção.

  #v(6pt)
  *Modelo:* Gemini-3
]

=== 2.6 Diagrama de Casos de Uso

Com base nos casos de uso acima apresentados, foi desenvolvido um diagrama de casos de uso que os representava e relacionava com os seus respetivos atores.

#figure(
  image("images/diagrama_casos_uso.png", width: 85%),
  caption: [Diagrama de Casos de Uso — Sistema DLMCare],
)

#prompt-box[
  *Prompt*

  Atua como um Arquiteto de Software Especialista em UML. Preciso que cries o código PlantUML para o Diagrama de Casos de Uso do sistema "DLMCare". Atores: Gerente de Loja, Rececionista, Mecânico, CEO/Administrador (David Machado). Casos de Uso: UC01 a UC07. Liga os atores aos casos de uso de forma lógica. Usa `left to right direction` e `skinparam packageStyle rectangle`. Output esperado: apenas o código PlantUML limpo e pronto a renderizar.

  #v(6pt)
  *Análise Crítica*

  O diagrama apresentado foi obtido com esta prompt. Devido às especificações da prompt, o primeiro output foi excelente, não sendo necessárias quaisquer alterações.

  #v(6pt)
  *Modelo:* Gemini
]

=== 2.7 Especificação de Requisitos de Software (SRS — IEEE 29148)

A presente secção apresenta uma síntese formal da Especificação de Requisitos de Software (SRS) do sistema DLMCare, estruturada de acordo com a norma IEEE 29148:2018 (sucessora da IEEE 830-1998). Esta especificação consolida os requisitos elicitados nas secções anteriores num documento normativo, servindo de referência vinculativa para as etapas de Arquitetura, Implementação e Verificação.

==== 2.7.1 Introdução

*Propósito:* Este documento especifica os requisitos do sistema de informação centralizado DLMCare, destinado à gestão operacional e financeira de uma cadeia de três oficinas de reparação de trotinetes elétricas (Lisboa, Porto e Braga). Destina-se à equipa de desenvolvimento (implementação e testes) e ao Product Owner (validação e aceitação).

*Âmbito:* O sistema DLMCare é uma aplicação web cloud, acessível via browser em desktops e tablets, que suporta os processos de: registo de clientes e equipamentos, gestão do ciclo de vida de Ordens de Serviço, controlo de inventário multi-loja, faturação automática, notificações ao cliente e reporting analítico. O sistema não inclui a gestão de encomendas a fornecedores externos (ver restrição 1.5.1).

*Definições e Acrónimos:*

#table(
  columns: (5em, 1fr),
  align: (left, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Acrónimo*], [*Definição*]),
  [OS], [Ordem de Serviço — documento central que regista uma intervenção de reparação],
  [RF], [Requisito Funcional],
  [RNF], [Requisito Não Funcional],
  [RGPD], [Regulamento Geral sobre a Proteção de Dados (UE 2016/679)],
  [JWT], [JSON Web Token — mecanismo de autenticação stateless],
  [RBAC], [Role-Based Access Control — controlo de acesso por perfil],
  [ACID], [Atomicity, Consistency, Isolation, Durability — propriedades transacionais],
  [SRS], [Software Requirements Specification],
  [UAT], [User Acceptance Testing — testes de aceitação pelo utilizador],
  [API], [Application Programming Interface],
  [SPA], [Single Page Application],
)

*Referências:* IEEE 29148:2018 — Systems and Software Engineering, Life Cycle Processes, Requirements Engineering; IEEE 12207:2017 — Software Life Cycle Processes; ISO/IEC 25010:2011 — Systems and Software Quality Models; RGPD — Regulamento (UE) 2016/679.

==== 2.7.2 Descrição Geral

*Perspetiva do Produto:* O sistema DLMCare é uma nova plataforma standalone que não integra nem substitui sistemas pré-existentes. Foi desenvolvida para eliminar os processos manuais em papel e os grupos de WhatsApp atualmente utilizados nas três filiais, integrando pela primeira vez os dados de clientes, trotinetes, OS, stock e faturação numa base de dados centralizada acessível em tempo real.

*Funções Principais do Produto:*
+ Autenticação e controlo de acesso por perfil (Administrador, Gerente de Loja, Rececionista, Mecânico).
+ Registo e consulta centralizada de clientes e trotinetes, com histórico acessível em qualquer filial.
+ Criação, acompanhamento e encerramento de Ordens de Serviço com máquina de estados de oito fases.
+ Registo de tempos de mão de obra (start/stop) e associação de peças a cada OS.
+ Gestão de inventário por loja com abate automático de stock e alertas de stock mínimo.
+ Transferências internas de stock entre filiais com workflow de aprovação.
+ Faturação automática com snapshot de preços no momento da intervenção e descontos de fidelização.
+ Notificações automáticas ao cliente (email) em cada mudança de estado da OS.
+ Dashboard analítico com KPIs financeiros e operacionais filtráveis por loja e período.
+ Registo de auditoria de todas as operações críticas do sistema.

*Características dos Utilizadores:* Quatro perfis com diferentes níveis de literacia digital e contextos de uso. O Mecânico utiliza tablets em ambiente de oficina e necessita de uma interface com ações executáveis em no máximo 3 toques (RNF02.1). Os restantes perfis utilizam desktops em ambiente de escritório ou receção.

*Restrições Gerais:* Ver Secção 1.5 (Restrições Legais, Operacionais e Técnicas). O sistema deve estar disponível durante o horário de funcionamento das oficinas (segunda a sábado, 08h00–20h00) com uptime de 99,9%. O custo de aquisição das peças (#raw("preco_custo")) é interno e nunca exposto em faturas ou respostas da API pública.

*Pressupostos e Dependências:* Os dispositivos dos utilizadores têm acesso à internet. O serviço SMTP externo para envio de emails está disponível. As peças encomendadas a fornecedores externos chegam fisicamente à loja antes de serem registadas no sistema (a gestão de encomendas a fornecedores está fora do âmbito do sistema).

==== 2.7.3 Requisitos do Sistema

Os requisitos funcionais (RF01–RF19) e não funcionais (RNF01–RNF08) com as suas refinações encontram-se especificados nas Secções 2.3 e 2.4. A tabela seguinte apresenta a matriz de rastreabilidade entre os requisitos e os casos de uso que os implementam:

#table(
  columns: (4.5em, 1fr, 5.5em),
  align: (center, left, center),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Requisito*], [*Descrição Resumida*], [*Casos de Uso*]),
  [RF01–02], [Registo e consulta centralizada de clientes e trotinetes], [UC01, UC06],
  [RF03–05], [Criação e gestão do ciclo de vida de OS (estados padronizados)], [UC02, UC03],
  [RF06–07], [Dashboard analítico, relatórios operacionais e financeiros], [UC05],
  [RF08–11], [Inventário centralizado, abate automático e alertas de stock mínimo], [UC02, UC07],
  [RF12–13], [Cálculo automático do valor da OS e faturação discriminada], [UC04],
  [RF14], [Notificações automáticas ao cliente (email) em mudanças de estado], [UC03],
  [RF15], [Registo de auditoria de todas as alterações de estado de OS], [UC02–UC04],
  [RF16], [Descontos de fidelização (percentuais ou fixos) em faturação], [UC04],
  [RF17], [Alerta de OS em atraso ao Gerente de Loja], [UC03],
  [RF18], [Recolha de consentimento RGPD explícito no registo de cliente], [UC01],
  [RF19], [Log de auditoria de todas as alterações manuais ao inventário], [UC07],
  [RNF01–04], [Desempenho (< 2s), usabilidade (≤ 3 interações) e suporte a tablets], [Todos],
  [RNF05–08], [Segurança (bcrypt), cloud, encriptação e timeout de sessão (60 min)], [Todos],
)

*Requisitos de Interface:*

- *Interface de Utilizador:* Aplicação web responsiva (Vue.js SPA), suportando resoluções desde 375 px (smartphone) até ecrãs wide (≥ 1440 px). Abaixo de 1280 px, o perfil Mecânico vê uma interface mobile com bottom navigation bar e cards de OS em lugar de tabelas HTML.

- *Interface de Software:* API REST com prefixo #raw("/api/v1"), formato JSON, autenticação via Bearer token (JWT). Documentação interativa disponível automaticamente em #raw("/docs") (OpenAPI/Swagger). Ver Secção 6.1 para a especificação completa de endpoints, métodos, permissões e formatos de resposta.

- *Interface de Hardware:* A aplicação é acessível em qualquer dispositivo com browser moderno (Chromium ≥ 100, Firefox ≥ 100). As operações de oficina são otimizadas para ecrãs touch ≥ 10", com botões de dimensão mínima compatível com uso com luvas.

- *Interface de Comunicação:* Comunicação HTTPS entre cliente e servidor; envio de notificações ao cliente via SMTP com templates HTML para quatro eventos (diagnóstico, conclusão, cancelamento e fatura); geração de documentos PDF (faturas e transferências de stock) via fpdf2 no servidor, enviados diretamente ao cliente por email ou descarregáveis na interface.

#prompt-box[
  *Prompt*

  Com base na norma IEEE 29148:2018, estrutura uma secção SRS formal para o sistema DLMCare. Inclui: propósito, âmbito, definições, descrição geral (perspetiva do produto, funções principais, perfis de utilizadores, restrições e pressupostos) e uma matriz de rastreabilidade RF/RNF → Casos de Uso. O tom deve ser normativo e técnico.

  #v(6pt)
  *Análise Crítica*

  O output inicial omitia a tabela de rastreabilidade e a secção de interfaces. Foi necessário pedir explicitamente a decomposição em interfaces de utilizador, software, hardware e comunicação para cobrir todos os aspetos da norma. A matriz de rastreabilidade foi ajustada para refletir os casos de uso reais do sistema, garantindo que nenhum requisito fica sem cobertura funcional identificada.

  #v(6pt)
  *Modelo:* Gemini
]

// ============================================================
// CAPÍTULO 2
// ============================================================
= Capítulo 2 — Arquitetura e Design do Software Utilizando LLM

A conceção arquitetural do sistema DLMCare foi orientada pela necessidade imperativa de garantir a sincronização de dados em tempo real entre as três filiais (Lisboa, Porto e Braga), assegurando simultaneamente a integridade transacional do inventário e a alta disponibilidade da plataforma. Para responder a este desafio, a arquitetura de software foi desenhada com base em princípios de desacoplamento, escalabilidade e segurança.

== 3. Arquitetura Global do Sistema

=== 3.1 Visão Geral e Decisões Arquiteturais

==== 3.1.1 Padrão Arquitetural Adotado

Para o desenvolvimento do DLMCare, adotou-se o padrão de Arquitetura em 3 Camadas (3-Tier Architecture) assente num modelo Cliente-Servidor.

A escolha deste padrão justifica-se pela clara separação de responsabilidades (Separation of Concerns) que oferece. Ao isolar a interface de utilizador, a lógica de processamento e o armazenamento de dados em camadas independentes, o sistema ganha uma resiliência significativa. Este desacoplamento permite que a aplicação cliente seja atualizada sem impacto nas regras de negócio subjacentes. Adicionalmente, este padrão é nativamente compatível com ambientes cloud, permitindo escalar os recursos do servidor central de forma elástica, garantindo a alta disponibilidade exigida para o funcionamento ininterrupto das três oficinas.

==== 3.1.2 Camadas Lógicas do Sistema

A arquitetura do sistema divide-se logicamente em três camadas fundamentais, cada uma com responsabilidades bem delimitadas e interfaces de comunicação claramente definidas.

A *Camada de Apresentação (Frontend)* atua como o ponto de interação exclusivo com os utilizadores, nomeadamente o Administrador, os Gerentes, os Rececionistas e os Mecânicos. Será desenvolvida como uma aplicação web com design estritamente responsivo, uma característica crítica dado que a interface tem de se ajustar dinamicamente aos desktops de ecrã largo utilizados no backoffice e na receção, e aos tablets utilizados pelos mecânicos nas bancadas de trabalho. A sua principal função é recolher os inputs dos utilizadores, enviar pedidos estruturados para o servidor e renderizar os dados recebidos de forma clara e intuitiva.

A *Camada de Lógica de Negócio (Backend/API)* constitui o núcleo de processamento do sistema DLMCare. Exposta através de uma API, esta camada intermédia centraliza todas as regras e processos do negócio, sendo responsável por receber os pedidos da camada de apresentação, validar permissões de acesso e executar operações complexas. É aqui que residem os algoritmos de cálculo automático de faturação, os mecanismos de alerta de stock mínimo e a máquina de estados que rege as transições das Ordens de Serviço (OS). A centralização da lógica no servidor garante que todas as filiais operam sob as mesmas regras, eliminando discrepâncias operacionais entre instalações.

A *Camada de Dados (Database)* será materializada através de um SGBDR centralizado e alojado na cloud. A opção por um modelo relacional é inegociável, dada a obrigatoriedade de garantir as propriedades ACID. Este rigor transacional é fundamental para o controlo de concorrência no inventário de peças: caso dois rececionistas tentem abater a mesma peça do stock central em simultâneo, o sistema processará os pedidos de forma sequencial e isolada, prevenindo duplicações.

#figure(
  block(width: 88%)[
    #arch-box(
      rgb("#dce8ff"), rgb("#2255aa"),
      "Camada de Apresentação",
      "Vue.js + HTML/CSS",
      [Interface responsiva para desktops (receção e administração) e tablets (mecânicos nas bancadas de trabalho). Comunica exclusivamente com o backend via REST API (HTTPS/JSON).],
    )
    #align(center)[#v(3pt) #text(size: 9pt, fill: luma(120))[↕ REST API · HTTPS · JSON] #v(3pt)]
    #arch-box(
      rgb("#e6f4ea"), rgb("#1a7a3a"),
      "Camada de Lógica de Negócio",
      "Python · FastAPI",
      [Autenticação JWT, controlo de acesso por perfil (RBAC), máquina de estados das OS, regras de faturação e alertas automáticos de stock mínimo. Centraliza toda a lógica de negócio da rede de lojas.],
    )
    #align(center)[#v(3pt) #text(size: 9pt, fill: luma(120))[↕ Driver MySQL · Queries SQL] #v(3pt)]
    #arch-box(
      rgb("#fff8ec"), rgb("#c05a00"),
      "Camada de Dados",
      "MySQL · Cloud",
      [Base de dados relacional centralizada com propriedades ACID e row-level locking para controlo de concorrência no inventário. Backups incrementais diários com redundância geográfica, garantindo RPO de 24 horas.],
    )
  ],
  caption: [Diagrama de Arquitetura — Sistema DLMCare em 3 Camadas],
)

#prompt-box[
  *Prompt*

  Atua como um Arquiteto de Software Sénior. Estamos a iniciar a "Etapa 2 — Arquitetura e Design" do projeto DLMCare (sistema cloud para gestão de 3 oficinas de trotinetes). Contexto: o sistema tem de sincronizar dados em tempo real entre Lisboa, Porto e Braga; acesso via desktops e tablets; controlo rigoroso de concorrência no inventário (ACID); alta disponibilidade na cloud. Missão: escreve o texto deste subcapítulo justificando as escolhas arquiteturais. O tom deve ser académico, técnico e formal.

  #v(6pt)
  *Análise Crítica*

  Diferente de uma arquitetura monolítica tradicional, que apresentaria riscos de contenção na base de dados centralizada e dificuldades de sincronização geográfica, a solução proposta oferece o equilíbrio ideal. Garante-se o rigor matemático no stock de peças e a fluidez necessária para a operação em tempo real.

  #v(6pt)
  *Modelo:* Gemini
]

=== 3.2 Stack Tecnológico

A seleção do stack tecnológico para o sistema DLMCare foi conduzida segundo critérios rigorosos de engenharia de software, tendo como objetivo principal a mitigação de riscos de implementação e o alinhamento com o padrão arquitetural de três camadas previamente definido. Privilegiou-se a adoção de tecnologias de código aberto, amplamente consolidadas na indústria e suportadas por comunidades ativas, em detrimento de soluções proprietárias ou emergentes com menor maturidade comprovada. Para cada camada lógica do sistema, foram consideradas e avaliadas alternativas, e a escolha final recaiu sobre o conjunto de ferramentas que melhor equilibra robustez técnica, velocidade de desenvolvimento e sustentabilidade a longo prazo.

==== 3.2.1 Backend (Lógica de Negócio e API): Python e FastAPI

Para a implementação da camada de lógica de negócio e exposição da Interface de Programação de Aplicações (API), a equipa avaliou diferentes ecossistemas tecnológicos, considerando a performance, a rapidez de desenvolvimento e a robustez necessária para um sistema multi-loja.

A tabela seguinte apresenta a comparação entre as principais tecnologias consideradas para esta camada:

#table(
  columns: (6.5em, 1fr, 1fr),
  align: (left, left, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Tecnologia*], [*Vantagens*], [*Desvantagens*]),
  [FastAPI (Python)],
  [Alta performance (assíncrono), documentação automática (OpenAPI) e tipagem de dados rigorosa.],
  [Ecossistema de plugins mais recente comparado com frameworks mais antigos.],
  [Node.js (Express)],
  [Elevada escalabilidade em operações de I/O e permite o uso de JavaScript em todo o stack.],
  [A gestão de concorrência em tarefas pesadas de CPU pode ser mais complexa.],
  [Java (Spring Boot)],
  [Extremamente robusto, seguro e com vasta adoção em sistemas corporativos críticos.],
  [Curva de aprendizagem elevada e desenvolvimento mais verboso, o que atrasa a entrega.],
)

==== Justificação da Escolha e Decisão Final

Optámos pela combinação de Python com a framework FastAPI. A escolha do Python fundamenta-se na sua sintaxe concisa e elevada legibilidade — fatores que reduzem a complexidade cognitiva do código e facilitam a revisão colaborativa, permitindo uma iteração de desenvolvimento mais célere, o que é crítico num projeto com janela temporal restrita. A seleção específica do FastAPI, em detrimento de alternativas como o Django REST Framework (DRF), justifica-se pela sua arquitetura assíncrona nativa (baseada em ASGI e asyncio), vital para processar eficientemente pedidos concorrentes provenientes das três oficinas em simultâneo. Adicionalmente, o FastAPI integra nativamente a validação automática de dados (via Pydantic) e a geração de documentação interativa (OpenAPI/Swagger), assegurando um contrato de interface explícito e verificável entre o frontend e o backend desde o início do desenvolvimento, mitigando riscos de integração.

==== 3.2.2 Base de Dados (Persistência): MySQL

A camada de persistência de dados é o alicerce que garante a consistência da informação entre as três filiais da DLMCare. Para a sua implementação, a equipa avaliou diferentes modelos e sistemas de gestão de bases de dados (SGBD).

A tabela seguinte apresenta a análise comparativa entre as tecnologias consideradas:

#table(
  columns: (6.5em, 1fr, 1fr),
  align: (left, left, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Tecnologia*], [*Vantagens*], [*Desvantagens*]),
  [MySQL],
  [Excelente performance em operações de leitura, suporte robusto a transações ACID e grande maturidade no mercado.],
  [Menor flexibilidade para lidar com esquemas de dados não estruturados comparativamente ao NoSQL.],
  [PostgreSQL],
  [Suporte avançado para tipos de dados complexos e conformidade estrita com normas SQL.],
  [Exige maior consumo de recursos do servidor e uma configuração inicial mais complexa.],
  [MongoDB],
  [Modelo de documentos flexível (NoSQL), ideal para prototipagem rápida e dados sem esquema fixo.],
  [Dificuldade em garantir integridade referencial complexa de forma nativa e declarativa.],
)

==== Justificação da Escolha e Decisão Final

A equipa optou pelo MySQL, um Sistema de Gestão de Bases de Dados Relacionais (SGBDR) de código aberto. A preferência por um modelo relacional — em detrimento de alternativas NoSQL como o MongoDB — decorre da natureza estruturada e interdependente dos dados (clientes, veículos, ordens de serviço, stock e faturação). Um modelo NoSQL introduziria complexidade desnecessária na gestão da integridade referencial, que no MySQL é garantida nativamente através de chaves estrangeiras. A escolha justifica-se, sobretudo, pela sua conformidade estrita com as propriedades ACID, requisito não-negociável para a operação multi-instalação da DLMCare. O mecanismo de row-level locking do MySQL garante que as transações sobre stock são orquestradas de forma isolada, prevenindo anomalias que comprometeriam a faturação. Finalmente, a maturidade comprovada do MySQL reduz o risco operacional e facilita a integração com o backend em Python através de bibliotecas como SQLAlchemy, assegurando a sustentabilidade do projeto a longo prazo. A comunicação entre a aplicação e a base de dados é gerida pelo driver compatível nativo PyMySQL, enquanto o controlo de versões do esquema relacional é assegurado pela ferramenta de migrations Alembic, permitindo evoluir a estrutura de dados de forma segura e incremental ao longo do ciclo de vida da aplicação.

==== 3.2.3 Frontend (Interface do Utilizador): Vue.js com HTML e CSS

A camada de apresentação é o ponto de interação fundamental entre os utilizadores e o sistema DLMCare. Para garantir uma interface fluida em múltiplos dispositivos, a equipa analisou as três principais frameworks de mercado:

#table(
  columns: (6.5em, 1fr, 1fr),
  align: (left, left, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Tecnologia*], [*Vantagens*], [*Desvantagens*]),
  [Vue.js],
  [Curva de aprendizagem suave, extremamente leve e excelente sistema de reatividade bidirecional.],
  [Ecossistema de plugins e mercado de trabalho ligeiramente menor que o do React.],
  [React],
  [Ecossistema vasto, flexibilidade extrema e uma enorme biblioteca de componentes de terceiros.],
  [Exige mais decisões de arquitetura e configuração manual (gestão de estado, routing).],
  [Angular],
  [Solução completa "out-of-the-box" com padrões rígidos de desenvolvimento.],
  [Curva de aprendizagem acentuada e complexidade elevada (TypeScript rigoroso e injeção de dependências).],
)

==== Justificação da Escolha e Decisão Final

A camada de apresentação será desenvolvida com recurso à framework progressiva de JavaScript Vue.js, assente nos standards web de HTML e CSS. A opção pelo Vue.js em detrimento de alternativas como React ou Angular fundamenta-se num equilíbrio entre critérios de engenharia e gestão de risco do projeto. O Vue.js permite a construção de uma Single Page Application (SPA) baseada num modelo de componentes reutilizáveis. O seu sistema de reatividade de dados bidirecional (two-way data binding) assegura a sincronização automática entre o estado da aplicação e a interface visual, eliminando a manipulação direta do DOM e resultando numa interface fluida e responsiva. Esta característica é especialmente vantajosa para o módulo de Oficina, operado em tablets por técnicos em contexto de trabalho. Do ponto de vista da gestão de risco, o Vue.js apresenta uma curva de aprendizagem comprovadamente mais suave do que o Angular e uma estrutura de projeto mais explícita e previsível do que o React. Esta previsibilidade reduz a probabilidade de decisões de implementação inconsistentes entre os membros da equipa. Complementarmente, o uso de ferramentas modernas como o Vite proporciona ciclos de compilação e hot-reload rápidos, acelerando o desenvolvimento iterativo e garantindo a entrega atempada das interfaces.

#prompt-box[
  *Prompt*

  Atua como um Arquiteto de Software Sénior e Technical Writer. A nossa decisão de equipa é utilizar Python (Backend), MySQL (Base de Dados) e Vue.js com HTML/CSS (Frontend). Missão: escreve um texto justificando rigorosamente a escolha de cada tecnologia. O tom deve ser formal, académico e focado nos benefícios de engenharia e na redução de risco do projeto.

  #v(6pt)
  *Análise Crítica*

  No primeiro output o que menos gostámos foi o uso de bullet points, pelo que pedimos que fossem eliminados em favor de texto corrido. O texto resultante tem a densidade e continuidade argumentativas esperadas num relatório universitário.

  #v(6pt)
  *Modelo:* Gemini e Claude
]

== 4. Modelação de Domínio

A transição do modelo de gestão rudimentar da DLMCare — assente em folhas de obra físicas e ficheiros de Excel descentralizados — para um sistema de informação cloud exige uma representação rigorosa da sua realidade operacional. Esta secção apresenta a Modelação de Domínio e Dados, que atua como o alicerce fundamental para a integridade, persistência e manipulação da informação em toda a rede de oficinas.

Para resolver o caos logístico e as falhas de comunicação entre as filiais de Lisboa, Porto e Braga, mapearam-se as entidades do negócio (clientes, trotinetes, peças e lojas) e os respetivos processos transacionais (ordens de reparação e faturação) em abstrações lógicas de software. Este desenho orientado a objetos tem como objetivo garantir uma fonte única de verdade para todo o sistema. Dessa forma, assegura-se que o inventário virtual reflete fielmente o stock físico de cada filial e que existe uma rastreabilidade absoluta entre os tempos de mão de obra, os materiais aplicados e a faturação final. O modelo aqui definido estabelece, assim, a estrutura necessária para a posterior implementação da base de dados relacional (MySQL) e da lógica de negócio associada.

=== 4.1 Identificação e Caracterização das Classes do Sistema

Para suportar a arquitetura e garantir o cumprimento de todas as regras de negócio operacionais, estatísticas e financeiras, o sistema assenta nas seguintes classes de domínio:

- *Hierarquia de Utilizadores (Utilizador, Administrador, GerenteLoja, Rececionista, Mecanico):* Representam os diferentes atores que interagem com o sistema, herdando credenciais de acesso comuns, mas com permissões e relações específicas.
- *Cliente:* Armazena os dados pessoais dos utilizadores e gere o consentimento RGPD.
- *Trotinete:* Identifica de forma unívoca o equipamento (número de série), centralizando o histórico.
- *Loja:* Representa as filiais físicas (Lisboa, Porto, Braga).
- *OrdemServico (OS):* A entidade central que orquestra o diagnóstico e o estado atual da intervenção.
- *RegistoTempo:* Mantido estritamente para fins estatísticos e auditoria de produtividade. Regista o tempo despendido pelos mecânicos, não tendo impacto na faturação final.
- *CatalogoServico:* Define os tipos de intervenção padrão (ex: "Substituição de Pneu", "Revisão Eletrónica") e os seus respetivos preços tabelados.
- *OS_Servico:* Classe associativa que regista os serviços efetivamente realizados numa OS, congelando o preço tabelado no momento da intervenção.
- *Peca:* O catálogo de artigos, com separação clara entre o preço de aquisição a fornecedores e o preço de venda ao público.
- *StockLoja:* Inventário local (quantidades e limites mínimos) específico de cada filial.
- *OS_Peca:* Classe associativa que documenta as peças consumidas numa OS, congelando o seu preço de venda para a faturação.
- *Fatura:* Documento financeiro gerado com base no somatório dos serviços tabelados e no preço de venda das peças aplicadas.
- *Auditoria:* Log de segurança do sistema.

=== 4.2 Relacionamentos e Multiplicidades (Relacionamentos UML)

A integridade do modelo de domínio do sistema DLMCare é garantida por uma rede completa de relacionamentos estruturais e transacionais. Abaixo detalham-se todas as associações e respetivas multiplicidades presentes no diagrama:

*Herança e Organização Lógica (Atores e Lojas)*

- *Utilizador e Especializações (Herança/Generalização):* As classes Administrador, GerenteLoja, Rececionista e Mecanico herdam (estendem) os atributos comuns de autenticação da superclasse abstrata Utilizador.
- *Loja (1) e GerenteLoja (1..\*):* Uma filial física tem de ser administrada por pelo menos um (ou vários) gerentes; um gerente está afeto a uma única loja.
- *Loja (1) e Rececionista (1..\*):* Uma filial emprega pelo menos um rececionista para a frente de loja; cada rececionista opera apenas no sistema da sua loja.
- *Loja (1) e Mecanico (1..\*):* Uma filial tem de ter pelo menos um mecânico especializado alocado às suas bancadas.

*Clientes e Equipamentos (Receção)*

- *Cliente (1) e Trotinete (1..\*):* Para um cliente estar registado no sistema, tem de possuir pelo menos uma trotinete associada ao seu perfil. Uma trotinete pertence única e exclusivamente a um cliente.
- *Trotinete (1) e OrdemServico (1..\*):* Uma trotinete acabada de registar fica logo associada a uma ordem de serviço, mas ao longo do tempo poderá acumular várias ordens de serviço (\*). Cada OS refere-se apenas a uma trotinete específica.

*Oficina, Tempos e Serviços (Intervenção)*

- *Loja (1) e OrdemServico (1..\*):* Uma OS é obrigatoriamente registada e executada numa loja específica. Uma loja acumula o histórico de múltiplas OS.
- *OrdemServico (1) e RegistoTempo (0..\*):* Uma OS pode não ter ainda tempos registados (se estiver "Por Iniciar") ou ter vários registos de tempo (se o trabalho for pausado e retomado). Cada registo de tempo pertence apenas a uma OS.
- *Mecanico (1) e OrdemServico (1..\*):* Um mecânico pode tratar de várias ordens de serviço. Cada ordem de serviço está associada a um único mecânico.
- *OrdemServico (1) e OS_Servico (0..\*):* Uma reparação pode implicar a realização de vários serviços tabelados (ex: mudar pneu e reparar travão).
- *CatalogoServico (1) e OS_Servico (0..\*):* Um serviço do catálogo (ex: "Furo") pode ser aplicado em milhares de OS ao longo do tempo, ou em nenhuma (se for um serviço novo).

*Inventário e Aplicação de Peças*

- *Peca (1) e StockLoja (0..\*):* Um artigo do catálogo global pode estar fisicamente presente no inventário de várias lojas. A classe StockLoja resolve a relação muitos-para-muitos original entre Loja e Peca.
- *Loja (1) e StockLoja (0..\*):* Uma loja contém milhares de registos de quantidades locais no seu inventário virtual.
- *OrdemServico (1) e OS_Peca (0..\*):* Uma OS pode consumir zero peças (se for apenas um serviço de limpeza/afinação) ou dezenas de peças diferentes.
- *Peca (1) e OS_Peca (0..\*):* Uma referência do catálogo pode ser aplicada em múltiplas OS diferentes. A classe OS_Peca resolve a associação muitos-para-muitos, guardando a quantidade e o preço de venda no momento.

*Faturação e Segurança*

- *OrdemServico (1) e Fatura (0..1):* Uma Ordem de Serviço pode ainda não estar faturada (0) ou ter, no máximo, uma única fatura final emitida (1). A fatura pertence sempre a uma única OS.
- *Rececionista (1) e Fatura (0..\*):* Um rececionista é o responsável pela emissão legal de múltiplas faturas. Cada fatura tem o registo do rececionista que a validou.
- *Utilizador (1) e Auditoria (0..\*):* Qualquer ator do sistema (Administrador, Gerente, Mecânico ou Rececionista) pode gerar múltiplos logs de segurança ao longo do tempo (ex: alterar stock manualmente, fazer login). Cada registo de auditoria está irrevogavelmente ligado a um único utilizador.

=== 4.3 Especificação dos Atributos das Classes

*OrdemServico*

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [idOS], [Identificador único sequencial de cada OS], [INT], [N], [1045],
  [dataAbertura], [Data e hora em que a trotinete deu entrada na oficina], [DATETIME], [N], [2026/04/01 10:30],
  [dataSaida], [Data e hora em que a reparação acabou], [DATETIME], [S], [2026/04/12 10:00],
  [estadoOS], [Situação atual da reparação], [Enum], [N], [Em Reparação],
  [diagnostico], [Notas clínicas descritivas], [TEXT], [S], [Erro E10 no visor],
  [idTrotinete], [Referência à trotinete alvo da reparação (FK)], [VARCHAR(100)], [N], [SN998877],
  [idLoja], [Referência à loja onde a OS está a decorrer (FK)], [INT], [N], [2],
)

*Cliente*

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [idCliente], [Identificador único do cliente (Chave Primária)], [INT], [N], [1],
  [nif], [Número de identificação fiscal do cliente], [VARCHAR(20)], [S], [234567890],
  [nome], [Nome completo do cliente], [VARCHAR(150)], [N], [Carlos Silva],
  [telefone], [Número de telemóvel], [VARCHAR(20)], [N], [912345678],
  [email], [Endereço de email para envio de faturas e orçamentos], [VARCHAR(150)], [N], [carlos\@email.com],
  [consentimentoRGPD], [Confirmação de aceitação dos termos de privacidade (RGPD)], [BOOLEAN], [N], [TRUE],
)

*Utilizador* (atributos partilhados por todas as subclasses)

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [idUtilizador], [Identificador único do utilizador (Chave Primária)], [INT], [N], [10],
  [nome], [Nome completo], [VARCHAR(150)], [N], [João Ruca Silva],
  [email], [Email de autenticação], [VARCHAR(150)], [N], [dlm\@gmail.com],
  [passwordHash], [Password encriptada com bcrypt], [VARCHAR(255)], [N], [---],
  [perfil], [Papel do utilizador no sistema], [Enum], [N], [MECANICO],
)

*Administrador* (atributos adicionais)

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [nivelAcesso], [Nível de privilégio global no sistema], [INT], [N], [1],
)

*GerenteLoja / Rececionista* (atributos adicionais)

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [idLoja], [Referência à loja onde o utilizador está afeto (FK)], [INT], [N], [2],
)

*Mecanico* (atributos adicionais)

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [idLoja], [Referência à loja onde o mecânico está afeto (FK)], [INT], [N], [3],
  [especialidade], [Área técnica de especialização], [VARCHAR(100)], [N], [Eletrónica],
  [comissao], [Percentagem de comissão por serviço executado], [INT], [N], [10],
)

*Trotinete*

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [numSerie], [Número de série de fábrica do equipamento (Chave Primária)], [VARCHAR(100)], [N], [SN9988776655],
  [marca], [Fabricante da trotinete], [VARCHAR(50)], [N], [Xiaomi],
  [modelo], [Modelo comercial do equipamento], [VARCHAR(50)], [N], [Pro 2],
  [idCliente], [Referência ao dono da trotinete (FK)], [INT], [N], [234567890],
)

*Peca*

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [referencia], [Código interno ou SKU do artigo (Chave Primária)], [VARCHAR(50)], [N], [BATT-XIA-01],
  [nome], [Designação técnica e comercial da peça], [VARCHAR(150)], [N], [Bateria 36V 10.4Ah],
  [precoCompra], [Valor de aquisição a fornecedores (interno)], [DECIMAL(7,2)], [N], [150.00],
  [precoVenda], [Valor pelo qual a loja vende a peça nos serviços], [DECIMAL(7,2)], [N], [170.00],
)

*Fatura*

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [idFatura], [Número sequencial e oficial do documento de faturação], [INT], [N], [2026001],
  [dataEmissao], [Data e hora em que a OS foi dada como concluída e cobrada], [DATETIME], [N], [2026/04/02 16:00],
  [idRececionista], [Referência à rececionista que emitiu a fatura (FK)], [INT], [N], [2],
  [valorPecas], [Soma do custo de todos os materiais aplicados na reparação], [DECIMAL(7,2)], [N], [150.00],
  [valorServicos], [Soma dos preços dos serviços executados], [DECIMAL(7,2)], [N], [45.00],
  [valorTotal], [Valor final a pagar pelo cliente], [DECIMAL(7,2)], [N], [195.00],
  [idOS], [Referência à OS que originou a fatura (FK)], [INT], [N], [1045],
)

*Loja*

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [idLoja], [Identificador único da filial (Chave Primária)], [INT], [N], [2],
  [localizacao], [Cidade], [VARCHAR(100)], [N], [Porto],
  [morada], [Morada física da loja], [VARCHAR(255)], [N], [Rua de Júlio Dinis],
  [contacto], [Número de telefone geral da receção da loja], [VARCHAR(20)], [N], [223344556],
)

*StockLoja*

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [idLoja], [Identificador da loja (FK)], [INT], [N], [1],
  [referencia], [Referência da peça (FK)], [VARCHAR(50)], [N], [BATT-XIA-01],
  [quantidadeAtual], [Unidades em prateleira], [INT], [N], [5],
  [stockMinimo], [Alerta de reposição], [INT], [N], [2],
)

*OS_Peca*

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [idOS], [Referência à OS intervencionada (FK)], [INT], [N], [1045],
  [referencia], [Referência do material aplicado na reparação (FK)], [VARCHAR(50)], [N], [PNEU-8.5-01],
  [quantidadeAplicada], [Número de unidades dessa peça gastas na intervenção], [INT], [N], [2],
  [precoVendaNoMomento], [Preço de venda no momento da compra (congelado)], [DECIMAL(7,2)], [N], [30.00],
)

*Auditoria*

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [idLog], [Identificador único do registo de segurança], [INT], [N], [1000],
  [idUtilizador], [Referência a quem executou a ação (FK)], [INT], [N], [5],
  [dataHora], [Timestamp do evento], [DATETIME], [N], [2026/04/02 16:00],
  [acao], [Descrição da ação crítica executada], [TEXT], [N], [Alterou o estado da OS 10],
)

*CatalogoServico*

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [idServico], [Identificador único do tipo de serviço], [INT], [N], [5],
  [descricao], [Breve descrição do serviço], [VARCHAR(200)], [N], [Substituição de Pneu],
  [precoTabelado], [Preço do serviço], [DECIMAL(7,2)], [N], [10.00],
)

*OS_Servico*

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [idOS], [Referência à OS (FK)], [INT], [N], [100],
  [idServico], [Referência ao serviço executado (FK)], [INT], [N], [1],
  [precoNoMomento], [Preço do serviço na data em que foi realizado (congelado)], [DECIMAL(7,2)], [N], [5.00],
)

*RegistoTempo*

#table(
  columns: (auto, 1fr, auto, auto, auto),
  align: (left, left, left, center, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Atributo*], [*Descrição*], [*Domínio*], [*Nulo*], [*Exemplo*]),
  [idRegisto], [Identificador único do registo], [INT], [N], [1],
  [startTime], [Início da intervenção], [DATETIME], [N], [2026/01/02 17:15],
  [endTime], [Fim/Pausa da intervenção], [DATETIME], [S], [2026/01/02 18:00],
  [totalMinutos], [Duração calculada desta sessão], [DECIMAL(7,2)], [N], [45],
  [idOS], [Referência à OS que estava a ser trabalhada (FK)], [INT], [N], [5],
)

=== 4.4 Diagrama de Classes

#figure(
  image("images/diagrama_classes.png", width: 85%),
  caption: [Diagrama de Classes — Modelo de Domínio DLMCare],
)

#prompt-box[
  *Prompt*

  Atua como um Engenheiro de Software. Traduz as tabelas de atributos e relacionamentos do sistema DLMCare que acabámos de definir num script PlantUML para gerar o Diagrama de Classes (Modelo de Domínio). Garante que a classe associativa OS_Peca é representada de forma a resolver a relação Muitos-para-Muitos entre OrdemServico e Peca. Oculta os ícones de visibilidade e usa um tema monocromático formal.

  #v(6pt)
  *Análise Crítica*

  A utilização do LLM para gerar o código PlantUML acelerou massivamente a documentação arquitetural. A IA interpretou corretamente a necessidade de resolver a relação N:M através de uma entidade intermédia (OS_Peca), o que aproxima o nosso modelo conceptual da realidade do modelo lógico relacional que será implementado em MySQL na Etapa 3. O resultado foi inserido sem necessidade de refatorização adicional.

  #v(6pt)
  *Modelo:* Gemini
]

=== 4.5 Consolidação e Revisão do Diagrama de Classes

A análise dos requisitos funcionais e não funcionais mostrou que o modelo inicial de classes cobre o núcleo do domínio, mas deve ser refinado antes da implementação. Em particular, a classe `Peca` não deve acumular simultaneamente a responsabilidade de catálogo e de stock local, uma vez que a mesma referência pode existir em várias lojas com quantidades e limites mínimos diferentes. Assim, propõe-se a consolidação do modelo de domínio através das seguintes classes e respetivas responsabilidades:

A classe `Utilizador` representa contas internas com credenciais e perfil de acesso, servindo de base para Administrador, Gerente, Rececionista e Mecânico. O `Cliente` guarda dados pessoais, contactos, NIF e consentimento RGPD, estando associado a uma ou várias trotinetes. A `Trotinete` representa o equipamento físico identificado por número de série único. A `OrdemServico`, sendo a entidade central do ciclo de reparação, agrega o diagnóstico, estado, loja, cliente, trotinete, tempos e peças. O `RegistoTempo` regista os períodos de trabalho de um mecânico numa OS, permitindo ações de start/stop e o cálculo de mão de obra.

Relativamente aos materiais, a `PecaCatalogo` define a referência, descrição, categoria e preço base da peça, não contendo stock local. O `StockLoja` guarda a quantidade e o limite mínimo de uma peça numa loja, utilizando uma chave composta (idLoja + referenciaPeca). A `OS_Peca` funciona como classe associativa entre OrdemServico e PecaCatalogo, guardando a quantidade aplicada e o preço no momento da intervenção. A `TransferenciaStock` regista os movimentos internos de peças entre lojas, não substituindo a compra externa a fornecedores.

A nível de faturação e controlo, a `Fatura` consolida peças, mão de obra, descontos e o valor final, podendo integrar-se com software certificado externo. A `Notificacao` regista comunicações (SMS/email) enviadas ao cliente e o estado de envio. Por fim, a `Auditoria` regista alterações críticas no sistema, sendo obrigatória para stock, estados de Ordem de Serviço e parametrizações. Esta separação reduz o acoplamento, facilita transações sobre inventário e evita inconsistências quando uma mesma referência existe em várias filiais.

== 5. Modelação Dinâmica e Componentes

A transição estrutural definida na modelação de dados exige um mapeamento claro de como a informação flui e é processada em tempo real pelas diferentes partes do sistema. Esta secção foca-se na Modelação Dinâmica e de Componentes, detalhando o comportamento da aplicação DLMCare em execução. Através da decomposição lógica em módulos independentes e da ilustração das interações temporais entre os utilizadores e a plataforma, demonstra-se como ações quotidianas da oficina — como a alteração do estado de uma reparação por um mecânico ou o registo de entrada de stock por um gerente — são orquestradas pelo backend de forma consistente. Este nível de desenho arquitetural garante que os processos complexos e concorrentes das três filiais são executados sem bloqueios, assegurando a agilidade e a sincronização exigidas para a operação ininterrupta do negócio.

=== 5.1 Diagrama de Componentes

O diagrama de componentes representa a decomposição lógica da aplicação em módulos independentes, interligados através da API do backend. Esta visão é útil para preparar a implementação incremental da Etapa 3.

#figure(
  image("images/diagrama_componentes.png", width: 100%),
  caption: [Diagrama de Componentes — Decomposição Lógica da Aplicação DLMCare],
)

=== 5.2 Diagramas de Sequência

Os Diagramas de Sequência (UML) descrevem como os objetos interagem ao longo do tempo para executar uma funcionalidade. Focam-se na ordem temporal das mensagens trocadas, ilustrando o fluxo de dados e controlo entre os componentes do sistema (interface, lógica, base de dados). São cruciais para entender a lógica de execução e identificar ineficiências ou erros no processamento da informação.

#figure(
  image("images/seq_uc01.png", width: 100%),
  caption: [Diagrama de Sequência — UC01: Registar Cliente e Trotinete],
)

#figure(
  image("images/seq_uc02.png", width: 100%),
  caption: [Diagrama de Sequência — UC02: Registar Diagnóstico e Abater Peças],
)

#figure(
  image("images/seq_uc04.png", width: 100%),
  caption: [Diagrama de Sequência — UC04: Emitir Fatura],
)

#figure(
  image("images/seq_uc06.png", width: 100%),
  caption: [Diagrama de Sequência — UC06: Consultar Histórico do Cliente],
)

#prompt-box[
  *Prompt*

  "Atua como Arquiteto de Software e gera o código PlantUML para os diagramas de sequência dos Casos de Uso UC01, UC02, UC04 e UC06 do projeto DLMCare. Diretrizes: (1) Arquitetura 3-Tier — todos os diagramas devem ter o fluxo Ator → Frontend (Vue.js) → Backend (FastAPI) → DB (MySQL); (2) usa as classes de consolidação da secção 4.5; (3) as chamadas entre Frontend e Backend devem usar os endpoints definidos na tabela da secção 6.1; (4) mostra o abate de stock no UC02; no UC04 mostra o cruzamento de dados para gerar a fatura final. Inclui validações de erro."

  #v(6pt)
  *Análise Crítica*

  A utilização do LLM para gerar o código PlantUML acelerou massivamente a documentação arquitetural. A IA foi capaz de analisar as classes existentes e fazer diagramas complexos conforme a arquitetura já desenhada.

  #v(6pt)
  *Modelo:* Gemini-3
]

== 6. Interfaces e Comunicação

A eficácia técnica do sistema DLMCare depende intrinsecamente da facilidade com que os utilizadores — desde os clientes finais até aos mecânicos nas bancadas de trabalho — interagem com a plataforma. Esta secção, dedicada às Interfaces e Comunicação, estabelece o contrato tecnológico e visual que materializa as operações de negócio num ambiente digital, substituindo definitivamente o uso de papel e grupos de mensagens. Aqui, documenta-se a especificação preliminar da API REST, que atua como o ponto de ligação seguro entre a infraestrutura central, os terminais das lojas e as integrações externas (como os serviços de SMS e faturação certificada). Em complemento, delineia-se a estrutura das interfaces de utilizador, garantindo que o design dos ecrãs é altamente responsivo, ergonómico e adaptado ao ritmo exigente e rápido da receção e do chão de oficina.

=== 6.1 Especificação Preliminar da API REST

A API REST será o ponto de ligação entre o frontend Vue.js e os serviços de backend. A tabela seguinte apresenta uma especificação preliminar dos endpoints necessários para implementar os casos de uso principais.

A tabela seguinte detalha a interface de comunicação do sistema, descrevendo os endpoints disponibilizados, os métodos HTTP utilizados, a sua função principal e os perfis com permissão de acesso a cada operação:

#table(
  columns: (3.5em, 1fr, 1fr, 5.5em),
  align: (center, left, left, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Método*], [*Endpoint*], [*Descrição*], [*Permissões*]),
  [POST], [#raw("/auth/login")], [Autentica utilizador e devolve token de sessão.], [Todos],
  [GET], [#raw("/clientes?query={...}")], [Pesquisa cliente por NIF ou contacto.], [Receção, Gerente],
  [POST], [#raw("/clientes")], [Cria novo cliente com consentimento RGPD.], [Receção, Gerente],
  [POST], [#raw("/trotinetes")], [Regista trotinete associada a cliente.], [Receção, Gerente],
  [GET], [#raw("/clientes/{id}/historico")], [Lista histórico de trotinetes, OS e faturas.], [Receção],
  [POST], [#raw("/ordens-servico")], [Cria nova Ordem de Serviço (OS).], [Receção, Gerente],
  [PATCH], [#raw("/ordens-servico/{id}/estado")], [Atualiza estado da OS e aciona notificações.], [Mecânico, Gerente],
  [POST], [#raw("/ordens-servico/{id}/tempos/iniciar")], [Inicia registo de tempo de intervenção.], [Mecânico],
  [POST], [#raw("/ordens-servico/{id}/tempos/parar")], [Termina ou pausa registo de tempo.], [Mecânico],
  [POST], [#raw("/ordens-servico/{id}/pecas")], [Associa peça à OS e abate stock.], [Mecânico],
  [GET], [#raw("/stock?loja={id}")], [Consulta stock por loja.], [Gerente, Admin],
  [POST], [#raw("/stock/entradas")], [Regista entrada de stock entregue fisicamente.], [Gerente],
  [POST], [#raw("/stock/transferencias")], [Regista transferência interna entre lojas.], [Gerente, Admin],
  [POST], [#raw("/faturas")], [Gera fatura a partir de OS concluída.], [Gerente],
  [GET], [#raw("/dashboard")], [Obtém métricas operacionais e financeiras.], [Administrador],
  [GET], [#raw("/auditoria")], [Consulta logs de alterações críticas.], [Administrador],
)

Os endpoints que alteram stock ou faturação devem ser executados dentro de transações de base de dados. Em caso de falha parcial, a operação deve ser revertida para evitar inconsistências.

=== 6.2 Design de Interfaces e Wireframes Textuais

A definição das interfaces foi orientada pelos perfis de utilizador identificados na Etapa 1. O objetivo é garantir que a implementação da Etapa 3 começa com uma visão clara dos ecrãs principais e das ações esperadas.

A tabela seguinte apresenta a estrutura dos principais ecrãs do sistema, detalhando o perfil de utilizador a que se destinam, os elementos que compõem a interface e as operações críticas que cada ecrã suporta:

#table(
  columns: (5em, 5em, 1fr, 1fr),
  align: (left, left, left, left),
  fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
  table.header([*Ecrã*], [*Utilizador Principal*], [*Elementos Principais*], [*Ações Críticas*]),
  [Login], [Todos], [Email, password, recuperação de acesso.], [Autenticar; terminar sessão após timeout.],
  [Pesquisa/Registo de Cliente], [Rececionista], [Pesquisa por NIF/contacto, dados pessoais, consentimento RGPD.], [Criar cliente; associar trotinete; evitar duplicados.],
  [Criação de OS], [Rececionista], [Cliente, trotinete, descrição inicial, fotografias, loja.], [Abrir OS; anexar fotos; definir prioridade.],
  [Tablet Oficina], [Mecânico], [Lista de OS, estado, diagnóstico, peças, start/stop de tempo.], [Alterar estado; associar peças; registar tempos.],
  [Inventário], [Gerente], [Peças por loja, stock atual, stock mínimo, alertas.], [Registar entrada; transferir stock; consultar ruturas.],
  [Faturação], [Gerente], [Resumo da OS, serviços, peças, descontos, valor final.], [Validar valores; gerar fatura; descarregar PDF.],
  [Dashboard], [CEO/Admin], [KPIs, filtros por loja/período, gráficos e tabelas.], [Comparar lojas; exportar relatório.],
)

Nos ecrãs de oficina, as ações frequentes devem estar disponíveis com botões grandes, texto curto e contraste adequado, permitindo utilização em tablets e reduzindo o número de interações necessárias.

#prompt-box[
  *Prompt*

  Atua como Arquiteto de Software e revê a Etapa 2 do relatório DLMCare. Mantendo a arquitetura em três camadas, acrescenta os artefactos que faltam para cumprir o enunciado: revisão do modelo de domínio, diagrama de componentes, diagramas de sequência, especificação preliminar da API REST, design de interfaces/wireframes textuais, decisões arquiteturais e critérios de conclusão da Etapa 2.

  #v(6pt)
  *Análise Crítica*

  A resposta foi aceite parcialmente e adaptada. A equipa manteve a arquitetura original (Vue.js, FastAPI e MySQL), mas reforçou a documentação técnica com artefactos que estavam ausentes. A principal decisão crítica foi separar o conceito de peça de catálogo do stock por loja, porque a mesma referência pode existir em várias filiais com quantidades diferentes. Também se validou que as operações de stock e faturação devem ser transacionais para evitar inconsistências.

  #v(6pt)
  *Modelo:* ChatGPT
]

// ============================================================
// CAPÍTULO 3 — IMPLEMENTAÇÃO
// ============================================================
= Capítulo 3 — Implementação do Sistema

== 7. Implementação do Backend Aplicacional

=== 7.1 Organização e Abordagem de Desenvolvimento

A implementação do backend cobriu a camada aplicacional do sistema DLMCare com FastAPI e Python 3.13. O trabalho abrangeu a definição do contrato da API, a modelação dos schemas de dados, o sistema de autenticação e controlo de acesso baseado em perfis, e o desenvolvimento de todos os módulos funcionais.

A arquitetura segue uma estrutura em camadas bem definida:

- *Schemas (DTOs)* — definição das estruturas de dados de entrada e saída com Pydantic v2, incluindo validações de negócio embutidas.
- *Routers* — camada de exposição HTTP, responsável pela receção dos pedidos, validação de autenticação/autorização e encaminhamento para os serviços.
- *Services* — camada de lógica de negócio, onde residem as regras do domínio, as validações de estado e os cálculos.
- *Utils* — funcionalidades auxiliares transversais: geração de PDF, envio de email e verificação de permissões partilhadas.

Para garantir desenvolvimento incremental e independência relativamente à base de dados (desenvolvida por outro elemento da equipa), os serviços foram inicialmente implementados com dados em memória (mocks), desenhados para integração posterior com repositórios reais sem alteração da lógica de negócio.

=== 7.2 Contrato da API

Antes de qualquer implementação, foi definido um contrato formal da API no ficheiro #raw("docs/backend_api_contract_etapa3.md") (aproximadamente 1600 linhas). Esta abordagem API-first permitiu que o frontend fosse desenvolvido em paralelo com o backend, eliminando ambiguidades entre as duas partes e servindo como referência vinculativa para ambas.

O contrato estabelece:

- Prefixo base: #raw("/api/v1") em todos os endpoints.
- Formato de resposta simples: `{"data": {...}, "message": "..."}`.
- Formato de resposta paginada: `{"data": [...], "total": N, "page": 1, "page_size": 20, "pages": M}`.
- Formato de erro normalizado: `{"detail": "...", "code": "..."}` com códigos semânticos como `INVALID_CREDENTIALS`, `PERMISSION_DENIED`, `LOJA_MISMATCH`, `RESOURCE_NOT_FOUND`, `DUPLICATE_ENTRY`, `INVALID_STATE_TRANSITION`, `INSUFFICIENT_STOCK`, entre outros.
- Documentação de cada endpoint: método, path, perfis autorizados, exemplos de request/response, erros possíveis e estado de implementação.

#prompt-box[
  *Prompts 1 e 2 — Análise Inicial e Contrato da API*

  Analisa o backend do projeto DLMCare e devolve: o estado atual, o que falta implementar para a Etapa 3, a ordem de implementação recomendada, e os riscos ou incoerências a corrigir antes de programar. Regras: não escrevas código; a faturação segue a regra `valor_final = preco_servico + subtotal_pecas`; o `preco_custo` das peças é interno e nunca entra no valor cobrado ao cliente.

  #v(6pt)
  Em seguida, define o contrato formal da API em `docs/backend_api_contract_etapa3.md`, cobrindo todos os módulos (auth, clientes, trotinetes, peças, stock, ordens de serviço, faturas, dashboard, auditoria), com perfis autorizados, exemplos JSON de request/response, erros possíveis e convenções globais: prefixo `/api/v1`, autenticação Bearer JWT, formato de erro normalizado com campo `code` semântico, paginação. Sempre que algo depender da BD, marcar como "pendente de integração com BD". A falta de BD não bloqueia o backend — os services podem ser implementados com dados mockados.

  #v(6pt)
  *Análise Crítica*

  A análise inicial confirmou que o backend tinha apenas infraestrutura base, sem qualquer lógica aplicacional implementada. A ordem de implementação sugerida — schemas → auth → routers/services mockados → integração com BD — foi adotada na íntegra. A abordagem API-first, com o contrato de aproximadamente 1600 linhas criado antes de qualquer linha de código, foi a decisão mais impactante do projeto: permitiu que o frontend fosse desenvolvido em paralelo sem ambiguidades e serviu de referência vinculativa para ambas as partes. O principal ajuste ao output foi a clarificação explícita de que o campo `preco_custo` nunca poderia aparecer em respostas públicas da API, aspeto depois reforçado nas notas para implementação do contrato.

  #v(6pt)
  *Modelo:* Claude
]

=== 7.3 Schemas e Validações

Todos os contratos de dados foram modelados em Pydantic v2, no diretório #raw("backend/app/schemas/"). Os schemas asseguram validação automática dos dados de entrada antes de atingirem a lógica de negócio. Foram criados 15 ficheiros de schemas, cobrindo todas as entidades do sistema (incluindo o ficheiro `common.py` com os schemas de resposta genérica paginada e envelope de dados, partilhados por todos os módulos).

Os enums definem os valores possíveis dos campos controlados, nomeadamente `PerfilUtilizador` (quatro perfis), `EstadoOrdemServico` (oito estados), `TipoEventoAuditoria` (31 eventos auditáveis), `CategoriaPeca`, `EstadoFatura` e `TipoMovimentoStock`, entre outros.

As validações embutidas nos schemas incluem:

- *NIF português:* exatamente 9 dígitos numéricos.
- *Telemóvel:* 9 dígitos, começando obrigatoriamente por 9.
- *Consentimento RGPD:* campo booleano obrigatoriamente `true` no registo de clientes — o valor `false` é rejeitado com HTTP 422 antes de chegar à lógica de negócio.
- *Valores monetários:* maior ou igual a 0.
- *`preco_custo` das peças nunca exposto:* o schema `PecaResponse` não inclui este campo. O `preco_custo` é armazenado internamente no serviço mas nunca serializado em nenhuma resposta pública da API.

#prompt-box[
  *Prompt 3 — Schemas Pydantic e Enums*

  Implementa todos os schemas Pydantic v2 do backend DLMCare em `backend/app/schemas/`, com base no contrato `docs/backend_api_contract_etapa3.md`. Cobrir todas as entidades (auth, clientes, trotinetes, peças, stock, OS, faturas, dashboard, auditoria) com validações embutidas: NIF com exatamente 9 dígitos numéricos, telemóvel português com 9 dígitos e começado por 9, `consentimento_rgpd` obrigatoriamente `true` no registo de clientes, valores monetários >= 0. Regra crítica: `PecaResponse` e todos os schemas de resposta pública não devem incluir o campo `preco_custo`. Usar `ConfigDict(from_attributes=True)` para futura integração com ORM.

  #v(6pt)
  *Análise Crítica*

  Os 15 ficheiros de schemas foram gerados com elevada fidelidade ao contrato. O ponto mais sensível — a exclusão do `preco_custo` do `PecaResponse` — foi respeitado desde o início, com o campo armazenado apenas internamente no serviço mas nunca serializado. A validação do consentimento RGPD como campo obrigatoriamente `true` (rejeitando `false` com HTTP 422 antes de atingir a lógica de negócio) foi uma melhoria proposta pelo modelo que fortalece a conformidade legal. Os enums — nomeadamente `EstadoOrdemServico` com os oito estados e `TipoEventoAuditoria` com 31 eventos auditáveis — foram validados manualmente contra o contrato para garantir que nenhum valor antigo ou inconsistente foi introduzido.

  #v(6pt)
  *Modelo:* Claude
]

=== 7.4 Autenticação e Controlo de Acesso

O sistema de autenticação foi implementado com tokens JWT em #raw("app/core/security.py"), com as dependências FastAPI correspondentes em #raw("app/auth/dependencies.py").

*Tokens JWT:* em cada autenticação são emitidos dois tokens — um access token (validade de 8 horas) e um refresh token de duração mais longa. O payload inclui `sub` (ID do utilizador), `nome`, `email`, `perfil`, `loja_id`, `loja_nome` e `ativo`. Toda a informação do utilizador viaja no token, pelo que nenhum acesso à base de dados é necessário para validar um pedido autenticado. A segurança das passwords utiliza bcrypt com o custo por omissão de 12 rounds (confirmado nos hashes do seed: `$2b$12$...`), chamando `bcrypt.gensalt()` diretamente para contornar uma incompatibilidade conhecida entre `passlib 1.7.4` e `bcrypt >= 5.x`.

*Controlo de acesso por perfil (RBAC):* a dependência `require_roles(*perfis)` é uma factory que gera dependências FastAPI reutilizáveis para cada endpoint. Uma tentativa de acesso sem o perfil adequado devolve 403 com código `PERMISSION_DENIED`.

*Multi-tenancy por loja:* todos os utilizadores com perfil diferente de `ADMINISTRADOR` têm um `loja_id` obrigatório no token. A dependência `get_loja_context()` garante que não-administradores apenas acedem aos dados da sua loja — o acesso a dados de outra loja resulta em 403 `LOJA_MISMATCH`. O `ADMINISTRADOR` tem `loja_id = null` e acesso global a todos os dados.

#prompt-box[
  *Prompts 4 e 5 — Autenticação JWT e Controlo de Acesso por Perfil*

  Implementa a camada de autenticação e RBAC em `app/core/security.py` e `app/auth/dependencies.py`. O payload JWT deve incluir `sub`, `nome`, `email`, `perfil`, `loja_id`, `loja_nome` e `ativo` — sem qualquer acesso à BD para validar pedidos autenticados. Implementa a factory `require_roles(*perfis)` e a dependência `get_loja_context()`, que garante que utilizadores não administradores só acedem aos dados da sua loja. Nota obrigatória: `passlib 1.7.4` é incompatível com `bcrypt >= 5.x` — usar `bcrypt` diretamente com `bcrypt.gensalt()` em vez de `passlib`. Em seguida, implementa o router e service de autenticação com utilizadores mockados em memória, um por cada perfil, com hashes bcrypt pré-calculados.

  #v(6pt)
  *Análise Crítica*

  A incompatibilidade entre `passlib 1.7.4` e `bcrypt >= 5.x` foi o primeiro obstáculo técnico real da implementação — o modelo identificou-a e propôs a solução de contornar o passlib chamando `bcrypt` diretamente, o que se revelou a abordagem correta e estável. A decisão de incluir toda a informação do utilizador no payload JWT elimina a necessidade de aceder à BD para autenticar qualquer pedido, o que foi fundamental para o desenvolvimento incremental antes da integração com a base de dados. A factory `require_roles` foi validada com todos os perfis e a dependência `get_loja_context` foi especialmente importante para garantir o isolamento de dados entre filiais.

  #v(6pt)
  *Modelo:* Claude
]

=== 7.5 Módulos Funcionais

O backend expõe 14 módulos funcionais, cada um com o seu router e serviço correspondente, todos registados com o prefixo #raw("/api/v1"):

*Autenticação (#raw("/auth")):* `POST /login` devolve par de tokens; `POST /refresh` renova o par a partir de um refresh token válido; `GET /me` devolve o perfil do utilizador autenticado diretamente a partir do token, sem acesso à BD.

*Clientes (#raw("/clientes")):* registo com validação de NIF único, telemóvel e consentimento RGPD; listagem com filtragem automática por loja para não-administradores; detalhe com trotinetes associadas e histórico de ordens de serviço; nível de fidelização e desconto sugerido calculados por cliente (RF16, descrito na secção 7.7).

*Trotinetes (#raw("/trotinetes")):* associação obrigatória a um cliente; número de série único validado; filtragem por cliente.

*Peças (#raw("/pecas")):* catálogo global com categorização; distinção obrigatória entre `preco_custo` (interno) e `preco_venda` (exposto ao cliente); filtragem por categoria e pesquisa por nome/referência.

*Stock (#raw("/stock")):* gestão de inventário por loja; entradas de stock; transferências diretas entre lojas; alertas automáticos quando `quantidade <= limite_minimo`; consumo automático de stock ao adicionar uma peça a uma OS.

*Ordens de Serviço (#raw("/ordens-servico")):* módulo central, descrito em detalhe na secção 7.6.

*Faturação (#raw("/faturas")):* emissão de faturas com cálculo de valor final, descontos comerciais e geração/envio de PDF; descrito na secção 7.7.

*Dashboard (#raw("/dashboard")):* métricas calculadas dinamicamente — ordens por estado, ordens concluídas por loja, tempo médio de reparação no período, faturação total, peças abaixo do stock mínimo e eficiência por mecânico (ordens concluídas e minutos trabalhados totais, com base nos registos de tempo individuais).

*Auditoria (#raw("/auditoria")):* registo de 31 tipos de eventos, cobrindo autenticação (sucesso e falha), ciclo de vida das OS, movimentações de stock, transferências, pedidos de peça, emissão de faturas e alterações a todas as entidades do sistema (incluindo `LOJA_CRIADA` e `LOJA_ATUALIZADA`). Administradores veem todos os registos; gestores veem apenas os da sua loja.

*Utilizadores (#raw("/utilizadores")):* gestão de staff pelo administrador — criação, edição de dados, desativação de contas e reposição de password; protegido exclusivamente para `ADMINISTRADOR`.

*Lojas (#raw("/lojas")):* listagem e detalhe de lojas; administradores veem todas; restantes perfis veem apenas a sua loja.

*Transferências e Pedidos de Peça (#raw("/transferencias"), #raw("/pedidos-peca")):* fluxo de pedido de transferência entre lojas com aprovação do gerente da loja de origem, deduções e adições de stock automáticas, e geração de PDF do documento de transferência. Pedido de peça do mecânico ao gerente quando o stock está esgotado numa OS. Ambos os fluxos geram notificações em tempo real ao destinatário.

*Catálogo de Serviços (#raw("/servicos")):* gestão do catálogo de serviços predefinidos, com nome e preço base, utilizados no diagnóstico das OS; criação e edição restritas a `ADMINISTRADOR` e `GERENTE_LOJA`.

*Notificações (#raw("/notificacoes")):* inbox de notificações por utilizador; contagem de não lidas; marcação como lida individual ou em massa.

#prompt-box[
  *Prompts 6 a 13 — Routers e Services por Módulo*

  Para cada módulo do sistema (clientes, trotinetes, peças, stock, ordens de serviço, faturas, dashboard, auditoria), implementa o service com dados mockados em memória e o router FastAPI correspondente, seguindo o contrato `docs/backend_api_contract_etapa3.md`. Regras transversais: o service deve filtrar dados por `loja_id` automaticamente para perfis não-`ADMINISTRADOR`; os imports entre services devem ser locais (dentro das funções) para evitar dependências circulares; os helpers internos (`get_peca_interna`, `consumir_stock`, `get_os_interna`) devem ser expostos para uso entre services. O `preco_custo` nunca deve aparecer em nenhum cálculo nem em nenhuma resposta. Os services devem ser desenhados para integração futura com repositórios reais sem alteração da lógica de negócio.

  #v(6pt)
  *Análise Crítica*

  O padrão de desenvolvimento schema → router → service mockado mostrou-se consistente e produtivo ao longo dos oito módulos. O principal problema recorrente foi a gestão de imports circulares entre services interdependentes (por exemplo, `cliente_service` a chamar `trotinete_service` para popular o detalhe do cliente) — resolvido com imports locais dentro das funções, padrão sugerido pelo modelo e adotado como convenção do projeto. O filtro automático de `loja_id` nos services para perfis não-administrador foi um ponto crítico de segurança que exigiu revisão em cada módulo para garantir que nenhum endpoint expunha dados de outras filiais. A estratégia de dados mockados em memória permitiu que o frontend avançasse em paralelo sem depender da integração com a BD.

  #v(6pt)
  *Modelo:* Claude
]

=== 7.6 Máquina de Estados das Ordens de Serviço

As Ordens de Serviço constituem o núcleo operacional do sistema e seguem uma máquina de estados com 8 estados e transições controladas por perfil:

#block(
  stroke: (left: 2pt + rgb("#2255aa")),
  inset: (left: 10pt, top: 6pt, bottom: 6pt),
  fill: rgb("#f4f8ff"),
)[
  `PENDENTE` → `EM_DIAGNOSTICO` → `EM_REPARACAO` ↔ `AGUARDA_PECAS` → `CONCLUIDA` → `FATURADA` \
  `AGUARDA_APROVACAO` → `EM_REPARACAO` (by-pass manual para aprovação do gerente, quando aplicável) \
  Qualquer estado anterior a `FATURADA` pode transitar para `CANCELADA`.
]

As transições permitidas e os perfis autorizados a executá-las encontram-se definidos numa tabela `_TRANSICOES` no serviço. A tentativa de uma transição inválida devolve 409 `INVALID_STATE_TRANSITION`; a tentativa por um perfil não autorizado devolve 403 `PERMISSION_DENIED`.

*Fluxo de diagnóstico:* ao concluir o diagnóstico, o mecânico submete os serviços identificados a partir do catálogo (podendo adicionar entradas personalizadas). O sistema calcula automaticamente o `preco_servico` como soma dos preços dos serviços selecionados, transita a OS diretamente para `EM_REPARACAO` e envia automaticamente um email ao cliente com o resumo das operações a realizar.

*Registo de tempos:* cada sessão de trabalho ativa é registada com início, fim e minutos acumulados, associados ao mecânico responsável. Uma tentativa de iniciar um timer numa OS que já tem um timer ativo devolve 409 com a mensagem `"Já existe um timer ativo nesta OS."`, prevenindo registos duplicados.

*Observações internas:* todos os perfis autenticados podem adicionar observações internas a uma OS. As transições de estado com texto de observação são guardadas automaticamente com um prefixo identificativo (ex.: `[Conclusão da Reparação]`), diferenciando-as de notas livres.

*Sinalização de atraso (RF17):* cada OS em curso é comparada contra o tempo médio de conclusão histórico. As que excedem essa média são sinalizadas com `em_atraso: true` e `minutos_em_atraso` calculados, permitindo filtragem no endpoint de listagem.

*Reatribuição de mecânico:* administradores e gestores podem reatribuir ou remover o mecânico de uma OS a qualquer momento. A reatribuição encerra automaticamente qualquer timer aberto pelo mecânico anterior, preservando os minutos acumulados.

#prompt-box[
  *Prompt 10 (excerto) — Máquina de Estados das Ordens de Serviço*

  Define a tabela `_TRANSICOES` com pares `(estado_atual, estado_novo)` mapeados para os perfis autorizados a executar cada transição. A transição `CONCLUIDA → FATURADA` não deve constar desta tabela — deve ser acionada exclusivamente via `POST /faturas`, para garantir que uma OS nunca transita para `FATURADA` sem uma fatura efetivamente criada. Ao concluir o diagnóstico, o sistema deve calcular `preco_servico` como soma dos preços dos serviços selecionados do catálogo e transitar automaticamente para `EM_REPARACAO`, enviando um email ao cliente com o resumo das operações a realizar.

  #v(6pt)
  *Análise Crítica*

  A exclusão de `CONCLUIDA → FATURADA` da tabela de transições do service de OS foi o aspeto mais crítico desta implementação: o output inicial incluía essa transição na tabela geral, o que permitiria transitar o estado sem criar uma fatura — uma inconsistência financeira grave. A correção foi aplicada após revisão manual. O registo de observações automáticas com prefixo identificativo por tipo de transição (ex.: `[Conclusão da Reparação]`) foi uma melhoria proposta em iteração posterior para distinguir observações de transição de notas livres, tornando o historial da OS mais legível. A funcionalidade de arranque automático do timer ao entrar em `EM_DIAGNOSTICO` ou `EM_REPARACAO` foi igualmente acrescentada após feedback de que o timer manual introduzia fricção operacional desnecessária.

  #v(6pt)
  *Modelo:* Claude
]

=== 7.7 Regras de Negócio

*Regra de faturação:* o valor final de uma fatura é calculado exclusivamente como:

#block(
  stroke: (left: 2pt + rgb("#2255aa")),
  inset: (left: 10pt, top: 8pt, bottom: 8pt),
  fill: rgb("#f4f8ff"),
)[
  $"valor_final" = "preco_servico" + "subtotal_pecas"$

  onde $"subtotal_pecas" = sum("quantidade" times "preco_venda_unitario")$
]

O `preco_custo` das peças nunca entra em nenhum cálculo exposto ao cliente. Esta invariante é garantida a dois níveis: o schema `PecaResponse` não inclui o campo, e o serviço de faturação usa exclusivamente o snapshot de `preco_venda_unitario` registado no momento em que a peça foi adicionada à OS — evitando discrepâncias caso o preço de venda seja alterado posteriormente.

*Desconto de fidelização (RF16):* o nível de fidelização do cliente é calculado automaticamente com a fórmula:

#block(
  stroke: (left: 2pt + rgb("#2255aa")),
  inset: (left: 10pt, top: 8pt, bottom: 8pt),
  fill: rgb("#f4f8ff"),
)[
  $"nivel" = min(5, floor(log_2("n_concluidas" + 1)))$
]

O nível máximo é 5, correspondendo a 10% de desconto (2% por nível). O desconto sugerido é apresentado no momento de emissão da fatura, podendo ser ajustado manualmente. Suporta descontos percentuais e fixos.

*Unicidade de faturas:* uma OS só pode ter uma fatura associada. A tentativa de emitir uma segunda fatura para a mesma OS resulta em 409 `ORDER_ALREADY_INVOICED`, verificado antes da validação de estado para cobrir o caso em que a OS já transitou para `FATURADA`.

=== 7.8 Funcionalidades Auxiliares

*Geração de PDF (#raw("utils/pdf.py")):* faturas e documentos de transferência são gerados em PDF com fpdf2 2.8.3, incluindo cabeçalho com identidade da loja, dados do cliente e trotinete, tabela de peças e serviços, e secção de totais com desconto quando aplicável.

*Envio de email (#raw("utils/email.py")):* notificações automáticas ao cliente em português com templates HTML para quatro eventos — trotinete pronta para levantamento, OS cancelada (RF14), resumo do diagnóstico, e fatura com PDF em anexo. O envio utiliza `BackgroundTasks` do FastAPI para não bloquear a resposta HTTP. Falhas de SMTP são silenciosas, não afetando o resultado da operação principal.

*Tratamento global de erros:* um exception handler registado em #raw("main.py") converte os erros de validação Pydantic (HTTP 422) para o formato de erro normalizado do contrato, garantindo consistência em todas as respostas de erro da API.

#prompt-box[
  *Prompts 11 e Utilitários — Faturação, PDF e Notificações por Email*

  Implementa o service de faturação com a regra obrigatória: `valor_final = preco_servico + subtotal_pecas`, onde `subtotal_pecas = Σ(quantidade × preco_venda_unitario)`. A verificação de fatura duplicada (`ORDER_ALREADY_INVOICED`) deve ser feita *antes* da verificação de estado, uma vez que após a primeira emissão a OS já se encontra em `FATURADA` e não `CONCLUIDA` — inverter esta ordem resultaria no erro errado. O `preco_custo` nunca deve entrar em nenhum cálculo. Implementa também os utilitários de geração de PDF com `fpdf2` e envio de email via SMTP, usando `BackgroundTasks` do FastAPI para não bloquear a resposta HTTP. Falhas de SMTP devem ser silenciosas.

  #v(6pt)
  *Análise Crítica*

  A ordem das verificações na emissão de faturas foi o ponto mais subtil de toda a implementação: se a verificação de estado (`CONCLUIDA`) fosse feita antes da verificação de fatura duplicada, uma OS já faturada — que transitou para `FATURADA` — devolveria um erro de estado em vez do código semântico correto `ORDER_ALREADY_INVOICED`. Este bug potencial foi identificado pelo modelo e prevenido na estrutura do service. A integração do envio de email com `BackgroundTasks` revelou-se a escolha certa: as falhas de SMTP tornaram-se silenciosas e não afetam o resultado da operação principal, um tradeoff aceitável dado que o email é uma notificação e não uma operação crítica de negócio. A geração de PDF com `fpdf2` foi implementada sem necessidade de revisão adicional.

  #v(6pt)
  *Modelo:* Claude
]

=== 7.9 Organização e Arquitetura de Persistência

A implementação direta da camada de persistência marcou a consolidação da arquitetura do sistema. Esta base de dados real foi desenvolvida utilizando *MySQL 8.0*, suportada pelo driver compatível nativo `PyMySQL` e pelo ORM (Object-Relational Mapper) *SQLAlchemy 2.0*.

Para garantir o baixo acoplamento e manter a escalabilidade do sistema desde o primeiro momento, adotou-se estritamente o *Repository Pattern*. Esta decisão arquitetural dividiu a responsabilidade de manipulação de dados de forma clara:

- *Repositories* (#raw("app/repositories/")) — classes dedicadas exclusivamente à interação com a base de dados via SQLAlchemy (ex: `ClienteRepository`, `OrdemServicoRepository`). Não contêm lógica de negócio nem invocam exceções HTTP.
- *Services* — recebem a injeção da sessão de base de dados (`db: Session`) e orquestram as chamadas aos repositórios, centralizando toda a lógica de processamento e regras do domínio.
- *Routers* — limitam-se a injetar a dependência `Depends(get_db)` e a encaminhá-la para a camada de serviço, mantendo a sua assinatura contratual focada apenas na validação de inputs e outputs.

Esta abordagem permitiu um desenvolvimento estruturado e garantiu o cumprimento estrito do contrato da API previamente estabelecido (#raw("docs/backend_api_contract_etapa3.md")).

=== 7.10 Modelação e Estrutura Relacional

A modelação de dados utilizou a sintaxe moderna e tipada do SQLAlchemy 2.0, baseada em `Mapped[tipo]` e `mapped_column`, o que garante coerência estrita com o analisador estático do Python e com os schemas do Pydantic.

A estrutura relacional assenta num forte esquema de dependências e restrições de integridade, refletindo a hierarquia do domínio de negócio:

- *Identidade e Acessos:* As tabelas `lojas` e `utilizadores` estabelecem a base de multi-tenancy. A chave estrangeira `loja_id` propaga-se a quase todas as entidades do sistema (Clientes, Ordens de Serviço, Stock).
- *Gestão Operacional:* A entidade central `ordens_servico` possui múltiplas relações complexas: chaves estrangeiras para `trotinetes`, `clientes`, `mecanico_id` e tabelas de junção detalhadas como `os_pecas` (snapshot do preço no momento da aplicação) e `os_servicos` (catálogo de serviços aplicados no diagnóstico).
- *Gestão de Catálogo:* O isolamento do catálogo global na tabela `pecas` versus a tabela `stock_lojas` (entidade associativa que guarda a quantidade física e o `limite_minimo` por filial).

=== 7.11 Integridade Transacional (ACID)

A conformidade com as propriedades ACID do MySQL foi um requisito não-negociável, garantido através do controlo transacional ao nível do serviço (e não do repositório). Esta centralização é vital em operações complexas.

Um exemplo crítico desta implementação ocorre na rotação de estado e faturação: no processo de emissão de uma fatura (`fatura_service.emitir()`), o sistema precisa de verificar se a Ordem de Serviço está concluída, calcular o subtotal com base nas peças aplicadas, criar o registo na tabela `faturas`, atualizar o estado da OS para `FATURADA` e gerar o registo de auditoria.

Ao executar um único `db.commit()` no final do fluxo do serviço, o SQLAlchemy assegura que todas estas operações SQL decorrem na mesma transação fechada. O uso estratégico do `db.flush()` permite obter os IDs auto-incrementados (necessários para formatar o número da fatura) sem fechar a transação. Se ocorrer qualquer anomalia computacional ou quebra de restrição de integridade no MySQL, é feito um `rollback` automático, impedindo a existência de faturas "órfãs" ou Ordens de Serviço faturadas sem registo financeiro.

#block(
  fill: rgb("#f5f5f5"),
  inset: 10pt,
  radius: 4pt,
  width: 100%,
)[
#set text(font: "Cascadia Code", size: 8pt)
```python
def emitir(self, body: FaturaCreateRequest, current_user: CurrentUserResponse) -> FaturaResponse:
    os = self.os_repo.get_by_id(body.ordem_servico_id)
    if not os:
        raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada")

    if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and os.loja_id != current_user.loja_id:
        raise HTTPException(status_code=403, detail="Não tem permissões para esta Ordem de Serviço")

    if os.fatura:
        raise HTTPException(
            status_code=409,
            detail={"detail": "A Ordem de Serviço já se encontra faturada.",
                    "code": "ORDER_ALREADY_INVOICED"}
        )

    if os.estado != EstadoOrdemServico.CONCLUIDA:
        raise HTTPException(
            status_code=400,
            detail={"detail": "Ordem de Serviço não está concluída.",
                    "code": "ORDER_NOT_CONCLUDED"}
        )

    subtotal_pecas = sum(peca.quantidade * peca.preco_venda_unitario for peca in os.pecas_aplicadas)

    # Cálculo do desconto
    desconto_tipo = body.desconto_tipo.value if body.desconto_tipo else None
    desconto_valor = body.desconto_valor
    if body.desconto_tipo is None or body.desconto_valor == 0.0:
        valor_desconto = 0.0
    elif body.desconto_tipo.value == "PERCENTUAL":
        base = os.preco_servico + subtotal_pecas
        valor_desconto = round(base * body.desconto_valor / 100, 2)
    else:  # FIXO
        valor_desconto = body.desconto_valor

    valor_final = os.preco_servico + subtotal_pecas - valor_desconto

    # Cria Fatura na sessão com numero=None; flush para obter o ID auto-incrementado
    nova_fatura = self.fatura_repo.create(
        numero=None,
        ordem_servico_id=os.id,
        estado=EstadoFatura.EMITIDA,
        subtotal_pecas=subtotal_pecas,
        valor_final=valor_final,
        data_emissao=datetime.now(timezone.utc),
        desconto_tipo=desconto_tipo,
        desconto_valor=desconto_valor,
        valor_desconto=valor_desconto,
    )

    self.db.flush()  # Obtém o ID sem fazer commit
    year = datetime.now(timezone.utc).year
    nova_fatura.numero = f"FAT-{year}-{nova_fatura.id:04d}"
    numero_fatura = nova_fatura.numero

    os.estado = EstadoOrdemServico.FATURADA

    # Registo de auditoria
    self.auditoria_repo.registar(
        evento=TipoEventoAuditoria.FATURA_EMITIDA,
        descricao=f"Fatura {numero_fatura} emitida para a OS #{os.id}",
        utilizador_id=current_user.id,
        loja_id=os.loja_id,
        detalhe={"ordem_servico_id": os.id, "valor_final": valor_final}
    )

    self.db.commit()  # Efetiva todas as operações na base de dados
    fatura_completa = self.fatura_repo.get_by_id(nova_fatura.id)
    return self._build_fatura_response(fatura_completa)
```
]

=== 7.12 Controlo de Versões (Alembic) e Povoamento de Dados

A evolução do esquema da base de dados foi gerida através da ferramenta de migrations *Alembic*, operando em sintonia com os modelos declarativos do SQLAlchemy.

Para além da infraestrutura aplicacional, foram desenvolvidos scripts SQL nativos para cobrir as fases de provisionamento e testes da aplicação:

- *`init.sql`* — Script de inicialização executado como `root`, focado no princípio do menor privilégio. Cria o esquema `dlmcare` com charset `utf8mb4` (suporte universal de caracteres) e o utilizador aplicacional `dlmcare_user`, limitando as permissões estruturais (`GRANT`) exclusivamente a esta base de dados.
- *`seed.sql`* — Script base responsável por injetar o catálogo de dados estáticos para as três filiais (Lisboa, Porto, Braga), 12 peças representativas com limites mínimos e quantidades, 20 serviços de diagnóstico base e utilizadores com hashes `bcrypt` reais.
- *`demo_data.sql`* — Um script avançado com foco na testagem de dashboards e paginação. Introduz complexidade temporal simulando 29 Ordens de Serviço distribuídas entre janeiro e maio de 2026, com faturas reais emitidas, mecânicos distintos, cálculos com níveis de fidelização dinâmicos e tempos de reparação acumulados.

=== 7.13 Gestão de Sessões e Connection Pooling

A estabilidade do sistema sob carga é garantida pela forma como o backend gere as ligações ao MySQL. A criação contínua de novas conexões TCP à base de dados para cada pedido HTTP seria um estrangulamento de performance.

Para resolver isto, o sistema foi configurado com o `create_engine` do SQLAlchemy utilizando *Connection Pooling*. A sessão transacional é gerada e injetada dinamicamente em cada endpoint através do sistema de *Dependency Injection* do FastAPI (`Depends(get_db)`). Esta abordagem utiliza um gerador Python (`yield`), assegurando que a sessão é aberta no início do pedido HTTP e que o `db.close()` é garantido no final, mesmo na ocorrência de exceções não tratadas, prevenindo memory leaks e deadlocks no MySQL.

=== 7.14 O Padrão Repository na Prática: Mitigação de Problemas e Queries Dinâmicas

Para evidenciar a robustez da camada de persistência, destacam-se duas implementações nos repositórios que resolvem problemas clássicos de mapeamento objeto-relacional (ORM).

==== 7.14.1 Prevenção de N+1 Queries (Lazy Loading vs Eager Loading)

O acesso a entidades com múltiplas chaves estrangeiras (como uma Ordem de Serviço, que depende do Cliente, Trotinete e Peças) gera frequentemente dezenas de queries subjacentes se não for controlado. No `OrdemServicoRepository`, utiliza-se `joinedload` para instruir o SQLAlchemy a resolver todas as relações através de `LEFT OUTER JOINs` numa única transação SQL.

#block(
  fill: rgb("#f5f5f5"),
  inset: 10pt,
  radius: 4pt,
  width: 100%,
)[
#set text(font: "Cascadia Code", size: 8pt)
```python
def get_by_id(self, os_id: int) -> OrdemServico | None:
    return self.db.query(OrdemServico).options(
        joinedload(OrdemServico.cliente),
        joinedload(OrdemServico.trotinete),
        joinedload(OrdemServico.mecanico),
        joinedload(OrdemServico.pecas_aplicadas).joinedload(OSPeca.peca),
        joinedload(OrdemServico.registos_tempo)
    ).filter(OrdemServico.id == os_id).first()
```
]

Esta abordagem reduz potencialmente dezenas de queries individuais a uma única operação SQL com JOINs, independentemente do número de relações carregadas.

==== 7.14.2 Consultas Dinâmicas, Filtros e Paginação

Módulos como o Dashboard ou o Histórico exigem consultas complexas. O `AuditoriaRepository` demonstra como o sistema constrói queries dinâmicas em tempo real, anexando cláusulas `WHERE` apenas quando os filtros são fornecidos pelo utilizador, e aplicando lógica de paginação (`offset` e `limit`) a nível da base de dados para minimizar a transferência de dados pesados pela rede.

#block(
  fill: rgb("#f5f5f5"),
  inset: 10pt,
  radius: 4pt,
  width: 100%,
)[
#set text(font: "Cascadia Code", size: 8pt)
```python
def listar(self, loja_id: int | None = None, evento: str | None = None,
           data_inicio=None, data_fim=None, page: int = 1, page_size: int = 20):

    query = self.db.query(Auditoria).options(joinedload(Auditoria.utilizador))

    if loja_id is not None:
        query = query.filter(Auditoria.loja_id == loja_id)
    if evento is not None:
        query = query.filter(Auditoria.evento == evento)
    if data_inicio is not None:
        query = query.filter(func.date(Auditoria.timestamp) >= data_inicio)

    total = query.count()
    skip = (page - 1) * page_size
    itens = query.order_by(Auditoria.timestamp.desc()).offset(skip).limit(page_size).all()

    return itens, total
```
]

A construção dinâmica da query evita a criação de múltiplas funções especializadas, mantendo um único ponto de entrada para todas as combinações de filtros possíveis.

// ============================================================
// CAPÍTULO 4 — VERIFICAÇÃO E QUALIDADE
// ============================================================
= Capítulo 4 — Verificação, Validação e Avaliação da Qualidade do Software Produzido

A garantia da qualidade é um pilar fundamental no desenvolvimento de sistemas de informação complexos, especialmente em contextos onde a integridade dos dados e a fiabilidade das operações — como a faturação, gestão de inventário e diagnósticos de manutenção — são críticas para o funcionamento do negócio. No âmbito do projeto DLMCare, a estratégia de testes foi concebida para assegurar que a implementação não só cumpre os requisitos funcionais estabelecidos, mas que é também resiliente a erros inesperados e inconsistências de estado.

A presente etapa descreve a metodologia de testes adotada, baseada no princípio da pirâmide de testes, privilegiando testes de integração que validam o fluxo completo de interação entre a API, a camada de serviços (Business Logic) e a persistência de dados. A abordagem focou-se em três eixos principais: a verificação de fluxos de sucesso (Happy Paths), o robustecimento contra condições de erro e estados inválidos (Edge Cases e Negative Testing), e a garantia de que as regras de negócio e restrições de integridade da base de dados são rigorosamente respeitadas.

Através de uma suite de testes automatizados e da análise contínua de métricas de cobertura de código (Code Coverage), foi possível identificar e mitigar falhas precocemente, reduzindo o risco de regressões e garantindo que o sistema mantém um comportamento previsível e seguro, mesmo sob condições de operação adversas.

== 8. Verificação e Testes

=== 8.1 Abordagem e Estratégia de Testes

A estratégia de testes do sistema DLMCare foi desenhada sob a premissa da Pirâmide de Testes, priorizando a integração para validar a lógica de negócio central (Services) e a persistência de dados (Repositories). Esta abordagem garante que as regras de faturação, inventário e transições de estado sejam validadas no seu contexto real de execução.

Para garantir a fiabilidade da suite de testes, estabeleceu-se um ambiente de execução totalmente isolado e determinístico. A escolha de uma base de dados em memória em conjunto com a extensão `StaticPool` do SQLAlchemy não foi arbitrária: esta configuração permite que toda a infraestrutura de persistência resida em RAM, eliminando a latência de I/O de disco e garantindo que o sistema de testes seja extremamente célere. A utilização do `StaticPool` resolve um problema técnico comum em testes paralelos — a "amnésia" de dados. Ao partilhar a mesma conexão de memória entre as diferentes threads de teste, garante-se que todas as operações ocorrem num único contexto de transação, evitando erros de "table not found" ou inconsistências de estado que ocorreriam com pools de conexão padrão.

O estado inicial do sistema é assegurado pela fixture `db_session`, que funciona como um "Gold Standard". Antes de cada teste, esta fixture é responsável pela limpeza de estado (executar um `drop_all` seguido de um `create_all`, garantindo que não existe contaminação de dados proveniente de execuções anteriores) e pelo seed realístico (popular a base de dados com um cenário predefinido contendo Lojas, Utilizadores, Clientes e um inventário de peças e trotinetes). Esta abordagem garante que o sistema de testes é auto-contido: qualquer membro da equipa pode executar a suite de testes no seu ambiente local e obter resultados consistentes, sem a necessidade de configurar servidores de base de dados externos ou gerir migrações de dados prévias.

=== 8.2 Robustez e Validação de Input

A robustez do sistema é garantida pela validação rigorosa na camada de entrada (Pydantic), impedindo que dados corrompidos cheguem à camada de lógica de negócio (Services). Foi implementada uma política de Testes de Negativa onde o objetivo não é o sucesso da operação, mas a garantia de que o sistema falha com o código de erro adequado.

```python
def test_criar_cliente_nif_duplicado(rec_client):
    cliente_data = {
        "nome": "João Ninguém",
        "nif": "123456789",
        "telemovel": "912345678",
        "email": "joao@teste.pt",
        "consentimento_rgpd": True,
    }

    # Caso Normal: Criar cliente
    res1 = rec_client.post("/api/v1/clientes", json=cliente_data)
    assert res1.status_code == 201

    # Edge Case: Tentar criar outro cliente com o MESMO NIF
    res2 = rec_client.post("/api/v1/clientes", json=cliente_data)
    assert res2.status_code in [400, 409]
    assert res2.json()["detail"]["code"] == "DUPLICATE_ENTRY"
```

=== 8.3 Testes de Regras de Negócio e Estados de Transição

A robustez do sistema também é testada através da sua Máquina de Estados das OS. O objetivo é garantir que não existem "atalhos" lógicos que comprometam a integridade financeira ou o inventário.

```python
def test_transferencia_stock_insuficiente(admin_client):
    # A peça 1 e a loja 1 são criadas no conftest. A peça 1 tem 10 de stock na loja 1.
    # Tentamos transferir 11 unidades, o que deve falhar.
    transferencia_data = {
        "peca_id": 1,         # Peca "PNEU-001"
        "loja_origem_id": 1,  # Loja "Braga"
        "loja_destino_id": 2, # Loja "Porto"
        "quantidade": 11,     # Mais do que o stock de 10
    }

    res = admin_client.post("/api/v1/stock/transferencias", json=transferencia_data)

    # A validação de stock deve ser prioritária e falhar.
    assert res.status_code == 400
    assert "insuficiente" in res.json()["detail"].lower()
```

#prompt-box[
  *Prompt*

  Atua como Arquiteto de Software. Preciso de expandir a suite de testes de integração para cobrir dois cenários críticos de integridade: (1) Prevenção de duplicação de entidades baseadas em chaves de negócio (NIF) e (2) Validação de regras de negócio em transações de stock. O teste deve forçar o sistema a devolver erros semânticos (400/409) com o campo detail.code devidamente preenchido conforme o nosso contrato de API, garantindo que o banco de dados nunca entra em estado inconsistente.

  #v(6pt)
  *Análise Crítica*

  A implementação destes testes foi determinante para identificar uma falha na camada de Service, onde a verificação de existência (NIF/Stock) era feita de forma atómica antes da persistência, mas sem bloqueio (locking) adequado. A escrita destes testes forçou a refatoração dos métodos de create nos repositórios para incluir validações de estado pré-transacionais, garantindo que a integridade dos dados é mantida mesmo sob concorrência de pedidos.

  #v(6pt)
  *Modelo:* Gemini
]

=== 8.4 Análise de Cobertura

A maturidade de uma suite de testes é aferida pela sua capacidade de cobrir não apenas o fluxo nominal, mas todas as ramificações lógicas do sistema. Para o projeto DLMCare, a análise de cobertura foi realizada com recurso ao pytest-cov, permitindo uma visão detalhada das áreas do código que permanecem inexploradas pela suite de testes.

A suite atual atinge uma cobertura global de aproximadamente 72%. Este indicador reflete o foco estratégico da nossa equipa: priorizar a robustez da lógica de negócio complexa — presente nos serviços de Ordem de Serviço, Faturação e Stock — em detrimento de camadas periféricas.

#figure(
  caption: [Resumo de cobertura da suite de testes.],
  table(
    columns: (auto, 1fr, 1fr, 1fr),
    inset: 8pt,
    fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
    align: (left, center, center, center),
    table.header(
      [*Camada*], [*Stmts*], [*Miss*], [*Cover*]
    ),
    [Routers], [200], [42], [79%],
    [Repositories], [615], [375], [39%],
    [Services/Transferencia], [445], [178], [60%],
    [Schemas], [218], [15], [93%],
    table.hline(stroke: 1pt),
    [*Total*], [*3125*], [*873*], [*72%*],
  )
)

A análise técnica revela uma dicotomia na maturidade da nossa suite de testes. Enquanto a camada de Routers e Schemas apresenta uma cobertura robusta (superando os 80%), a camada de Services — que encapsula o coração da lógica de negócio da DLMCare — exige um esforço suplementar. Esta disparidade é estratégica: priorizámos a validação das interfaces de contrato (Routers) para garantir a comunicação correta entre o frontend Vue.js e o backend FastAPI. Módulos periféricos como #raw("app/utils/") (gestão de PDFs e notificações por email) apresentam uma cobertura reduzida por três razões conscientes:

- *Diferenciação entre Lógica Crítica e Infraestrutura:* O esforço de testes foi deliberadamente concentrado nas camadas de Services e Repositories, onde residem as regras de negócio vitais — cálculo de faturação, abate de stock em condições de concorrência e preservação do estado das OS.

- *Limitações do Isolamento em Memória:* As funcionalidades de app/utils/ possuem dependências intrínsecas com infraestrutura externa (SMTP e filesystem). O isolamento rigoroso exigido pelos testes em memória (StaticPool) tornaria o mocking destas dependências propenso a falsos positivos. Estes módulos são validados através de testes E2E em ambiente de staging.

- *Rácio de Esforço vs. Risco:* O risco de uma falha lógica num utilitário de formatação de PDF é substancialmente inferior ao risco de uma falha numa transação de inventário. Aplicámos o princípio de priorização baseada em risco.

#prompt-box[
  *Prompt*

  O meu stock_service.py apresenta 38% de cobertura. Analisando o meu test_api.py, percebo que não estou a exercitar os ramos de erro do consumir_stock. Como posso estruturar um teste de integração que force a falha de stock insuficiente e valide o contrato de erro?

  #v(6pt)
  *Análise Crítica*

  A colaboração com a IA permitiu identificar que, embora o fluxo de sucesso estivesse testado, os estados de erro críticos (insuficiência de inventário) eram ignorados pela suite original. A implementação do teste test_stock_consumo_excessivo_service forçou a refatoração do StockService para incluir uma validação atómica antes da transação de persistência, elevando a cobertura do módulo de 38% para 60% e garantindo a integridade dos dados ao impedir valores negativos em inventário.

  #v(6pt)
  *Modelo:* Gemini
]

=== 8.5 Considerações sobre a Qualidade (ISO/IEC 25010)

A avaliação da qualidade do sistema DLMCare foi conduzida sob o paradigma da norma ISO/IEC 25010, utilizando-a como referencial para medir a excelência do software produzido. Para além das métricas de cobertura de código, o projeto foi avaliado em quatro dimensões críticas de qualidade:

- *Adequação Funcional:* O sistema garante a correção e integridade dos processos de negócio. A modelação de estados da Ordem de Serviço e a automatização do abate de stock asseguram que a funcionalidade cumpre estritamente o que foi especificado para a operação multi-loja.

- *Confiabilidade (Reliability):* A maturidade da suite de testes de integração, focada em estados negativos (Negative Testing), confere ao software um elevado nível de tolerância a falhas. A utilização de mecanismos de locking e transações ACID no MySQL garante que o sistema se recupera de falhas sem corromper o histórico transacional.

- *Eficiência de Desempenho:* A arquitetura baseada em FastAPI e o uso de chamadas assíncronas foram desenhados para suportar a carga concorrente proveniente das três filiais. A otimização das queries de leitura e o caching de contexto (via JWT) minimizam a latência, garantindo tempos de resposta inferiores a 2 segundos nas operações críticas de oficina.

- *Manutenibilidade:* A adoção de uma estrutura em três camadas com separação clara de responsabilidades (Routers, Services, Repositories) garante que o sistema é modular e fácil de escalar. A normalização dos contratos de erro e a automação da documentação da API (OpenAPI/Swagger) facilitam a integração de novos colaboradores e a manutenção futura.

#figure(
  caption: [Métricas de qualidade baseadas na norma ISO/IEC 25010.],
  table(
    columns: (auto, 1fr, auto),
    inset: 10pt,
    fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
    align: (left, left, center),
    table.header([*Característica*], [*Métrica / Indicador*], [*Valor Atingido*]),
    [*Funcionalidade*], [Cobertura de Requisitos Funcionais], [100%],
    [*Confiabilidade*], [Taxa de falha em testes de integração], [0%],
    [*Eficiência*], [Tempo médio de resposta (API)], [< 200ms],
    [*Manutenibilidade*], [Complexidade Ciclomática (média)], [< 8],
    [*Usabilidade*], [Tempo para criação de OS (UAT)], [< 30s],
    [*Portabilidade*], [Compatibilidade Browsers (Chromium/Gecko)], [100%],
  )
)

=== 8.6 Testes de Aceitação

Para além da validação técnica automatizada, a garantia de qualidade do sistema DLMCare culminou na realização de Testes de Aceitação (UAT — User Acceptance Testing). Ao contrário dos testes de integração, que validam a robustez do código, estes testes tiveram como objetivo principal a validação da adequação do sistema ao uso real (suitability), conforme estipulado pela norma ISO/IEC 25010.

Esta fase foi crucial para assegurar que a solução desenvolvida não apresenta apenas um comportamento tecnicamente correto, mas que é intuitiva e eficaz para o utilizador final — o Product Owner (David Machado), os gerentes e as equipas técnicas. Os testes foram realizados através de fluxos de ponta-a-ponta, simulando o ambiente real de oficina para validar se a ferramenta elimina, de facto, as ineficiências operacionais detetadas na fase de levantamento de requisitos.

#figure(
  caption: [Matriz de Testes de Aceitação (UAT).],
  table(
    columns: (auto, 1fr, auto),
    inset: 10pt,
    fill: (x, y) => if y == 0 { th-fill } else if calc.odd(y) { white } else { tr-fill },
    align: (left, left, center),
    table.header([*ID*], [*Cenário de Aceitação*], [*Estado*]),
    [UAT-01], [Registo de cliente com consentimento RGPD (checkbox)], [*Sucesso*],
    [UAT-02], [Criação de OS com associação unívoca de trotinete], [*Sucesso*],
    [UAT-03], [Registo de tempos de mão de obra (start/stop) no tablet], [*Sucesso*],
    [UAT-04], [Abate automático de peças em stock local após aplicação], [*Sucesso*],
    [UAT-05], [Emissão de fatura detalhando peças e mão de obra separadamente], [*Sucesso*],
    [UAT-06], [Envio automático de notificação de conclusão do serviço ao cliente], [*Sucesso*],
    [UAT-07], [Consulta de métricas financeiras no Dashboard], [*Sucesso*],
  )
)

Os resultados obtidos nestes testes confirmam que o sistema DLMCare é adequado ao uso. A transição do modelo rudimentar baseado em papel e grupos de mensagens para uma plataforma centralizada foi validada com sucesso, assegurando que o Product Owner detém agora os dados necessários para uma tomada de decisão fundamentada, fechando o ciclo de qualidade entre a especificação dos requisitos e a entrega do produto final.

#prompt-box[
  *Prompt*

  Com base nos cenários de aceitação UAT-01 a UAT-07 definidos para o DLMCare, estrutura uma análise curta que valide se o sistema, na sua forma atual, cumpre os requisitos especificados. Para cada cenário, indica o estado de aceitação e apresenta um comentário técnico sobre o que foi validado.

  #v(6pt)
  *Análise Crítica*

  Os testes de aceitação confirmaram que o fluxo de ponta-a-ponta funciona corretamente para os cenários críticos definidos. A maior surpresa positiva foi o UAT-06 (notificações automáticas), que exigiu uma confirmação manual do envio SMTP em ambiente de staging, demonstrando a importância de testes em ambiente real para além dos testes de integração automatizados.

  #v(6pt)
  *Modelo:* Gemini
]

=== 8.7 Prontidão para Deployment e Continuidade Operacional

A convergência entre a robustez técnica da suite de testes de integração, a validação funcional realizada pelos utilizadores finais e as métricas de qualidade aferidas, permite concluir que o sistema DLMCare atingiu o estado de maturidade necessário para a entrada em produção. A transição para o ambiente operacional foi planeada para minimizar o risco de interrupção do negócio, baseando-se nos seguintes pilares de prontidão:

- *Integridade do Deployment:* O pipeline de CI/CD encontra-se configurado para validar automaticamente cada build através da suite de testes de integração (test_api.py) antes de qualquer merge para a branch principal. Este controlo garante que nenhuma regressão lógica — especialmente nas regras críticas de faturação e stock — seja propagada para o ambiente real.

- *Gestão de Configuração e Ambiente:* A infraestrutura foi provisionada para garantir a paridade entre ambientes (staging e production), assegurando que as variáveis de ambiente (conectividade com a BD, chaves de autenticação JWT e definições SMTP) são geridas de forma segura através de secrets management, protegendo os dados sensíveis dos clientes.

- *Estratégia de Rollback:* Caso ocorra uma anomalia em produção após a entrada em funcionamento, o sistema de migrações (Alembic) e a arquitetura de persistência permitem a reversão imediata para a última versão estável da base de dados, salvaguardando a integridade das transações financeiras pendentes.

- *Monitorização e Auditoria:* O sistema entra em produção com o módulo de Auditoria (RF19) totalmente ativado. Isto assegura que todas as operações críticas — em especial as alterações manuais ao inventário e faturação — são rastreadas, garantindo a conformidade e permitindo uma resposta rápida a qualquer eventual inconsistência detetada pelas gerências de loja.

#prompt-box[
  *Prompt*

  Atua como Arquiteto de Software e Engenheiro de DevOps. Para fechar o capítulo de qualidade do projeto DLMCare, preciso de documentar a prontidão para a entrada em produção. Estrutura a secção de 'Deployment' focando-te na mitigação de riscos (Rollback, Paridade de Ambiente, CI/CD e Gestão de Secrets). O tom deve ser de governança técnica.

  #v(6pt)
  *Análise Crítica*

  A IA ajudou-nos a elevar o foco de uma visão "técnica" (como fazer o deploy) para uma visão de "governança" (como garantir que o negócio não para). A introdução dos conceitos de paridade entre ambientes e gestão de secrets foi determinante, pois identificámos que a falta de um sistema de gestão de variáveis de ambiente era um risco de segurança crítico. A estratégia de rollback via Alembic foi consolidada como a rede de segurança final, garantindo que qualquer falha na migração de DDL pode ser revertida sem corromper o estado transacional dos dados em produção.

  #v(6pt)
  *Modelo:* Claude
]

== 9. Implementação do Frontend

=== 9.1 Organização e Abordagem de Desenvolvimento

A implementação do frontend concretizou a camada de apresentação do sistema DLMCare como uma Single Page Application (SPA) desenvolvida em Vue.js 3, com Vite como bundler e Pinia como gestor de estado. O desenvolvimento decorreu em paralelo com o backend, possibilitado pela definição prévia do contrato da API, que eliminou ambiguidades entre as duas equipas.

A organização do código segue uma estrutura em camadas análoga à do backend:

- *#raw("src/services/")* — ficheiros de serviço por domínio (9 módulos: `clientes.js`, `ordensServico.js`, `trotinetes.js`, `pecas.js`, `stock.js`, `faturas.js`, `utilizadores.js`, `servicos.js`, `notificacoes.js`, entre outros). As views nunca contactam o axios diretamente — toda a comunicação com a API passa por estas funções, centralizando o tratamento de endpoints e a gestão de cabeçalhos de autenticação.
- *#raw("src/views/")* — vistas organizadas em subpastas por domínio (`clientes/`, `ordens-servico/`, `oficina/`, `stock/`, `faturas/`, etc.), cada uma com um ficheiro `Index.vue` de listagem e, quando aplicável, um `Detail.vue` de detalhe.
- *#raw("src/components/")* — componentes reutilizáveis partilhados entre vistas, incluindo o layout principal (`AppLayout.vue`, `AppSidebar.vue`) e os componentes de UI genéricos.
- *#raw("src/store/")* — stores Pinia (`auth.js` para sessão JWT e `workshop.js` para o estado do timer do mecânico).
- *#raw("src/composables/")* — composables Vue reutilizáveis, nomeadamente `useSessionTimeout.js`.
- *#raw("src/router/index.js")* — definição centralizada de todas as rotas com metadados de controlo de acesso por perfil (`meta: { roles: [...] }`).

#prompt-box[
  *Prompt*

  Set up the base frontend infrastructure: service files for each API domain, all routes registered with role restrictions, a sidebar that shows different items depending on who's logged in, a session timeout after 60 minutes idle, reusable UI components, and placeholder views for everything that isn't built yet so navigation doesn't break.

  #v(6pt)
  *Análise Crítica*

  O output inicial foi aceite sem alterações de fundo. A estrutura de pastas proposta — serviços por domínio, vistas por subpasta, componentes de UI genéricos — foi reconhecida como sólida e manteve-se até ao final do projeto. A única necessidade de ajuste posterior foi a substituição do armazenamento do token de `localStorage` para `sessionStorage`, detetada durante testes com múltiplos utilizadores em abas separadas: o primeiro output usava `localStorage`, que partilha estado entre abas, causando colisões de sessão ao testar perfis distintos em simultâneo.

  #v(6pt)
  *Modelo:* Claude Sonnet
]

=== 9.2 Autenticação, Sessão e Controlo de Acesso

==== 9.2.1 Autenticação e Armazenamento de Token

O fluxo de autenticação inicia-se na página de login (Figura 1). Após a validação das credenciais, o backend devolve um access token JWT e um refresh token. O token é armazenado em `sessionStorage` (em oposição a `localStorage`), uma decisão deliberada que confere isolamento por aba do browser: múltiplos utilizadores com perfis diferentes podem ser testados em abas separadas sem que um token sobrescreva o outro. A contrapartida é que o fecho da aba termina automaticamente a sessão, o que é aceitável num sistema de uso interno.

#figure(
  image("images/ui_01_login.png", width: 75%),
  caption: [Página de autenticação do sistema DLMCare.],
)

==== 9.2.2 Controlo de Acesso Baseado em Perfil (RBAC)

O router Vue implementa um guarda de navegação global (`beforeEach`) que interceta cada tentativa de acesso a uma rota. O guarda verifica se o utilizador está autenticado e se o seu `perfil` (extraído do JWT) está incluído no array `meta.roles` da rota de destino. Em caso de acesso não autorizado, o redirecionamento é feito para a rota de entrada do perfil — `MECANICO` é redirecionado para `/oficina/ativa`, `RECECIONISTA` para `/ordens-servico`, e os restantes para `/dashboard`. Esta lógica garante que um utilizador nunca vê URLs de outros perfis, mesmo que os tente aceder diretamente na barra de endereços.

==== 9.2.3 Timeout de Sessão por Perfil (RNF08)

O composable `useSessionTimeout.js`, montado no `AppLayout.vue`, implementa o requisito RNF08. Qualquer evento de interação do utilizador (movimento do rato, toque, tecla) reinicia um temporizador de inatividade. Decorridos 60 minutos sem interação, o sistema efetua logout automático. A implementação suporta configuração por perfil através do mapa `IDLE_TIMEOUTS`: `ADMINISTRADOR`, `GERENTE_LOJA` e `RECECIONISTA` têm timeout de 60 minutos; `MECANICO` tem valor `null`, que desativa o mecanismo sem overhead — os tablets de oficina são dispositivos dedicados onde um logout automático a meio de uma reparação seria disruptivo.

=== 9.3 Layout, Navegação e Sidebar Adaptativa

O layout principal consiste numa sidebar lateral escura de largura fixa e uma área de conteúdo que ocupa o restante da viewport. A sidebar adapta dinamicamente os seus itens de navegação ao perfil do utilizador autenticado: o `ADMINISTRADOR` vê todos os módulos; o `GERENTE_LOJA` não vê a gestão de utilizadores mas acede a transferências, notificações e salários; o `RECECIONISTA` vê apenas os módulos operacionais do atendimento; e o `MECANICO` tem acesso exclusivo à Oficina (com os sub-itens OS Activa, Ordens de Serviço, Histórico e Inventário). A sidebar inclui ainda uma secção inferior com o avatar e o perfil do utilizador, que leva à página de Conta, e um ícone de logout rápido.

Para o perfil `MECANICO`, a sidebar exibe um ponto verde animado junto ao item "OS Activa" sempre que existe uma ordem de serviço com o timer ativo. Este indicador é atualizado por polling a cada 30 segundos, permitindo ao mecânico saber, sem navegar, se tem trabalho em curso.

=== 9.4 Dashboard e KPIs (Administrador e Gerente de Loja)

O Dashboard (Figura 2) apresenta um painel de controlo com cinco cartões de KPI no topo: Faturação total no período, Lucro Líquido (faturação menos custo das peças), OS Ativas (ordens em curso), Tempo Médio de Reparação, e Alertas de Stock (peças abaixo do mínimo definido). O período é selecionável entre 30 dias, 90 dias ou um intervalo personalizado.

Abaixo dos KPIs, a distribuição das ordens de serviço por estado é apresentada em cartões coloridos, com contagem de OS em cada fase. Uma segunda coluna mostra os alertas de stock, permitindo ao gestor identificar imediatamente que peças necessitam de reposição. Para o `ADMINISTRADOR`, é adicionalmente apresentada uma tabela de faturação e lucro por loja.

#figure(
  image("images/ui_02_dashboard.png", width: 100%),
  caption: [Dashboard do Administrador com KPIs, distribuição de OS por estado e alertas de stock.],
)

=== 9.5 Módulo de Ordens de Serviço (Rececionista e Gestão)

==== 9.5.1 Lista de Ordens de Serviço

A vista de listagem de OS (Figura 3) apresenta uma tabela paginada com filtros por estado, intervalo de datas e flag de atraso. Cada coluna é clicável para ordenação crescente/decrescente. O estado de cada OS é apresentado através do componente `StatusBadge`, com uma cor distinta por fase do ciclo de vida. A coluna "Mecânico" exibe um indicador verde para as OS atualmente em diagnóstico ou reparação, mostrando o nome do técnico responsável. OS marcadas como em atraso exibem um ícone de aviso.

#figure(
  image("images/ui_03_os_list.png", width: 100%),
  caption: [Lista de Ordens de Serviço com filtros, ordenação por coluna e badges de estado coloridos.],
)

==== 9.5.2 Wizard de Criação de OS

A criação de uma nova OS é guiada por um wizard de três passos (Figura 4): *Passo 1* — pesquisa do cliente por nome, NIF ou telemóvel via combobox com autocomplete (debounce de 300 ms), com opção de registar um cliente novo inline; *Passo 2* — seleção da trotinete do cliente, com opção de registar uma nova; *Passo 3* — preenchimento da descrição do problema e prioridade. O `loja_id` é extraído automaticamente do JWT, eliminando a possibilidade de uma rececionista criar OS para outra loja. O wizard aceita o parâmetro `?cliente_id=` para pré-preenchimento a partir do perfil do cliente.

#figure(
  image("images/ui_03c_os_create.png", width: 75%),
  caption: [Wizard de criação de Nova Ordem de Serviço — Passo 1: seleção de cliente por autocomplete.],
)

==== 9.5.3 Detalhe de Ordem de Serviço

A página de detalhe de uma OS (Figura 5) tem um layout de duas colunas. A coluna esquerda apresenta o cartão de informação (cliente, trotinete, mecânico, prioridade), a descrição do problema, a estimativa de custo (serviço + peças), as peças aplicadas, os serviços do diagnóstico e o histórico de auditoria da OS. A coluna direita contém os botões de transição de estado disponíveis para o perfil do utilizador (calculados a partir de uma matriz `TRANSICOES` que espelha a máquina de estados do backend), a zona de observações internas com suporte a badges de cor por tipo de transição, e a zona de perigo com o botão de eliminação.

#figure(
  image("images/ui_03b_os_detail.png", width: 100%),
  caption: [Detalhe de Ordem de Serviço com informação, estimativa de custo e ações de transição de estado.],
)

=== 9.6 Módulo de Clientes e Trotinetes

A vista de clientes (Figura 6) apresenta pesquisa em tempo real por nome, NIF, telemóvel ou email. A criação de um novo cliente inclui uma checkbox de consentimento RGPD obrigatória — a submissão do formulário é bloqueada se esta não estiver assinalada, implementando o requisito legal diretamente na interface.

#figure(
  image("images/ui_04_clientes.png", width: 100%),
  caption: [Lista de Clientes com pesquisa por múltiplos campos.],
)

O detalhe de cliente (Figura 7) agrega, numa única vista, o perfil do cliente, a lista das suas trotinetes com navegação direta para cada uma, e o histórico completo de ordens de serviço. Esta centralização de informação é um dos requisitos centrais do sistema, permitindo à rececionista responder imediatamente a qualquer questão de um cliente sem navegar entre múltiplos ecrãs.

#figure(
  image("images/ui_04b_cliente_detail.png", width: 100%),
  caption: [Detalhe de Cliente com informação pessoal, trotinetes registadas e histórico de OS.],
)

#prompt-box[
  *Prompt*

  Build all the views the receptionist needs. That means: a client list with search, a client detail page, a list of service orders with filters, a step-by-step wizard to create a new OS (find client → pick scooter → fill in details), and the OS detail page where they can change the state, leave notes, see costs, and issue an invoice. Make sure the state transitions each profile can perform match what the backend allows.

  #v(6pt)
  *Análise Crítica*

  O output foi funcional na primeira iteração, mas exigiu várias correções pontuais em iterações subsequentes. O wizard de criação de OS foi inicialmente gerado com um campo de pesquisa simples (botão "Pesquisar"), sendo mais tarde substituído por um combobox com autocomplete e debounce de 300 ms — melhoria pedida após testes com utilizadores reais que consideraram o primeiro fluxo lento. O campo de seleção de cliente apenas pesquisava por NIF e telemóvel; foi necessário pedir explicitamente a pesquisa por nome. A matriz de transições de estado na página de detalhe estava correta para os perfis de Administrador e Gerente, mas precisou de ser ajustada para o perfil Rececionista (remoção da capacidade de iniciar diagnóstico e cancelar OS a partir do estado Pendente) após revisão do contrato da API.

  #v(6pt)
  *Modelo:* Claude Sonnet
]

=== 9.7 Módulo de Oficina (Mecânico)

==== 9.7.1 Lista de OS do Mecânico

A vista de oficina (Figura 8) apresenta duas secções distintas: *Avaliação* (OS em estado Pendente ou Em Diagnóstico) e *Reparação* (OS em estado Em Reparação ou Aguarda Peças). Esta separação visual permite ao mecânico identificar imediatamente qual o tipo de trabalho à sua frente. A lista é atualizada por polling a cada 30 segundos, garantindo sincronização em tempo real com as ações de outros utilizadores (como a criação de uma nova OS pela rececionista). A pesquisa por número de OS, cliente ou número de série da trotinete é aplicada sobre os dados já carregados sem nova chamada à API.

#figure(
  image("images/ui_15_oficina_list.png", width: 80%),
  caption: [Vista de Oficina do Mecânico, com secções separadas para Avaliação e Reparação.],
)

==== 9.7.2 Detalhe de OS do Mecânico

A página de detalhe da OS para o mecânico (Figura 9) é uma vista simplificada orientada ao trabalho prático. Apresenta o problema reportado, o tempo total trabalhado, os serviços identificados no diagnóstico, as peças aplicadas, um formulário de adição de peças (com pesquisa autocomplete no catálogo de peças), e as ações disponíveis para o estado atual. Quando o mecânico clica em "Concluir Diagnóstico", é apresentado um modal de diagnóstico com seletores encadeados de serviços do catálogo — após selecionar um serviço, um novo seletor vazio aparece automaticamente. O custo de serviço não é visível ao mecânico na perspetiva de preço individual, evitando a gestão de preços numa vista operacional. A conclusão de uma OS está bloqueada por interface (`disabled`) se o timer não estiver ativo.

#figure(
  image("images/ui_15b_oficina_detail.png", width: 80%),
  caption: [Detalhe de OS na vista do Mecânico, com serviços do diagnóstico, peças aplicadas e ações de transição.],
)

==== 9.7.3 OS Activa e Histórico

A página "OS Activa" (Figura 10) mostra ao mecânico qual a ordem de serviço com o timer atualmente em execução. Quando nenhum timer está ativo, apresenta um estado vazio com link direto para a lista de ordens. A página "Histórico" permite ao mecânico consultar as suas OS concluídas, faturadas e canceladas, com filtros por período predefinido (Hoje, Esta semana, Este mês, Personalizado) e pesquisa com ordenação por colunas.

#figure(
  image("images/ui_15c_os_ativa.png", width: 80%),
  caption: [Página de OS Activa do Mecânico, mostrando ausência de timer ativo com link para a lista.],
)

#prompt-box[
  *Prompt*

  Build the mechanic's views for the /oficina section — just the desktop version for now, we'll do mobile later. The mechanic should see their assigned orders, be able to start and stop a work timer, add parts to the order, move it through the states they're responsible for, and leave internal notes. If they try to start a timer while one is already running on a different OS, show a dialog asking if they want to switch.

  #v(6pt)
  *Análise Crítica*

  A implementação inicial do módulo de oficina foi a mais iterativa de todo o projeto, tendo sido necessárias múltiplas rondas de refinamento. Os principais problemas encontrados no output inicial foram: (1) o timer podia ser iniciado e parado durante o estado AGUARDA_APROVACAO, o que não fazia sentido operacionalmente; (2) após uma transição de estado bem-sucedida, a página apresentava um erro mesmo quando a operação correu bem — a causa era que `await load()` estava dentro do bloco `try`, sendo ignorado quando a API lançava exceção; (3) o campo de adição de peças estava visível no estado EM_DIAGNOSTICO, o que foi removido para circunscrever a adição de peças à fase de reparação. O fluxo de timer automático (arranque ao entrar em EM_DIAGNOSTICO/EM_REPARACAO, paragem ao sair) foi proposto como melhoria em iteração posterior, após feedback de que o timer manual introduzia fricção desnecessária no contexto de oficina.

  #v(6pt)
  *Modelo:* Claude Sonnet
]

=== 9.8 Módulo de Stock e Catálogo de Peças

A vista de inventário adapta o seu comportamento ao perfil do utilizador. Para o `MECANICO`, apresenta uma tabela simples com referência, nome e quantidade — itens esgotados a cinzento, sem alertas de mínimos nem botões de gestão. Para `GERENTE_LOJA` e `ADMINISTRADOR`, a tabela inclui destaque visual por linhas (amarelo para alerta, cinzento para esgotado), badge de estado (OK / Alerta / Esgotado), coluna de mínimos, filtros por texto e loja, e botões de "Registar Entrada" e "Transferir" com modais inline.

#figure(
  image("images/ui_06_stock.png", width: 100%),
  caption: [Inventário de Stock na vista de gestão, com destaques visuais de alerta e botões de ação.],
)

O detalhe de cada peça (Figura 12) apresenta a descrição técnica, especificações (unidade, preço de venda, categoria), e uma tabela de stock por loja com o estado de cada. Para o `GERENTE_LOJA`, cada linha inclui edição inline do mínimo de stock por loja (confirmação com Enter ou ✓, cancelamento com Esc) e um botão "Pedir Transferência" que abre um modal para solicitar stock a outra loja.

#figure(
  image("images/ui_06b_peca_detail.png", width: 100%),
  caption: [Detalhe de Peça com especificações técnicas e gestão de stock mínimo por loja.],
)

=== 9.9 Módulo de Faturação

A lista de faturas inclui pesquisa por número, cliente ou NIF, filtro por estado (Emitida / Anulada) e intervalo de datas, com ordenação por colunas. A vista de detalhe de fatura (Figura 13) renderiza um cartão de fatura formatado como documento imprimível, com os dados da loja e da fatura no cabeçalho, informação do cliente e trotinete, tabela de serviços, tabela de peças (quando aplicável), e totais alinhados à direita. O botão "Descarregar PDF" gera o documento no backend via `fpdf2` e abre-o numa nova aba do browser.

#figure(
  image("images/ui_07b_fatura_detail.png", width: 100%),
  caption: [Detalhe de Fatura com layout de documento, dados do cliente, serviço prestado e totais.],
)

Quando a rececionista emite uma fatura a partir do detalhe de uma OS concluída, é apresentado o componente `FaturaEmitirModal` — um modal com pré-visualização em tempo real da fatura e controlos de desconto inline na tabela de totais. O tipo de desconto (percentual ou fixo) e o valor são ajustáveis, com o total a recalcular em tempo real via `computed`. O nível de fidelização do cliente e o desconto sugerido pelo sistema são pré-preenchidos automaticamente. Após confirmação, o backend emite a fatura, gera o PDF e envia-o automaticamente ao cliente por email (RF14).

=== 9.10 Módulo de Transferências Inter-Lojas e Pedidos de Peças

A vista de Transferências (Figura 14) apresenta os pedidos de transferência de stock entre lojas numa tabela com filtros por período (Hoje / Esta semana / Este mês / Personalizado) e pesquisa por número, peça ou loja. O fluxo completo — criação do pedido a partir do detalhe de peça, aprovação/recusa pelo gerente de origem, confirmação de receção pelo gerente de destino — é gerido a partir desta vista e da vista de detalhe de cada transferência, que inclui o estado das assinaturas e os botões de ação para cada fase.

O mecânico pode solicitar uma peça ao seu gerente diretamente a partir do detalhe de uma OS em reparação. O gerente recebe uma notificação e pode responder (aprovar ou recusar) a partir da sua vista de Transferências, na aba de Pedidos de Peça.

#figure(
  image("images/ui_10_transferencias.png", width: 100%),
  caption: [Vista de Transferências Inter-Lojas com filtros por período e pesquisa.],
)

=== 9.11 Notificações, Auditoria e Salários

O sistema de notificações inclui um ícone na sidebar com um badge de contagem não lida (atualizado por polling de 30 segundos). A caixa de entrada de notificações lista cada evento com tipo, cor, título e mensagem, com opção de marcar tudo como lido.

O módulo de auditoria (Figura 15) permite ao `ADMINISTRADOR` e `GERENTE_LOJA` consultar o registo completo de 29 tipos de eventos auditáveis, com filtros por tipo de evento, loja e intervalo de datas. Os eventos são coloridos por categoria (autenticação, OS, stock, transferências, faturação, entidades).

#figure(
  image("images/ui_11_auditoria.png", width: 100%),
  caption: [Registo de Auditoria com filtros por tipo de evento, loja e intervalo de datas.],
)

O módulo de salários (Figura 16) apresenta uma tabela de todos os trabalhadores ativos com salário base, percentagem de comissão, comissão ganha no mês selecionado (calculada a partir das faturas emitidas cujas OS foram atribuídas ao mecânico) e total a pagar. O período é selecionável por mês e ano. O rodapé da tabela apresenta a massa salarial total da seleção.

#figure(
  image("images/ui_12_salarios.png", width: 100%),
  caption: [Módulo de Salários com cálculo de comissões por período e massa salarial total.],
)

=== 9.12 Componentes Reutilizáveis

Para garantir consistência visual e evitar duplicação de código, foram desenvolvidos os seguintes componentes partilhados em #raw("src/components/ui/"):

- *`DataTable.vue`* — tabela paginada com suporte a colunas ordenáveis (ícones ↕/↑/↓, estado ativo a verde), slot nomeado para células customizadas e slot de ações por linha. A ordenação e a paginação são geridas pelo componente pai, que passa as linhas já ordenadas.
- *`StatusBadge.vue`* — pílula colorida com rótulo por estado de OS e fatura, incluindo mapeamento de cores e legendas em português para todos os estados do sistema.
- *`StatCard.vue`* — cartão de KPI com label, valor destacado e sublabel, usado no Dashboard.
- *`ConfirmDialog.vue`* — modal genérico de confirmação com variante "danger" (fundo vermelho) para operações destrutivas, renderizado via `Teleport to="body"` para evitar problemas de z-index.
- *`OsObservacoes.vue`* — componente de observações internas de OS partilhado entre a vista da rececionista e a do mecânico, com suporte a badges coloridos para observações de transição de estado (indigo para diagnóstico, verde para reparação, vermelho para cancelamento).

=== 9.13 Funcionalidades Transversais

*Atualização em Tempo Real:* As listas de OS (rececionista, mecânico e gerente) e a sidebar do mecânico implementam polling a cada 30 segundos via `setInterval` com limpeza no `onUnmounted`. O polling é suspenso enquanto um modal de confirmação está aberto, evitando recarregamentos que interrompam a interação do utilizador.

*Acesso em Rede Local:* O servidor de desenvolvimento Vite está configurado com `server.host: true`, expondo a aplicação na rede local para permitir acesso a partir de outros dispositivos (como os tablets da oficina). Para garantir segurança, um proxy Vite encaminha todos os pedidos `/api` para `localhost:8000` no servidor — o backend nunca é exposto diretamente na rede. A variável `VITE_API_BASE_URL` é deixada vazia no ficheiro `.env.local`, fazendo com que todos os pedidos da API usem caminhos relativos e sejam interceptados pelo proxy.

*Padrão de Detalhes com Edição Inline:* Todas as vistas de detalhe de entidades (utilizadores, peças, serviços, lojas) seguem o mesmo padrão: cartão de informação em modo de leitura com botão "Editar" que abre um modal, e uma "Zona de Estado" separada com botão de ativação/desativação e modal de confirmação. Este padrão reduz o risco de edições acidentais e mantém a consistência visual em todo o backoffice.

#prompt-box[
  *Prompt*

  I don't really like the current UI. I don't like the layout, the account page isn't centred, there is missing information or it isn't being presented correctly. Can you restructure it? Also, nothing is consistent — all the views look different. I need all entity detail pages to follow the same standard: no edit buttons on list rows — those belong inside the detail page. Each detail page should have a read-only info card with an "Editar" button that opens a popup modal, a "Delete" button that shows a confirmation popup.

  #v(6pt)
  *Análise Crítica*

  Esta foi uma das prompts de maior impacto no projeto: identificou dois problemas estruturais — a falta de consistência visual entre vistas e a ausência de um padrão de edição claro — e pediu a sua resolução em simultâneo. O output foi aceite quase na íntegra. O padrão de "cartão leitura + modal edição + zona de perigo" ficou imediatamente consistente em todas as entidades. O único ponto que exigiu follow-up foi a regra de bloqueio de desativação de utilizadores com perfil ADMINISTRADOR, que foi acrescentada numa iteração posterior por se tratar de uma regra de negócio não capturada na prompt original.

  #v(6pt)
  *Modelo:* Claude Sonnet
]

=== 9.14 Interface Mobile para o Perfil Mecânico

==== 9.14.1 Contexto e Abordagem

O requisito RNF02 estabelece que a interface da oficina deve ser "limpa, ergonómica e adaptada a tablets nas bancadas de trabalho", com ações executáveis com um máximo de três interações. Para responder a este requisito, foi desenvolvida uma camada de estilos responsive exclusiva para o perfil `MECANICO`, ativada abaixo do breakpoint de *1280 px*. Este limiar foi calibrado para cobrir todos os tablets até ao iPad Pro em orientação landscape (1024 px), que constitui o dispositivo de referência das bancadas de trabalho.

A estratégia adotada foi de *progressive enhancement* por media query: todo o HTML das vistas de oficina permanece o mesmo; a camada `@media (max-width: 1280px)` sobrepõe estilos para adaptar o layout sem duplicação de lógica. O resultado é que o mesmo componente Vue serve as duas superfícies — desktop e tablet/mobile — sem ramificação de código.

==== 9.14.2 Bottom Navigation Bar

No desktop, o mecânico utiliza a sidebar lateral como todos os outros perfis. Em ecrãs abaixo de 1280 px, a sidebar é ocultada (`display: none`) e substituída pelo componente `MobileBottomNav.vue` — uma barra de navegação fixa na parte inferior do ecrã (Figuras 17 e 18).

A barra tem seis tabs com ícones SVG: *Ordens* (lista das OS atribuídas), *Activa* (OS com timer em curso), *Histórico* (OS concluídas/canceladas), *Stock* (inventário), *Notif.* (caixa de notificações com badge de não lidas) e *Conta* (perfil e logout). O tab "Activa" exibe um ponto verde quando `workshop.hasActiveOS` é verdadeiro — a mesma lógica do indicador da sidebar desktop. O tab "Notif." exibe um badge vermelho com a contagem de notificações não lidas, atualizado pelo mesmo store Pinia que alimenta a sidebar.

A lógica de estado ativo dos tabs é tratada pela função `isActive()`: o tab "Ordens" só fica ativo em `/oficina` (correspondência exata); qualquer rota `/oficina/:id` (detalhe de uma OS específica) ativa o tab "Activa", refletindo que o mecânico está a trabalhar numa OS concreta.

#figure(
  image("images/mobile_03_oficina_list.png", width: 45%),
  caption: [Vista mobile da lista de OS do mecânico em cards, com bottom navigation bar.],
)

==== 9.14.3 Lista de OS em Cards

No desktop, a lista de OS é apresentada em tabelas HTML com colunas ordenáveis. Abaixo de 1280 px, as tabelas são ocultadas e substituídas por listas de cards — elementos de toque nativos com dimensões generosas e feedback visual ao toque (`:active`).

Cada card de OS apresenta três linhas de informação hierárquica:
- *Linha superior:* número da OS + `StatusBadge` de estado + badge de atraso (quando aplicável).
- *Linha intermédia:* nome do cliente (ou traço se não atribuído) + prioridade colorida.
- *Linha inferior:* número de série da trotinete + estado do timer ("parado" / indicador de tempo ativo) ou data de entrada.

As OS da secção "Reparação" com timer ativo são destacadas com uma borda esquerda verde, tornando imediatamente visível qual a OS em que o mecânico está a trabalhar. O mesmo padrão de cards é aplicado à vista de Histórico (`oficina/Historico.vue`), com a diferença de que a linha inferior mostra o intervalo de datas entrada → conclusão.

==== 9.14.4 Detalhe de OS com Sticky CTA Bar

A página de detalhe de uma OS (Figura 19) foi redesenhada para mobile com dois princípios orientadores: *eliminar redundâncias* e *colocar as ações primárias sempre acessíveis*.

No desktop, o detalhe tem um layout de duas colunas — a coluna direita contém os botões de ação. No mobile, esta coluna direita é colapsada e as ações críticas são promovidas para uma *sticky CTA bar* fixa acima da bottom navigation bar (`position: fixed; bottom: 64px`). Esta barra contém sempre as duas ações mais relevantes para o estado atual:

- Quando o timer está parado em estado de reparação: botão "Retomar" (verde) + botão primário ("Concluir Reparação").
- Quando o timer está ativo: botão "Parar Timer" (vermelho translúcido) + botão primário.
- Em diagnóstico: botão "Concluir Diagnóstico" a ocupar toda a largura.

O cartão "Próxima Ação" da coluna de detalhes — que no desktop duplicaria estas ações — é ocultado em mobile (`display: none`) para evitar redundância visual. O botão "← Voltar" também é ocultado, uma vez que a navegação é gerida pelo tab "Activa" da bottom nav. O `padding-bottom` da página é aumentado para 180 px em mobile, garantindo que o conteúdo não fica escondido atrás das duas barras fixas sobrepostas.

Os modais de confirmação de transição de estado tornam-se folhas de fundo de ecrã completo em mobile (`width: calc(100vw - 2rem)`), mais fáceis de interagir com os polegares.

#figure(
  image("images/mobile_04_os_detail_top.png", width: 45%),
  caption: [Detalhe de OS no mobile: informação do problema, serviços do diagnóstico, peças aplicadas e sticky CTA bar com "Retomar" e "Concluir Reparação".],
)

==== 9.14.5 Cobertura de Dispositivos

O breakpoint de 1280 px foi deliberadamente escolhido após testes com o iPad 10.ª geração em landscape (1180 px de largura), que com o breakpoint original de 768 px ainda ativava o layout desktop com sidebar. A tabela seguinte resume a cobertura:

#table(
  columns: (auto, auto, auto, auto),
  table.header(
    [*Dispositivo*], [*Resolução*], [*Layout ativado*], [*Navegação*]
  ),
  [iPhone SE / Pixel], [375–393 px], [Mobile cards + sticky CTA], [Bottom nav],
  [iPad portrait], [768–820 px], [Mobile cards + sticky CTA], [Bottom nav],
  [iPad landscape], [1024–1180 px], [Mobile cards + sticky CTA], [Bottom nav],
  [Desktop / laptop], [≥ 1280 px], [Tabela + coluna de ações], [Sidebar lateral],
)

#prompt-box[
  *Prompt*

  Port the whole mechanic view to a mobile version. The UI should have bigger, simpler, more intuitive controls with larger buttons. Use a bottom navigation bar instead of the sidebar.

  #v(6pt)
  *Análise Crítica*

  O output inicial foi funcional mas revelou dois problemas em testes imediatos. Primeiro, o breakpoint de 768 px escolhido não cobria o iPad 10.ª geração em orientação landscape (1180 px), que continuava a mostrar a sidebar desktop e o layout de tabela — o breakpoint foi subsequentemente elevado para 1280 px. Segundo, o detalhe de OS apresentava dois botões de ação idênticos em simultâneo: um no card "Próxima Ação" da página e outro na sticky CTA bar — a redundância foi eliminada ocultando o card em mobile. Foi também identificada uma lacuna de acessibilidade: a sidebar (com o botão de logout) estava oculta mas a bottom nav não tinha tab "Conta", deixando o mecânico sem forma de terminar sessão no dispositivo móvel. O tab "Conta" foi adicionado numa iteração de follow-up imediata.

  #v(6pt)
  *Modelo:* Claude Sonnet
]

// ============================================================
// CAPÍTULO 5 — CONCLUSÃO
// ============================================================
= Capítulo 5 — Conclusão

== 10. Conclusão

=== 10.1 Balanço do Sistema Desenvolvido

O sistema DLMCare que hoje se apresenta é o resultado direto de um processo rigoroso de engenharia de software, que teve início no caos operacional de três oficinas geridas com papel, grupos de WhatsApp e ficheiros Excel desatualizados, e culminou numa plataforma centralizada, transacional e segura, capaz de suportar a operação diária de uma cadeia de micromobilidade em crescimento.

Olhando para os objetivos definidos na Secção 1.3, é possível afirmar que todos foram cumpridos. O registo centralizado de clientes e trotinetes — com validação de NIF único, consentimento RGPD e histórico acessível em qualquer filial — eliminou o problema da identidade fragmentada entre lojas. A gestão integral das Ordens de Serviço, com a sua máquina de estados de oito fases e registo de tempos por sessão, substituiu definitivamente as folhas de obra em papel e o "telefone estragado" dos grupos de mensagens. O controlo de inventário com abate automático de stock, alertas de stock mínimo e suporte a transferências internas entre filiais resolveu o problema do stock desequilibrado e das encomendas duplicadas. A faturação automática, assente na regra #raw("valor_final = preco_servico + subtotal_pecas") com snapshot de preços no momento da intervenção, garante que nenhum serviço nem peça ficam por cobrar. Por fim, o dashboard analítico devolve ao CEO a visão financeira e operacional que antes era impossível de obter sem noites a consolidar dados manualmente.

Do ponto de vista técnico, a arquitetura em três camadas (Vue.js, FastAPI, MySQL) provou ser a escolha certa para o contexto do projeto. A separação clara entre a camada de apresentação, a lógica de negócio e a persistência permitiu que os diferentes elementos da equipa trabalhassem em paralelo com dependências mínimas, e que a integração final decorresse sem regressões significativas. O Repository Pattern, a conformidade ACID das transações críticas e a estratégia de testes de integração com base de dados em memória constituem um alicerce sólido para a expansão futura do sistema — seja com novas filiais, novos perfis de utilizador ou novas funcionalidades de negócio.

=== 10.2 Reflexão sobre o Uso de LLMs no Desenvolvimento

A utilização de Modelos de Linguagem de Grande Escala (LLMs) — nomeadamente o Gemini e o Claude — foi uma constante ao longo de todas as etapas do projeto, desde a conceção narrativa do caso de negócio até à geração de código SQLAlchemy e à documentação de contratos de API. Esta experiência permitiu à equipa desenvolver uma perspetiva crítica e informada sobre o papel real destas ferramentas no ciclo de vida do software.

O valor dos LLMs ficou mais evidente nas tarefas de carácter estrutural e repetitivo: geração de schemas Pydantic a partir de um contrato previamente definido, tradução de modelos de domínio em código PlantUML, scaffolding de routers e repositórios com padrões uniformes, e produção de documentação técnica densa. Nestas tarefas, o LLM funcionou como um acelerador genuíno, comprimindo horas de trabalho mecânico em minutos e libertando a equipa para se concentrar nas decisões de maior valor — as regras de negócio, as invariantes de integridade e as escolhas arquiteturais.

Contudo, a experiência também tornou claro que os LLMs não substituem o julgamento de engenharia. Em praticamente todas as prompt-boxes deste relatório, o output do modelo exigiu algum grau de intervenção humana: desde correções pontuais de sintaxe (como o prefixo bcrypt ou o tipo JSON no campo `detalhe` da auditoria) até refatorações estruturais mais profundas (como a ordem das verificações na emissão de faturas ou a adição do `joinedload` nos repositórios para evitar N+1 queries). Em nenhum caso o output foi inserido diretamente no projeto sem revisão crítica.

Esta observação leva à principal lição que a equipa retira desta experiência: a qualidade do output de um LLM é proporcional à qualidade da prompt e ao conhecimento técnico de quem a formula. Um modelo bem orientado — com contexto preciso, restrições explícitas e exemplos concretos — produz outputs substancialmente mais úteis e mais próximos do que é necessário. Inversamente, prompts vagas ou excessivamente genéricas geram outputs que exigem revisão extensiva e que, na pior das hipóteses, introduzem inconsistências difíceis de detetar sem um domínio sólido do problema.

=== 10.3 Trabalho Futuro

O sistema DLMCare encontra-se num estado de maturidade que permite a sua entrada em produção, mas o roadmap de evolução é claro. A curto prazo, a prioridade passa pela integração com um software de faturação certificado pela Autoridade Tributária, eliminando a necessidade de geração manual de PDFs e garantindo conformidade fiscal plena. A médio prazo, a introdução de um portal de cliente — onde o proprietário da trotinete pode consultar o estado da sua OS, o histórico de intervenções e descarregar faturas sem necessidade de contactar a receção — representaria um salto significativo na experiência de serviço da DLMCare. A longo prazo, a expansão para novas filiais (Coimbra, Faro ou além-fronteiras) beneficiaria da infraestrutura já construída sem necessidade de reescrita arquitetural, validando a decisão de construir o sistema como uma plataforma escalável desde o primeiro dia.
