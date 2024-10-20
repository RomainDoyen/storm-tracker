import getIconUrl from '../js/data/classification.js';

var map = L.map('map').setView([10, 20], 2);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap'
}).addTo(map);

var defaultView = [10, 20];
var defaultZoom = 2;
var cycloneMarkers = {};
var haloLayer = null;

function loadCyclones() {
    fetch('/cyclones-data')
        .then(response => response.json())
        .then(cyclones => {

            var item0 = document.getElementById('active-storms');
            var cycloneList = "<ul>";

            cyclones.forEach((cyclone, index) => {
                cycloneList += `
                  <li id="cyclone-${index}" class="cyclone-item">
                    <h4>${cyclone.name} (${cyclone.idCyclone})</h4> 
                  </li>`;

                var customIcon = L.icon({
                    iconUrl: getIconUrl(cyclone.classification),
                    iconSize: [50, 50]
                });

                var marker = L.marker([cyclone.lat, cyclone.lon], { icon: customIcon })
                    .bindPopup(`
                        <b>Nom:</b> ${cyclone.name}<br>
                        <b>ID de la tempête:</b> ${cyclone.idCyclone}<br>
                        <b>Vitesse maximale des vents:</b> ${cyclone.vmax} km/h<br>
                        <b>Pression minimale:</b> ${cyclone.mslp} bar<br>
                        <b>Classification:</b> ${cyclone.classification}<br>
                    `)
                    .addTo(map);

                cycloneMarkers[index] = marker;
            });
            cycloneList += "</ul>";
            item0.innerHTML = cycloneList;

            var selectedCycloneIndex = null;

            cyclones.forEach((cyclone, index) => {
                var listItem = document.getElementById(`cyclone-${index}`);
                listItem.addEventListener('click', function() {
                    if (selectedCycloneIndex === index) {
                        listItem.classList.remove('selected');
                        selectedCycloneIndex = null;

                        if (haloLayer) {
                            map.removeLayer(haloLayer);
                            haloLayer = null;
                        }
        
                        return;
                    }

                    document.querySelectorAll('.cyclone-item').forEach(function(item) {
                        item.classList.remove('selected');
                    });
        
                    listItem.classList.add('selected');
                    selectedCycloneIndex = index;

                    map.setView([cyclone.lat, cyclone.lon], 4);
                  
                    if (haloLayer) {
                        map.removeLayer(haloLayer);
                    }

                    haloLayer = L.circle([cyclone.lat, cyclone.lon], {
                        color: 'blue',
                        fillColor: '#30a1e6',
                        fillOpacity: 0.5,
                        radius: 300000
                    }).addTo(map);
                });
            });
        })
        .catch(error => console.error('Erreur lors du chargement des cyclones:', error));
}

function updateCyclones() {
    fetch('/cyclones-data')
        .then(response => response.json())
        .then(cyclones => {
            map.eachLayer(function (layer) {
                if (layer instanceof L.Marker) {
                    map.removeLayer(layer);
                }
            });

            cyclones.forEach(cyclone => {
                var customIcon = L.icon({
                    iconUrl: getIconUrl(cyclone.classification),
                    iconSize: [50, 50]
                });

                L.marker([cyclone.lat, cyclone.lon], { icon: customIcon })
                    .bindPopup(`
                        <b>Nom:</b> ${cyclone.name}<br>
                        <b>ID de la tempête:</b> ${cyclone.idCyclone}<br>
                        <b>Vitesse maximale des vents:</b> ${cyclone.vmax} km/h<br>
                        <b>Pression minimale:</b> ${cyclone.mslp} bar<br>
                        <b>Classification:</b> ${cyclone.classification}<br>
                    `)
                    .addTo(map);
            });
        })
        .catch(error => console.error('Erreur lors du chargement des cyclones:', error));
}

setInterval(updateCyclones, 600000); // Mettre à jour toutes les 10 minutes (600000 ms)

map.scrollWheelZoom.disable();
map.dragging.disable();

var isZoomEnabled = false;

function toggleZoom() {
    if (isZoomEnabled) {
        map.scrollWheelZoom.disable();
        map.dragging.disable();
        this.innerHTML = 'Activer Zoom';
    } else {
        map.scrollWheelZoom.enable();
        map.dragging.enable();
        this.innerHTML = 'Désactiver Zoom';
    }
    isZoomEnabled = !isZoomEnabled;
}

function resetMapView() {
    map.setView(defaultView, defaultZoom);
}

var zoomToggleButton = L.control({ position: 'topright' });
var resetViewButton = L.control({ position: 'topright' });

zoomToggleButton.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
    div.innerHTML = 'Activer Zoom';
    div.style.backgroundColor = '#aa0e0b';
    div.style.color = '#fff';
    div.style.padding = '5px';
    div.style.cursor = 'pointer';
    div.onclick = toggleZoom;
    return div;
};

resetViewButton.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
    div.innerHTML = 'Vue par défaut';
    div.style.backgroundColor = '#006494';
    div.style.color = '#fff';
    div.style.padding = '5px';
    div.style.cursor = 'pointer';
    div.onclick = resetMapView;
    return div;
};

zoomToggleButton.addTo(map);
resetViewButton.addTo(map);

map.whenReady(function() {
    loadCyclones();
    updateCyclones();
});
