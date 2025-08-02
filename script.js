document.addEventListener('DOMContentLoaded', function() {
    // Set current year in footer
    document.getElementById('current-year').textContent = new Date().getFullYear();
    
    // Set last update date/time
    updateLastUpdateTime();
    
    // Load metadata and files
    loadFilesMetadata();
});

function updateLastUpdateTime() {
    const now = new Date();
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    document.getElementById('last-update').textContent = now.toLocaleDateString('pt-BR', options);
}

async function loadFilesMetadata() {
    try {
        const response = await fetch('files_metadata.json');
        if (!response.ok) {
            throw new Error('Erro ao carregar metadados');
        }
        const data = await response.json();
        displayFiles(data.files);
        displayMetadata(data.metadata);
    } catch (error) {
        console.error('Error loading metadata:', error);
        displayError();
    }
}

function displayFiles(files) {
    const m3uContainer = document.getElementById('m3u-files');
    const epgContainer = document.getElementById('epg-files');
    
    // Clear loading states
    m3uContainer.innerHTML = '';
    epgContainer.innerHTML = '';
    
    let hasM3U = false;
    let hasEPG = false;
    
    files.forEach(file => {
        const card = document.createElement('div');
        card.className = 'file-card';
        
        const icon = file.type === 'm3u' ? '<i class="fas fa-list"></i>' : '<i class="fas fa-calendar-alt"></i>';
        const fileType = file.type === 'm3u' ? 'Playlist M3U' : 'Guia EPG';
        
        card.innerHTML = `
            <h3>${icon} ${file.name}</h3>
            <p class="file-type">${fileType}</p>
            <p class="file-size">Tamanho: ${formatFileSize(file.size)}</p>
            <p class="file-updated">Atualizado: ${new Date(file.updated).toLocaleString('pt-BR')}</p>
            <a href="${file.name}" download>Baixar</a>
        `;
        
        if (file.type === 'm3u') {
            m3uContainer.appendChild(card);
            hasM3U = true;
        } else {
            epgContainer.appendChild(card);
            hasEPG = true;
        }
    });
    
    if (!hasM3U) {
        m3uContainer.innerHTML = '<div class="error-message">Nenhuma playlist M3U disponível no momento.</div>';
    }
    
    if (!hasEPG) {
        epgContainer.innerHTML = '<div class="error-message">Nenhum guia EPG disponível no momento.</div>';
    }
}

function displayMetadata(metadata) {
    const infoContainer = document.getElementById('metadata-info');
    const nextUpdate = new Date(metadata.next_update);
    
    infoContainer.innerHTML = `
        <p><strong>Total de arquivos:</strong> ${metadata.total_files} (${metadata.m3u_count} M3U, ${metadata.epg_count} EPG)</p>
        <p><strong>Próxima atualização:</strong> ${nextUpdate.toLocaleString('pt-BR')}</p>
    `;
}

function displayError() {
    const m3uContainer = document.getElementById('m3u-files');
    const epgContainer = document.getElementById('epg-files');
    
    m3uContainer.innerHTML = '<div class="error-message">Erro ao carregar as playlists. Por favor, tente recarregar a página.</div>';
    epgContainer.innerHTML = '<div class="error-message">Erro ao carregar os guias EPG. Por favor, tente recarregar a página.</div>';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
}