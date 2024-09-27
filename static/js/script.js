function performPing() {
    const ipAddress = document.getElementById('ipAddress').value;
    const locationSelect = document.getElementById('locationSelect');
    const newLocationInput = document.getElementById('newLocation');
    let location = locationSelect.value || newLocationInput.value;
 
    fetch('/ping', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ip: ipAddress, location })
    })
    .then(response => response.json())
    .then(data => {
        if (data.result) {
            typeWriter(data.result, 'pingResult');
            addLocationToDropdown(location);
        } else {
            typeWriter(`Error: ${data.error}`, 'pingResult');
        }
    })
    .catch(error => console.error('Error:', error));
 }
 
 
 function selectLocation() {
    const locationSelect = document.getElementById('locationSelect');
    alert(`Selected Location: ${locationSelect.value}`);
 }
 
 function addLocationToDropdown(location) {
    const selects = [
        document.getElementById('locationSelect'),
        document.getElementById('locationSelectLatency'),
        document.getElementById('stabilityLocationSelect')
    ];
    
    selects.forEach(select => {
        if (![...select.options].some(option => option.value === location)) {
            const option = document.createElement('option');
            option.value = location;
            option.textContent = location;
            select.appendChild(option);
        }
    });
}
function checkLatency() {
    const ipAddress = document.getElementById('ipAddress').value;
    const locationSelect = document.getElementById('locationSelectLatency');
    const newLocationInput = document.getElementById('newLocation');
    let location = locationSelect.value || newLocationInput.value;
 
    fetch('/check_latency', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ip: ipAddress, location })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('latencyResult').textContent =
            `Average Latency: ${data.average_latency} ms\n${data.recommendation}`;
    })
    .catch(error => console.error('Error:', error));
 }
 function checkStability() {
    const location = document.getElementById('stabilityLocationSelect').value;
 
    fetch('/check_stability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ location })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('stabilityResult').textContent = data.message;
    })
    .catch(error => console.error('Error:', error));
 }
 
 function typeWriter(text, elementId, speed = 50) {
    let i = 0;
    const element = document.getElementById(elementId);
    element.textContent = '';
 
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
 }
 
 function toggleTheme() {
    const body = document.body;
 
    if (body.classList.contains('light-mode')) {
        body.classList.replace('light-mode', 'dark-mode');
        document.getElementById('themeToggle').textContent = '🌔';
    } else {
        body.classList.replace('dark-mode', 'light-mode');
        document.getElementById('themeToggle').textContent = '🌒';
    }
 }

 function showMainContent() {
    const intro = document.getElementById('intro');
    const mainContent = document.getElementById('mainContent');
 
    intro.style.display = 'none';
    mainContent.style.display = 'block';
    mainContent.classList.add('fade-in');
 }
 function fetchLocations() {
    fetch('/locations')
    .then(response => response.json())
    .then(locations => {
        const selects = [
            document.getElementById('locationSelect'),
            document.getElementById('locationSelectLatency'),
            document.getElementById('stabilityLocationSelect')
        ];
        
        locations.forEach(location => {
            selects.forEach(select => {
                const option = document.createElement('option');
                option.value = location;
                option.textContent = location;
                select.appendChild(option);
            });
        });
    })
    .catch(error => console.error('Error fetching locations:', error));
 }
 
 
 document.addEventListener('DOMContentLoaded', () => {
    document.body.classList.add('light-mode'); // Default to light mode
    fetchLocations(); // Populate dropdown on load
 });