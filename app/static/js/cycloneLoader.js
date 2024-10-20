import getIconUrl from '../data/classification.js';

var cycloneMarkers = {};
var haloLayer = null;

export function loadCyclones(map) {
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

            attachCycloneEvents(cyclones, map);
        })
        .catch(error => console.error('Erreur lors du chargement des cyclones:', error));
}

function attachCycloneEvents(cyclones, map) {
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
}
