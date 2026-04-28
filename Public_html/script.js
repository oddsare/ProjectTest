// Slider value display
const sliders = document.querySelectorAll(".slider");
sliders.forEach(slider => {
    const valueDisplay = slider.parentElement.nextElementSibling.querySelector(".slider-value");
    valueDisplay.textContent = slider.value;
    slider.addEventListener("input", () => {
        valueDisplay.textContent = slider.value;
    });
});

// Survey form submission
const form = document.getElementById("dormForm");
form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(form);
    const responses = Object.fromEntries(formData.entries());

    try {
        const response = await fetch(`${API_BASE}/api/survey`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(responses)
        });

        const data = await response.json();

        if (response.ok) {
            window.location.href = 'dashboard.html';
        } else {
            alert(data.message || 'Failed to submit survey. Please try again.');
        }
    } catch (error) {
        alert('Unable to connect to server. Please try again.');
    }
});
