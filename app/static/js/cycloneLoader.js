import getIconUrl from '../data/classification.js';
import { getFirestore, collection, getDocs } from "https://www.gstatic.com/firebasejs/11.6.0/firebase-firestore.js";

var cycloneMarkers = {};
var haloLayer = null;

function groupCyclonesByBasin(cyclones) {
    const groups = {
        'north_atlantic': { name: 'Atlantique Nord', cyclones: [] },
        'east_pacific': { name: 'Pacifique Est', cyclones: [] },
        'west_pacific': { name: 'Pacifique Ouest', cyclones: [] },
        'south_indian': { name: 'Océan Indien Sud', cyclones: [] },
        'north_indian': { name: 'Océan Indien Nord', cyclones: [] },
        'unknown': { name: 'Zone Inconnue', cyclones: [] }
    };

    cyclones.forEach(cyclone => {
        const basin = cyclone.basin || 'unknown';
        if (groups[basin]) {
            groups[basin].cyclones.push(cyclone);
        } else {
            groups.unknown.cyclones.push(cyclone);
        }
    });

    return groups;
}

function createBasinSection(basinName, cyclones) {
    if (cyclones.length === 0) return '';

    let html = `<div class="basin-section">
        <h3>${basinName}</h3>
        <ul>`;

    cyclones.forEach(cyclone => {
        const sourceTag = cyclone.source ? `<span class="source-tag">${cyclone.source.toUpperCase()}</span>` : '';
        const investTag = cyclone.is_invest ? '<span class="invest-tag">INVEST</span>' : '';
        
        html += `
            <li id="cyclone-${cyclone.idCyclone}" class="cyclone-item">
                <h4>${cyclone.name} (${cyclone.idCyclone})</h4>
                <div class="cyclone-details">
                    ${sourceTag}
                    ${investTag}
                    <p>Classification: ${cyclone.classification}</p>
                    <p>Vents max: ${cyclone.vmax} km/h</p>
                    <p>Pression: ${cyclone.mslp} bar</p>
                    <p>Dernière mise à jour: ${cyclone.last_update || 'N/A'}</p>
                </div>
            </li>`;
    });

    html += `</ul></div>`;
    return html;
}

export async function loadCyclones(map) {
    try {
        const db = getFirestore();
        const cyclonesRef = collection(db, "Cyclones");
        const snapshot = await getDocs(cyclonesRef);
        const cyclones = snapshot.docs.map(doc => doc.data());

        var item0 = document.getElementById('active-storms');
        
        if (cyclones.length === 0) {
            item0.innerHTML = '<p class="no-storms">Aucun cyclone actif actuellement.</p>';
            return;
        }

        const groupedCyclones = groupCyclonesByBasin(cyclones);
        let html = '';

        // Créer les sections pour chaque bassin
        Object.entries(groupedCyclones).forEach(([basin, data]) => {
            if (data.cyclones.length > 0) {
                html += createBasinSection(data.name, data.cyclones);
            }
        });

        item0.innerHTML = html;

        // Ajouter les marqueurs sur la carte
        cyclones.forEach((cyclone, index) => {
            var customIcon = L.icon({
                iconUrl: getIconUrl(cyclone.classification),
                iconSize: [50, 50]
            });

            var marker = L.marker([cyclone.lat, cyclone.lon], { icon: customIcon })
                .bindPopup(`
                    <div class="popup-content">
                        <h3>${cyclone.name} (${cyclone.idCyclone})</h3>
                        <p><strong>Source:</strong> ${cyclone.source ? cyclone.source.toUpperCase() : 'N/A'}</p>
                        <p><strong>Classification:</strong> ${cyclone.classification}</p>
                        <p><strong>Vents max:</strong> ${cyclone.vmax} km/h</p>
                        <p><strong>Pression:</strong> ${cyclone.mslp} bar</p>
                        <p><strong>Bassin:</strong> ${groupedCyclones[cyclone.basin]?.name || 'Inconnu'}</p>
                        <p><strong>Dernière mise à jour:</strong> ${cyclone.last_update || 'N/A'}</p>
                    </div>
                `)
                .addTo(map);

            cycloneMarkers[cyclone.idCyclone] = marker;
        });

        attachCycloneEvents(cyclones, map);
    } catch (error) {
        console.error('Erreur lors du chargement des cyclones:', error);
        document.getElementById('active-storms').innerHTML = 
            '<p class="error-message">Erreur lors du chargement des données. Veuillez réessayer plus tard.</p>';
    }
}

function attachCycloneEvents(cyclones, map) {
    cyclones.forEach(cyclone => {
        var listItem = document.getElementById(`cyclone-${cyclone.idCyclone}`);
        if (!listItem) return;

        listItem.addEventListener('click', function() {
            // Supprimer le halo précédent s'il existe
            if (haloLayer) {
                map.removeLayer(haloLayer);
                haloLayer = null;
            }

            // Centrer la carte sur le cyclone
            map.setView([cyclone.lat, cyclone.lon], 4);

            // Créer un nouveau halo
            haloLayer = L.circle([cyclone.lat, cyclone.lon], {
                color: 'blue',
                fillColor: '#30a1e6',
                fillOpacity: 0.5,
                radius: 300000
            }).addTo(map);

            // Mettre à jour les classes CSS
            document.querySelectorAll('.cyclone-item').forEach(item => {
                item.classList.remove('selected');
            });
            listItem.classList.add('selected');
        });
    });
}
