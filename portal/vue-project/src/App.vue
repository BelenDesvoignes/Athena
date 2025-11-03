<script setup>
import { RouterView } from 'vue-router';
// Importa el navbar o componentes de layout si los tienes aquí
// import AppNavbar from './components/AppNavbar.vue'; 
</script>

<template>
  <div id="app-wrapper">
    <!-- Aquí iría cualquier layout fijo (Navbar, Footer) -->

    <!-- 🔑 CLAVE: Aquí se inyecta el contenido de la ruta / -->
    <RouterView /> 
  </div>
</template>

<style>
/* Estilos globales */
#app-wrapper {
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
/* Asegúrate de que no haya estilos conflictivos aquí */
</style>