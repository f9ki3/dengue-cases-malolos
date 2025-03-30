// Initialize the map
const map = L.map("map", {
  center: [14.8435589, 120.7975402], // Default coordinates
  zoom: 12,
  zoomControl: false, // Disable the default zoom control
});

// Add a tile layer to the map
// Define the tile layers
const regularLayer = L.tileLayer(
  "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
);
const satelliteLayer = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  {
    attribution: "Tiles © Esri",
  }
);

// Add the regular layer by default
regularLayer.addTo(map);

// Toggle map mode
let isSatellite = false;
document.getElementById("map-mode").addEventListener("click", () => {
  if (isSatellite) {
    map.removeLayer(satelliteLayer);
    map.addLayer(regularLayer);
  } else {
    map.removeLayer(regularLayer);
    map.addLayer(satelliteLayer);
  }
  isSatellite = !isSatellite;
});

// Define custom icon
const customIcon = L.icon({
  iconUrl: "/static/img/pin.png", // Path to your custom pin image
  iconSize: [32, 32], // Size of the icon
  iconAnchor: [16, 32], // Point of the icon which will correspond to marker's location
  popupAnchor: [0, -32], // Point from which the popup will open relative to the iconAnchor
});

const yearSelect = document.getElementById("year-select");
const monthSelect = document.getElementById("month-select");

// Disable month-select by default
monthSelect.disabled = true;

// Store markers to clear them when filters update
let markers = [];
let circles = [];

// Listen for real-time input changes in the search box
document.getElementById("search-input").addEventListener("input", function () {
  fetchBarangayCases();
});

function fetchBarangayCases() {
  const year = yearSelect.value;
  const month = monthSelect.value;
  const search = document.getElementById("search-input").value.trim();

  monthSelect.disabled = !year;
  if (!year) monthSelect.value = "";

  let url = "/getBarangayCases";
  const params = new URLSearchParams();
  if (year) params.append("year", year);
  if (month) params.append("month", month);
  if (search) params.append("search", search);
  if (params.toString()) url += `?${params.toString()}`;

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      // Clear existing markers and circles
      markers.forEach((marker) => map.removeLayer(marker));
      circles.forEach((circle) => map.removeLayer(circle));

      markers = [];
      circles = [];

      const listGroup = document.querySelector(".list-group");
      listGroup.innerHTML = "";

      data.sort((a, b) => b.Cases - a.Cases);

      let hasGreen = false,
        hasOrange = false,
        hasRed = false;

      data.forEach(({ Barangay, Cases, Latitude, Longitude }) => {
        let color = "green";
        if (Cases > 10 && Cases <= 50) {
          color = "orange";
          hasOrange = true;
        } else if (Cases > 50) {
          color = "red";
          hasRed = true;
        } else {
          hasGreen = true;
        }

        const circle = L.circle([Latitude, Longitude], {
          color: color,
          fillColor: color,
          fillOpacity: 0.5,
          radius: Cases * 5,
        }).addTo(map);
        circles.push(circle);

        const marker = L.marker([Latitude, Longitude], {
          icon: customIcon,
        }).addTo(map);
        marker.bindPopup(`<b>${Barangay}</b><br>Cases: ${Cases}`);
        markers.push(marker);

        const listItem = document.createElement("li");
        listItem.className =
          "list-group-item d-flex justify-content-between align-items-start clickable";
        listItem.style.cursor = "pointer";
        listItem.innerHTML = `
          <div class="ms-2 me-auto">
            <div class="fw-bold fs-6">${Barangay}</div>
            <div class="fs-6">Latitude: ${Latitude}</div>
            <div class="fs-6">Longitude: ${Longitude}</div>
          </div>
          <span class="badge text-bg-${
            color === "green"
              ? "success"
              : color === "orange"
              ? "warning"
              : "danger"
          } rounded-pill">${Cases}</span>
        `;

        listItem.addEventListener("click", () => {
          marker.openPopup();
          map.panTo([Latitude, Longitude]);
        });

        listGroup.appendChild(listItem);
      });

      updateLegend(hasGreen, hasOrange, hasRed);
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

function updateLegend(hasGreen, hasOrange, hasRed) {
  const legendDiv = document.querySelector(".info.legend");
  legendDiv.innerHTML = "<h6>Risk Levels</h6>";

  if (hasGreen) {
    legendDiv.innerHTML += `<div><span style="background: green; width: 15px; height: 15px; display: inline-block; margin-right: 5px;"></span> Low Risk (0–10 cases)</div>`;
  }
  if (hasOrange) {
    legendDiv.innerHTML += `<div><span style="background: orange; width: 15px; height: 15px; display: inline-block; margin-right: 5px;"></span> Moderate Risk (11–50 cases)</div>`;
  }
  if (hasRed) {
    legendDiv.innerHTML += `<div><span style="background: red; width: 15px; height: 15px; display: inline-block; margin-right: 5px;"></span> High Risk (51+ cases)</div>`;
  }
}

// Event listeners for year and month select elements
yearSelect.addEventListener("change", fetchBarangayCases);
monthSelect.addEventListener("change", fetchBarangayCases);

// Initial fetch when the page loads to show all barangay cases
fetchBarangayCases();

// Zoom controls functionality
document
  .getElementById("zoom-in")
  .addEventListener("click", () => map.zoomIn());
document
  .getElementById("zoom-out")
  .addEventListener("click", () => map.zoomOut());

function resetFilterMapping() {
  // Reset the dropdown values
  yearSelect.value = "";
  monthSelect.value = "";
  monthSelect.disabled = true;

  // Clear the search input field
  document.getElementById("search-input").value = "";

  // Clear existing markers and circles from the map
  markers.forEach((marker) => map.removeLayer(marker));
  circles.forEach((circle) => map.removeLayer(circle));

  markers = [];
  circles = [];

  // Clear the list
  const listGroup = document.querySelector(".list-group");
  listGroup.innerHTML = "";

  // Fetch all barangay cases (no filters)
  fetchBarangayCases();
}

// Add a legend to the map

// Initial legend setup
const legend = L.control({ position: "bottomright" });

legend.onAdd = function () {
  const div = L.DomUtil.create("div", "info legend");
  div.innerHTML = "<h6>Risk Levels</h6>";
  return div;
};

legend.addTo(map);
