<template>
  <div class="filtros-container">
    <!-- Filtro por texto -->
    <input
      v-model="searchTerm"
      @input="updateFilters"
      type="text"
      placeholder="Buscar sitio..."
      class="input-filtro"
    />

    <!-- Filtro por provincia -->
    <select v-model="province" @change="updateFilters" class="select-filtro">
      <option value="">Todas las provincias</option>
      <option
        v-for="prov in provinces"
        :key="prov"
        :value="prov"
      >
        {{ prov }}
      </option>
    </select>

    <!-- Orden -->
    <select v-model="orderBy" @change="updateFilters" class="select-filtro">
      <option value="registrado">Más recientes</option>
      <option value="nombre">Nombre (A-Z)</option>
      <option value="calificacion">Mejor calificados</option>
    </select>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const searchTerm = ref(route.query.search || '')
const province = ref(route.query.province || '')
const orderBy = ref(route.query.order_by || 'registrado')
const orderDirection = ref(route.query.order || 'desc')
const provinces = ref([])

const API_BASE_URL = 'http://localhost:5000/api'

// ✅ Cargar provincias desde el endpoint correcto
const fetchProvinces = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/provinces`)
    if (!response.ok) throw new Error('Error al obtener provincias')
    provinces.value = await response.json()
  } catch (err) {
    console.error('Error al cargar provincias:', err)
  }
}

// ✅ Actualizar filtros (mantiene todos los query params compatibles con la API)
const updateFilters = () => {
  router.push({
    path: '/sitios',
    query: {
      search: searchTerm.value || undefined,
      province: province.value || undefined,
      order_by: orderBy.value || 'registrado',
      order: orderDirection.value || 'desc',
      page: 1 // 👈 reinicia a la primera página cada vez que cambian los filtros
    }
  })
}

onMounted(fetchProvinces)
</script>

<style scoped>
.filtros-container {
  display: flex;
  gap: 10px;
  margin: 20px 0;
  flex-wrap: wrap;
}
.input-filtro,
.select-filtro {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1em;
}
</style>
