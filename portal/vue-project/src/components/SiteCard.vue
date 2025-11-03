<template>
  <router-link :to="`/sitios/${site.id}`" class="site-card">
    <div class="card-image-container">
      <img :src="site.image_url || '/default-image.jpg'" :alt="site.name" class="card-image">
    </div>
    <div class="card-body">
      <h3 class="card-title">{{ site.name }}</h3>
      <p class="card-location">{{ site.city }}, {{ site.province }}</p>
      
      <div v-if="site.rating" class="card-rating">
        <span class="star-icon">⭐</span>
        <span class="rating-value">{{ site.rating.toFixed(1) }}</span>
      </div>
    </div>
  </router-link>
</template>

<script setup>
// Options API o Composition API (setup)
import { defineProps } from 'vue';

const props = defineProps({
  site: {
    type: Object,
    required: true,
    // Estructura mínima esperada:
    // { id, name, city, province, rating, image_url }
  }
});
</script>

<style scoped>
/* Estilos Mobile First */
.site-card {
  display: block;
  text-decoration: none;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  margin: 10px 0;
  transition: transform 0.2s;
  /* (Asegúrate de que este estilo sea responsive) */
}
.site-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
/* ... Estilos para imagen, título, etc. ... */
</style>