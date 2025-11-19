<template>
  <router-link :to="`/sitios/${site.id}`" class="site-card">
    <div class="card-image-container">
      <img 
        :src="site.image_url || '/default-image.jpg'" 
        :alt="site.image_title || site.name" 
        class="card-image"
      />
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
import { defineProps } from 'vue';

const props = defineProps({
  site: {
    type: Object,
    required: true,
  }
});
</script>

<style scoped>
.site-card {
  display: block;
  text-decoration: none;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  margin: 10px 0;
  transition: transform 0.2s;
}
.site-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}


.card-image-container {
  width: 100%;
  height: 180px;     
  overflow: hidden;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover; 
  object-position: center; 
}
</style>
