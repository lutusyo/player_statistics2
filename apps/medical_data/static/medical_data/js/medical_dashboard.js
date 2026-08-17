document.addEventListener("DOMContentLoaded", function () {

    const complaintCanvas =
        document.getElementById("complaintChart");

    const teamCanvas =
        document.getElementById("teamChart");

    const dailyCanvas =
        document.getElementById("dailyChart");


    if (complaintCanvas) {

        new Chart(complaintCanvas, {

            type: "doughnut",

            data: {

                labels: complaintLabels,

                datasets: [{
                    data: complaintValues
                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        position: "right"
                    }

                }

            }

        });

    }


    if (teamCanvas) {

        new Chart(teamCanvas, {

            type: "bar",

            data: {

                labels: teamLabels,

                datasets: [{
                    label: "New Injuries",
                    data: teamValues
                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }

                },

                plugins: {

                    legend: {
                        display: false
                    }

                }

            }

        });

    }


    if (dailyCanvas) {

        new Chart(dailyCanvas, {

            type: "line",

            data: {

                labels: dateLabels,

                datasets: [{

                    label: "Medical Visits",

                    data: dateValues,

                    tension: 0.3,

                    fill: true

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    y: {

                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        }

                    }

                }

            }

        });

    }

});