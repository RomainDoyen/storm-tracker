import getIconUrl from '../data/classification.js';
import { getFirestore, collection, getDocs } from "https://www.gstatic.com/firebasejs/11.6.0/firebase-firestore.js";

// Variable globale pour stocker la référence de la carte
let globalMap = null;

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

    const basinId = basinName.toLowerCase().replace(/\s+/g, '-');
    const isFirstSection = basinName === 'Atlantique Nord'; // Ouvrir le premier accordéon par défaut

    let html = `<div class="basin-section" data-basin="${basinId}">
        <div class="basin-header ${isFirstSection ? 'active' : ''}" onclick="toggleAccordion('${basinId}')">
            <h3 class="basin-title">${basinName} (${cyclones.length})</h3>
            <span class="accordion-icon">▼</span>
        </div>
        <div class="basin-content ${isFirstSection ? 'active' : ''}">
            <div class="basin-content-inner">
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

    html += `</ul>
            </div>
        </div>
    </div>`;
    return html;
}

export async function loadCyclones(map) {
    globalMap = map; // Stocker la référence de la carte
    const loadingSpinner = document.getElementById('loading-spinner');
    const activeStorms = document.getElementById('active-storms');
    
    try {
        // Afficher le spinner
        loadingSpinner.classList.remove('loading-hidden');
        activeStorms.classList.add('loading-hidden');
        
        const db = getFirestore();
        const cyclonesRef = collection(db, "Cyclones");
        const snapshot = await getDocs(cyclonesRef);
        const cyclones = snapshot.docs.map(doc => doc.data());

        // Masquer le spinner et afficher les données
        loadingSpinner.classList.add('loading-hidden');
        activeStorms.classList.remove('loading-hidden');
        activeStorms.classList.add('data-loaded');
        
        if (cyclones.length === 0) {
            activeStorms.innerHTML = '<p class="no-storms">Aucun cyclone actif actuellement.</p>';
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

        activeStorms.innerHTML = html;

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
        
        // Masquer le spinner et afficher l'erreur
        loadingSpinner.classList.add('loading-hidden');
        activeStorms.classList.remove('loading-hidden');
        activeStorms.innerHTML = 
            '<div class="error-message">' +
            '<p>❌ Erreur lors du chargement des données</p>' +
            '<p>Veuillez réessayer plus tard ou vérifier votre connexion.</p>' +
            '<button onclick="location.reload()" class="retry-button">🔄 Réessayer</button>' +
            '</div>';
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

// Fonction pour forcer la mise à jour des données
async function forceRefreshData() {
    const refreshButton = document.getElementById('refresh-button');
    const originalText = refreshButton.innerHTML;
    
    try {
        // Désactiver le bouton et afficher un spinner
        refreshButton.disabled = true;
        refreshButton.innerHTML = `
            <img src="/static/images/refresh-cw-alt-2-svgrepo-com.svg" alt="Actualiser" class="refresh-icon loading">
        `;
        
        // Appeler l'API pour forcer la mise à jour
        const response = await fetch('/force-update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Attendre un peu puis recharger les données
            setTimeout(async () => {
                if (globalMap) {
                    await loadCyclones(globalMap);
                }
            }, 2000);
        } else {
            console.error('Erreur lors de la mise à jour:', result.message);
        }
    } catch (error) {
        console.error('Erreur lors de la mise à jour:', error);
    } finally {
        // Réactiver le bouton
        refreshButton.disabled = false;
        refreshButton.innerHTML = originalText;
    }
}

// Fonction pour gérer les accordéons
window.toggleAccordion = function(basinId) {
    const basinSection = document.querySelector(`[data-basin="${basinId}"]`);
    if (!basinSection) return;

    const header = basinSection.querySelector('.basin-header');
    const content = basinSection.querySelector('.basin-content');
    const icon = basinSection.querySelector('.accordion-icon');

    const isActive = header.classList.contains('active');

    if (isActive) {
        // Fermer l'accordéon
        header.classList.remove('active');
        content.classList.remove('active');
        icon.style.transform = 'rotate(0deg)';
    } else {
        // Ouvrir l'accordéon
        header.classList.add('active');
        content.classList.add('active');
        icon.style.transform = 'rotate(180deg)';
    }
};

// Initialiser le bouton de rafraîchissement
document.addEventListener('DOMContentLoaded', function() {
    const refreshButton = document.getElementById('refresh-button');
    if (refreshButton) {
        refreshButton.addEventListener('click', forceRefreshData);
    }
});
