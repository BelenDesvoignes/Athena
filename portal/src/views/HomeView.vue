<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import FeaturedSection from '@/components/FeaturedSection.vue';

const router = useRouter();

const searchText = ref('');

const performSearch = () => {
  if (searchText.value.trim()) {
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
  padding: 20px 0;
  background-color: white;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.search-bar {
  display: flex;
  justify-content: center;
  margin-top: 5px;
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
  background-color: #deddd9;
  color: #070e48;
  cursor: pointer;
  font-weight: bold;
}

.search-bar button:hover {
  background-color: #cbc8c3;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

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