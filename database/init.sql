-- =============================================================
--  DLMCare — Script de inicialização da base de dados
--  Cria o schema e o utilizador da aplicação.
--  Correr como root do MySQL uma única vez.
-- =============================================================

-- Criar base de dados
CREATE DATABASE IF NOT EXISTS dlmcare
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Criar utilizador da aplicação (substituir a password)
CREATE USER IF NOT EXISTS 'dlmcare_user'@'%' IDENTIFIED BY 'DlmCare_2026!';

-- Conceder permissões apenas ao schema dlmcare
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER
    ON dlmcare.*
    TO 'dlmcare_user'@'%';

FLUSH PRIVILEGES;

-- Confirmar
SELECT 'Base de dados dlmcare criada com sucesso.' AS mensagem;
