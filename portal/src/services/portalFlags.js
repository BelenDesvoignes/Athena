const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export async function checkPortalStatus() {
  try {
    const res = await fetch(`${API_BASE_URL}/flags`)
    const data = await res.json()

    return {
      maintenance: data.maintenance || false,
      message: data.message || null
    }
  } catch (err) {
    console.error("Error verificando estado del portal:", err)

    return {
      maintenance: false,
      message: null
    }
  }
}
