
document.addEventListener("DOMContentLoaded", function () {

    const teamSelect = document.getElementById("id_team");
    const playerSelect = document.getElementById("id_player");

    if (!teamSelect || !playerSelect) {
        return;
    }

    teamSelect.addEventListener("change", function () {

        const teamId = this.value;

        playerSelect.innerHTML = '<option value="">Select Player</option>';

        if (!teamId) {
            return;
        }

        fetch(`/medical_data/ajax/load-players/?team=${teamId}`)
            .then(response => response.json())
            .then(data => {

                data.forEach(player => {

                    const option = document.createElement("option");

                    option.value = player.id;
                    option.textContent = player.name;

                    playerSelect.appendChild(option);
                });

            })
            .catch(error => {
                console.error("Error loading players:", error);
            });
    });

});