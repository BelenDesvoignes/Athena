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

const router = useRouter()
const route = useRoute()

// Inicialización de filtros desde los Query Params
const searchTerm = ref(route.query.search || '')
const province = ref(route.query.province || '')
const city = ref(route.query.city || '')
const state = ref(route.query.state || '')

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
        selectedTags.value = route.query.tags.split(',').map(id => parseInt(id)).filter(id => !isNaN(id));
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

  const query = {
    search: searchTerm.value || undefined,
    province: province.value || undefined,
    city: city.value || undefined,
    state: state.value || undefined,
    tags: tagsParam,
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
