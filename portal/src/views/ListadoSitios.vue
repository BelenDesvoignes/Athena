<template>
  <div class="listado-sitios-page">
    <header>
      <h1>Listado de Sitios Históricos</h1>
      <p v-if="currentOrder">Orden actual: **{{ currentOrder }}**</p>
      <p v-if="currentNameFilter">Filtro de búsqueda: **{{ currentNameFilter }}**</p>
    </header>

    <main>
        <div v-if="isLoading" class="status-message">Cargando sitios...</div>
        <div v-else-if="error" class="error-message">❌ Error al cargar el listado: {{ errorMessage }}</div>
        
        <div v-else-if="sites.length > 0" class="list-grid">
            <SiteCard 
                v-for="site in sites" 
                :key="site.id" 
                :site="site" 
            />
        </div>
        <div v-else class="empty-message">
            No se encontraron sitios con los filtros aplicados.
        </div>
        
        </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import SiteCard from '@/components/SiteCard.vue';

const route = useRoute();

// --- Estados ---
const sites = ref([]);
const isLoading = ref(true);
const error = ref(null);
const errorMessage = ref('');

const API_BASE_URL = 'https://grupo19.proyecto2025.linti.unlp.edu.ar/api'; 

// --- Computed Properties para Query Params ---
// Captura el orden enviado por FeaturedSection (ej: 'latest')
const currentOrder = computed(() => route.query.order_by || 'latest'); 
// Captura el texto de búsqueda enviado por HomeView (ej: 'museo')
const currentNameFilter = computed(() => route.query.name || ''); 

// --- Lógica de Carga ---
const fetchSitesList = async () => {
    isLoading.value = true;
    error.value = null;
    errorMessage.value = '';

    // 1. Construir la URL con todos los filtros
    let url = `${API_BASE_URL}/sites?`;
    
    // Añadir el orden
    url += `order_by=${currentOrder.value}`;

    // Añadir el filtro de búsqueda por nombre/descripción (si existe)
    if (currentNameFilter.value) {
        url += `&name=${currentNameFilter.value}`;
    }
    
    // NOTA: Aquí agregarías la paginación: `&page=${currentPage.value}&per_page=12`

    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Error al obtener el listado. Código: ${response.status}`);
        }
        
        const data = await response.json();
        sites.value = data.sites || data; // Asumiendo que devuelve un array o un objeto con clave 'sites'

    } catch (err) {
        console.error('Fetch error for site list:', err);
        errorMessage.value = err.message;
        error.value = true;
    } finally {
        isLoading.value = false;
    }
};

// 3. Re-cargar al cambiar los parámetros
// Usamos 'watch' para detectar cambios en la URL (al cambiar la búsqueda o el orden)
watch([currentOrder, currentNameFilter], () => {
    fetchSitesList();
});


onMounted(() => {
    fetchSitesList();
});
</script>

<style scoped>
/* Estilos específicos del listado */
.list-grid {
    display: grid;
    /* Adapta el número de columnas para el listado */
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    padding: 20px 0;
}
</style>

