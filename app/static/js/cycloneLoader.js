import getIconUrl from '../data/classification.js';

// Variable globale pour stocker la référence de la carte
let globalMap = null;
const UPDATE_WAIT_MS = 240000;

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

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (ch) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }[ch]));
}

function showPlotName(name) {
    const plotName = document.getElementById('plot-name');
    if (!plotName) return;
    plotName.textContent = name || 'Tempêtes actives';
    plotName.classList.toggle('is-storm', Boolean(name));
}

function createBasinSection(basinName, cyclones) {
    if (cyclones.length === 0) return '';

    const basinId = basinName.toLowerCase().replace(/\s+/g, '-');
    const chevron = '<svg class="chevron" viewBox="0 0 12 12" aria-hidden="true"><path d="M2.2 4.2 6 8l3.8-3.8" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="square"/></svg>';

    let html = `<div class="basin-section" data-basin="${basinId}">
        <button type="button" class="basin-header active" aria-expanded="true" onclick="toggleAccordion('${basinId}')">
            <h2 class="basin-title">${escapeHtml(basinName)} (${cyclones.length})</h2>
            <span class="accordion-icon">${chevron}</span>
        </button>
        <div class="basin-content active">
            <div class="basin-content-inner">
                <div class="fix-columns" aria-hidden="true"><span>Nom</span><span>Vent</span><span>Pression</span></div>
                <ul>`;

    cyclones.forEach(cyclone => {
        const sourceTag = cyclone.source ? `<span class="source-tag">${escapeHtml(cyclone.source.toUpperCase())}</span>` : '';
        const investTag = cyclone.is_invest ? '<span class="invest-tag">Invest</span>' : '';

        html += `
            <li id="cyclone-${escapeHtml(cyclone.idCyclone)}" class="cyclone-item" tabindex="0">
                <h3 class="fix-name"><span class="fix-title">${escapeHtml(cyclone.name)}</span><span class="fix-id">${escapeHtml(cyclone.idCyclone)}</span></h3>
                <div class="cyclone-details">
                    <p class="fix-class">${escapeHtml(cyclone.classification)}</p>
                    <p class="fix-wind"><span class="num">${escapeHtml(cyclone.vmax)}</span> <span class="unit">km/h</span></p>
                    <p class="fix-pressure"><span class="num">${escapeHtml(cyclone.mslp)}</span> <span class="unit">bar</span></p>
                    <div class="fix-meta">${sourceTag}${investTag}</div>
                    <p class="fix-time">${escapeHtml(cyclone.last_update || 'N/A')}</p>
                </div>
            </li>`;
    });

    html += `</ul>
            </div>
        </div>
    </div>`;
    return html;
}

function setLoading(isLoading) {
    const loadingSpinner = document.getElementById('loading-spinner');
    const activeStorms = document.getElementById('active-storms');
    const mapLoading = document.getElementById('map-loading');
    loadingSpinner.classList.toggle('loading-hidden', !isLoading);
    activeStorms.classList.toggle('loading-hidden', isLoading);
    if (mapLoading) {
        mapLoading.classList.toggle('loading-hidden', !isLoading);
    }
}

function showLoading() {
    setLoading(true);
}

function showStormError(message) {
    const activeStorms = document.getElementById('active-storms');
    setLoading(false);
    activeStorms.innerHTML =
        '<div class="error-message">' +
        '<p>' + escapeHtml(message) + '</p>' +
        '<p>Vérifiez la connexion, puis relancez la lecture.</p>' +
        '<button type="button" onclick="location.reload()" class="retry-button">Réessayer</button>' +
        '</div>';
}

function clearStormLayers(map) {
    Object.keys(cycloneMarkers).forEach((id) => {
        map.removeLayer(cycloneMarkers[id]);
        delete cycloneMarkers[id];
    });
    if (haloLayer) {
        map.removeLayer(haloLayer);
        haloLayer = null;
    }
}

function renderCyclones(map, cyclones) {
    const activeStorms = document.getElementById('active-storms');

    clearStormLayers(map);
    showPlotName(null);
    setLoading(false);
    activeStorms.classList.add('data-loaded');

    if (!cyclones.length) {
        activeStorms.innerHTML = '<p class="no-storms">Aucun cyclone actif actuellement.</p>';
        return;
    }

    const groupedCyclones = groupCyclonesByBasin(cyclones);
    let html = '';
    Object.entries(groupedCyclones).forEach(([basin, data]) => {
        if (data.cyclones.length > 0) {
            html += createBasinSection(data.name, data.cyclones);
        }
    });
    activeStorms.innerHTML = html;

    cyclones.forEach((cyclone) => {
        var customIcon = L.icon({
            iconUrl: getIconUrl(cyclone.classification),
            iconSize: [50, 50],
            iconAnchor: [25, 25],
            tooltipAnchor: [0, -26]
        });

        var marker = L.marker([cyclone.lat, cyclone.lon], { icon: customIcon })
            .bindTooltip(escapeHtml(cyclone.name), {
                permanent: true,
                direction: 'top',
                className: 'storm-label',
                opacity: 1
            })
            .bindPopup(`
                <div class="popup-content">
                    <h3>${escapeHtml(cyclone.name)}</h3>
                    <p><strong>Identifiant</strong> ${escapeHtml(cyclone.idCyclone)}</p>
                    <p><strong>Source</strong> ${escapeHtml(cyclone.source ? cyclone.source.toUpperCase() : 'N/A')}</p>
                    <p><strong>Classe</strong> ${escapeHtml(cyclone.classification)}</p>
                    <p><strong>Vent</strong> ${escapeHtml(cyclone.vmax)} km/h</p>
                    <p><strong>Pression</strong> ${escapeHtml(cyclone.mslp)} bar</p>
                    <p><strong>Bassin</strong> ${escapeHtml(groupedCyclones[cyclone.basin]?.name || 'Inconnu')}</p>
                    <p><strong>Relevé</strong> ${escapeHtml(cyclone.last_update || 'N/A')}</p>
                </div>
            `)
            .addTo(map);

        cycloneMarkers[cyclone.idCyclone] = marker;
    });

    attachCycloneEvents(cyclones, map);
}

function scheduleRefreshWhenIdle() {
    if (scheduleRefreshWhenIdle.timer) {
        return;
    }
    scheduleRefreshWhenIdle.timer = setInterval(async () => {
        try {
            const statusResponse = await fetch('/status');
            if (!statusResponse.ok) {
                return;
            }
            const status = await statusResponse.json();
            if (status.is_updating || !globalMap) {
                return;
            }
            clearInterval(scheduleRefreshWhenIdle.timer);
            scheduleRefreshWhenIdle.timer = null;
            const response = await fetch('/cyclones-data');
            const payload = await response.json();
            if (Array.isArray(payload)) {
                renderCyclones(globalMap, payload);
            }
        } catch (error) {
            console.error('Erreur lors de la mise à jour automatique:', error);
        }
    }, 3000);
}

async function waitForCurrentData() {
    const deadline = Date.now() + UPDATE_WAIT_MS;
    let latest = null;
    let lastError = 'Réponse invalide';

    while (Date.now() < deadline) {
        let statusResponse;
        let dataResponse;
        try {
            statusResponse = await fetch('/status');
            dataResponse = await fetch('/cyclones-data');
        } catch (error) {
            lastError = 'Service en cours de réveil';
            await new Promise((resolve) => setTimeout(resolve, 1500));
            continue;
        }
        const status = statusResponse.ok ? await statusResponse.json() : { is_updating: true };
        let payload = null;
        try {
            payload = await dataResponse.json();
        } catch (error) {
            payload = null;
        }
        if (!dataResponse.ok || !Array.isArray(payload)) {
            lastError = (payload && payload.error) || 'Réponse invalide';
            await new Promise((resolve) => setTimeout(resolve, 1500));
            continue;
        }
        latest = payload;
        if (!status.is_updating) {
            return payload;
        }
        if (payload.length) {
            scheduleRefreshWhenIdle();
            return payload;
        }
        await new Promise((resolve) => setTimeout(resolve, 1500));
    }

    if (latest) {
        return latest;
    }
    throw new Error(lastError);
}

export async function loadCyclones(map) {
    globalMap = map;
    showLoading();

    try {
        renderCyclones(map, await waitForCurrentData());
    } catch (error) {
        console.error('Erreur lors du chargement des cyclones:', error);
        showStormError('Erreur lors du chargement des données');
    }
}

function focusStorm(map, latlng) {
    const zoom = 4;
    const narrow = window.matchMedia('(max-width: 860px)').matches;
    const panel = document.querySelector('.panel');
    const point = map.project(latlng, zoom);
    if (panel) {
        const box = panel.getBoundingClientRect();
        if (narrow) {
            point.y += box.height / 2;
        } else {
            point.x -= (box.width + 20) / 2;
        }
    }
    map.setView(map.unproject(point, zoom), zoom, { animate: true });
}

function selectCyclone(cyclone, listItem, map) {
    if (haloLayer) {
        map.removeLayer(haloLayer);
        haloLayer = null;
    }

    focusStorm(map, [cyclone.lat, cyclone.lon]);

    haloLayer = L.circle([cyclone.lat, cyclone.lon], {
        color: '#c5342a',
        weight: 1.5,
        fillColor: '#c5342a',
        fillOpacity: 0.07,
        radius: 280000
    }).addTo(map);
    haloLayer.bringToBack();

    document.querySelectorAll('.cyclone-item').forEach(item => {
        item.classList.remove('selected');
    });
    listItem.classList.add('selected');
    showPlotName(cyclone.name);
}

function attachCycloneEvents(cyclones, map) {
    cyclones.forEach(cyclone => {
        var listItem = document.getElementById(`cyclone-${cyclone.idCyclone}`);
        if (!listItem) return;

        const choose = () => selectCyclone(cyclone, listItem, map);
        listItem.addEventListener('click', choose);
        listItem.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                choose();
            }
        });

        const marker = cycloneMarkers[cyclone.idCyclone];
        if (marker) {
            marker.on('click', choose);
        }
    });
}

// Fonction pour forcer la mise à jour des données
async function forceRefreshData() {
    const refreshButton = document.getElementById('refresh-button');

    try {
        refreshButton.disabled = true;
        showLoading();
        
        // Appeler l'API pour forcer la mise à jour
        const response = await fetch('/force-update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success' && Array.isArray(result.cyclones)) {
            if (globalMap) {
                renderCyclones(globalMap, result.cyclones);
            }
        } else {
            console.error('Erreur lors de la mise à jour:', result.message);
            showStormError(result.message || 'Erreur lors de la mise à jour');
        }
    } catch (error) {
        console.error('Erreur lors de la mise à jour:', error);
        showStormError('Erreur lors de la mise à jour');
    } finally {
        refreshButton.disabled = false;
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

    header.classList.toggle('active', !isActive);
    header.setAttribute('aria-expanded', String(!isActive));
    content.classList.toggle('active', !isActive);
    if (icon) {
        icon.style.transform = '';
    }
};

// Initialiser le bouton de rafraîchissement
document.addEventListener('DOMContentLoaded', function() {
    const refreshButton = document.getElementById('refresh-button');
    if (refreshButton) {
        refreshButton.addEventListener('click', forceRefreshData);
    }
});

setInterval(async () => {
    const refreshButton = document.getElementById('refresh-button');
    if (!globalMap || (refreshButton && refreshButton.disabled)) {
        return;
    }
    try {
        const statusResponse = await fetch('/status');
        if (!statusResponse.ok || (await statusResponse.json()).is_updating) {
            return;
        }
        const response = await fetch('/cyclones-data');
        const payload = await response.json();
        if (Array.isArray(payload)) {
            renderCyclones(globalMap, payload);
        }
    } catch (error) {
        console.error('Erreur lors du rafraîchissement périodique:', error);
    }
}, 10 * 60 * 1000);
