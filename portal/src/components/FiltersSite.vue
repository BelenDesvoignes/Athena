<template>
  <div class="filtros-container">
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

    <!-- NUEVO: Filtro por Favoritos (visible solo si hay token) -->
    <div v-if="token" class="favorites-filter-group">
        <label class="favorite-checkbox">
            <input
                type="checkbox"
                v-model="onlyFavorites"
                @change="updateFilters"
            />
            <span>Mis Favoritos</span>
        </label>
    </div>
    <!-- FIN NUEVO -->

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
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // Importado
import { storeToRefs } from 'pinia' // Importado

const router = useRouter()
const route = useRoute()

// Inicialización de Auth Store para obtener el token
const authStore = useAuthStore()
const { token } = storeToRefs(authStore) // Obteniendo el token

// Inicialización de filtros desde los Query Params
const searchTerm = ref(route.query.search || '')
const province = ref(route.query.province || '')
const city = ref(route.query.city || '')
const state = ref(route.query.state || '')
// NUEVO: Inicialización del filtro de favoritos
const onlyFavorites = ref(route.query.favorites === 'true')

// Variables que se envían al router
const orderBy = ref(route.query.order_by || 'registrado')
const orderDirection = ref(route.query.order || 'desc')

const orderByCombined = ref(
  (route.query.order_by && route.query.order)
  ? `${route.query.order_by}_${route.query.order}`
  : 'registrado_desc' // Valor por defecto para la UI
)

const availableTags = ref([])
const selectedTags = ref([])

const provinces = ref([])

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Función para cargar provincias
const fetchProvinces = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/provinces`)
    if (!response.ok) throw new Error('Error al obtener provincias')
    provinces.value = await response.json()
  } catch (err) {
    console.error('Error al cargar provincias:', err)
  }
}

// Función para cargar tags
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
      // Se asegura de que la URL maneje números (aunque la API podría aceptar strings)
        selectedTags.value = Array.isArray(route.query.tags)
            ? route.query.tags.map(id => parseInt(id)).filter(id => !isNaN(id))
            : route.query.tags.split(',').map(id => parseInt(id)).filter(id => !isNaN(id));
    } else {
        selectedTags.value = [];
    }
}

// Maneja el valor combinado del select de orden
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

// Actualizar filtros y push a router
const updateFilters = () => {
  const tagsParam = selectedTags.value.length > 0 ? selectedTags.value.join(',') : undefined;
  // NUEVO: Determinar si se envía el filtro de favoritos
  const favoritesParam = onlyFavorites.value ? 'true' : undefined;

  const query = {
    search: searchTerm.value || undefined,
    province: province.value || undefined,
    city: city.value || undefined,
    state: state.value || undefined,
    tags: tagsParam,
    favorites: favoritesParam, // Incluyendo el nuevo parámetro
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

// Resetear formulario completo
const resetForm = () => {
    searchTerm.value = '';
    province.value = '';
    city.value = '';
    state.value = '';
    onlyFavorites.value = false; // Reset de favoritos
    selectedTags.value = [];
    orderBy.value = 'registrado';
    orderDirection.value = 'desc';
    orderByCombined.value = 'registrado_desc';
}

// Exponer función resetForm al padre
defineExpose({
    resetForm
})

// Observa cambios en query params externos
watch(
    () => route.query.tags,
    initSelectedTags,
    { immediate: true }
);

// Sincronizar UI de ordenamiento si cambia URL externa
watch(
    [() => route.query.order_by, () => route.query.order],
    ([newOrderBy, newOrder]) => {
        orderBy.value = newOrderBy || 'registrado';
        orderDirection.value = newOrder || 'desc';
        orderByCombined.value = `${orderBy.value}_${orderDirection.value}`;
    }
);

// Sincronizar UI de favoritos si cambia URL externa
watch(
    () => route.query.favorites,
    (newFavorites) => {
        onlyFavorites.value = newFavorites === 'true';
    },
    { immediate: true }
);

onMounted(() => {
    fetchProvinces();
    fetchTags();
    initSelectedTags();
});
</script>

<style scoped>
.filtros-container {
  display: flex;
  gap: 10px;
  margin: 20px 0;
  flex-wrap: wrap;
  align-items: flex-start;
}
.input-filtro,
.select-filtro {
  padding: 8px 12px;
  border: 1px solid #d7d6d6;
  border-radius: 6px;
  font-size: 1em;
}

/*  ESTILOS PARA FAVORITOS */
.favorites-filter-group {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    border: 1px solid #e6e3e3;
    border-radius: 6px;
    background-color: #ffffff;
}

.favorite-checkbox {
    display: flex;
    align-items: center;
    cursor: pointer;
    font-weight: bold;
    color: #0f0e0e;
}

.favorite-checkbox input[type="checkbox"] {
    transform: scale(1.2);
    margin-right: 8px;
    accent-color: #0f0f0f;
}

/* estilos de tags */
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
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  transition: background-color 0.2s;
}

.tag-checkbox:hover {
  background-color: #f0f0f0;
}

/* Tag seleccionado*/
.tag-checkbox input:checked + span {
  background-color: #e0e0e0;
  border-radius: 4px;
  padding: 0;
  display: inline-block;
  width: 100%;
}
</style>