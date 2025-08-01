let lastPlayerId = null;
let lastTeamId = null;

// ⏱️ Load time from localStorage
let minute = localStorage.getItem('minute') ? parseInt(localStorage.getItem('minute')) : 0;
let second = localStorage.getItem('second') ? parseInt(localStorage.getItem('second')) : 0;

// Start the timer and update DOM
function startTimer() {
    setInterval(() => {
        second++;
        if (second === 60) {
            minute++;
            second = 0;
        }
        localStorage.setItem('minute', minute);
        localStorage.setItem('second', second);

        document.getElementById("minute").textContent = minute;
        document.getElementById("second").textContent = second;
    }, 1000);
}
startTimer();

// 💡 Highlight selected button
function highlightButton(playerId) {
    document.querySelectorAll('.player-btn').forEach(btn => {
        btn.style.backgroundColor = 'lightblue';
    });

    if (playerId) {
        const btn = document.getElementById(`player-${playerId}`);
        if (btn) {
            btn.style.backgroundColor = 'green';
        }
    }
}

// 🔁 Update pass count visually
function incrementPassCount(playerId) {
    const btn = document.getElementById(`player-${playerId}`);
    if (btn) {
        let count = parseInt(btn.dataset.passCount || 0);
        count += 1;
        btn.dataset.passCount = count;

        const span = btn.querySelector('.pass-count');
        if (span) {
            span.textContent = count;
        }
    }
}

// 🧠 Save pass to backend
function recordPass(fromPlayerId, toPlayerId, fromTeamId, toTeamId, isSuccessful = true, isPossessionRegained = false) {
    fetch('/tagging/save-pass/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            match_id: matchId,
            from_player_id: fromPlayerId,
            to_player_id: toPlayerId,
            from_team_id: fromTeamId,
            to_team_id: toTeamId,
            minute: minute,
            second: second,
            x_start: null,
            y_start: null,
            x_end: null,
            y_end: null,
            is_successful: isSuccessful,
            is_possession_regained: isPossessionRegained
        })
    }).then(res => res.json()).then(data => {
        if (data.status === 'success') {
            document.getElementById('last-pass').textContent = `From ${fromPlayerId} → To ${toPlayerId}`;
            incrementPassCount(toPlayerId);
            highlightButton(toPlayerId);
        } else {
            alert("Failed to save pass: " + data.message);
        }
    });
}

// 🔘 When player button is clicked
document.querySelectorAll('.player-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const playerId = btn.dataset.playerId;
        const teamId = btn.dataset.teamId;

        if (lastPlayerId) {
            recordPass(lastPlayerId, playerId, lastTeamId, teamId, true, false);
        }

        lastPlayerId = playerId;
        lastTeamId = teamId;
        highlightButton(playerId);
    });
});

// 🟥 Opponent team (ball lost)
document.getElementById('opponent-btn').addEventListener('click', () => {
    const opponentTeamId = document.getElementById('opponent-btn').dataset.teamId;

    if (lastPlayerId && lastTeamId) {
        recordPass(lastPlayerId, null, lastTeamId, opponentTeamId, false, false);
        highlightButton(null);
        lastPlayerId = null;
        lastTeamId = null;
    }
});

// 🍪 Get CSRF token
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
