<template>
  <div class="listado-sitios-page">

    <header>
      <BackButton />
      <h1>Listado de Sitios Históricos</h1>
      <!-- FiltersSite maneja todos los filtros, incluyendo el de favoritos -->
      <FiltersSite ref="filtersSiteRef" />

      <div class="controls-group">
        <div class="map-controls">
          <button
            @click="openMapModal"
            :class="{'btn-active': isModalOpen}"
            class="map-toggle-button"
          >
            Ver mapa de sitios
          </button>

          <button v-if="Object.keys(route.query).length > 0"
                  @click="clearAllFilters"
                  class="clear-filters-button">
            Limpiar Filtros
          </button>
        </div>
      </div>
    </header>

    <main>
      <div v-if="isLoading" class="status-message">Cargando sitios...</div>
      <div v-else-if="error" class="error-message">❌ Error al cargar el listado: {{ error }}</div>

      <div v-else-if="sites.length > 0" class="list-grid">
        <SiteCard
          v-for="site in sites"
          :key="site.id"
          :site="site"
          @toggle-favorite="fetchSitesList"
        />
      </div>

      <div v-else class="empty-message">
        No se encontraron sitios con los filtros aplicados.
      </div>
    </main>

    <!-- PAGINACIÓN -->
    <nav v-if="pagination.total > 0" class="pagination-controls">
      <p class="pagination-info">
        Página {{ pagination.page }} de {{ pagination.pages }}
      </p>

      <button @click="goToPage(pagination.page - 1)"
              :disabled="pagination.page === 1"
              class="pagination-button">
        ← Anterior
      </button>

      <button @click="goToPage(pagination.page + 1)"
              :disabled="pagination.page === pagination.pages"
              class="pagination-button">
        Siguiente →
      </button>
    </nav>

    <!-- MODAL MAPA -->
    <div v-if="isModalOpen" class="modal-overlay" @click.self="isModalOpen = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Mapa de Sitios Históricos</h2>
          <button class="close-button" @click="isModalOpen = false">&times;</button>
        </div>

        <div class="modal-body">
          <SiteMap
            ref="siteMapRef"
            :sites="sites"
            :lat="currentLat"
            :lon="currentLon"
            :radius="currentRadius"
            @filterByLocation="applyUserLocationFilter"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import FiltersSite from '@/components/FiltersSite.vue'
import SiteCard from '@/components/SiteCard.vue'
import SiteMap from '@/components/SiteMap.vue'
import BackButton from '@/components/BackButton.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { token } = storeToRefs(authStore) 

const filtersSiteRef = ref(null)
const siteMapRef = ref(null)

const sites = ref([])
const isLoading = ref(true)
const error = ref('')
const isModalOpen = ref(false)

const isFavoriteFilterActive = computed(() => route.query.favorites === 'true')

const currentLat = computed(() => route.query.lat || null)
const currentLon = computed(() => route.query.lon || null)
const currentRadius = computed(() => route.query.radius || null)


const clearAllFilters = () => {
  filtersSiteRef.value?.resetForm?.()
  router.push({ query: {} })
}


const openMapModal = async () => {
  isModalOpen.value = true
  await nextTick()
  siteMapRef.value?.forceUpdate()
}


const applyUserLocationFilter = ({ lat, lon, radius }) => {
  router.push({
    query: {
      ...route.query,
      lat,
      lon,
      radius,
      order_by: "distancia",
      order: "asc",
      page: 1
    }
  })
}


const pagination = ref({
  page: 1,
  pages: 1,
  total: 0,
  per_page: 10
})

const goToPage = (p) => {
  if (p < 1 || p > pagination.value.pages) return
  router.push({ query: { ...route.query, page: p } })
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const fetchSitesList = async () => {
  isLoading.value = true
  error.value = ''

  
  const orderBy = route.query.order_by || "registrado";
  const order = route.query.order || "desc";
  const page = route.query.page || 1;
  const perPage = route.query.per_page || 10;


  const params = new URLSearchParams({
    order_by: orderBy,
    order: order,
    page: page,
    per_page: perPage,
  })

  
  const dynamic = ["search", "province", "city", "state", "tags", "lat", "lon", "radius"]
  dynamic.forEach(p => route.query[p] && params.append(p, route.query[p]))

  const fetchingFavorites = isFavoriteFilterActive.value;
  let headers = {};

  if (fetchingFavorites) {
    
    params.append('is_favorite', 'true');

  
    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`;
    } else {
      
      isLoading.value = false;
      error.value = "Debes iniciar sesión para filtrar tus sitios favoritos.";
      sites.value = [];
    
      const newQuery = { ...route.query };
      delete newQuery.favorites;
      router.replace({ query: newQuery });
      return;
    }
  }

  try {
    const res = await fetch(`${API_BASE_URL}/sites?${params.toString()}`, { headers })

    if (!res.ok) {
      throw new Error(`Fallo la solicitud del listado. Código: ${res.status}`);
    }

    const data = await res.json()

    sites.value = data.data || []
    pagination.value = {
      page: data.page,
      pages: data.pages,
      total: data.total,
      per_page: data.per_page,
    }

    

  } catch (e) {
    console.error("Error al obtener sitios:", e);
    error.value = e.message || 'Ocurrió un error inesperado al cargar los sitios.';
  } finally {
    isLoading.value = false
  }
}

watch(() => route.query, fetchSitesList, { immediate: true })
onMounted(fetchSitesList)
</script>

<style scoped>
/* Estilos sin cambios */
.controls-group {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    align-items: center;
    margin-bottom: 15px;
}
.map-controls { display: flex; gap: 15px; }

h1 { margin-bottom: 10px; }
.list-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; padding: 20px 0; }
.status-message, .error-message, .empty-message { text-align: center; margin-top: 40px; color: #666; }
.error-message { color: #0f0f0f; font-weight: bold; background-color: #ffeaea; padding: 15px; border-radius: 8px; border: 1px solid #ffcccc; }


.map-toggle-button, .proximity-filter-button, .clear-filters-button {
    border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: background-color 0.2s;
}
.map-toggle-button { background-color: #071a78; color: white; }
.proximity-filter-button { background-color: #007bff; color: white; }
.clear-filters-button { background-color: #071a78; color: white; }

.map-toggle-button:hover, .proximity-filter-button:not(:disabled):hover { background-color: #0056b3; }
.proximity-filter-button:disabled { background-color: #6c757d; cursor: not-allowed; }
.map-toggle-button.btn-active, .proximity-filter-button.btn-active { background-color: #28a745; }
.clear-filters-button:hover { background-color: #ef4444; }

.pagination-controls { display: flex; justify-content: center; align-items: center; gap: 20px; padding: 20px 0; margin-top: 20px; border-top: 1px solid #eee; }
.pagination-info { color: #555; font-size: 1em; font-weight: 500; }
.pagination-button { background-color: #071a78; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: background-color 0.2s; }
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
    min-height: 500px;
}
</style>