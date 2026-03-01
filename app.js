// ============================================
// Majalah Bitcoin - Main Application Script
// ============================================

/**
 * Load news data from JSON file
 */
async function loadNews() {
    try {
        const response = await fetch('data/news.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error loading news:', error);
        return [];
    }
}

/**
 * Format date to Malay format
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Intl.DateTimeFormat('ms-MY', options).format(date);
}

/**
 * Create a news card element
 */
function createNewsCard(article) {
    const card = document.createElement('div');
    card.className = 'news-card';
    card.innerHTML = `
        <img src="${article.image}" alt="${article.title}" class="news-card-image" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 200%22%3E%3Crect fill=%22%23f5f5f5%22 width=%22400%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 font-size=%2224%22 fill=%22%23999%22 text-anchor=%22middle%22 dominant-baseline=%22middle%22%3EBitcoin News%3C/text%3E%3C/svg%3E'">
        <div class="news-card-content">
            <div class="news-card-date">${formatDate(article.date)}</div>
            <h3 class="news-card-title">${article.title}</h3>
            <p class="news-card-summary">${article.summary}</p>
            <div class="news-card-footer">
                <span class="news-card-author">${article.author}</span>
                <a href="berita.html?id=${article.id}" class="read-more">Baca →</a>
            </div>
        </div>
    `;
    
    card.addEventListener('click', () => {
        window.location.href = `berita.html?id=${article.id}`;
    });
    
    return card;
}

/**
 * Render news grid on index page
 */
async function renderNewsGrid() {
    const container = document.getElementById('newsContainer');
    if (!container) return;

    const news = await loadNews();
    
    if (news.length === 0) {
        container.innerHTML = '<p class="loading">Tiada berita tersedia pada masa ini.</p>';
        return;
    }

    container.innerHTML = '';
    news.forEach(article => {
        container.appendChild(createNewsCard(article));
    });
}

/**
 * Get URL parameters
 */
function getUrlParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

/**
 * Render article detail page
 */
async function renderArticleDetail() {
    const container = document.getElementById('articleContainer');
    const relatedContainer = document.getElementById('relatedContainer');
    
    if (!container) return;

    const articleId = getUrlParam('id');
    const news = await loadNews();
    const article = news.find(a => a.id === articleId);

    if (!article) {
        container.innerHTML = '<p class="loading">Artikel tidak ditemukan.</p>';
        return;
    }

    // Render main article
    container.innerHTML = `
        <article>
            <div class="article-header">
                <div class="article-meta">
                    <div class="article-meta-item">
                        <span>📅 ${formatDate(article.date)}</span>
                    </div>
                    <div class="article-meta-item">
                        <span>✍️ ${article.author}</span>
                    </div>
                </div>
                <h1 class="article-title">${article.title}</h1>
            </div>
            <img src="${article.image}" alt="${article.title}" class="article-image" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 800 400%22%3E%3Crect fill=%22%23f5f5f5%22 width=%22800%22 height=%22400%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 font-size=%2232%22 fill=%22%23999%22 text-anchor=%22middle%22 dominant-baseline=%22middle%22%3EBitcoin News%3C/text%3E%3C/svg%3E'">
            <div class="article-content">
                ${article.content}
            </div>
            <div class="article-source">
                <strong>Sumber Asal:</strong> <a href="${article.source_url}" target="_blank" rel="noopener noreferrer">${article.source_url}</a>
            </div>
        </article>
    `;

    // Render related articles
    if (relatedContainer) {
        const related = news.filter(a => a.id !== articleId).slice(0, 3);
        if (related.length > 0) {
            relatedContainer.innerHTML = related.map(a => `
                <a href="berita.html?id=${a.id}" class="related-card">
                    <div class="related-card-title">${a.title}</div>
                    <div class="related-card-date">${formatDate(a.date)}</div>
                </a>
            `).join('');
        }
    }
}

/**
 * Initialize page based on current location
 */
document.addEventListener('DOMContentLoaded', () => {
    const isDetailPage = window.location.pathname.includes('berita.html');
    
    if (isDetailPage) {
        renderArticleDetail();
    } else {
        renderNewsGrid();
    }
});
