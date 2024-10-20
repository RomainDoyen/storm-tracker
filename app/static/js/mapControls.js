var isZoomEnabled = false;

export function setupMapControls(map) {
    var zoomToggleButton = L.control({ position: 'topright' });

    zoomToggleButton.onAdd = function () {
        var div = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
        div.innerHTML = 'Activer le Zoom par défilement';
        div.style.backgroundColor = '#aa0e0b';
        div.style.color = '#fff';
        div.style.padding = '5px';
        div.style.cursor = 'pointer';
        div.onclick = toggleZoom.bind(div, map);
        return div;
    };

    zoomToggleButton.addTo(map);

    var resetViewButton = L.control({ position: 'topright' });

    resetViewButton.onAdd = function () {
        var div = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
        div.innerHTML = 'Remettre la vue par défaut';
        div.style.backgroundColor = '#006494';
        div.style.color = '#fff';
        div.style.padding = '5px';
        div.style.cursor = 'pointer';
        div.onclick = function () {
            map.setView([10, 20], 2);
        };
        return div;
    };

    resetViewButton.addTo(map);
}

function toggleZoom(map) {
    if (isZoomEnabled) {
        map.scrollWheelZoom.disable();
        map.dragging.disable();
        this.innerHTML = 'Activer le Zoom par défilement';
    } else {
        map.scrollWheelZoom.enable();
        map.dragging.enable();
        this.innerHTML = 'Désactiver le Zoom par défilement';
    }
    isZoomEnabled = !isZoomEnabled;
}
