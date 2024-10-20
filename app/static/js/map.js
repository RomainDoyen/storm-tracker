import { loadCyclones } from './cycloneLoader.js';
import { setupMapControls } from './mapControls.js';

var map = L.map('map', {
    scrollWheelZoom: false,
    dragging: false
}).setView([10, 20], 2);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap'
}).addTo(map);

loadCyclones(map);

setupMapControls(map);
