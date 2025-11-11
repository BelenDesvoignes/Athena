<template>
    <section class="featured-section">
        <header class="section-header">
            <h2>{{ title }}</h2>
            <!-- Solo mostramos el botón si hay elementos y si tiene una ruta definida -->
            <RouterLink 
                v-if="listRoute && sites.length > 0" 
                :to="listRoute" 
                class="btn-ver-todos"
            >
                Ver todos &gt;
            </RouterLink>
        </header>

        <div v-if="isLoading" class="status-message loading-pulse">
            Cargando {{ title.toLowerCase() }}...
        </div>

        <div v-else-if="error" class="status-message error-box">
            ❌ Error al cargar los sitios: {{ errorMessage }}
            <p v-if="orderByParam === 'favorites'">Por favor, inicie sesión para ver sus favoritos.</p>
        </div>

        <div v-else-if="sites.length > 0" class="site-list">
            <!-- 🔑 Itera sobre los sitios y usa el componente SiteCard -->
            <SiteCard v-for="site in sites" :key="site.id" :site="site" />
        </div>

        <div v-else class="status-message empty-box">
            No se encontró contenido para esta sección.
        </div>
    </section>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import SiteCard from './SiteCard.vue';

// Define Props
const props = defineProps({
    title: {
        type: String,
        required: true
    },
    // Parámetro para la API: 'registrado', 'nombre', 'calificacion', 'favorites'
    orderByParam: {
        type: String,
        required: true
    },
    // Ruta a la que enlaza el botón "Ver todos"
    listRoute: {
        type: String,
        default: '/sitios'
    }
});

// --- Estados ---
const sites = ref([]);
const isLoading = ref(true);
const error = ref(null);
const errorMessage = ref('');

// Constantes
const API_BASE_URL = 'https://grupo19.proyecto2025.linti.unlp.edu.ar/api';
const MAX_SITES = 4; // Límite de tarjetas a mostrar en la Home

// --- Lógica de Carga ---
const fetchSites = async () => {
    isLoading.value = true;
    error.value = null;
    errorMessage.value = '';

    // Como estamos en modo PÚBLICO (sin auth.js), deshabilitamos 'favorites'
    if (props.orderByParam === 'favorites') {
        errorMessage.value = 'Esta funcionalidad requiere iniciar sesión.';
        isLoading.value = false;
        return;
    }

    // 1. 🚧 Construcción de la URL
    const url = `${API_BASE_URL}/sites?order_by=${props.orderByParam}&per_page=${MAX_SITES}`;
    
    // 2. 📡 Realizar la Petición
    try {
        const response = await fetch(url);

        if (!response.ok) {
            // Manejo de errores HTTP específicos (ej: 404, 500)
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        sites.value = data.data || [];

    } catch (err) {
        console.error(`Fetch error for ${props.title}:`, err);
        errorMessage.value = err.message || 'Error desconocido al conectar con la API.';
        error.value = true;
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    fetchSites();
});
</script>

<style scoped>
.featured-section {
    margin-bottom: 40px;
    padding: 10px;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
}

.section-header h2 {
    font-size: 1.8em;
    color: #444;
}

.btn-ver-todos {
    text-decoration: none;
    color: #3f51b5; /* Color primario */
    font-weight: bold;
    transition: color 0.3s;
}

.btn-ver-todos:hover {
    color: #ffc107;
}

/* Grid de sitios */
.site-list {
    display: grid;
    /* Mobile First: Mínimo 1 columna, máximo 4 */
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
}

/* Mensajes de estado */
.status-message {
    padding: 20px;
    text-align: center;
    border-radius: 8px;
    font-size: 1.1em;
}

.loading-pulse {
    color: #3f51b5;
    font-style: italic;
    background-color: #e8eaf6;
}

.error-box {
    background-color: #ffebee;
    color: #c62828;
    border: 1px solid #ef9a9a;
}

.empty-box {
    background-color: #f5f5f5;
    color: #757575;
}

/* Ajustes para tablet/desktop */
@media (max-width: 768px) {
    .site-list {
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    }
}
</style>
