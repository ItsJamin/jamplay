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
    getCurrentData();

    $('#search-input').on('blur', function () {
        setTimeout(() => $('#search-results').hide(), 200); // Kurze Verzögerung, damit Klicks auf Suchergebnisse registriert werden
    });
});

/* ----- UI Updates & Error Handling ----- */

function formatTime(seconds) {
    let min = Math.floor(seconds / 60);
    let sec = Math.floor(seconds % 60);
    // let milsec = Math.floor((seconds % 1) * 100);
    return `${min}:${sec < 10 ? "0" : ""}${sec}`;
}

function applyTranslations() {
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

function playTrack(song, play=true) {
    if (audioElement) {
        audioElement.pause();
        audioElement = null;
    }
    audioElement = new Audio(`api/play?song=${song}`);
    if (play) {
        audioElement.play();
        $('#play-pause-btn').html('<i class="bi bi-pause"></i>');
    }
    else {
        $('#play-pause-btn').html('<i class="bi bi-play"></i>');
    }
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

    sendPlayerStatus()
}

function skipTrack() {
    if (queue.length > 0) {
        playTrack(queue[0]);
        $('#current-song').text(queue[0]);
        document.title = queue[0];
        queue.splice(0, 1);
        updateQueue();
        sendPlayerStatus();
    } else {
        $('#play-pause-btn').html('<i class="bi bi-play"></i>');
        audioElement.pause();
        audioElement = null;
        $('#current-song').text("- " + lang.no_song_playing + " -");
        $('#progress-bar').css('width', `${0}%`);
        $('#progress-thumb').css('left', `${0}%`);
        $('#time-display').text(`- / -`);
        document.title = "JamPlayer";
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
    }, 10);
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
    addToQueue();
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
        const element = results.eq(selectedSearchIndex)[0];
        element.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
}

/* ----- Download-Button ----- */

function addToQueue() {
    const input = $('#search-input').val().trim();
    
    console.log(input);
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

/* ----- Queue Management ----- */

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
                 draggable="true"
                 aria-label="${song}, ${index + 1}">
                <span class="song-name">${song}</span>
                <i class="bi bi-trash delete-song"></i>
            </div>
        `);

        // Show delete button on hover (desktop) or always on mobile
        if ('ontouchstart' in window) {
            item.find('.delete-song').show();
        } else {
            item.hover(
                function() { $(this).find('.delete-song').fadeIn(150); },
                function() { $(this).find('.delete-song').fadeOut(150); }
            );
        }

        // Delete button functionality
        item.find('.delete-song').on('click', function(e) {
            e.stopPropagation();
            queue.splice(index, 1);
            updateQueue();
        });

        // Song name click/tap functionality
        if (!'ontouchstart' in window) {
            item.find('.song-name').on('click', function() {
                const movedItem = queue.splice(index, 1)[0];
                queue.splice(0, 0, movedItem);
                skipTrack();
                updateQueue();
            });
        }

        // Drag & Drop events
        item[0].addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', index.toString());
            setTimeout(() => item.addClass('dragging'), 0);
        });

        item[0].addEventListener('dragend', () => {
            item.removeClass('dragging');
            updateQueue();
        });

        item[0].addEventListener('dragover', (e) => {
            e.preventDefault();
            if (!item.hasClass('dragover')) {
                item.addClass('dragover');
                setTimeout(() => item.removeClass('dragover'), 100);
            }
        });

        item[0].addEventListener('drop', (e) => {
            e.preventDefault();
            const fromIndex = parseInt(e.dataTransfer.getData('text/plain'));
            const toIndex = index;
            
            if (fromIndex !== toIndex) {
                const [movedItem] = queue.splice(fromIndex, 1);
                queue.splice(toIndex, 0, movedItem);
                updateQueue();
            }
        });

        // Keyboard navigation
        item.on('keydown', function(event) {
            const focusedIndex = $(this).index();

            if (event.ctrlKey) {
                if (event.key === 'ArrowUp') {
                    if (focusedIndex > 0) {
                        const movedItem = queue.splice(focusedIndex, 1)[0];
                        queue.splice(focusedIndex - 1, 0, movedItem);
                        $(this).prev().focus();
                        updateQueue();
                    }
                    event.preventDefault();
                } else if (event.key === 'ArrowDown') {
                    if (focusedIndex < queue.length - 1) {
                        const movedItem = queue.splice(focusedIndex, 1)[0];
                        queue.splice(focusedIndex + 1, 0, movedItem);
                        $(this).next().focus();
                        updateQueue();
                    }
                    event.preventDefault();
                }
            } else if (event.key === 'ArrowUp') {
                $(this).prev().focus();
                event.preventDefault();
            } else if (event.key === 'ArrowDown') {
                $(this).next().focus();
                event.preventDefault();
            } else if (event.key === 'Delete' || event.key === 'Backspace') {
                queue.splice(focusedIndex, 1);
                updateQueue();
                event.preventDefault();
            } else if (event.key === ' ' || event.key === 'Enter') {
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
}

/* ----- Progress Bar Functions ----- */

function updateProgressBar() {
    if (isDragging || !audioElement || !audioElement.duration) return;

    const progress = (audioElement.currentTime / audioElement.duration) * 100;
    let time = `${formatTime(audioElement.currentTime)} / ${formatTime(audioElement.duration)}`;
    $('#progress-bar').css('width', `${progress}%`);
    $('#progress-thumb').css('left', `${progress}%`);
    $('#time-display').text(time);

    // document.title = `${formatTime(audioElement.currentTime)}` + " " + document.getElementById("current-song").textContent;

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
    sendPlayerStatus();
}

/* ----- Feedback to Back-End ----- */
let statusUpdateTimeout = null;

function sendPlayerStatus() {
    if (!audioElement || !audioElement.src) return;

    if (statusUpdateTimeout) {
        clearTimeout(statusUpdateTimeout);
    }


    statusUpdateTimeout = setTimeout(() => {
        fetch('/api/player/status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: audioElement ? $('#current-song').text().trim(): "",
                position: audioElement ? audioElement.currentTime: 0,
                playing: audioElement ? !audioElement.paused: false,
                time: Date.now()
            })
        }).catch(err => console.error(err));
    }, 10);
}

function getCurrentData() {
    fetch('/api/player/status')
    .then(response => response.json())
    .then(data => {
        if (data.error) throw new Error(data.error);
        if (data.name) {
            playTrack(data.name, false);
            if (!audioElement || (!audioElement.src && audioElement.paused)) return;

            if (data.time) {
                audioElement.currentTime = data.time;
            } else {
                audioElement.currentTime = 0;
            }
            updateProgressBar();
        }
    });
}

/* Mobile Responsiveness */ 
function enableTouchClickFallback(selector, handler) {
    let touchMoved = false;

    $(document).on('touchstart', selector, function() {
        touchMoved = false;
    });

    $(document).on('touchmove', selector, function() {
        touchMoved = true;
    });

    $(document).on('touchend', selector, function(e) {
        if (!touchMoved) {
            e.preventDefault();
            handler.call(this, e);
        }
    });

    $(document).on('click', selector, function(e) {
        handler.call(this, e);
    });
}
