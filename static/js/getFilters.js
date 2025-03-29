// Fetch Year data from the /getYear endpoint
fetch("/getYear")
  .then((response) => response.json())
  .then((data) => {
    const yearSelect = document.getElementById("year-select");

    // Loop through the years array and append options to the Year select dropdown
    data.years.forEach((year) => {
      const option = document.createElement("option");
      option.value = year; // The year value
      option.textContent = year; // The year text displayed in the dropdown
      yearSelect.appendChild(option);
    });
  })
  .catch((error) => {
    console.error("Error fetching year data:", error);
  });

// Fetch Month data from the /getMonths endpoint
fetch("/getMonths")
  .then((response) => response.json())
  .then((data) => {
    const monthSelect = document.getElementById("month-select");

    // Loop through the months array and append options to the Month select dropdown
    data.months.forEach((month) => {
      const option = document.createElement("option");
      option.value = month; // The month value
      option.textContent = month; // The month text displayed in the dropdown
      monthSelect.appendChild(option);
    });
  })
  .catch((error) => {
    console.error("Error fetching month data:", error);
  });
