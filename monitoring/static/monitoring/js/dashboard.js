function initMap(waterBodiesData) {
    const map = L.map('map').setView([37, -95], 4);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    waterBodiesData.forEach(item => {
        if (item.latitude && item.longitude) {
            L.marker([item.latitude, item.longitude])
                .addTo(map)
                .bindPopup(`<strong>${item.name}</strong>`);
        }
    });
}
