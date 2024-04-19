document.addEventListener('DOMContentLoaded', function() {
    const fromInput = document.getElementById('from-input');
    const toInput = document.getElementById('to-input');
    const fromCitiesList = document.getElementById('from-cities-list');
    const toCitiesList = document.getElementById('to-cities-list');

    function filterCitiesList(input, citiesList) {
        const inputValue = input.value.toLowerCase();
        const cities = citiesList.querySelectorAll('li');

        cities.forEach(function(city) {
            const cityName = city.textContent.toLowerCase();
            if (cityName.includes(inputValue)) {
                city.style.display = 'block';
            } else {
                city.style.display = 'none';
            }
        });
    }

    fromInput.addEventListener('focus', function() {
        fromCitiesList.style.display = 'flex';
    });

    toInput.addEventListener('focus', function() {
        toCitiesList.style.display = 'flex';
    });

    document.addEventListener('click', function(event) {
        if (!fromInput.contains(event.target) && !fromCitiesList.contains(event.target)) {
            fromCitiesList.style.display = 'none';
            filterCitiesList(fromInput, fromCitiesList);
        }
        if (!toInput.contains(event.target) && !toCitiesList.contains(event.target)) {
            toCitiesList.style.display = 'none';
            filterCitiesList(toInput, toCitiesList);
        }
    });

    fromInput.addEventListener('input', function() {
        filterCitiesList(fromInput, fromCitiesList);
    });

    toInput.addEventListener('input', function() {
        filterCitiesList(toInput, toCitiesList);
    });
});