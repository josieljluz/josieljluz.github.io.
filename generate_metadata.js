const fs = require('fs');
const path = require('path');

// Lista de arquivos esperados
const expectedFiles = [
    'epgbrasil.m3u',
    'epgbrasilportugal.m3u',
    'epgportugal.m3u',
    'PiauiTV.m3u',
    'm3u@proton.me.m3u',
    'playlist.m3u',
    'playlists.m3u',
    'pornstars.m3u',
    'epgbrasil.xml.gz',
    'epgbrasilportugal.xml.gz',
    'epgportugal.xml.gz'
];

// Gerar metadados
function generateMetadata() {
    const files = [];
    let m3uCount = 0;
    let epgCount = 0;

    expectedFiles.forEach(filename => {
        try {
            const filePath = path.join(__dirname, filename);
            if (fs.existsSync(filePath)) {
                const stats = fs.statSync(filePath);
                const fileType = filename.endsWith('.m3u') ? 'm3u' : 'epg';
                
                if (fileType === 'm3u') m3uCount++;
                if (fileType === 'epg') epgCount++;

                files.push({
                    name: filename,
                    type: fileType,
                    size: stats.size,
                    updated: stats.mtime.toISOString()
                });
            }
        } catch (error) {
            console.error(`Error processing file ${filename}:`, error);
        }
    });

    // Calcular próxima atualização (daqui a 24 horas)
    const nextUpdate = new Date();
    nextUpdate.setHours(nextUpdate.getHours() + 24);

    const metadata = {
        generated_at: new Date().toISOString(),
        next_update: nextUpdate.toISOString(),
        m3u_count: m3uCount,
        epg_count: epgCount,
        total_files: files.length
    };

    const output = {
        metadata,
        files
    };

    fs.writeFileSync('files_metadata.json', JSON.stringify(output, null, 2));
    console.log('Metadata generated successfully!');
}

generateMetadata();