document.getElementById('healthForm')?.addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = {};
    const inputs = document.querySelectorAll('#healthForm input[type="radio"]:checked');

    inputs.forEach(input => {
        formData[input.name] = input.value;
    });

    document.querySelector('.loader').style.display = 'block';

    fetch('/analyze_health', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    })
    .then(res => res.json())
    .then(data => {
        document.querySelector('.loader').style.display = 'none';

        if (data.error) {
            alert("Something went wrong.");
            return;
        }

        const container = document.getElementById('resultContainer');
        container.innerHTML = `
            <h2 style="color:${data.color}">${data.risk_level}</h2>
            <p>${data.message}</p>
        `;
        container.style.display = 'block';
    })
    .catch(err => {
        document.querySelector('.loader').style.display = 'none';
        alert("Server error.");
        console.error(err);
    });
});
