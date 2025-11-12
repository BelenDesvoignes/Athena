<template>
  <div class="listado-sitios-page">
    <header>
      <h1>Listado de Sitios Históricos</h1>
      <FiltersSite />

      <p v-if="currentSearch" class="status-info">
        Filtro de búsqueda: <strong>{{ currentSearch }}</strong>
      </p>
      <p v-if="currentProvince" class="status-info">
        Provincia: <strong>{{ currentProvince }}</strong>
      </p>
      <p v-if="currentOrder" class="status-info">
        Orden actual: <strong>{{ currentOrder }}</strong>
      </p>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import FiltersSite from '@/components/FiltersSite.vue'
import SiteCard from '@/components/SiteCard.vue'

const route = useRoute()

const sites = ref([])
const isLoading = ref(true)
const error = ref(null)
const errorMessage = ref('')


const API_BASE_URL = 'https://admin-grupo19.proyecto2025.linti.unlp.edu.ar/api';


// --- Computed (vinculados a query params) ---
const currentSearch = computed(() => route.query.search || '')
const currentProvince = computed(() => route.query.province || '')
const currentOrder = computed(() => route.query.order_by || 'registrado')
const currentOrderDirection = computed(() => route.query.order || 'desc')
const currentCity = computed(() => route.query.city || '')
const currentState = computed(() => route.query.state || '')
const currentTags = computed(() => route.query.tags || '')
const currentPage = computed(() => route.query.page || 1)
const perPage = computed(() => route.query.per_page || 10)

// --- Fetch principal ---
const fetchSitesList = async () => {
  isLoading.value = true
  error.value = null
  errorMessage.value = ''

  // 🔗 Construcción de URL dinámica con todos los filtros válidos
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

  const url = `${API_BASE_URL}?${params.toString()}`

  try {
    const response = await fetch(url)
    if (!response.ok) throw new Error(`Error al obtener el listado (${response.status})`)

    const data = await response.json()
    sites.value = data.data || []
  } catch (err) {
    console.error('Error al cargar sitios:', err)
    error.value = true
    errorMessage.value = err.message
  } finally {
    isLoading.value = false
  }
}

// 🔄 Actualiza automáticamente si cambian filtros o búsqueda
watch(
  [currentSearch, currentProvince, currentOrder, currentOrderDirection, currentCity, currentState, currentTags, currentPage],
  fetchSitesList
)

onMounted(fetchSitesList)
</script>

<style scoped>
h1 {
  margin-bottom: 10px;
}
.status-info {
  color: #666;
  font-size: 0.9rem;
}
.list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px 0;
}
.status-message,
.error-message,
.empty-message {
  text-align: center;
  margin-top: 40px;
  color: #666;
}
.loader {
  width: 18px;
  height: 18px;
  border: 3px solid #ddd;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  display: inline-block;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
