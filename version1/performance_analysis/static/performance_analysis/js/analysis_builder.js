
document.addEventListener("DOMContentLoaded", function () {

    const container = document.getElementById("periodContainer");
    const template = document.getElementById("periodTemplate");
    const addButton = document.getElementById("addPeriod");

    const totalForms = document.getElementById("id_periods-TOTAL_FORMS");
    const comparisonMode = document.getElementById("comparisonMode");

    const sameTeamsSection = document.getElementById("sameTeamsSection");

    function activePeriods() {
        return [...container.querySelectorAll(".period-card")]
            .filter(card => {
                const deleteInput = card.querySelector(
                    'input[name$="-DELETE"]'
                );

                return !deleteInput || deleteInput.value !== "true";
            });
    }

    function updatePeriodNumbers() {
        activePeriods().forEach((card, index) => {
            const title = card.querySelector(".period-title");

            if (title) {
                title.innerHTML =
                    `<i class="bi bi-calendar3 me-2"></i> Reporting Period ${index + 1}`;
            }
        });

        container.querySelectorAll(".remove-period").forEach(button => {
            button.disabled = activePeriods().length <= 2;
        });
    }

    function updateComparisonMode() {
        const mode = comparisonMode.value;
        const isSameTeams = mode === "SAME_TEAMS";

        sameTeamsSection.style.display = isSameTeams ? "block" : "none";

        document.querySelectorAll(".period-team-selection").forEach(section => {
            section.style.display = isSameTeams ? "none" : "block";
        });
    }

    addButton.addEventListener("click", function () {

        const index = parseInt(totalForms.value, 10);

        const html = template.innerHTML.replaceAll(
            "__prefix__",
            index
        );

        container.insertAdjacentHTML("beforeend", html);

        totalForms.value = index + 1;

        updateComparisonMode();
        updatePeriodNumbers();
    });

    container.addEventListener("click", function (event) {

        const button = event.target.closest(".remove-period");

        if (!button) return;

        if (activePeriods().length <= 2) {
            return;
        }

        const card = button.closest(".period-card");

        const deleteInput = card.querySelector(
            'input[name$="-DELETE"]'
        );

        if (deleteInput) {
            deleteInput.value = "true";
        }

        card.style.display = "none";

        updatePeriodNumbers();
    });

    comparisonMode.addEventListener("change", updateComparisonMode);

    updateComparisonMode();
    updatePeriodNumbers();

});
