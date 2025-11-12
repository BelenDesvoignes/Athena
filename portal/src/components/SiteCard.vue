<template>
  <router-link :to="`/sitios/${site.id}`" class="site-card">
    <div class="card-image-container">
      <img
        :src="site.image_url || defaultImage"
        :alt="site.name"
        class="card-image"
      />
    </div>

    <div class="card-body">
      <h3 class="card-title">{{ site.name }}</h3>
      <p class="card-location">{{ site.city }}, {{ site.province }}</p>

      <div v-if="site.category" class="card-category">
        <span class="category-chip">{{ site.category }}</span>
      </div>

      <div v-if="site.rating" class="card-rating">
        <span class="star-icon">⭐</span>
        <span class="rating-value">{{ site.rating.toFixed(1) }}</span>
      </div>

      <p v-if="site.description" class="card-description">
        {{ truncate(site.description, 80) }}
      </p>
    </div>
  </router-link>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  site: {
    type: Object,
    required: true
  }
})

const defaultImage = '/default-image.jpg'

const truncate = (text, maxLength) =>
  text?.length > maxLength ? text.slice(0, maxLength) + '…' : text
</script>

<style scoped>
.site-card {
  display: block;
  text-decoration: none;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 12px;
  overflow: hidden;
  margin: 10px 0;
  transition: transform 0.2s, box-shadow 0.2s;
  background: white;
}
.site-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
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
}
.card-body {
  padding: 12px 16px;
}
.card-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 4px;
  color: #222;
}
.card-location {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 6px;
}
.card-category .category-chip {
  background-color: #eef2ff;
  color: #3b82f6;
  font-size: 0.8rem;
  padding: 3px 8px;
  border-radius: 8px;
  display: inline-block;
  margin-bottom: 6px;
}
.card-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #ffb400;
  font-size: 0.9rem;
}
.card-description {
  color: #555;
  font-size: 0.85rem;
  margin-top: 6px;
  line-height: 1.3;
}
</style>
