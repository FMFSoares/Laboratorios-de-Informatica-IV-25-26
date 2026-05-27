-- ==============================================================================
-- DLMCare — Dados de Demonstração para o Dashboard Admin
-- Cobre todas as lojas, estados de OS, períodos de Jan–Mai 2026 e faturas reais
-- ==============================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- =============================================================================
-- 1. NOVOS UTILIZADORES (Mecânicos e Recepcionistas para Porto e Braga)
-- =============================================================================

INSERT INTO utilizadores (id, nome, email, password_hash, perfil, loja_id, ativo, comissao) VALUES
(8,  'Paulo Martins',  'paulo.martins@dlmcare.pt',  '$2b$12$VzA.1mbIMc7KAnR4qvJpCOB7Tti/XtP258Pus7wg8hd/BKEynrmSC', 'MECANICO',    2, 1, 10),
(9,  'Rita Sousa',     'rita.sousa@dlmcare.pt',     '$2b$12$VzA.1mbIMc7KAnR4qvJpCOB7Tti/XtP258Pus7wg8hd/BKEynrmSC', 'RECECIONISTA', 2, 1, NULL),
(10, 'Luís Gonçalves', 'luis.goncalves@dlmcare.pt', '$2b$12$VzA.1mbIMc7KAnR4qvJpCOB7Tti/XtP258Pus7wg8hd/BKEynrmSC', 'MECANICO',    3, 1, 12),
(11, 'Carla Dias',     'carla.dias@dlmcare.pt',     '$2b$12$VzA.1mbIMc7KAnR4qvJpCOB7Tti/XtP258Pus7wg8hd/BKEynrmSC', 'RECECIONISTA', 3, 1, NULL);


-- =============================================================================
-- 2. NOVOS CLIENTES (3 em Lisboa, 4 no Porto, 3 em Braga)
-- =============================================================================

INSERT INTO clientes (id, nome, nif, telemovel, email, morada, consentimento_rgpd, data_registo, loja_id) VALUES
-- Loja 1 — Lisboa
(3,  'Filipa Santos',   '234567890', '912345678', 'filipa.santos@email.pt',   'Rua Augusta 45, Lisboa',            1, '2025-09-10 10:00:00', 1),
(4,  'Rui Gomes',       '345678901', '923456789', 'rui.gomes@email.pt',       'Av. de Roma 12, Lisboa',            1, '2025-10-05 11:00:00', 1),
(5,  'Beatriz Costa',   '456789012', '934567890', 'beatriz.costa@email.pt',   'Rua do Ouro 78, Lisboa',            1, '2025-11-20 09:30:00', 1),
-- Loja 2 — Porto
(6,  'Pedro Oliveira',  '567890123', '945678901', 'pedro.oliveira@email.pt',  'Rua de Santa Catarina 55, Porto',   1, '2025-08-15 14:00:00', 2),
(7,  'Marta Silva',     '678901234', '956789012', 'marta.silva@email.pt',     'Av. dos Aliados 90, Porto',         1, '2025-09-22 10:30:00', 2),
(8,  'André Ferreira',  '789012345', '967890123', 'andre.ferreira@email.pt',  'Rua do Bonjardim 130, Porto',       1, '2025-10-18 15:00:00', 2),
(9,  'Catarina Lopes',  '890123456', '978901234', 'catarina.lopes@email.pt',  'Rua Formosa 22, Porto',             1, '2025-12-03 09:00:00', 2),
-- Loja 3 — Braga
(10, 'Nuno Barbosa',    '901234567', '989012345', 'nuno.barbosa@email.pt',    'Av. da Liberdade 15, Braga',        1, '2025-09-05 16:00:00', 3),
(11, 'Mariana Cruz',    '112345678', '990123456', 'mariana.cruz@email.pt',    'Rua do Souto 8, Braga',             1, '2025-11-14 11:00:00', 3),
(12, 'Francisco Alves', '223456789', '901234567', 'francisco.alves@email.pt', 'Largo do Paço 3, Braga',            1, '2026-01-08 10:00:00', 3);


-- =============================================================================
-- 3. NOVAS TROTINETES (uma por novo cliente + uma extra para Carlos)
-- =============================================================================

INSERT INTO trotinetes (id, cliente_id, marca, modelo, numero_serie, ano_compra, cor, observacoes_tecnicas, data_registo) VALUES
(3,  2,  'Xiaomi',  'Mi Electric Scooter 3', 'XM2025003CC', 2023, 'Preto',    NULL,                        '2025-10-01 09:00:00'),
(4,  3,  'Segway',  'Ninebot Max G30',        'SN2025004DD', 2024, 'Cinzento', NULL,                        '2025-09-10 10:15:00'),
(5,  4,  'Xiaomi',  'Mi Essential',           'XM2025005EE', 2023, 'Branco',   'Pneu dianteiro já trocado', '2025-10-05 11:30:00'),
(6,  5,  'Segway',  'Ninebot E45',            'SN2025006FF', 2024, 'Azul',     NULL,                        '2025-11-20 09:45:00'),
(7,  6,  'Xiaomi',  'Mi Electric Scooter 4', 'XM2025007GG', 2024, 'Preto',    NULL,                        '2025-08-15 14:30:00'),
(8,  7,  'Cecotec', 'Bongo Serie A',          'CC2025008HH', 2023, 'Vermelho', NULL,                        '2025-09-22 10:45:00'),
(9,  8,  'Segway',  'Ninebot S Max',          'SN2025009II', 2024, 'Cinzento', 'Bateria trocada em 2025',   '2025-10-18 15:20:00'),
(10, 9,  'Xiaomi',  'Mi Electric Scooter 3', 'XM2025010JJ', 2024, 'Branco',   NULL,                        '2025-12-03 09:15:00'),
(11, 10, 'Kaabo',   'Skywalker 8S',           'KB2025011KK', 2023, 'Preto',    NULL,                        '2025-09-05 16:20:00'),
(12, 11, 'Xiaomi',  'Mi Essential',           'XM2025012LL', 2024, 'Rosa',     NULL,                        '2025-11-14 11:30:00'),
(13, 12, 'Inokim',  'Light 2',                'IK2026013MM', 2025, 'Cinzento', NULL,                        '2026-01-08 10:30:00');


-- =============================================================================
-- 4. NOVAS ORDENS DE SERVIÇO (29 OS distribuídas Jan–Mai 2026)
-- =============================================================================

INSERT INTO ordens_servico (id, numero, trotinete_id, cliente_id, loja_id, mecanico_id, estado, prioridade, descricao_problema, preco_servico, data_entrada, data_conclusao, tempo_total_minutos) VALUES

-- ── LOJA 1 (Lisboa) — Mecânicos: Tiago (4), João (5) ──────────────────────

-- Janeiro
(12, 'OS-2026-0012', 3,  2,  1, 4,    'FATURADA',          'NORMAL',  'Pneu traseiro furado, cliente não consegue circular.',                       25.00, '2026-01-08 09:30:00', '2026-01-10 16:00:00', 85),
(13, 'OS-2026-0013', 4,  3,  1, 5,    'FATURADA',          'ALTA',    'Bateria não segura carga. Autonomia caiu para menos de 5 km.',               49.00, '2026-01-20 10:00:00', '2026-01-22 15:00:00', 120),
-- Fevereiro
(14, 'OS-2026-0014', 5,  4,  1, 4,    'FATURADA',          'NORMAL',  'Pneu traseiro completamente gasto, substituição urgente.',                   18.00, '2026-02-03 08:30:00', '2026-02-05 14:00:00', 60),
(15, 'OS-2026-0015', 6,  5,  1, 5,    'FATURADA',          'URGENTE', 'Motor parou a funcionar a meio de uma viagem. Cliente ficou imobilizado.',   95.00, '2026-02-18 11:00:00', '2026-02-19 17:00:00', 180),
-- Março
(16, 'OS-2026-0016', 3,  2,  1, 4,    'FATURADA',          'NORMAL',  'Revisão anual completa solicitada pelo cliente.',                            35.00, '2026-03-05 09:00:00', '2026-03-08 16:30:00', 150),
-- Abril
(17, 'OS-2026-0017', 4,  3,  1, 5,    'FATURADA',          'ALTA',    'Controlador avariado, trotinete não responde ao acelerador.',                75.00, '2026-04-01 10:30:00', '2026-04-03 15:00:00', 140),
(18, 'OS-2026-0018', 1,  1,  1, 4,    'FATURADA',          'NORMAL',  'Travões com pouca resposta. Pastilhas completamente desgastadas.',           37.00, '2026-04-15 09:00:00', '2026-04-17 14:00:00', 95),
(40, 'OS-2026-0040', 5,  4,  1, NULL, 'CANCELADA',         'NORMAL',  'Ruído estranho na roda. Cliente cancelou antes de entrada em oficina.',       0.00, '2026-04-28 09:00:00', NULL,                  NULL),
-- Maio
(19, 'OS-2026-0019', 5,  4,  1, 5,    'CONCLUIDA',         'NORMAL',  'Regulação dos travões e limpeza geral pedida pelo cliente.',                 18.00, '2026-05-05 08:00:00', '2026-05-07 17:00:00', 70),
(20, 'OS-2026-0020', 6,  5,  1, 4,    'EM_REPARACAO',      'ALTA',    'Bateria a inchar. Possível defeito de fábrica. Em substituição.',            49.00, '2026-05-15 10:00:00', NULL,                  NULL),
(21, 'OS-2026-0021', 3,  2,  1, 5,    'AGUARDA_APROVACAO', 'NORMAL',  'Revisão completa e pneu dianteiro necessita substituição. Orçamento enviado.',53.00,'2026-05-20 09:00:00', NULL,                  NULL),
(22, 'OS-2026-0022', 1,  1,  1, NULL, 'PENDENTE',          'NORMAL',  'Trotinete não liga após queda. Aguarda avaliação inicial.',                   0.00, '2026-05-27 08:00:00', NULL,                  NULL),

-- ── LOJA 2 (Porto) — Mecânico: Paulo (8) ──────────────────────────────────

-- Janeiro
(23, 'OS-2026-0023', 7,  6,  2, 8,    'FATURADA',          'NORMAL',  'Câmara de ar furou. Solicita reparação rápida.',                            10.00, '2026-01-15 09:30:00', '2026-01-18 16:00:00', 45),
-- Fevereiro
(24, 'OS-2026-0024', 8,  7,  2, 8,    'FATURADA',          'ALTA',    'Bateria completamente morta, não aceita carga.',                            49.00, '2026-02-10 10:00:00', '2026-02-12 17:00:00', 110),
-- Março
(25, 'OS-2026-0025', 9,  8,  2, 8,    'FATURADA',          'NORMAL',  'Manutenção preventiva: diagnóstico geral e limpeza.',                       25.00, '2026-02-28 09:00:00', '2026-03-01 15:00:00', 90),
(26, 'OS-2026-0026', 10, 9,  2, 8,    'FATURADA',          'URGENTE', 'Motor com cheiro a queimado. Trotinete imobilizada no local.',              95.00, '2026-03-12 11:00:00', '2026-03-13 18:00:00', 200),
-- Abril
(27, 'OS-2026-0027', 7,  6,  2, 8,    'FATURADA',          'NORMAL',  'Revisão semestral. Verificação completa de todos os sistemas.',             35.00, '2026-04-08 09:00:00', '2026-04-10 16:00:00', 135),
-- Maio
(28, 'OS-2026-0028', 8,  7,  2, 8,    'CONCLUIDA',         'NORMAL',  'Pastilhas de travão gastas. Travão traseiro com resposta insuficiente.',    30.00, '2026-05-10 10:00:00', '2026-05-13 15:00:00', 80),
(29, 'OS-2026-0029', 9,  8,  2, 8,    'EM_DIAGNOSTICO',    'ALTA',    'Trotinete perde velocidade a meio das viagens. Diagnóstico em curso.',       0.00, '2026-05-22 09:00:00', NULL,                  NULL),
(30, 'OS-2026-0030', 10, 9,  2, 8,    'AGUARDA_PECAS',     'ALTA',    'Pneu traseiro necessita substituição. A aguardar peça em stock.',           18.00, '2026-05-16 10:00:00', NULL,                  NULL),
(31, 'OS-2026-0031', 7,  6,  2, NULL, 'PENDENTE',          'NORMAL',  'Barulho estranho na roda traseira durante a marcha. Por avaliar.',           0.00, '2026-05-27 09:00:00', NULL,                  NULL),
(32, 'OS-2026-0032', 8,  7,  2, 8,    'EM_REPARACAO',      'URGENTE', 'Motor com falha intermitente. Trotinete para sem aviso prévio.',            95.00, '2026-05-21 14:00:00', NULL,                  NULL),

-- ── LOJA 3 (Braga) — Mecânico: Luís (10) ─────────────────────────────────

-- Janeiro/Fevereiro
(33, 'OS-2026-0033', 11, 10, 3, 10,   'FATURADA',          'NORMAL',  'Pneu traseiro sem aderência. Substituição necessária.',                     18.00, '2026-01-25 09:00:00', '2026-01-28 15:00:00', 65),
(34, 'OS-2026-0034', 12, 11, 3, 10,   'FATURADA',          'ALTA',    'Revisão completa antes da época de primavera.',                             35.00, '2026-02-15 10:00:00', '2026-02-17 16:00:00', 130),
-- Março
(35, 'OS-2026-0035', 13, 12, 3, 10,   'FATURADA',          'NORMAL',  'Pastilhas de travão dianteiro totalmente gastas.',                          22.00, '2026-03-20 09:00:00', '2026-03-22 15:00:00', 75),
-- Maio
(36, 'OS-2026-0036', 11, 10, 3, 10,   'CONCLUIDA',         'NORMAL',  'Diagnóstico e limpeza geral. 2ª visita do cliente.',                        25.00, '2026-05-03 08:00:00', '2026-05-06 17:00:00', 55),
(37, 'OS-2026-0037', 12, 11, 3, 10,   'EM_REPARACAO',      'NORMAL',  'Controlador queimado após exposição a chuva intensa.',                      75.00, '2026-05-19 10:00:00', NULL,                  NULL),
(38, 'OS-2026-0038', 13, 12, 3, NULL, 'CANCELADA',         'NORMAL',  'Cliente trouxe para diagnóstico mas desistiu da reparação após orçamento.',  0.00, '2026-05-14 09:00:00', NULL,                  NULL),
(39, 'OS-2026-0039', 11, 10, 3, 10,   'AGUARDA_APROVACAO', 'ALTA',    'Revisão completa + pastilhas gastas. Orçamento enviado ao cliente.',        57.00, '2026-05-23 10:00:00', NULL,                  NULL);


-- =============================================================================
-- 5. SERVIÇOS DE DIAGNÓSTICO (os_servicos)
-- =============================================================================

INSERT INTO os_servicos (id, ordem_servico_id, servico_id, nome, preco) VALUES
-- OS-0012 (25.00 = 15+10)
(3,  12, 1,  'Diagnóstico Geral',                   15.00),
(4,  12, 6,  'Reparação de Furo',                   10.00),
-- OS-0013 (49.00)
(5,  13, 2,  'Substituição de Bateria',             49.00),
-- OS-0014 (18.00)
(6,  14, 5,  'Substituição de Pneu Traseiro',       18.00),
-- OS-0015 (95.00)
(7,  15, 11, 'Substituição de Motor',               95.00),
-- OS-0016 (35.00)
(8,  16, 15, 'Revisão Completa',                    35.00),
-- OS-0017 (75.00)
(9,  17, 12, 'Substituição de Controlador',         75.00),
-- OS-0018 (37.00 = 22+15)
(10, 18, 8,  'Substituição de Pastilhas de Travão', 22.00),
(11, 18, 1,  'Diagnóstico Geral',                   15.00),
-- OS-0019 (18.00 = 8+10)
(12, 19, 7,  'Regulação de Travões',                 8.00),
(13, 19, 16, 'Limpeza e Lubrificação Geral',        10.00),
-- OS-0020 (49.00 — EM_REPARACAO)
(14, 20, 2,  'Substituição de Bateria',             49.00),
-- OS-0021 (53.00 = 35+18 — AGUARDA_APROVACAO)
(15, 21, 15, 'Revisão Completa',                    35.00),
(16, 21, 4,  'Substituição de Pneu Dianteiro',      18.00),
-- OS-0023 (10.00)
(17, 23, 6,  'Reparação de Furo',                   10.00),
-- OS-0024 (49.00)
(18, 24, 2,  'Substituição de Bateria',             49.00),
-- OS-0025 (25.00 = 15+10)
(19, 25, 1,  'Diagnóstico Geral',                   15.00),
(20, 25, 16, 'Limpeza e Lubrificação Geral',        10.00),
-- OS-0026 (95.00)
(21, 26, 11, 'Substituição de Motor',               95.00),
-- OS-0027 (35.00)
(22, 27, 15, 'Revisão Completa',                    35.00),
-- OS-0028 (30.00 = 22+8)
(23, 28, 8,  'Substituição de Pastilhas de Travão', 22.00),
(24, 28, 7,  'Regulação de Travões',                 8.00),
-- OS-0030 (18.00 — AGUARDA_PECAS)
(25, 30, 5,  'Substituição de Pneu Traseiro',       18.00),
-- OS-0032 (95.00 — EM_REPARACAO)
(26, 32, 11, 'Substituição de Motor',               95.00),
-- OS-0033 (18.00)
(27, 33, 5,  'Substituição de Pneu Traseiro',       18.00),
-- OS-0034 (35.00)
(28, 34, 15, 'Revisão Completa',                    35.00),
-- OS-0035 (22.00)
(29, 35, 8,  'Substituição de Pastilhas de Travão', 22.00),
-- OS-0036 (25.00 = 15+10)
(30, 36, 1,  'Diagnóstico Geral',                   15.00),
(31, 36, 16, 'Limpeza e Lubrificação Geral',        10.00),
-- OS-0037 (75.00 — EM_REPARACAO)
(32, 37, 12, 'Substituição de Controlador',         75.00),
-- OS-0039 (57.00 = 35+22 — AGUARDA_APROVACAO)
(33, 39, 15, 'Revisão Completa',                    35.00),
(34, 39, 8,  'Substituição de Pastilhas de Travão', 22.00);


-- =============================================================================
-- 6. PEÇAS APLICADAS (os_pecas)
-- =============================================================================

INSERT INTO os_pecas (id, ordem_servico_id, peca_id, quantidade, preco_venda_unitario) VALUES
-- OS-0013: Bateria 36V 7.5Ah Xiaomi
(5,  13, 1, 1,  89.90),
-- OS-0014: Pneu Traseiro 8.5x2
(6,  14, 3, 1,  18.90),
-- OS-0015: Motor Hub 250W
(7,  15, 7, 1, 195.00),
-- OS-0017: Controlador ESC Xiaomi
(8,  17, 8, 1,  59.90),
-- OS-0018: Pastilhas de Travão
(9,  18, 5, 1,  12.50),
-- OS-0020: Bateria 48V 10Ah Ninebot (EM_REPARACAO, peça já aplicada)
(10, 20, 2, 1, 119.90),
-- OS-0024: Bateria 36V 7.5Ah Xiaomi (Porto)
(11, 24, 1, 1,  89.90),
-- OS-0026: Motor Hub 250W (Porto)
(12, 26, 7, 1, 195.00),
-- OS-0028: Pastilhas de Travão (Porto — CONCLUIDA)
(13, 28, 5, 1,  12.50),
-- OS-0033: Pneu Traseiro 8.5x2 (Braga)
(14, 33, 3, 1,  18.90),
-- OS-0034: Câmara de Ar 10x2.5 × 2 (Braga — revisão completa)
(15, 34, 4, 2,   9.90),
-- OS-0035: Pastilhas de Travão (Braga)
(16, 35, 5, 1,  12.50);


-- =============================================================================
-- 7. FATURAS (uma por cada OS em estado FATURADA)
-- Valor = preco_servico (os_servicos) + subtotal_pecas (os_pecas)
-- =============================================================================

INSERT INTO faturas (id, numero, ordem_servico_id, data_emissao, estado, subtotal_pecas, valor_final, desconto_tipo, desconto_valor, valor_desconto) VALUES
-- Lisboa
(3,  'FAT-2026-0003', 12, '2026-01-10 16:30:00', 'EMITIDA',   0.00,  25.00, NULL,         0.00,  0.00),  -- diag + furo
(4,  'FAT-2026-0004', 13, '2026-01-22 15:30:00', 'EMITIDA',  89.90, 138.90, NULL,         0.00,  0.00),  -- bat serv + bat peça
(5,  'FAT-2026-0005', 14, '2026-02-05 14:30:00', 'EMITIDA',  18.90,  36.90, NULL,         0.00,  0.00),  -- pneu serv + pneu peça
(6,  'FAT-2026-0006', 15, '2026-02-19 17:30:00', 'EMITIDA', 195.00, 290.00, NULL,         0.00,  0.00),  -- motor serv + motor peça
(7,  'FAT-2026-0007', 16, '2026-03-08 17:00:00', 'EMITIDA',   0.00,  35.00, NULL,         0.00,  0.00),  -- revisão
(8,  'FAT-2026-0008', 17, '2026-04-03 15:30:00', 'EMITIDA',  59.90, 134.90, NULL,         0.00,  0.00),  -- ctr serv + ctr peça
(9,  'FAT-2026-0009', 18, '2026-04-17 14:30:00', 'EMITIDA',  12.50,  49.50, NULL,         0.00,  0.00),  -- pastilhas + diag + peça
-- Porto
(10, 'FAT-2026-0010', 23, '2026-01-18 16:30:00', 'EMITIDA',   0.00,  10.00, NULL,         0.00,  0.00),  -- furo
(11, 'FAT-2026-0011', 24, '2026-02-12 17:30:00', 'EMITIDA',  89.90, 138.90, NULL,         0.00,  0.00),  -- bat serv + bat peça
(12, 'FAT-2026-0012', 25, '2026-03-01 15:30:00', 'EMITIDA',   0.00,  25.00, NULL,         0.00,  0.00),  -- diag + limpeza
(13, 'FAT-2026-0013', 26, '2026-03-13 18:30:00', 'EMITIDA', 195.00, 275.50, 'PERCENTUAL', 5.00, 14.50),  -- motor + 5% desconto fidelidade
(14, 'FAT-2026-0014', 27, '2026-04-10 16:30:00', 'EMITIDA',   0.00,  35.00, NULL,         0.00,  0.00),  -- revisão
-- Braga
(15, 'FAT-2026-0015', 33, '2026-01-28 15:30:00', 'EMITIDA',  18.90,  36.90, NULL,         0.00,  0.00),  -- pneu serv + pneu peça
(16, 'FAT-2026-0016', 34, '2026-02-17 16:30:00', 'EMITIDA',  19.80,  54.80, NULL,         0.00,  0.00),  -- revisão + 2× câmara
(17, 'FAT-2026-0017', 35, '2026-03-22 15:30:00', 'EMITIDA',  12.50,  34.50, NULL,         0.00,  0.00);  -- pastilhas serv + peça


SET FOREIGN_KEY_CHECKS = 1;

SELECT CONCAT('OSs totais: ', COUNT(*)) AS resumo FROM ordens_servico
UNION ALL
SELECT CONCAT('Faturas totais: ', COUNT(*)) FROM faturas
UNION ALL
SELECT CONCAT('Clientes totais: ', COUNT(*)) FROM clientes
UNION ALL
SELECT CONCAT('Trotinetes totais: ', COUNT(*)) FROM trotinetes;
