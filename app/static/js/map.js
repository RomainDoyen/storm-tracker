import { loadCyclones } from './cycloneLoader.js';
import { setupMapControls } from './mapControls.js';

var map = L.map('map', { zoomControl: false }).setView([10, 20], 2);
L.control.zoom({ position: 'topright' }).addTo(map);

var chartAttribution = 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ';
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16,
    attribution: chartAttribution
}).addTo(map);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16
}).addTo(map);

loadCyclones(map);
setupMapControls(map);

function placeAttribution() {
    var narrow = window.matchMedia('(max-width: 860px)').matches;
    map.attributionControl.setPosition(narrow ? 'topleft' : 'bottomright');
}

placeAttribution();
window.addEventListener('resize', function () {
    placeAttribution();
    map.invalidateSize();
});
