-- ==============================================================================
-- DLMCare - Script de Povoamento Inicial (Seed)
-- Criação: David Lopes Machado
-- Objetivo: Inserir dados base para testes da Etapa 3 e 4
-- ==============================================================================

-- Desativar verificações temporariamente para inserção limpa
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE stock_lojas;
TRUNCATE TABLE pecas;
TRUNCATE TABLE utilizadores;
TRUNCATE TABLE lojas;

SET FOREIGN_KEY_CHECKS = 1;

-- 1. LOJAS
INSERT INTO lojas (id, nome, cidade, morada, telefone, email, ativo) VALUES
(1, 'DLMCare Lisboa', 'Lisboa', 'Avenida Almirante Reis, nº 74B, Lisboa', '210000001', 'lisboa@dlmcare.pt', 1),
(2, 'DLMCare Porto', 'Porto', 'Rua de Júlio Dinis, Porto', '220000001', 'porto@dlmcare.pt', 1),
(3, 'DLMCare Braga', 'Braga', 'Avenida da Liberdade, Braga', '253000001', 'braga@dlmcare.pt', 1);


-- 2. UTILIZADORES (Staff)
-- Hash Bcrypt para a password comum: "123456"
-- Nota: O Enum respeita o contrato do projeto (ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA, MECANICO)
INSERT INTO utilizadores (id, nome, email, password_hash, perfil, loja_id, ativo, comissao) VALUES
(1, 'David Lopes Machado', 'david@dlmcare.pt', '$2b$12$VzA.1mbIMc7KAnR4qvJpCOB7Tti/XtP258Pus7wg8hd/BKEynrmSC', 'ADMINISTRADOR', NULL, 1, NULL),

-- Equipa Lisboa (Loja 1)
(2, 'José Barros', 'jose.barros@dlmcare.pt', '$2b$12$VzA.1mbIMc7KAnR4qvJpCOB7Tti/XtP258Pus7wg8hd/BKEynrmSC', 'GERENTE_LOJA', 1, 1, NULL),
(3, 'Inês Carvalho', 'ines.carvalho@dlmcare.pt', '$2b$12$VzA.1mbIMc7KAnR4qvJpCOB7Tti/XtP258Pus7wg8hd/BKEynrmSC', 'RECECIONISTA', 1, 1, NULL),
(4, 'Tiago Mendes', 'tiago.mendes@dlmcare.pt', '$2b$12$VzA.1mbIMc7KAnR4qvJpCOB7Tti/XtP258Pus7wg8hd/BKEynrmSC', 'MECANICO', 1, 1, 10),
(5, 'João Ruca Silva', 'joao.silva@dlmcare.pt', '$2b$12$VzA.1mbIMc7KAnR4qvJpCOB7Tti/XtP258Pus7wg8hd/BKEynrmSC', 'MECANICO', 1, 1, 10),

-- Equipa Porto (Loja 2)
(6, 'Miguel Torres', 'miguel.torres@dlmcare.pt', '$2b$12$VzA.1mbIMc7KAnR4qvJpCOB7Tti/XtP258Pus7wg8hd/BKEynrmSC', 'GERENTE_LOJA', 2, 1, NULL),

-- Equipa Braga (Loja 3)
(7, 'Sofia Almeida', 'sofia.almeida@dlmcare.pt', '$2b$12$VzA.1mbIMc7KAnR4qvJpCOB7Tti/XtP258Pus7wg8hd/BKEynrmSC', 'GERENTE_LOJA', 3, 1, NULL);


-- 3. PEÇAS (Catálogo base com 12 peças representativas)
INSERT INTO pecas (id, referencia, nome, categoria, descricao, unidade, preco_custo, preco_venda, ativo) VALUES
(1,  'PEC-BAT-001', 'Bateria 36V 7.5Ah Xiaomi',   'BATERIA',     'Bateria de lítio padrão',    'unidade', 42.0,  89.9,  1),
(2,  'PEC-BAT-002', 'Bateria 48V 10Ah Ninebot',   'BATERIA',     'Bateria de alta capacidade', 'unidade', 58.0,  119.9, 1),
(3,  'PEC-PNE-001', 'Pneu Traseiro 8.5x2',        'PNEU',        'Pneu anti-furo traseiro',    'unidade', 8.5,   18.9,  1),
(4,  'PEC-PNE-002', 'Câmara de Ar 10x2.5',        'PNEU',        'Câmara de ar reforçada',     'unidade', 4.0,   9.9,   1),
(5,  'PEC-TRA-001', 'Pastilhas de Travão',        'TRAVAO',      'Par de pastilhas disco',     'par',     5.0,   12.5,  1),
(6,  'PEC-TRA-002', 'Disco de Travão 120mm',      'TRAVAO',      'Disco metálico traseiro',    'unidade', 6.5,   15.9,  1),
(7,  'PEC-MOT-001', 'Motor Hub 250W',             'MOTOR',       'Motor roda dianteira 250W',  'unidade', 95.0,  195.0, 1),
(8,  'PEC-CTR-001', 'Controlador ESC Xiaomi',     'CONTROLADOR', 'Placa controladora M365',    'unidade', 28.0,  59.9,  1),
(9,  'PEC-CTR-002', 'Display Dashboard LED',      'CONTROLADOR', 'Painel LED Bluetooth',       'unidade', 18.0,  45.0,  1),
(10, 'PEC-LUZ-001', 'Farol Frontal LED 5W',       'LUZ',         'Luz frontal de substituição','unidade', 12.0,  25.0,  1),
(11, 'PEC-ACE-001', 'Suporte Telemóvel',          'ACESSORIO',   'Suporte guiador universal',  'unidade', 5.5,   14.9,  1),
(12, 'PEC-OUT-001', 'Kit Parafusos M4 (50 un)',   'OUTRO',       'Kit ferragens inox',         'caixa',   1.0,   4.5,   1);


-- 4. STOCK (Inventário cruzado)
-- Inserções das 12 peças geradas automaticamente para as 3 lojas
-- Quantidades entre 0-20, limites entre 2-5
INSERT INTO stock_lojas (peca_id, loja_id, quantidade, limite_minimo) VALUES
-- Loja 1 (Lisboa)
(1,  1, 15, 3),
(2,  1, 4,  2),
(3,  1, 20, 5),
(4,  1, 10, 4),
(5,  1, 12, 5),
(6,  1, 8,  3),
(7,  1, 2,  2),
(8,  1, 5,  2),
(9,  1, 7,  3),
(10, 1, 18, 4),
(11, 1, 11, 3),
(12, 1, 3,  2),
-- Loja 2 (Porto)
(1,  2, 8,  3),
(2,  2, 0,  2),
(3,  2, 14, 5),
(4,  2, 2,  4),
(5,  2, 19, 5),
(6,  2, 5,  3),
(7,  2, 1,  2),
(8,  2, 0,  2),
(9,  2, 4,  3),
(10, 2, 12, 4),
(11, 2, 8,  3),
(12, 2, 1,  2),
-- Loja 3 (Braga)
(1,  3, 10, 3),
(2,  3, 2,  2),
(3,  3, 5,  5),
(4,  3, 16, 4),
(5,  3, 8,  5),
(6,  3, 3,  3),
(7,  3, 0,  2),
(8,  3, 4,  2),
(9,  3, 6,  3),
(10, 3, 20, 4),
(11, 3, 15, 3),
(12, 3, 0,  2);