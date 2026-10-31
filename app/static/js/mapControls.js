var isMapLocked = false;

export function setupMapControls(map) {
    var lockButton = L.control({ position: 'topright' });

    lockButton.onAdd = function () {
        var div = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
        div.setAttribute('role', 'button');
        div.tabIndex = 0;
        div.textContent = 'Verrouiller la carte';
        L.DomEvent.disableClickPropagation(div);
        var toggle = function () {
            isMapLocked = !isMapLocked;
            if (isMapLocked) {
                map.scrollWheelZoom.disable();
                map.dragging.disable();
                div.textContent = 'Déverrouiller la carte';
            } else {
                map.scrollWheelZoom.enable();
                map.dragging.enable();
                div.textContent = 'Verrouiller la carte';
            }
        };
        div.addEventListener('click', toggle);
        div.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                toggle();
            }
        });
        return div;
    };

    lockButton.addTo(map);

    var resetViewButton = L.control({ position: 'topright' });

    resetViewButton.onAdd = function () {
        var div = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
        div.setAttribute('role', 'button');
        div.tabIndex = 0;
        div.textContent = 'Vue du monde';
        L.DomEvent.disableClickPropagation(div);
        var reset = function () {
            map.setView([10, 20], 2);
        };
        div.addEventListener('click', reset);
        div.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                reset();
            }
        });
        return div;
    };

    resetViewButton.addTo(map);
}
