// Weather Dashboard Script

// Store cities and data
let cities = [];
let weatherData = {};

// Initialize charts
let temperatureChart, rainfallChart, humidityChart, windChart;

// DOM Elements
const cityInput = document.getElementById('cityInput');
const addCityBtn = document.getElementById('addCityBtn');
const cityList = document.getElementById('cityList');
const alertsContainer = document.getElementById('alertsContainer');

// Add event listeners
addCityBtn.addEventListener('click', addCity);
cityInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        addCity();
    }
});

// Initialize the dashboard
window.addEventListener('load', initDashboard);

function initDashboard() {
    // Initialize charts
    initializeCharts();

    // Start data updates
    fetchData();
    setInterval(fetchData, 5000); // Update every 5 seconds
}

function initializeCharts() {
    const temperatureCtx = document.getElementById('temperatureChart').getContext('2d');
    const rainfallCtx = document.getElementById('rainfallChart').getContext('2d');
    const humidityCtx = document.getElementById('humidityChart').getContext('2d');
    const windCtx = document.getElementById('windChart').getContext('2d');

    // Temperature Chart
    temperatureChart = new Chart(temperatureCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperature (°C)',
                data: [],
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#ffffff'
                    }
                },
                title: {
                    display: true,
                    text: 'Temperature Trends',
                    color: '#ffffff',
                    font: {
                        size: 16
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        color: '#ffffff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    title: {
                        display: true,
                        text: 'Temperature (°C)',
                        color: '#ffffff'
                    }
                },
                x: {
                    ticks: {
                        color: '#ffffff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });

    // Rainfall Chart
    rainfallChart = new Chart(rainfallCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Rainfall (mm)',
                data: [],
                backgroundColor: ctx => {
                    const value = ctx.dataset.data[ctx.dataIndex];
                    // Color code based on rainfall amount
                    if (value > 30) return 'rgba(255, 0, 0, 0.7)'; // Red for heavy rain
                    if (value > 15) return 'rgba(255, 165, 0, 0.7)'; // Orange for moderate rain
                    return 'rgba(54, 162, 235, 0.7)'; // Blue for light rain
                },
                borderColor: ctx => {
                    const value = ctx.dataset.data[ctx.dataIndex];
                    if (value > 30) return 'rgba(255, 0, 0, 1)';
                    if (value > 15) return 'rgba(255, 165, 0, 1)';
                    return 'rgba(54, 162, 235, 1)';
                },
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#ffffff'
                    }
                },
                title: {
                    display: true,
                    text: 'Rainfall Data',
                    color: '#ffffff',
                    font: {
                        size: 16
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#ffffff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    title: {
                        display: true,
                        text: 'Rainfall (mm)',
                        color: '#ffffff'
                    }
                },
                x: {
                    ticks: {
                        color: '#ffffff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });

    // Humidity Chart
    humidityChart = new Chart(humidityCtx, {
        type: 'radar',
        data: {
            labels: [],
            datasets: [{
                label: 'Humidity (%)',
                data: [],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(75, 192, 192, 1)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#ffffff'
                    }
                },
                title: {
                    display: true,
                    text: 'Humidity Levels',
                    color: '#ffffff',
                    font: {
                        size: 16
                    }
                }
            },
            scales: {
                r: {
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: '#ffffff'
                    },
                    ticks: {
                        color: '#ffffff',
                        backdropColor: 'transparent'
                    }
                }
            }
        }
    });

    // Wind Speed Chart
    windChart = new Chart(windCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                label: 'Wind Speed (m/s)',
                data: [],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        color: '#ffffff'
                    }
                },
                title: {
                    display: true,
                    text: 'Wind Speed Distribution',
                    color: '#ffffff',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

// Fetch data from the backend API
async function fetchData() {
    try {
        // Fetch weather data
        const weatherResponse = await fetch('http://localhost:5000/api/weather');
        const weather = await weatherResponse.json();

        // Fetch alerts
        const alertsResponse = await fetch('http://localhost:5000/api/alerts');
        const alerts = await alertsResponse.json();

        // Update our data
        weatherData = weather;
        cities = Object.keys(weatherData);

        // Update UI
        updateCityCards();
        updateCharts();
        updateAlerts(alerts);

    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Update city cards
function updateCityCards() {
    // Clear existing cards
    cityList.innerHTML = '';

    // Create cards for each city
    cities.forEach(city => {
        renderCityCard(city);
    });
}

// Render a city card
function renderCityCard(cityName) {
    const data = weatherData[cityName];
    if (!data) return;

    // Determine weather icon based on description
    let weatherIcon = '☀️';
    if (data.description.includes('rain')) {
        weatherIcon = '🌧️';
    } else if (data.description.includes('cloud')) {
        weatherIcon = '☁️';
    } else if (data.description.includes('snow')) {
        weatherIcon = '❄️';
    } else if (data.description.includes('thunder')) {
        weatherIcon = '⛈️';
    }

    const cityCard = document.createElement('div');
    cityCard.className = 'city-card';
    cityCard.innerHTML = `
        <h3>${cityName} ${weatherIcon}</h3>
        <div class="weather-info">
            <div class="info-item">
                <span class="info-label">Temperature</span>
                <span class="info-value">${data.temperature}°C</span>
            </div>
            <div class="info-item">
                <span class="info-label">Humidity</span>
                <span class="info-value">${data.humidity}%</span>
            </div>
            <div class="info-item">
                <span class="info-label">Rainfall</span>
                <span class="info-value">${data.rainfall || 0} mm</span>
            </div>
            <div class="info-item">
                <span class="info-label">Pressure</span>
                <span class="info-value">${data.pressure} hPa</span>
            </div>
            <div class="info-item">
                <span class="info-label">Wind Speed</span>
                <span class="info-value">${data.wind_speed} m/s</span>
            </div>
            <div class="info-item">
                <span class="info-label">Condition</span>
                <span class="info-value">${data.description}</span>
            </div>
        </div>
    `;
    cityList.appendChild(cityCard);
}

// Update charts with new data
function updateCharts() {
    if (!temperatureChart || !rainfallChart || !humidityChart || !windChart) return;

    // Prepare data for charts
    const labels = cities;
    const temperatures = cities.map(city => weatherData[city]?.temperature || 0);
    const rainfall = cities.map(city => weatherData[city]?.rainfall || 0);
    const humidity = cities.map(city => weatherData[city]?.humidity || 0);
    const windSpeed = cities.map(city => weatherData[city]?.wind_speed || 0);

    // Update temperature chart
    temperatureChart.data.labels = labels;
    temperatureChart.data.datasets[0].data = temperatures;
    temperatureChart.update();

    // Update rainfall chart
    rainfallChart.data.labels = labels;
    rainfallChart.data.datasets[0].data = rainfall;
    rainfallChart.update();

    // Update humidity chart
    humidityChart.data.labels = labels;
    humidityChart.data.datasets[0].data = humidity;
    humidityChart.update();

    // Update wind speed chart
    windChart.data.labels = labels;
    windChart.data.datasets[0].data = windSpeed;
    windChart.update();
}

// Update alerts section
function updateAlerts(alerts) {
    alertsContainer.innerHTML = '';

    if (alerts.length === 0) {
        alertsContainer.innerHTML = '<p>No active alerts</p>';
        return;
    }

    alerts.forEach(alert => {
        const alertElement = document.createElement('div');
        alertElement.className = `alert ${alert.severity}`;
        alertElement.textContent = alert.message;
        alertsContainer.appendChild(alertElement);

        // Auto-remove alert after 15 seconds
        setTimeout(() => {
            if (alertElement.parentNode) {
                alertElement.remove();
            }
        }, 15000);
    });
}

// Add a new city to monitor
async function addCity() {
    const cityName = cityInput.value.trim();
    if (cityName) {
        try {
            const response = await fetch('http://localhost:5000/api/monitor/city', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ city: cityName })
            });

            if (response.ok) {
                alert(`City ${cityName} added to monitoring list. Data will appear when available.`);
                cityInput.value = '';
            } else {
                const error = await response.json();
                alert(`Error: ${error.error || 'Failed to add city'}`);
            }
        } catch (error) {
            console.error('Error adding city:', error);
            alert('Error adding city. Please try again.');
        }
    }
}