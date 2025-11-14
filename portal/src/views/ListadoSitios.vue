<template>
  <div class="listado-sitios-page">
    <header>
      <h1>Listado de Sitios Históricos</h1>
      <FiltersSite ref="filtersSiteRef" /> 

      <div class="map-controls">
        <button 
          @click="openMapModal" 
          :class="{'btn-active': isModalOpen}" 
          class="map-toggle-button"
        >
          Ver Mapa de Sitios
        </button>

        <button 
          @click="applyProximityFilter" 
          :disabled="isProximityFilterActive"
          :class="{'btn-active': isProximityFilterActive}" 
          class="proximity-filter-button"
        >
          Filtrar a 1000 km de CABA
        </button>

        <button v-if="Object.keys(route.query).length > 0" 
              @click="clearAllFilters" 
              class="clear-filters-button">
          Limpiar Filtros
        </button>
      </div>
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
    
    <nav v-if="pagination.total > 0" class="pagination-controls">
        <p class="pagination-info">
          Página {{ pagination.page }} de {{ pagination.pages }} 
          (Total de sitios: {{ pagination.total }})
        </p>

        <button 
          @click="goToPage(pagination.page - 1)" 
          :disabled="pagination.page === 1"
          class="pagination-button"
        >
          &larr; Anterior
        </button>

        <button 
          @click="goToPage(pagination.page + 1)" 
          :disabled="pagination.page === pagination.pages"
          class="pagination-button"
        >
          Siguiente &rarr;
        </button>
    </nav>

    <!-- MODAL DEL MAPA -->
    <div v-if="isModalOpen" class="modal-overlay" @click.self="isModalOpen = false">
      <div class="modal-content">
        <div class="modal-header">
            <h2>Mapa de Sitios Históricos</h2>
            <button class="close-button" @click="isModalOpen = false">&times;</button>
        </div>
        <div class="modal-body">
            <!-- Referencia al mapa para llamar a forceUpdate -->
            <SiteMap ref="siteMapRef" :sites="sites" />
        </div>
      </div>
    </div>
    <!-- FIN MODAL DEL MAPA -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FiltersSite from '@/components/FiltersSite.vue'
import SiteCard from '@/components/SiteCard.vue'
import SiteMap from '@/components/SiteMap.vue' 

const filtersSiteRef = ref(null)
const siteMapRef = ref(null)

const route = useRoute()
const router = useRouter()

const sites = ref([])
const isLoading = ref(true)
const error = ref(null)
const errorMessage = ref('')

const isModalOpen = ref(false)

const FIXED_GEO_PARAMS = {
    lat: -34.6037, 
    lon: -58.3816, 
    radius: 1000,
}

const pagination = ref({
  page: 1,
  pages: 1,
  total: 0,
  per_page: 10
})

const clearAllFilters = () => {
    if (filtersSiteRef.value && filtersSiteRef.value.resetForm) {
        filtersSiteRef.value.resetForm()
    }
    router.push({ query: {} }) 
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const currentLat = computed(() => route.query.lat || null)
const currentLon = computed(() => route.query.lon || null)
const currentRadius = computed(() => route.query.radius || null)
const isProximityFilterActive = computed(() => !!currentLat.value && !!currentLon.value && !!currentRadius.value)

const currentSearch = computed(() => route.query.search || '')
const currentProvince = computed(() => route.query.province || '')
const currentOrder = computed(() => route.query.order_by || 'registrado')
const currentOrderDirection = computed(() => route.query.order || 'desc')
const currentCity = computed(() => route.query.city || '')
const currentState = computed(() => route.query.state || '')
const currentTags = computed(() => route.query.tags || '')
const currentPage = computed(() => route.query.page || 1)
const perPage = computed(() => route.query.per_page || 10)

const openMapModal = async () => {
    isModalOpen.value = true;
    await nextTick();
    if (siteMapRef.value && siteMapRef.value.forceUpdate) {
        siteMapRef.value.forceUpdate();
    }
}

const applyProximityFilter = () => {
  router.push({
    query: {
      ...route.query, 
      lat: FIXED_GEO_PARAMS.lat,
      lon: FIXED_GEO_PARAMS.lon,
      radius: FIXED_GEO_PARAMS.radius,
      order_by: 'distancia', 
      order: 'asc', 
      page: 1
    }
  });
}

const goToPage = (pageNumber) => {
    if (pageNumber < 1 || pageNumber > pagination.value.pages) return;

    router.push({
        query: {
            ...route.query,
            page: pageNumber
        }
    })
}

const fetchSitesList = async () => {
  isLoading.value = true
  error.value = null
  errorMessage.value = ''

  const params = new URLSearchParams({
    order_by: currentOrder.value,
    order: currentOrderDirection.value,
    page: currentPage.value,
    per_page: perPage.value
  })

  if (currentSearch.value) params.append('search', currentSearch.value)
  if (currentProvince.value) params.append('province', currentProvince.value)
  if (currentCity.value) params.append('city', currentCity.value)
  if (currentState.value) params.append('state', currentState.value)
  if (currentTags.value) params.append('tags', currentTags.value)
  if (currentLat.value) params.append('lat', currentLat.value)
  if (currentLon.value) params.append('lon', currentLon.value)
  if (currentRadius.value) params.append('radius', currentRadius.value)

  const url = `${API_BASE_URL}/sites?${params.toString()}`

  try {
    const response = await fetch(url)
    if (!response.ok) throw new Error(`Error al obtener el listado (${response.status})`)

    const data = await response.json()
    sites.value = data.data || [] 
    
    pagination.value = {
        page: data.page,
        pages: data.pages,
        total: data.total,
        per_page: data.per_page
    }
  } catch (err) {
    console.error('Error al cargar sitios:', err)
    error.value = true
    errorMessage.value = err.message
  } finally {
    isLoading.value = false
  }
}

watch(
  [() => route.query.search, () => route.query.province, () => route.query.order_by, () => route.query.order, () => route.query.city, () => route.query.state, () => route.query.tags, () => route.query.page, () => route.query.lat, () => route.query.lon, () => route.query.radius], 
  fetchSitesList,
  { immediate: true }
)

onMounted(fetchSitesList)
</script>

<style scoped>
h1 { margin-bottom: 10px; }
.list-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; padding: 20px 0; }
.status-message, .error-message, .empty-message { text-align: center; margin-top: 40px; color: #666; }

.map-controls { display: flex; gap: 15px; margin-bottom: 15px; }
.map-toggle-button, .proximity-filter-button, .clear-filters-button {
    border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: background-color 0.2s; 
}
.map-toggle-button { background-color: #007bff; color: white; }
.proximity-filter-button { background-color: #007bff; color: white; }
.clear-filters-button { background-color: #f87171; color: white; }

.map-toggle-button:hover, .proximity-filter-button:not(:disabled):hover { background-color: #0056b3; }
.proximity-filter-button:disabled { background-color: #6c757d; cursor: not-allowed; }
.map-toggle-button.btn-active, .proximity-filter-button.btn-active { background-color: #28a745; }
.clear-filters-button:hover { background-color: #ef4444; }

.pagination-controls { display: flex; justify-content: center; align-items: center; gap: 20px; padding: 20px 0; margin-top: 20px; border-top: 1px solid #eee; }
.pagination-info { color: #555; font-size: 1em; font-weight: 500; }
.pagination-button { background-color: #3b82f6; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: background-color 0.2s; }
.pagination-button:disabled { background-color: #93c5fd; cursor: not-allowed; }
.pagination-button:not(:disabled):hover { background-color: #2563eb; }

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    padding: 20px;
    border-radius: 8px;
    width: 90%;
    max-width: 1000px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    position: relative;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
    margin-bottom: 10px;
}

.close-button {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #999;
}

.modal-body {
    flex-grow: 1;
    min-height: 500px; /* important: define min-height so map has space */
}
</style>
