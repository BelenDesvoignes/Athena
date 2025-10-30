<template>
  <div class="home-portal">
    
    <header class="hero-section">
      <h1>Athena</h1> 
      <div class="search-bar">
        <input 
          type="text" 
          v-model="searchText" 
          placeholder="Buscar sitios por nombre o descripción..." 
          @keyup.enter="performSearch"
        >
        <button @click="performSearch">🔍 Buscar</button>
      </div>
    </header>

    <main class="main-content">
      
      <FeaturedSection 
        title="🔥 Más Visitados" 
        orderByParam="visits-desc" 
      />
      
      <FeaturedSection 
        title="🏆 Mejor Puntuados" 
        orderByParam="rating-5-1" 
      />

      <FeaturedSection 
        title="🆕 Recientemente Agregados" 
        orderByParam="latest" 
      />
      
      <!-- Se ha eliminado la directiva v-if="authStore.isLoggedIn" para evitar el error. 
           Esta sección estará oculta/deshabilitada en FeaturedSection si se usa 
           el orderByParam="favorites" sin token. -->
      <!-- Si la quieres ver, puedes ponerla sin el v-if por ahora, pero sabes que fallará 
           la llamada a la API si no existe el Store. Por ahora la dejo comentada 
           ya que no tienes la lógica de login/token activa: -->
      <!-- <FeaturedSection 
        title="⭐ Tus Favoritos" 
        orderByParam="favorites" 
        listRoute="/me/favorites"
      /> -->

    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'; 
import { useRouter } from 'vue-router';
import FeaturedSection from '@/components/FeaturedSection.vue';
// 🛑 LÍNEAS ELIMINADAS: La importación de useAuthStore causa la pantalla en blanco.
// import { useAuthStore } from '../stores/auth'; 

const router = useRouter();

const searchText = ref('');

// 🛑 LÍNEAS ELIMINADAS: La inicialización de authStore causa la pantalla en blanco.
// const authStore = useAuthStore(); 


const performSearch = () => {
  if (searchText.value.trim()) {
    // Redirige al Listado (/sitios) pasando el texto de búsqueda como parámetro 'query'
    router.push({ 
      path: '/sitios', 
      query: { name: searchText.value } 
    });
  }
};
</script>

<style scoped>

.home-portal {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.hero-section {
  text-align: center;
  padding: 40px 0;
  background-color: white;
  border-radius: 10px;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.hero-section h1 {
  color: #3f51b5;
  font-size: 2.5em;
  margin-bottom: 10px;
}

.search-bar {
  display: flex;
  justify-content: center;
  margin-top: 15px;
  padding: 0 10px;
}

.search-bar input, .search-bar button {
  padding: 12px 15px;
  font-size: 1.1em;
  border-radius: 8px;
  border: none;
  transition: all 0.3s ease;
}

.search-bar input {
    flex-grow: 1;
    max-width: 450px; 
    border: 2px solid #ddd;
    margin-right: 10px;
}

.search-bar button {
  background-color: #ffc107; 
  color: #333;
  cursor: pointer;
  font-weight: bold;
}

.search-bar button:hover {
  background-color: #ffae00;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

/* Adaptación para pantallas pequeñas */
@media (max-width: 600px) {
    .search-bar {
        flex-direction: column;
    }
    .search-bar input {
      margin-right: 0;
      margin-bottom: 10px;
      max-width: none;
    }
}

.main-content {
  margin-top: 40px;
}
</style>
