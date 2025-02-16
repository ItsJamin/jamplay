document.addEventListener("DOMContentLoaded", function() {
    loadSongs();
    //loadQueue();
});

async function loadSongs() {
    const response = await fetch("/songs");
    const songs = await response.json();
    const songList = document.getElementById("song-list");
    songList.innerHTML = "";
    songs.forEach(song => {
        let li = document.createElement("li");
        li.className = "list-group-item d-flex justify-content-between align-items-center border-0 shadow-sm mb-2 p-3";
        li.innerHTML = `<strong class = 'title'>${song.title}</strong> - ${song.artist} 
            <button class="btn btn-primary btn-sm" onclick="addToQueue(${song.id})">Add</button>`;
        songList.appendChild(li);
    });
}

async function loadQueue() {
    const response = await fetch("/queue");
    const queueData = await response.json();
    const queueList = document.getElementById("queue-list");
    queueList.setAttribute("value","");
    queueData.queue.forEach(song => {
        let li = document.createElement("li");
        li.className = "list-group-item border-0 shadow-sm mb-2 p-3";
        li.innerHTML = `<strong>${song}</strong>`;
        queueList.appendChild(li);
    });
}

async function addToQueue(songId) {
    await fetch("/queue/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ song_id: songId })
    });
    loadQueue();
}

async function playNextSong() {
    const response = await fetch("/queue/next");
    const song = await response.json();
    alert(`Now playing: ${song.next_song}`);
    loadQueue();
}

async function uploadSong() {
    let url = document.getElementById("song-url").value;
    if (!url) return alert("Please enter a URL");
    document.getElementById.innerText = "";
    const response = await fetch("/songs/upload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url })
    });
    if (response.ok) {
        alert("Song download started!");
        loadSongs();
    }
}

function filterSongs() {
    console.log("Checking...")
    let input = document.getElementById("search-bar").value.toLowerCase().trim();
    let items = document.querySelectorAll("#song-list li");

    console.log(items.length);

    items.forEach(item => {
        let titleElement = item.querySelector(".title");
        if (titleElement) {
            let titleText = titleElement.textContent.toLowerCase().trim();
            console.log(titleText, input);
            item.style.visibility = titleText.includes(input) ? "visible" : "hidden";
            item.style.height = titleText.includes(input) ? "auto" : "0px"; // Damit es keinen Platz einnimmt
        }
    });
}


