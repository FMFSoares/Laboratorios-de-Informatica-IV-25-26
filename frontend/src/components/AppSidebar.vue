<script setup>
import { RouterLink } from 'vue-router';
</script>

<template>
  <aside class="app-sidebar">
    <nav>
      <ul>
        <li>
          <router-link :to="{ name: 'Dashboard' }" class="nav-link">Dashboard</router-link>
        </li>
        <!-- Outros links de navegação serão adicionados aqui -->
        <!-- Ex:
        <li><router-link to="/clientes" class="nav-link">Clientes</router-link></li>
        <li><router-link to="/ordens-servico" class="nav-link">Ordens de Serviço</router-link></li>
        <li><router-link to="/stock" class="nav-link">Stock</router-link></li>
        -->
      </ul>
    </nav>
  </aside>
</template>

<style scoped>
.app-sidebar {
  width: 240px;
  background-color: #2c3e50;
  color: #ecf0f1;
  padding-top: 1rem;
  flex-shrink: 0;
}

nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-link {
  display: block;
  padding: 1rem 1.5rem;
  color: #ecf0f1;
  text-decoration: none;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: #34495e;
}

.router-link-exact-active {
  background-color: #1abc9c;
  color: #ffffff;
}
</style>
