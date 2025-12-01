<template>
  <div class="map-container">
    <l-map
      ref="map"
      :zoom="zoom"
      :center="initialCenter"
      :options="{ attributionControl: false }"
      class="leaflet-map"
      @click="onMapClick"
    >
      <l-tile-layer :url="url" :attribution="attribution" />

      <!-- Marcadores de sitios dentro del radio -->
      <l-marker 
        v-for="site in filteredSites"
        :key="site.id"
        :lat-lng="[site.latitude, site.longitude]"
      >
        <l-popup>
          <div class="site-popup">
            <strong>{{ site.name }}</strong>
            <p>{{ site.short_description }}</p>
          </div>
        </l-popup>
      </l-marker>
    </l-map>

    <!-- SELECTOR DE RADIO -->
    <div class="radius-selector">
      <label>Radio:</label>
      <select v-model="radiusKm" @change="updateCircleAndEmit">
        <option v-for="r in radioOptions" :key="r" :value="r">
          {{ r }} km
        </option>
      </select>
    </div>
  </div>
</template>

<script>
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { LMap, LTileLayer, LMarker, LPopup } from '@vue-leaflet/vue-leaflet';
import { latLngBounds } from "leaflet";

/* === Fix iconos por defecto === */
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
});

/* === Icono rojo para marcador del usuario === */
const redMarkerIcon = L.icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default {
  name: "SiteMap",
  components: { LMap, LTileLayer, LMarker, LPopup },

  props: {
    sites: { type: Array, default: () => [] },
    lat: [String, Number],
    lon: [String, Number],
    radius: [String, Number],
  },

  emits: ["filterByLocation"],

  data() {
    return {
      url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a>',
      zoom: 6,
      initialCenter: [-34.6037, -58.3816],

      radiusKm: 1000,
      radioOptions: [100, 500, 1000, 10000],

      selectedLat: null,
      selectedLon: null,
      circleLayer: null,
      pointMarker: null, 
      userClickedInThisModal: false,
    };
  },

  computed: {
    filteredSites() {
      if (!this.selectedLat || !this.selectedLon) return this.sites || [];
      return (this.sites || []).filter(s => this.distanceKm(
        this.selectedLat,
        this.selectedLon,
        s.latitude,
        s.longitude
      ) <= this.radiusKm);
    }
  },

  watch: {
    lat: "syncFromProps",
    lon: "syncFromProps",
    radius: "syncFromProps",
  },

  methods: {
    distanceKm(lat1, lon1, lat2, lon2) {
      const R = 6371;
      const toRad = v => v * Math.PI / 180;
      const dLat = toRad(lat2 - lat1);
      const dLon = toRad(lon2 - lon1);
      const a =
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
        Math.sin(dLon/2) * Math.sin(dLon/2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
      return R * c;
    },

    syncFromProps() {
      const map = this.$refs?.map?.leafletObject;
      if (!map || this.lat == null || this.lon == null) return;

      this.selectedLat = parseFloat(this.lat);
      this.selectedLon = parseFloat(this.lon);
      this.radiusKm = parseInt(this.radius || this.radiusKm);

      setTimeout(() => {
        map.setView([this.selectedLat, this.selectedLon], 10);
        this.drawCircle();
      }, 120);
    },

    forceUpdate() {
      this.userClickedInThisModal = false;

      this.$nextTick(() => {
        const map = this.$refs?.map?.leafletObject;
        if (!map) return;

        setTimeout(() => {
          map.invalidateSize();

          if (this.lat != null && this.lon != null) {
            this.syncFromProps();
            return;
          }

          if (this.sites && this.sites.length > 0) {
            const first = this.sites.find(s => s.latitude != null && s.longitude != null);
            if (first) {
              setTimeout(() => {
                this.selectedLat = parseFloat(first.latitude);
                this.selectedLon = parseFloat(first.longitude);
                this.drawCircle();
                map.setView([this.selectedLat, this.selectedLon], 10);
              }, 80);
              return;
            }
          }

          if (this.sites && this.sites.length > 1) {
            const coords = this.sites
              .filter(s => s.latitude != null && s.longitude != null)
              .map(s => [s.latitude, s.longitude]);
            if (coords.length > 0) {
              const bounds = latLngBounds(coords);
              map.fitBounds(bounds, { padding: [50, 50] });
              return;
            }
          }

          map.setView(this.initialCenter, 6);
        }, 250);
      });
    },

    fitMapToSites(sites) {
      const map = this.$refs?.map?.leafletObject;
      if (!map) return;
      if (!sites || sites.length === 0) return map.setView(this.initialCenter, 6);

      const coords = sites
        .filter(s => s.latitude != null && s.longitude != null)
        .map(s => [s.latitude, s.longitude]);

      if (coords.length === 1) {
        map.setView([coords[0][0], coords[0][1]], 10);
      } else if (coords.length > 1) {
        const bounds = latLngBounds(coords);
        map.fitBounds(bounds, { padding: [50, 50] });
      } else {
        map.setView(this.initialCenter, 6);
      }
    },

    onMapClick(e) {
      const map = this.$refs?.map?.leafletObject;
      if (!map) return;

      this.userClickedInThisModal = true;
      this.selectedLat = e.latlng.lat;
      this.selectedLon = e.latlng.lng;

      // el marcador del usuario se crea 1 sola vez
      if (!this.pointMarker) {
        this.pointMarker = L.marker([this.selectedLat, this.selectedLon], {
          icon: redMarkerIcon
        }).addTo(map);
      } else {
        this.pointMarker.setLatLng([this.selectedLat, this.selectedLon]);
      }

      this.drawCircle();
      this.emitFilter();
    },

    drawCircle() {
      const map = this.$refs?.map?.leafletObject;
      if (!map || this.selectedLat == null || this.selectedLon == null) return;

      if (this.circleLayer) map.removeLayer(this.circleLayer);

      this.circleLayer = L.circle([this.selectedLat, this.selectedLon], {
        radius: (this.radiusKm || 1000) * 1000,
        color: "#9ca3af",
        fillColor: "#d1d5db",
        fillOpacity: 0.35,
      }).addTo(map);
    },

    updateCircleAndEmit() {
      this.drawCircle();
      this.emitFilter();
    },

    emitFilter() {
      if (this.selectedLat == null || this.selectedLon == null) return;

      this.$emit("filterByLocation", {
        lat: this.selectedLat,
        lon: this.selectedLon,
        radius: this.radiusKm,
      });
    },
  },

  mounted() {
    this.radiusKm = parseInt(this.radius || this.radiusKm || 1000);

    if (this.lat != null && this.lon != null) {
      this.selectedLat = parseFloat(this.lat);
      this.selectedLon = parseFloat(this.lon);
    }

    this.forceUpdate();
  }
};
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 500px;
  position: relative;
}

.leaflet-map {
  width: 100%;
  height: 100%;
}

.radius-selector {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background: rgba(255, 255, 255, 0.9);
  padding: 6px 10px;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  display: flex;
  gap: 6px;
  align-items: center;
  z-index: 1000;
}
</style>
