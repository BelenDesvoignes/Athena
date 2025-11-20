import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import vue3GoogleLogin from 'vue3-google-login'

import 'leaflet/dist/leaflet.css'
const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vue3GoogleLogin, {
  clientId: '232000351425-24js56duevv9punmo0qc6dpiqhstr74t.apps.googleusercontent.com'
})

app.mount('#app')
