setTimeout(() => { document.body.style.opacity = '1'; }, 60);

// Anime Player State
let currentAnimeId = null;
let currentAnimeTitle = '';
let currentEp = 1;
let totalEpisodes = 12;
let currentSource = 'megaplay_sub';
const recommendedIds = [174154, 145064, 40748, 1735, 269, 21, 101922, 11061, 16498];

async function loadRecommended() {
    const grid = document.getElementById('resultsGrid');
    if(!grid) return;
    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px 0;">Loading recommended hits...</div>';

    const graphqlQuery = `
        query ($idIn: [Int]) {
            Page (perPage: 12) {
                media (id_in: $idIn, type: ANIME, sort: POPULARITY_DESC) {
                    id
                    title { romaji english }
                    coverImage { large }
                    episodes
                }
            }
        }
    `;

    try {
        const response = await fetch('https://graphql.anilist.co', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: graphqlQuery, variables: { idIn: recommendedIds } })
        });
        const data = await response.json();
        renderCards(data.data.Page.media, grid);
    } catch (err) {
        grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px 0;">Type an anime name above to begin.</div>';
    }
}

async function searchAnime() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) { loadRecommended(); return; }

    const grid = document.getElementById('resultsGrid');
    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px 0;">Searching database...</div>';

    const graphqlQuery = `
        query ($search: String) {
            Page (perPage: 20) {
                media (search: $search, type: ANIME) {
                    id
                    title { romaji english }
                    coverImage { large }
                    episodes
                }
            }
        }
    `;

    try {
        const response = await fetch('https://graphql.anilist.co', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: graphqlQuery, variables: { search: query } })
        });
        const data = await response.json();
        const animeList = data.data.Page.media;
        grid.innerHTML = '';
        
        if (animeList.length === 0) {
            grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px 0;">No anime found.</div>';
            return;
        }
        renderCards(animeList, grid);
    } catch (err) {
        grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px 0;">Failed to fetch results.</div>';
    }
}

function renderCards(animeList, grid) {
    grid.innerHTML = '';
    animeList.forEach(anime => {
        const title = anime.title.english || anime.title.romaji;
        const eps = anime.episodes || '?';
        const card = document.createElement('div');
        card.className = 'game-card';
        card.style.cursor = 'pointer';
        card.onclick = () => selectAnime(anime.id, title, anime.episodes);

        card.innerHTML = `
            <img src="${anime.coverImage.large}" alt="${title}">
            <div>
              <h3>${title}</h3>
              <span style="font-size:11px; color:#4a5640;">${eps} Episodes</span>
            </div>
            <button style="margin-top:6px; width:100%;">WATCH</button>
        `;
        grid.appendChild(card);
    });
}

window.selectAnime = function(id, title, eps, startEp = 1) {
    currentAnimeId = id;
    currentAnimeTitle = title;
    totalEpisodes = eps || 12;

    document.getElementById('resultsGrid').style.display = 'none';
    document.getElementById('playerView').style.display = 'block';
    document.getElementById('watchTitle').innerText = title;
    document.getElementById('episodeCountBadge').innerText = `${totalEpisodes} EPS`;

    buildEpisodeList();
    playEpisode(startEp);
    window.scrollTo({ top: document.getElementById('anime-section').offsetTop - 20, behavior: 'smooth' });
}

function buildEpisodeList() {
    const episodeGrid = document.getElementById('episodeGrid');
    episodeGrid.innerHTML = '';
    const limit = Math.min(totalEpisodes, 1500);

    for (let i = 1; i <= limit; i++) {
        const btn = document.createElement('button');
        btn.id = `ep-btn-${i}`;
        btn.innerText = `EP ${i}`;
        btn.onclick = () => playEpisode(i);
        episodeGrid.appendChild(btn);
    }
}

function getEmbedUrl(source, id, ep) {
    switch(source) {
        case 'megaplay_sub': return `https://megaplay.buzz/stream/ani/${id}/${ep}/sub`;
        case 'megaplay_dub': return `https://megaplay.buzz/stream/ani/${id}/${ep}/dub`;
        default: return `https://megaplay.buzz/stream/ani/${id}/${ep}/sub`;
    }
}

function setSource(srcKey, btnEl) {
    currentSource = srcKey;
    document.querySelectorAll('.provider-btn').forEach(b => b.classList.remove('active'));
    btnEl.classList.add('active');
    playEpisode(currentEp);
}

function playEpisode(epNum) {
    currentEp = epNum;
    document.querySelectorAll('#episodeGrid button').forEach(b => {
        b.style.background = '#e3e9d3';
        b.style.color = 'var(--ink)';
    });

    const activeBtn = document.getElementById(`ep-btn-${epNum}`);
    if(activeBtn) {
        activeBtn.style.background = 'var(--green)';
        activeBtn.style.color = 'var(--cream)';
    }

    document.getElementById('videoPlayer').src = getEmbedUrl(currentSource, currentAnimeId, epNum);
}

function goBack() {
    document.getElementById('playerView').style.display = 'none';
    document.getElementById('resultsGrid').style.display = 'grid';
    document.getElementById('videoPlayer').src = '';
}

// Trigger initial load
loadRecommended();
