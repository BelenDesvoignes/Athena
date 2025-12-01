<template>
  <div class="filter-controls-wrapper">
    <!-- Header/Botón de Colapso (visible solo en móvil) -->
    <div class="filter-header" @click="isFiltersOpen = !isFiltersOpen">
      <h3>
        Filtros de Búsqueda
      </h3>
      <span class="toggle-icon">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          :class="{ 'rotate-up': isFiltersOpen }"
        >
          <path d="M11.9997 10.8284L7.04996 15.7782L5.63574 14.364L11.9997 8L18.3637 14.364L16.9495 15.7782L11.9997 10.8284Z" />
        </svg>
      </span>
    </div>

    <!-- Contenido colapsable (filtros) -->
    <div :class="['filtros-container', { 'is-open': isFiltersOpen }]">
      <input
        v-model="searchTerm"
        @input="updateFilters"
        type="text"
        placeholder="Buscar sitio..."
        class="input-filtro"
      />

      <input
        v-model="city"
        @input="updateFilters"
        type="text"
        placeholder="Ciudad (ej: Epecuén)"
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

      <select v-model="state" @change="updateFilters" class="select-filtro">
        <option value="">Estado de conservación</option>
        <option value="EXCELENTE">Excelente</option>
        <option value="BUENO">Bueno</option>
        <option value="REGULAR">Regular</option>
        <option value="MALO">Malo</option>
      </select>

      <select v-model="orderByCombined" @change="handleCombinedOrderChange" class="select-filtro">
        <option value="">Ordenar por...</option>
        <option value="registrado_desc">Más recientes</option>
        <option value="registrado_asc">Más antiguos</option>
        <option value="nombre_asc">Nombre (A-Z)</option>
        <option value="nombre_desc">Nombre (Z-A)</option>
        <option value="calificacion_desc">Mejor calificados</option>
        <option value="calificacion_asc">Peor calificados</option>
      </select>

      <!-- FILTRO FAVORITOS: Botón de filtro con estilos unificados -->
      <label v-if="token" class="tag-checkbox favorite-filter-button">
        <input
          type="checkbox"
          :value="true"
          v-model="onlyFavorites"
          @change="updateFilters"
        />
        <span>Mis Favoritos</span>
      </label>

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
            <span>{{ tag.name }}</span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const router = useRouter()
const route = useRoute()


const authStore = useAuthStore()
const { token } = storeToRefs(authStore)


const isFiltersOpen = ref(true);


const searchTerm = ref(route.query.search || '')
const province = ref(route.query.province || '')
const city = ref(route.query.city || '')
const state = ref(route.query.state || '')

const onlyFavorites = ref(route.query.favorites === 'true')


const orderBy = ref(route.query.order_by || 'registrado')
const orderDirection = ref(route.query.order || 'desc')

const orderByCombined = ref(
  (route.query.order_by && route.query.order)
  ? `${route.query.order_by}_${route.query.order}`
  : 'registrado_desc' 
)

const availableTags = ref([])
const selectedTags = ref([])

const provinces = ref([])

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;


const fetchProvinces = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/provinces`)
    if (!response.ok) throw new Error('Error al obtener provincias')
    provinces.value = await response.json()
  } catch (err) {
    console.error('Error al cargar provincias:', err)
  }
}


const fetchTags = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/tags`)
    if (!response.ok) throw new Error('Error al obtener tags')
    availableTags.value = await response.json()
  } catch (err) {
    console.error('Error al cargar tags:', err)
  }
}

const initSelectedTags = () => {
    if (route.query.tags) {
     
        selectedTags.value = Array.isArray(route.query.tags)
            ? route.query.tags.map(id => parseInt(id)).filter(id => !isNaN(id))
            : route.query.tags.split(',').map(id => parseInt(id)).filter(id => !isNaN(id));
    } else {
        selectedTags.value = [];
    }
}

const handleCombinedOrderChange = () => {
  const value = orderByCombined.value;

  if (value) {
    const parts = value.split('_');
    if (parts.length === 2) {
      orderBy.value = parts[0];
      orderDirection.value = parts[1];
    }
  } else {
    orderBy.value = 'registrado';
    orderDirection.value = 'desc';
  }
  updateFilters();
}


const updateFilters = () => {
  const tagsParam = selectedTags.value.length > 0 ? selectedTags.value.join(',') : undefined;
 
  const favoritesParam = onlyFavorites.value ? 'true' : undefined;

  const query = {
    search: searchTerm.value || undefined,
    province: province.value || undefined,
    city: city.value || undefined,
    state: state.value || undefined,
    tags: tagsParam,
    favorites: favoritesParam,
    order_by: orderBy.value || 'registrado',
    order: orderDirection.value || 'desc',
    page: 1
  };

  console.log("🔹 Query params que se envían:", query);

  router.push({
    path: '/sitios',
    query
  });
}


const resetForm = () => {
    searchTerm.value = '';
    province.value = '';
    city.value = '';
    state.value = '';
    onlyFavorites.value = false; 
    selectedTags.value = [];
    orderBy.value = 'registrado';
    orderDirection.value = 'desc';
    orderByCombined.value = 'registrado_desc';
   
    if (window.innerWidth < 768) {
        isFiltersOpen.value = false;
    }
}


defineExpose({
    resetForm
})

watch(
    () => route.query.tags,
    initSelectedTags,
    { immediate: true }
);

watch(
    [() => route.query.order_by, () => route.query.order],
    ([newOrderBy, newOrder]) => {
        orderBy.value = newOrderBy || 'registrado';
        orderDirection.value = newOrder || 'desc';
        orderByCombined.value = `${orderBy.value}_${orderDirection.value}`;
    }
);

watch(
    () => route.query.favorites,
    (newFavorites) => {
        onlyFavorites.value = newFavorites === 'true';
       
        if (newFavorites === 'true') {
             isFiltersOpen.value = true;
        }
    },
    { immediate: true }
);

onMounted(() => {
    fetchProvinces();
    fetchTags();
    initSelectedTags();
  
    if (window.innerWidth < 768) {
        isFiltersOpen.value = false;
    }
});
</script>

<style scoped>

.filter-controls-wrapper {
  margin-bottom: 20px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  cursor: pointer;
  border-bottom: 1px solid #ddd;
  color: #071a78;
  transition: background-color 0.2s;
}

.filter-header:hover {
    background-color: #f7f7f7;
}

.filter-header h3 {
  font-size: 1.2em;
  margin: 0;
  display: flex;
  align-items: center;
}

.toggle-icon {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.toggle-icon svg {
    width: 100%;
    height: 100%;
    fill: currentColor;
    transform: rotate(180deg);
}

.toggle-icon .rotate-up {
  transform: rotate(0deg);
}

.filtros-container {
    display: none;
    overflow: hidden;
    padding: 0;
    opacity: 0;
    transition: all 0.3s ease-in-out;
}

.filtros-container.is-open {
    display: flex;
    opacity: 1;
    padding: 10px 0 0;
}

/* MEDI QUERY: Desktop (pantallas medianas y grandes) */
@media (min-width: 768px) {
    .filter-header {
        display: none;
    }
    .filtros-container {
        display: flex !important;
        opacity: 1 !important;
        padding: 20px 0 0;
        margin: 0;
    }
}

/* ESTILOS DE FILTROS BASE */
.filtros-container {
  gap: 10px;
  flex-wrap: wrap;
  align-items: flex-start;
}
.input-filtro,
.select-filtro {
  padding: 8px 12px;
  border: 1px solid #d7d6d6;
  border-radius: 6px;
  font-size: 1em;
  flex-grow: 1;
  min-width: 150px;
}


/* ESTILOS PARA MIS FAVORITOS (tamaño corregido V2) */

.favorite-filter-button {

    padding: 8px 12px !important;
    border-radius: 6px !important;
    font-size: 1em !important;
    flex-grow: 1;
    min-width: 150px;

    font-weight: normal !important;
    color: #141414 !important;
    border-color: #d7d6d6 !important;
    background-color: white !important;
}

.favorite-filter-button span {
    padding: 0 !important;
}

.favorite-filter-button input:checked + span {
    background-color: #071a78;
    color: white;

    border-radius: 4px;
    padding: 0;
    display: inline-block;
    width: 100%;
}



.tag-filter-group {
    padding: 8px 12px;
    border: 1px solid #e6e3e3;
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

.tag-checkbox input[type="checkbox"] {
    display: none;
}

.tag-checkbox {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.9em;
    cursor: pointer;
    padding: 4px 8px;
    border: 1px solid #dbdada;
    border-radius: 4px;
    background-color: white;
    transition: background-color 0.2s;
}

.tag-checkbox:hover {
    background-color: #f0f0f0;
}

/* Tag seleccionado*/
.tag-checkbox input:checked + span {
    background-color: #d0d0d0;
    color: rgb(14, 13, 13);
    border-radius: 4px;
    padding: 0;
    display: inline-block;
    width: 100%;
}
</style>