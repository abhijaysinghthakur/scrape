document.addEventListener('DOMContentLoaded', () => {
    const manualAddForm = document.getElementById('add-competitor-form');
    const manualUrlInput = document.getElementById('competitor-url');
    const competitorListDiv = document.getElementById('competitor-list');
    const suggestForm = document.getElementById('suggest-form');
    const userUrlInput = document.getElementById('user-url');
    const suggestionsLoader = document.getElementById('suggestions-loader');
    const suggestionsResultDiv = document.getElementById('suggestions-result');

    // --- Core Functions ---
    function renderCompetitors(competitors) {
        competitorListDiv.innerHTML = '';
        if (competitors.length === 0) {
            competitorListDiv.innerHTML = '<p>No competitors being tracked yet.</p>';
        } else {
            competitors.forEach(competitor => {
                const item = document.createElement('div');
                item.className = 'competitor-item';
                item.innerHTML = `
                    <div class="competitor-info"><span>${competitor.url}</span></div>
                    <div class="actions">
                        <a href="/scan-result/${competitor.id}" class="action-btn scan-btn">Scan Now</a>
                        <button class="action-btn delete-btn" data-id="${competitor.id}">Delete</button>
                    </div>`;
                competitorListDiv.appendChild(item);
            });
        }
    }

    async function fetchCompetitors() {
        const response = await fetch('/api/competitors', { cache: 'no-store' });
        const competitors = await response.json();
        renderCompetitors(competitors);
    }

    async function addCompetitor(url) {
        await fetch('/api/competitors', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url }),
        });
        fetchCompetitors(); // Refresh the main list
    }

    // --- Event Listeners ---
    manualAddForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const url = manualUrlInput.value.trim();
        if (url) {
            addCompetitor(url);
            manualUrlInput.value = '';
        }
    });

    suggestForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const userUrl = userUrlInput.value.trim();
        if (!userUrl) return;

        suggestionsLoader.style.display = 'block';
        suggestionsResultDiv.innerHTML = '';

        try {
            const response = await fetch('/api/suggest-competitors', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: userUrl }),
            });
            const data = await response.json();
            
            if (data.error) {
                suggestionsResultDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
            } else {
                let listHtml = '<ul>';
                data.suggestions.forEach(url => {
                    listHtml += `<li><span>${url}</span><button class="action-btn add-suggestion-btn" data-url="${url}">+ Add</button></li>`;
                });
                listHtml += '</ul>';
                suggestionsResultDiv.innerHTML = listHtml;
            }
        } catch (error) {
            suggestionsResultDiv.innerHTML = `<p style="color: red;">An error occurred.</p>`;
        } finally {
            suggestionsLoader.style.display = 'none';
        }
    });

    competitorListDiv.addEventListener('click', async (event) => {
        if (event.target.classList.contains('delete-btn')) {
            if (confirm('Are you sure?')) {
                await fetch(`/api/competitors/${event.target.dataset.id}`, { method: 'DELETE' });
                fetchCompetitors();
            }
        }
    });

    suggestionsResultDiv.addEventListener('click', async (event) => {
        if (event.target.classList.contains('add-suggestion-btn')) {
            const urlToAdd = event.target.dataset.url;
            addCompetitor(urlToAdd);
            event.target.textContent = 'Added!';
            event.target.disabled = true;
        }
    });

    // --- Initial Load ---
    fetchCompetitors();
});