<template>
  <div class="map-container">
    <l-map
      ref="map"
      :zoom="zoom"
      :center="center"
      :options="{ attributionControl: false }"
      class="leaflet-map"
    >
      <l-tile-layer :url="url" :attribution="attribution" />

      <l-marker 
        v-for="site in sites" 
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
  </div>
</template>

<script>
import "leaflet/dist/leaflet.css"; 
import L from "leaflet";
import { LMap, LTileLayer, LMarker, LPopup } from '@vue-leaflet/vue-leaflet';
import { latLngBounds } from "leaflet";

// Fix de iconos (necesario con Vite)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href
});

export default {
  name: "SiteMap",
  components: { LMap, LTileLayer, LMarker, LPopup },
  props: {
    sites: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  data() {
    return {
      url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      attribution: '&copy; <a target="_blank" href="http://osm.org/copyright">OpenStreetMap</a> contributors',
      zoom: 6,
      center: [-34.6037, -58.3816]
    };
  },

  methods: {
    fitMapToSites(sites) {
      const map = this.$refs?.map?.leafletObject;
      if (!map) return;

      const latLngs = sites.map(s => [s.latitude, s.longitude]);
      if (latLngs.length > 0) {
        const bounds = latLngBounds(latLngs);
        map.fitBounds(bounds, { padding: [50, 50] });
      } else {
        map.setView(this.center, this.zoom);
      }
    },

    forceUpdate() {
      this.$nextTick(() => {
        const map = this.$refs?.map?.leafletObject;
        if (!map) return;

        setTimeout(() => {
          map.invalidateSize();
          this.fitMapToSites(this.sites);
        }, 250);
      });
    }
  },

  mounted() {
    this.forceUpdate();
  }
};
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 500px; /* Altura real del mapa (crítico para Leaflet) */
  position: relative;
  z-index: 1;
}

.leaflet-map {
  width: 100%;
  height: 100%;
}

.site-popup strong {
  display: block;
  margin-bottom: 3px;
  font-size: 1.1em;
  color: #333;
}

.site-popup p {
  margin: 0;
  font-size: 0.9em;
  color: #666;
}
</style>
