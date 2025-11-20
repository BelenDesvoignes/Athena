import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { jwtDecode } from 'jwt-decode';

// Keys para localStorage
const TOKEN_KEY = 'authToken';
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
            // 1. Decodificar JWT de Google para obtener info del perfil
            const googleJwt = googleResponse.credential;
            const decoded = jwtDecode(googleJwt);

            const profile = {
                name: decoded.name,
                email: decoded.email,
                imageUrl: decoded.picture,
            };

            // 2. Llamada al backend para obtener/crear el usuario y obtener el ID
            const API_URL = import.meta.env.VITE_API_LOGIN_URL;

            const res = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: profile.email,
                    name: profile.name // El backend usa 'name' también
                }),
            });

            if (!res.ok) {
                // Si el backend falla (ej: 500, 400), intentamos obtener los detalles
                let errorDetails = `Status: ${res.status}`;
                try {
                    const data = await res.json();
                    errorDetails += `, Details: ${data.error || JSON.stringify(data)}`;
                } catch (e) {
                    // Si no puede parsear JSON (ej: respuesta es HTML de un error 500)
                    errorDetails += `, Response Type: No JSON (revisar logs del servidor)`;
                }
                throw new Error(`Error en el backend: ${errorDetails}`);
            }

            const data = await res.json();

            const flaskToken = data.access_token;

            if (!flaskToken) {
                throw new Error("El backend no devolvió un token de acceso.");
            }


            // 3. Guardar el estado en el Store y localStorage
            token.value = flaskToken;  //guardo token de flask
            user.value = profile;
            userId.value = data.user.id.toString(); // Guardar el ID retornado por Flask

            localStorage.setItem(TOKEN_KEY, flaskToken);
            localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
            localStorage.setItem(USER_ID_KEY, data.user.id.toString());

            console.log("✅ Inicio de sesión exitoso. Usuario ID:", userId.value);
            return true;

        } catch (error) {
            console.error("🚨 Error al procesar login:", error);
            // Mostrar alerta más específica al usuario
            if (error.message.includes('Failed to fetch')) {
                 window.alert('Error de Conexión: No se pudo conectar con el servidor. Revisa la URL y CORS.');
            } else {
                 window.alert(`Error al iniciar sesión: ${error.message}`);
            }
            // Limpiar el estado por si acaso
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