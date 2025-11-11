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
const currentOrder = computed(() => route.query.order_by || 'registrado'); 
const currentNameFilter = computed(() => route.query.search || ''); 

// --- Lógica de Carga ---
const fetchSitesList = async () => {
    isLoading.value = true;
    error.value = null;
    errorMessage.value = '';

    try {
        const fullUrlString = `${API_BASE_URL}/sites`;
        const url = new URL(fullUrlString);

        // Agregar parámetros de búsqueda codificados
        url.searchParams.set('order_by', currentOrder.value);
        
        // Usar 'search' para el filtro de nombre, coherente con HomeView
        if (currentNameFilter.value) {
            url.searchParams.set('search', currentNameFilter.value);
        }

        // Opcional: agregar paginación si luego implementas currentPage/perPage
        // url.searchParams.set('page', currentPage.value);
        // url.searchParams.set('per_page', 12);

        const response = await fetch(url.toString());

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        // Asegúrate de leer de data.data, como en FeaturedSection
        sites.value = data.data || [];

    } catch (err) {
        console.error('Fetch error for site list:', err);
        errorMessage.value = err.message;
        error.value = true;
    } finally {
        isLoading.value = false;
    }
};

// --- Re-cargar al cambiar los parámetros ---
watch([currentOrder, currentNameFilter], () => {
    fetchSitesList();
});

onMounted(() => {
    fetchSitesList();
});
</script>

<style scoped>
.list-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    padding: 20px 0;
}
</style>
