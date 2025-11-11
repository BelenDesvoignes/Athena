// src/stores/auth.js

import { defineStore } from 'pinia';
import { computed } from 'vue';

// Clave para guardar el token en localStorage
const TOKEN_KEY = 'authToken';

export const useAuthStore = defineStore('auth', () => {
    // --- State (Estado) ---
    
    // Inicializa el token leyendo desde localStorage o null si no existe
    const token = ref(localStorage.getItem(TOKEN_KEY) || null);
    
    // Aquí puedes guardar la información del usuario (ej: nombre, email) si el token lo tiene
    // Por simplicidad, lo inicializamos a null
    const user = ref(null); 

    // --- Getters (Propiedades Calculadas) ---
    
    // Devuelve true si hay un token, indicando que el usuario está logueado.
    const isLoggedIn = computed(() => !!token.value);

    // Devuelve los headers necesarios para peticiones autenticadas
    const authHeader = computed(() => {
        if (token.value) {
            return {
                Authorization: `Bearer ${token.value}`
            };
        }
        return {};
    });

    // --- Actions (Acciones) ---
    
    /**
     * Establece el token JWT en el estado y en el localStorage.
     * @param {string} newToken - El token JWT recibido después del login.
     * @param {object} userData - Datos del usuario (opcional).
     */
    const login = (newToken, userData = null) => {
        token.value = newToken;
        localStorage.setItem(TOKEN_KEY, newToken);
        
        // Opcional: Decodificar el token o llamar a un endpoint para obtener datos del usuario
        user.value = userData; 
    };

    /**
     * Cierra la sesión, limpia el estado y remueve el token de localStorage.
     */
    const logout = () => {
        token.value = null;
        user.value = null;
        localStorage.removeItem(TOKEN_KEY);
    };

    // Retornar las propiedades y métodos que serán accesibles
    return {
        token,
        user,
        isLoggedIn,
        authHeader,
        login,
        logout
    };
});