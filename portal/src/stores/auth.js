import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { jwtDecode } from 'jwt-decode';

// Keys para localStorage
// Usando 'jwt_token' para compatibilidad con ListadoSitios.vue
const TOKEN_KEY = 'jwt_token';
const PROFILE_KEY = 'userProfile';
const USER_ID_KEY = 'userId';

export const useAuthStore = defineStore('auth', () => {
    // --- State ---
    const token = ref(localStorage.getItem(TOKEN_KEY) || null);
    const user = ref(JSON.parse(localStorage.getItem(PROFILE_KEY)) || null);
    const userId = ref(localStorage.getItem(USER_ID_KEY) || null);

    // --- Getters ---
    const isLoggedIn = computed(() => !!user.value && !!token.value);

    // Header para el backend (Crucial para Favoritos)
    const authHeader = computed(() => {
        if (token.value) {
            return { Authorization: `Bearer ${token.value}` };
        }
        return {};
    });

    // --- Actions ---

    /**
     * Procesa la respuesta de Google, registra/autentica el usuario en el backend
     * y guarda el estado globalmente.
     */
    const loginWithGoogle = async (googleResponse) => {
        if (!googleResponse?.credential) {
            console.error("No se recibió el token de Google.");
            return false;
        }

        try {
            //  Decodificar JWT de Google para obtener info del perfil
            const googleJwt = googleResponse.credential;
            const decoded = jwtDecode(googleJwt);

            const profile = {
                name: decoded.name,
                email: decoded.email,
                imageUrl: decoded.picture,
            };

            //  Llamada al backend (Flask) para autenticar y obtener su JWT propio
            const API_URL = import.meta.env.VITE_API_LOGIN_URL;

            // Enviamos el token de Google para que Flask lo valide con Google
            const res = await fetch(API_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${googleJwt}`
                },
                body: JSON.stringify({
                    email: profile.email,
                    name: profile.name
                }),
            });

            if (!res.ok) {
                let errorDetails = `Status: ${res.status}`;
                try {
                    const data = await res.json();
                    errorDetails += `, Details: ${data.error || JSON.stringify(data)}`;
                } catch (e) {
                    errorDetails += `, Response Type: No JSON (revisar logs del servidor)`;
                }
                throw new Error(`Error en el backend: ${errorDetails}`);
            }

            const data = await res.json();

            //  AJUSTE DE CLAVE CLAVE
            // Intentamos obtener el token de varias claves comunes en la respuesta de Flask.
            const flaskAccessToken = data.access_token || data.auth_token || data.token;

            if (!flaskAccessToken) {
                // Si aún no se encuentra, lanzamos un error más informativo para el desarrollador.
                console.error("Respuesta completa del backend:", data);
                throw new Error("El backend no devolvió el access_token, auth_token, o token necesario.");
            }

            //  Guardar el estado en el Store y localStorage (usando el token de Flask)
            token.value = flaskAccessToken;
            user.value = profile;
            // Asumimos que el ID está en data.user.id
            userId.value = data.user?.id?.toString();

            // Si el ID del usuario no existe, esto podría ser un problema para la función de favoritos.
            if (!userId.value) {
                console.warn("ADVERTENCIA: No se pudo obtener el ID del usuario de la respuesta del backend.");
            }

            // Guardamos el token de Flask que ListadoSitios.vue espera
            localStorage.setItem(TOKEN_KEY, flaskAccessToken);
            localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
            localStorage.setItem(USER_ID_KEY, userId.value);

            console.log("✅ Inicio de sesión exitoso. Usuario ID:", userId.value);
            return true;

        } catch (error) {
            console.error("🚨 Error al procesar login:", error);
            if (error.message.includes('Failed to fetch')) {
                 window.alert('Error de Conexión: No se pudo conectar con el servidor.');
            } else {
                 window.alert(`Error al iniciar sesión: ${error.message}`);
            }
            logout();
            return false;
        }
    };

    /**
     * Cierra la sesión, limpia el estado y el localStorage.
     */
    const logout = () => {
        token.value = null;
        user.value = null;
        userId.value = null;
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(PROFILE_KEY);
        localStorage.removeItem(USER_ID_KEY);
    };

    // Retornar todo lo necesario
    return {
        token,
        user,
        userId,
        isLoggedIn,
        authHeader,
        loginWithGoogle,
        logout,
    };
});