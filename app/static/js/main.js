let audioElement = null;
let updateInterval = null;
let lastSearchQuery = '';
let searchTimeout = null;
let selectedSearchIndex = -1;
let isDragging = false;
let queue = [];

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

    $('#search-input').on('blur', function () {
        setTimeout(() => $('#search-results').hide(), 200); // Kurze Verzögerung, damit Klicks auf Suchergebnisse registriert werden
    });
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
    resetButtonState();
}

/* ----- Music Player Controls ----- */

function playTrack(song) {
    if (audioElement) {
        audioElement.pause();
        audioElement = null;
    }
    audioElement = new Audio(`api/play?song=${song}`);
    audioElement.play();
    $('#play-pause-btn').html('<i class="bi bi-pause"></i>');
    $('#current-song').text(song);

    audioElement.addEventListener("timeupdate", updateProgressBar);
    audioElement.addEventListener("ended", skipTrack);
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
    if (queue.length > 0) {
        if (queue.length > 0) {
            playTrack(queue[0]);
            $('#current-song').text(queue[0]);
            queue.splice(0, 1);
            updateQueue();

        } else {
            audioElement = null;
            $('#current-song').text("- " + lang.no_song_playing + " -");
        }
    }
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
        /* if (query.length === 0) {
            $('#search-results').hide();
            return;
        } */
        
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
    $('#search-input').focus();
    $('#add-btn').prop('disabled', song === '');
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
                <div class="search-item" data-name="${song}">
                    ${song}
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
    selectSong();
    if (!input) return;
    const isYoutube = isYoutubeUrl(input);

    let rename = null;
    if (isYoutube) {
        rename = prompt(lang.rename_song);
    }
    showLoadingState(isYoutube);

    const payload = isYoutube ? 
        { url: input, rename: rename } : 
        { song: input + '.wav' };

    fetch('/api/queue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) throw new Error(data.error);
        queue.push(data.name);
        updateQueue();
        if (!audioElement) {
            skipTrack();
        }
        resetButtonState();
    })
    .catch(showError);
    
    $('#search-input').val('');
}

function showLoadingState(isYoutube) {
    const btn = $('#add-btn');
    btn.prop('disabled', true);
    
    const btnText = document.getElementById("add-btn").querySelector(".btn-text");
    
    if (isYoutube) {
        btnText.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${lang.downloading}`;
    } else {
        btnText.textContent = lang.add_to_queue_btn;
    }
}

function resetButtonState() {
    $('#add-btn').prop('disabled', false);
    document.getElementById("add-btn").querySelector(".btn-text").textContent = lang.add_to_queue_btn;
}


/* ----- Queue Management ----- */

function updateQueue() {
    const queueList = $('#queue-list');
    const focusedIndex = queueList.find('.list-group-item:focus').index(); 
    queueList.empty();

    queue.forEach((song, index) => {
        const item = $(`
            <div class="list-group-item draggable" 
                 tabindex="0"
                 data-index="${index}"
                 aria-label="${song}, ${index + 1}">
                <span class="song-name">${song}</span>
                <i class="bi bi-trash delete-song"></i>
            </div>
        `);

        item.hover(
            function () { $(this).find('.delete-song').fadeIn(150); },
            function () { $(this).find('.delete-song').fadeOut(150); }
        );

        item.find('.delete-song').on('click', () => {
            queue.splice(index, 1);
            updateQueue();
        });

        // Keyboard-Controls
        item.on('keydown', function (event) {
            const focusedIndex = item.index();

            if (event.ctrlKey) {
                if (event.key === 'ArrowUp') {
                    if (focusedIndex > 0) {
                        const movedItem = queue.splice(focusedIndex, 1)[0];
                        queue.splice(focusedIndex - 1, 0, movedItem);
                        item.prev().focus();
                        updateQueue();
                    }
                    event.preventDefault();
                } else if (event.key === 'ArrowDown') {
                    if (focusedIndex < queue.length - 1) {
                        const movedItem = queue.splice(focusedIndex, 1)[0];
                        queue.splice(focusedIndex + 1, 0, movedItem);
                        item.next().focus();
                        updateQueue();
                    }
                    event.preventDefault();
                }
            } else if (event.key == 'ArrowUp') {
                item.prev().focus();
                event.preventDefault();
            } else if (event.key == 'ArrowDown') {
                item.next().focus();
                event.preventDefault();
            } else if (event.key === 'Delete' || event.key === 'Backspace') {
                queue.splice(focusedIndex, 1);
                updateQueue();
                event.preventDefault();
            } else if (event.key === 'Space' || event.key === 'Enter') {
                const movedItem = queue.splice(focusedIndex, 1)[0];
                queue.splice(0, 0, movedItem);
                skipTrack();
                updateQueue();
                event.preventDefault();
            }
        });

        queueList.append(item);
    });

    // Set focus back
    if (focusedIndex >= 0) {
        queueList.find('.list-group-item').eq(focusedIndex).focus();
    }

    new Sortable(queueList[0], {
        animation: 200,
        ghostClass: 'dragging',
        onStart: function (evt) {
            evt.from.querySelectorAll('.list-group-item').forEach(item => {
                item.setAttribute('tabindex', '-1');
            });
        },
        onEnd: function (evt) {
            evt.from.querySelectorAll('.list-group-item').forEach(item => {
                item.setAttribute('tabindex', '0');
            });
            const oldIndex = evt.oldIndex;
            const newIndex = evt.newIndex;

            if (oldIndex !== newIndex) {
                const movedItem = queue.splice(oldIndex, 1)[0];
                queue.splice(newIndex, 0, movedItem);
                updateQueue();
            }
        }
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
