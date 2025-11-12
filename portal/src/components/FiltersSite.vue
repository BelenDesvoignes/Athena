<template>
  <div class="filtros-container">
    <input
      v-model="searchTerm"
      @input="updateFilters"
      type="text"
      placeholder="Buscar sitio..."
      class="input-filtro"
    />

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
    
    <input
      v-model="city"
      @input="updateFilters"
      type="text"
      placeholder="Ciudad (ej: Epecuén)"
      class="input-filtro"
    />

    <select v-model="state" @change="updateFilters" class="select-filtro">
      <option value="">Estado de conservación</option>
      <option value="EXCELENTE">Excelente</option>
      <option value="BUENO">Bueno</option>
      <option value="REGULAR">Regular</option>
      <option value="MALO">Malo</option>
    </select>

    <select v-model="orderBy" @change="handleOrderChange" class="select-filtro">
      <option value="registrado">Más recientes</option>
      <option value="nombre">Nombre (A-Z)</option>
      <option value="calificacion">Mejor calificados</option>
    </select>

    <div class="tag-filter-group">
        <label>Tags:</label>
        <div class="tags-list">
            <label v-for="tag in availableTags" :key="tag.id" class="tag-checkbox">
                <input 
                    type="checkbox" 
                    :value="tag.id" 
                    v-model="selectedTags" 
                    @change="updateFilters"
                />
                {{ tag.name }}
            </label>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Inicialización de filtros desde los Query Params
const searchTerm = ref(route.query.search || '')
const province = ref(route.query.province || '')
const city = ref(route.query.city || '') // Nuevo
const state = ref(route.query.state || '') // Nuevo
const orderBy = ref(route.query.order_by || 'registrado')
const orderDirection = ref(route.query.order || 'desc')
// Tags
const availableTags = ref([]) // Lista de todos los tags posibles
const selectedTags = ref([]) // IDs de los tags seleccionados

const provinces = ref([])

const API_BASE_URL = 'https://admin-grupo19.proyecto2025.linti.unlp.edu.ar/api';


// Función para cargar provincias (existente)
const fetchProvinces = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/provinces`)
    if (!response.ok) throw new Error('Error al obtener provincias')
    provinces.value = await response.json()
  } catch (err) {
    console.error('Error al cargar provincias:', err)
  }
}

// Función para cargar tags (Nuevo)
const fetchTags = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/tags`)
    if (!response.ok) throw new Error('Error al obtener tags')
    availableTags.value = await response.json()
  } catch (err) {
    console.error('Error al cargar tags:', err)
  }
}

// Inicializa los tags seleccionados desde los query params
const initSelectedTags = () => {
    if (route.query.tags) {
        selectedTags.value = route.query.tags.split(',').map(id => parseInt(id)).filter(id => !isNaN(id));
    } else {
        selectedTags.value = [];
    }
}


// Manejo especial para el cambio de orden (para fijar la dirección 'desc' o 'asc')
const handleOrderChange = () => {
    // Si se ordena por nombre, la dirección debe ser 'asc' (A-Z)
    if (orderBy.value === 'nombre') {
        orderDirection.value = 'asc';
    } 
    // Para 'registrado' (más reciente) y 'calificacion' (mejor calificados) es 'desc'
    else {
        orderDirection.value = 'desc';
    }
    updateFilters();
}

// Actualizar filtros: empuja los query params al router
const updateFilters = () => {
  // Concatena los IDs de los tags seleccionados en una cadena separada por comas
  const tagsParam = selectedTags.value.length > 0 ? selectedTags.value.join(',') : undefined;

  router.push({
    path: '/sitios',
    query: {
      search: searchTerm.value || undefined,
      province: province.value || undefined,
      city: city.value || undefined, // Nuevo
      state: state.value || undefined, // Nuevo
      tags: tagsParam, // Nuevo
      
      order_by: orderBy.value || 'registrado',
      order: orderDirection.value || 'desc',
      page: 1 // Reinicia a la primera página cada vez que cambian los filtros
    }
  })
}

// Observa el cambio en los query params externos (por si el usuario navega con URL)
watch(
    () => route.query.tags, 
    initSelectedTags, 
    { immediate: true }
);
watch(
    () => route.query.order_by, 
    (newVal) => { 
        orderBy.value = newVal || 'registrado';
        // Ajusta la dirección al cambiar el orden para mantener la consistencia
        if (newVal === 'nombre') orderDirection.value = 'asc';
        else orderDirection.value = 'desc';
    }
);


onMounted(() => {
    fetchProvinces();
    fetchTags(); // Cargar los tags al montar el componente
    initSelectedTags();
});
</script>

<style scoped>
.filtros-container {
  display: flex;
  gap: 10px;
  margin: 20px 0;
  flex-wrap: wrap;
  align-items: flex-start; /* Para alinear el grupo de tags */
}
.input-filtro,
.select-filtro {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1em;
}

/* Estilos para el nuevo grupo de tags */
.tag-filter-group {
    padding: 8px 12px;
    border: 1px solid #ccc;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    background-color: #f9f9f9;
}
.tag-filter-group > label {
    font-weight: bold;
    font-size: 0.9em;
    color: #555;
}
.tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.tag-checkbox {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.9em;
    cursor: pointer;
    padding: 4px 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: white;
}
.tag-checkbox:hover {
    background-color: #f0f0f0;
}
</style>