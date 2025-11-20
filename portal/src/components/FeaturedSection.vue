<template>
<section class="featured-section">
<header class="section-header">
<h2>{{ title }}</h2>
<RouterLink
  v-if="sites.length > 0"
  :to="{
    path: listRoute,
    query: {
      favorites: props.isFavorite,
      order_by: props.orderByParam,
      order: 'desc'
    }
  }"
  class="btn-ver-todos"
>
Ver todos &gt;
</RouterLink>
</header>
<div v-if="isLoading" class="status-message loading-pulse">
Cargando {{ title.toLowerCase() }}...
</div>
<div v-else-if="error" class="status-message error-box">
❌ Error al cargar los sitios: **{{ errorMessage }}**
<p v-if="props.isFavorite && errorMessage.includes('401')">
Tu sesión ha expirado o no estás autorizado. Por favor, vuelve a iniciar sesión.
</p>
</div>
<div v-else-if="sites.length > 0" class="site-list">
<SiteCard v-for="site in sites" :key="site.id" :site="site" />
</div>
<div v-else-if="props.isFavorite" class="status-message empty-box">
Aún no tienes sitios marcados como favoritos.
</div>
<div v-else class="status-message empty-box">
No se encontró contenido para esta sección.
</div>
</section>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import SiteCard from './SiteCard.vue';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';
const authStore = useAuthStore();
const { token, isLoggedIn } = storeToRefs(authStore);
const props = defineProps({
title: { type: String, required: true },
orderByParam: { type: String, required: true },
listRoute: { type: String, default: '/sitios' },
isFavorite: { type: Boolean, default: false }
});
const sites = ref([]);
const isLoading = ref(true);
const error = ref(false);
const errorMessage = ref('');
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const MAX_SITES = 4;
const fetchSites = async () => {
isLoading.value = true;
error.value = false;
errorMessage.value = '';
if (props.isFavorite && !isLoggedIn.value) {
errorMessage.value = 'Esta funcionalidad requiere iniciar sesión.';
isLoading.value = false;
error.value = true;
return;
}
const params = new URLSearchParams({
order_by: props.orderByParam,
order: 'desc',
per_page: MAX_SITES
});
const headers = {};
if (props.isFavorite) {
params.append('is_favorite', 'true');
headers['Authorization'] = `Bearer ${token.value}`;
}
const url = `${API_BASE_URL}/sites?${params.toString()}`;
try {
const response = await fetch(url, { headers });
if (response.status === 401) {
throw new Error(`HTTP error! status: 401 - No Autorizado`);
}
if (!response.ok) {
throw new Error(`HTTP error! status: ${response.status}`);
}
const data = await response.json();
sites.value = data.data || [];
} catch (err) {
console.error(`Fetch error for ${props.title}:`, err);
errorMessage.value = err.message || 'Error desconocido al conectar con la API.';
error.value = true;
} finally {
isLoading.value = false;
}
};
onMounted(() => {
fetchSites();
});
</script>

<style scoped>
.featured-section { margin-bottom: 40px; padding: 10px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
.section-header h2 { font-size: 1.8em; color: #444; }
.btn-ver-todos { text-decoration: none; color: #3f51b5; font-weight: bold; transition: color 0.3s; }
.btn-ver-todos:hover { color: #ffc107; }
.site-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.status-message { padding: 20px; text-align: center; border-radius: 8px; font-size: 1.1em; }
.loading-pulse { color: #3f51b5; font-style: italic; background-color: #e8eaf6; }
.error-box { background-color: #ffebee; color: #c62828; border: 1px solid #ef9a9a; }
.empty-box { background-color: #f5f5f5; color: #757575; }
@media (max-width: 768px) { .site-list { grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); } }
</style>
