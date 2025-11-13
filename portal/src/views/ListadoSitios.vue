<template>
  <div class="listado-sitios-page">
    <header>
      <h1>Listado de Sitios Históricos</h1>
      <FiltersSite ref="filtersSiteRef" /> 

      <button v-if="Object.keys(route.query).length > 0" 
              @click="clearFilters" 
              class="clear-filters-button">
          Limpiar Filtros
      </button>

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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FiltersSite from '@/components/FiltersSite.vue'
import SiteCard from '@/components/SiteCard.vue'

const route = useRoute()
const router = useRouter()
const filtersSiteRef = ref(null) 

const sites = ref([])
const isLoading = ref(true)
const error = ref(null)
const errorMessage = ref('')

const pagination = ref({
    page: 1,
    pages: 1,
    total: 0,
    per_page: 10
})

const API_BASE_URL = 'https://admin-grupo19.proyecto2025.linti.unlp.edu.ar/api';


const clearFilters = () => {
    if (filtersSiteRef.value && filtersSiteRef.value.resetForm) {
        filtersSiteRef.value.resetForm()
    }
    router.push({ query: {} })
}

// --- Computed (vinculados a query params) ---
const currentSearch = computed(() => route.query.search || '')
const currentProvince = computed(() => route.query.province || '')
const currentOrder = computed(() => route.query.order_by || 'registrado')
const currentOrderDirection = computed(() => route.query.order || 'desc')
const currentCity = computed(() => route.query.city || '')
const currentState = computed(() => route.query.state || '')
const currentTags = computed(() => route.query.tags || '')
const currentPage = computed(() => route.query.page || 1) // 👈 Es importante que tome el 'page' de la URL
const perPage = computed(() => route.query.per_page || 10)

const goToPage = (pageNumber) => {
    // Asegura que el número de página sea válido
    if (pageNumber < 1 || pageNumber > pagination.value.pages) {
        return;
    }
    
    // Mantiene todos los filtros actuales y solo cambia el parámetro 'page'
    router.push({
        query: {
            ...route.query,
            page: pageNumber
        }
    })
}

// --- Fetch principal ---
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

// 🔄 El watcher observa cambios en CUALQUIER query param para recargar
watch(
  [currentSearch, currentProvince, currentOrder, currentOrderDirection, currentCity, currentState, currentTags, currentPage],
  fetchSitesList
)

onMounted(fetchSitesList)
</script>

<style scoped>
/* Estilos existentes */
h1 { margin-bottom: 10px; }
.list-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; padding: 20px 0; }
.status-message, .error-message, .empty-message { text-align: center; margin-top: 40px; color: #666; }
.clear-filters-button { background-color: #f87171; color: white; border: none; padding: 8px 15px; margin-bottom: 15px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: background-color 0.2s; }
.clear-filters-button:hover { background-color: #ef4444; }

.pagination-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    padding: 20px 0;
    margin-top: 20px;
    border-top: 1px solid #eee;
}
.pagination-info {
    color: #555;
    font-size: 1em;
    font-weight: 500;
}
.pagination-button {
    background-color: #3b82f6;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 5px;
    cursor: pointer;
    font-weight: bold;
    transition: background-color 0.2s;
}
.pagination-button:disabled {
    background-color: #93c5fd;
    cursor: not-allowed;
}
.pagination-button:not(:disabled):hover {
    background-color: #2563eb;
}
</style>