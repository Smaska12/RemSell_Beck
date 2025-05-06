document.getElementById('city').addEventListener('input', function() {
    var selectedCity = this.value;
    var addressInput = document.getElementById('address');
    var datalist = document.getElementById('addresses');

    fetch('/autocomplete-address/?city=' + selectedCity)
        .then(response => response.json())
        .then(data => {
            datalist.innerHTML = '';
            data.addresses.forEach(function(address) {
                var option = document.createElement('option');
                option.value = address;
                datalist.appendChild(option);
            });
        })
        .catch(error => console.error('Error:', error));
});