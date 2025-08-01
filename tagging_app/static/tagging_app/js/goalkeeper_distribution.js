const methodSelect = document.getElementById('method');
const detailButtonsDiv = document.getElementById('detail-buttons');
let selectedDetail = null;

methodSelect.addEventListener('change', () => {
    const method = methodSelect.value;
    let details = [];

    if (method === 'from_feet') {
        details = ['play_onto', 'play_into', 'play_around', 'play_beyond', 'other_feet'];
    } else if (method === 'from_hands') {
        details = ['side_kick', 'from_hands', 'drop_kick'];
    } else if (method === 'throw') {
        details = ['over_arm', 'under_arm', 'side_arm', 'chest_pass'];
    }

    detailButtonsDiv.innerHTML = '';
    selectedDetail = null;

    details.forEach(detail => {
        const btn = document.createElement('button');
        btn.textContent = detail.replaceAll('_', ' ');
        btn.type = 'button';
        btn.onclick = () => {
            selectedDetail = detail;
            document.querySelectorAll('#detail-buttons button').forEach(b => b.style.background = '');
            btn.style.background = 'lightblue';
        };
        detailButtonsDiv.appendChild(btn);
    });
});

document.getElementById('gk-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const gkId = document.getElementById('goalkeeper').value;
    const teamId = document.getElementById('goalkeeper').selectedOptions[0].dataset.team;
    const method = methodSelect.value;

    if (!selectedDetail || !method) {
        alert('Please select method and detail.');
        return;
    }

    const payload = {
        match_id: matchId,
        goalkeeper_id: gkId,
        team_id: teamId,
        minute: parseInt(document.getElementById('minute').value),
        second: parseInt(document.getElementById('second').value),
        involvement_duration: parseFloat(document.getElementById('duration').value) || null,
        method: method,
        detail: selectedDetail,
        is_complete: document.getElementById('is_complete').checked,
        is_goal_conceded: document.getElementById('is_goal_conceded').checked
    };

    fetch('/tagging/save-goalkeeper-event/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(payload)
    }).then(res => res.json())
      .then(data => {
          if (data.status === 'success') {
              alert('Saved successfully!');
              this.reset();
              detailButtonsDiv.innerHTML = '';
          } else {
              alert('Error: ' + data.message);
          }
      });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let c of cookies) {
            const cookie = c.trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
