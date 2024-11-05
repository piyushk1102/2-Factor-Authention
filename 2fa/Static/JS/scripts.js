// scripts.js

document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const inputs = form.querySelectorAll('input');
            let valid = true;

            inputs.forEach(input => {
                if (input.type !== "submit" && input.value.trim() === "") {
                    valid = false;
                    alert(`Please fill in the ${input.name} field.`);
                    e.preventDefault();
                }
            });
        });
    });
});
