<script setup>
import { ref, computed, onMounted } from 'vue'; 
import { useRouter } from 'vue-router';
import FeaturedSection from '@/components/FeaturedSection.vue';


const router = useRouter();

const searchText = ref(''); 

const performSearch = () => {
  if (searchText.value.trim()) {
    // Redirige al Listado (/sitios) pasando el texto de búsqueda como parámetro 'query'
    router.push({ 
      path: '/sitios', 
      query: { search: searchText.value } 
    });
  }
};

</script>

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
        orderByParam="nombre" 
      />
      
      <FeaturedSection 
        title="🏆 Mejor Puntuados" 
        orderByParam="calificacion" 
      />

      <FeaturedSection 
        title="🆕 Recientemente Agregados" 
        orderByParam="registrado" 
      />
      
  

    </main>
  </div>
</template>


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

.google-login {
  margin-top: 25px;
}

.google-login button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  font-size: 1.1em;
  font-weight: bold;
  color: #555;
  background-color: white;
  border: 2px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.google-login button:hover {
  background-color: #f5f5f5;
  border-color: #ccc;
}

.google-login img {
  width: 20px;
  height: 20px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 15px;
  font-size: 1.1em;
  font-weight: bold;
  color: #555;
  background-color: white;
  border: 2px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 5px;
}

.btn:hover {
  background-color: #f5f5f5;
  border-color: #ccc;
}
</style>
