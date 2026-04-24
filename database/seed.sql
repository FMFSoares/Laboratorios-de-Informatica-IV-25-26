-- =============================================================
--  DLMCare — Seed inicial (dados de teste)
--  Correr DEPOIS das migrations do Alembic estarem aplicadas.
-- =============================================================

USE dlmcare;

-- Lojas
INSERT INTO lojas (nome, cidade, morada, telefone, email) VALUES
('DLMCare Lisboa', 'Lisboa', 'Av. da Liberdade 100, 1250-096 Lisboa', '213000001', 'lisboa@dlmcare.pt'),
('DLMCare Porto',  'Porto',  'Rua de Santa Catarina 200, 4000-450 Porto', '222000001', 'porto@dlmcare.pt'),
('DLMCare Braga',  'Braga',  'Rua do Souto 50, 4700-010 Braga',          '253000001', 'braga@dlmcare.pt');

-- Utilizadores (passwords em bcrypt — valor abaixo = "password123")
INSERT INTO utilizadores (nome, email, password_hash, perfil, loja_id, ativo) VALUES
('Admin CEO',         'admin@dlmcare.pt',        '$2b$12$placeholderHashAdmin',        'ADMINISTRADOR',    NULL, TRUE),
('Ana Rececionista',  'ana.lisboa@dlmcare.pt',   '$2b$12$placeholderHashRececionista', 'RECECIONISTA',     1,    TRUE),
('Bruno Mecânico',    'bruno.lisboa@dlmcare.pt', '$2b$12$placeholderHashMecanico',     'MECANICO',         1,    TRUE),
('Carlos Gerente',    'carlos.porto@dlmcare.pt', '$2b$12$placeholderHashGerente',      'GERENTE_LOJA',     2,    TRUE);

-- NOTA: Substituir os placeholderHash por hashes reais gerados com:
--   python -c "from passlib.hash import bcrypt; print(bcrypt.hash('password123'))"
