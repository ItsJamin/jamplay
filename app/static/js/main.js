let audioElement = null;
let updateInterval = null;
let lastSearchQuery = '';
let searchTimeout = null;
let selectedSearchIndex = -1;
let isDragging = false;

$(document).ready(function() {
    // Event Listeners
    $('#search-input').on('input', handleSearchInput);
    $('#search-input').on('keydown', handleKeyboardNavigation);
    $('#search-results').on('click', '.search-item', selectSong);
    $('#play-pause-btn').on('click', togglePlayPause);
    $('#skip-btn').on('click', skipTrack);
    $('#add-btn').on('click', addToQueue);

    // Progress Bar Events
    $('#progress-container').on('click', seekAudio);
    $('#progress-thumb').on('mousedown', startDrag);
    $(document).on('mousemove', onDrag);
    $(document).on('mouseup', stopDrag);

    // Initial UI setup
    applyTranslations();
    handleSearchInput();

    setTimeout(updateQueue, 5000);
    // Not necessary? setInterval(sendPlayerStatus, 2000);
    sendPlayerStatus();
});

/* ----- UI Updates & Error Handling ----- */

function applyTranslations() {
    document.querySelector(".card-title i.bi-music-note-beamed").nextSibling.nodeValue = " " + lang.current_song;
    document.getElementById("current-song").textContent = "- " + lang.no_song_playing + " -";
    document.getElementById("search-input").setAttribute("placeholder", lang.default_search_text);
    document.getElementById("add-btn").querySelector(".btn-text").textContent = lang.add_to_queue_btn;
    document.querySelector(".card-title i.bi-list-ol").nextSibling.nodeValue = " "+lang.queue;
}

function showError(message) {
    const alert = $('#error-alert');
    alert.text(message).removeClass('d-none');
    setTimeout(() => alert.addClass('d-none'), 3000);
}

/* ----- Music Player Controls ----- */

function playTrack(song) {
    audioElement = new Audio(`api/play?song=${encodeURIComponent(song.name)}`);
    audioElement.play();
    $('#play-pause-btn').html('<i class="bi bi-pause"></i>');
    $('#current-song').text(song.name);

    audioElement.addEventListener("timeupdate", updateProgressBar);
}

function togglePlayPause() {
    if (!audioElement || (!audioElement.src && audioElement.paused)) return;

    if (audioElement.paused) {
        audioElement.play();
        $('#play-pause-btn').html('<i class="bi bi-pause"></i>');
    } else {
        audioElement.pause();
        $('#play-pause-btn').html('<i class="bi bi-play"></i>');
    }

    sendPlayerStatus();
}

function skipTrack() {
    if (!audioElement || !audioElement.src) return;

    audioElement.pause();
    audioElement = null;

    $('#progress-bar').css('width', `${0}%`);
    $('#progress-thumb').css('left', `${0}%`);
    document.getElementById("current-song").textContent = "- " + lang.no_song_playing + " -";

    updateQueue();
    setTimeout(100,sendPlayerStatus());

}

/* ----- Search & Song Selection ----- */

function handleSearchInput() {
    const query = $('#search-input').val().trim();
    
    if (query === lastSearchQuery) return;
    
    clearTimeout(searchTimeout);    
    lastSearchQuery = query;
    
    $('#add-btn').prop('disabled', query === '');
    selectedSearchIndex = -1;
    
    if (isYoutubeUrl(query)) {
        return;
    }
    
    // Debounce search to avoid excessive API calls
    searchTimeout = setTimeout(() => {
        if (query.length === 0) {
            $('#search-results').hide();
            return;
        }
        
        fetch(`/api/songs?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(handleSearchResults)
            .catch(error => showError(error.message));
    }, 300);
}

function isYoutubeUrl(input) {
    return /youtube\.com|youtu\.be/.test(input);
}

function selectSong() {
    const song = $(this).data('name');
    $('#search-input').val(song);
    $('#search-results').hide();
}

function handleSearchResults(songs) {
    const results = $('#search-results');
    results.empty();
    selectedSearchIndex = -1;
    
    if (songs.length === 0) {
        results.append('<div class="search-item text-muted">No results found</div>');
    } else {
        songs.forEach(song => {
            results.append(`
                <div class="search-item" data-name="${song.name}">
                    ${song.name}
                </div>
            `);
        });
    }
    results.show();
}

function handleKeyboardNavigation(event) {
    const results = $('#search-results .search-item');
    if (results.length === 0) return;

    if (event.key === 'ArrowDown') {
        event.preventDefault();
        selectedSearchIndex = (selectedSearchIndex + 1) % results.length;
    } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        selectedSearchIndex = (selectedSearchIndex - 1 + results.length) % results.length;
    } else if (event.key === 'Enter') {
        event.preventDefault();
        if (selectedSearchIndex >= 0) {
            results.eq(selectedSearchIndex).click();
        }
        return;
    }
    
    results.removeClass('active');
    if (selectedSearchIndex >= 0) {
        results.eq(selectedSearchIndex).addClass('active');
    }
}

/* ----- Download-Button ----- */

function addToQueue() {
    const input = $('#search-input').val().trim();
    const isYoutube = isYoutubeUrl(input);

    const payload = isYoutube ? 
        { url: input } : 
        { song: input + '.wav' };

    showLoadingState(isYoutube);

    fetch('/api/queue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) throw new Error(data.error);
        $('#search-input').val('');
        updateQueue();
    })
    .catch(showError)
    .finally(() => resetButtonState());
}

function showLoadingState(isYoutube) {
    const btn = $('#add-btn');
    btn.prop('disabled', true);
    document.getElementById("add-btn").querySelector(".btn-text").textContent = isYoutube ? 
        lang.downloading: 
        lang.add_to_queue_btn;
}

function resetButtonState() {
    $('#add-btn').prop('disabled', false);
    document.getElementById("add-btn").querySelector(".btn-text").textContent = lang.add_to_queue_btn;
}


/* ----- Queue Management ----- */

function updateQueue() {
    fetch('/api/queue')
        .then(response => response.json())
        .then(queue => {
            $('#queue-list').empty();
            queue.forEach((song, index) => {
                $('#queue-list').append(`
                    <div class="list-group-item">
                        <div class="song-info">
                            <span class="song-position">${index + 1}.</span>
                            <span class="song-name">${song.name}</span>
                        </div>
                    </div>
                `);
            });

            if ((!audioElement) && queue.length > 0) {
                playTrack(queue[0]);

                setTimeout(updateQueue, 500);
            }

            $('#play-pause-btn, #skip-btn').prop('disabled', !audioElement);
        });
}

/* ----- Progress Bar Functions ----- */

function updateProgressBar() {
    if (isDragging || !audioElement || !audioElement.duration) return;

    const progress = (audioElement.currentTime / audioElement.duration) * 100;
    $('#progress-bar').css('width', `${progress}%`);
    $('#progress-thumb').css('left', `${progress}%`);

    if (progress > 99) {
        setTimeout(skipTrack, 200);
    }
}

// Click on progress bar to seek to a specific position
function seekAudio(event) {
    if (!audioElement || !audioElement.duration) return;

    const rect = $('#progress-container')[0].getBoundingClientRect();
    const offsetX = event.clientX - rect.left;
    const percentage = offsetX / rect.width;

    audioElement.currentTime = percentage * audioElement.duration;
}

// Handle dragging of the progress thumb
function startDrag(event) {
    isDragging = true;
}

function onDrag(event) {
    if (!isDragging || !audioElement || !audioElement.duration) return;

    const rect = $('#progress-container')[0].getBoundingClientRect();
    let offsetX = event.clientX - rect.left;
    offsetX = Math.max(0, Math.min(offsetX, rect.width));

    const percentage = offsetX / rect.width;
    audioElement.currentTime = percentage * audioElement.duration;

    $('#progress-bar').css('width', `${percentage * 100}%`);
    $('#progress-thumb').css('left', `${percentage * 100}%`);
}

function stopDrag() {
    isDragging = false;
}

/* ----- Feedback to Back-End ----- */
function sendPlayerStatus() {
    if (!audioElement || !audioElement.src) return;

    fetch('/api/player/status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            song: $('#current-song').text().trim(),
            currentTime: audioElement.currentTime,
            duration: audioElement.duration,
            isPlaying: !audioElement.paused
        })
    }).catch(err => console.error(err));
}
