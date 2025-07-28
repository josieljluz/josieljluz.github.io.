# playlists.py
import os
import requests
from hashlib import md5
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('playlists_download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configurações
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT_DIR = os.getcwd()  # Pasta raiz do repositório
TIMEOUT = 20  # Aumentado para conexões lentas
RETRIES = 3
MAX_WORKERS = 5

def validate_url(url):
    """Valida se a URL é válida."""
    if not url.startswith(("http://", "https://")):
        return False
    # Verificação adicional de URL
    return True if '.' in url.split('//')[1] else False

def download_file(url, filename, retries=RETRIES):
    """Baixa um arquivo diretamente na pasta raiz com tratamento robusto."""
    save_path = os.path.join(OUTPUT_DIR, filename)
    temp_path = os.path.join(OUTPUT_DIR, f"temp_{filename}")
    
    if not validate_url(url):
        logger.error(f"URL inválida: {url}")
        return False

    for attempt in range(retries):
        try:
            logger.info(f"Tentativa {attempt + 1}/{retries} para {filename}")
            
            # Baixa para um arquivo temporário primeiro
            with requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True) as response:
                response.raise_for_status()
                
                with open(temp_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
            
            # Verifica se o arquivo temporário é válido
            if os.path.getsize(temp_path) > 1024:  # Mínimo 1KB
                # Verificação específica para arquivos gzip
                if filename.endswith('.gz'):
                    try:
                        with gzip.open(temp_path, 'rb') as test_gz:
                            test_gz.read(100)  # Testa leitura parcial
                    except Exception as e:
                        logger.error(f"Arquivo gzip inválido: {e}")
                        os.remove(temp_path)
                        continue
                
                # Move o arquivo temporário para o destino final
                if os.path.exists(save_path):
                    os.remove(save_path)
                os.rename(temp_path, save_path)
                
                # Gera hash MD5
                with open(save_path, 'rb') as f:
                    file_hash = md5(f.read()).hexdigest()
                
                logger.info(f"Download concluído: {filename} ({os.path.getsize(save_path)/1024:.2f} KB) | MD5: {file_hash}")
                return True
            else:
                logger.error(f"Arquivo muito pequeno ou vazio: {temp_path}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
        except Exception as e:
            logger.error(f"Erro ao baixar {filename}: {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    return False

def cleanup_old_files():
    """Remove arquivos antigos antes de baixar novos."""
    logger.info("Limpando arquivos antigos...")
    
    extensions = ('.m3u', '.M3U', '.gz', '.xml.gz')
    removed_count = 0
    
    for filename in os.listdir(OUTPUT_DIR):
        if filename.lower().endswith(extensions):
            try:
                os.remove(os.path.join(OUTPUT_DIR, filename))
                logger.debug(f"Removido: {filename}")
                removed_count += 1
            except Exception as e:
                logger.error(f"Erro ao remover {filename}: {e}")
    
    logger.info(f"Total de arquivos antigos removidos: {removed_count}")

def get_files_to_download():
    """Retorna os arquivos para download com URLs atualizadas."""
    return {
        "m3u": {
            "epgbrasil.M3U": "http://m3u4u.com/m3u/3wk1y24kx7uzdevxygz7",
            "epgbrasilportugal.M3U": "http://m3u4u.com/m3u/782dyqdrqkh1xegen4zp",			  
            "epgportugal.M3U": "http://m3u4u.com/m3u/jq2zy9epr3bwxmgwyxr5",
            "PiauiTV.M3U": "https://gitlab.com/josieljefferson12/playlists/-/raw/main/PiauiTV.m3u",
            "m3u_proton.M3U": "https://gitlab.com/josieljefferson12/playlists/-/raw/main/m3u4u_proton.me.m3u",
            "playlist.M3U": "https://gitlab.com/josieljefferson12/playlists/-/raw/main/playlist.m3u",
            "playlists.M3U": "https://gitlab.com/josielluz/playlists/-/raw/main/playlists.m3u",
            "pornstars.M3U": "https://gitlab.com/josieljefferson12/playlists/-/raw/main/pornstars.m3u"
        },
        "gz": {
            "epgbrasil.xml.gz": "http://m3u4u.com/epg/3wk1y24kx7uzdevxygz7",
            "epgbrasilportugal.xml.gz": "http://m3u4u.com/epg/782dyqdrqkh1xegen4zp",
            "epgportugal.xml.gz": "http://m3u4u.com/epg/jq2zy9epr3bwxmgwyxr5"
        }
    }

def download_all_files():
    """Processa todos os downloads em paralelo."""
    files_to_download = get_files_to_download()
    logger.info("Iniciando downloads automáticos...")
    
    start_time = datetime.now()
    success_count = 0
    total_files = sum(len(files) for files in files_to_download.values())
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for ext, files in files_to_download.items():
            for filename, url in files.items():
                future = executor.submit(download_file, url.strip(), filename)
                futures[future] = filename
        
        for future in as_completed(futures):
            filename = futures[future]
            try:
                if future.result():
                    success_count += 1
                else:
                    logger.error(f"Falha no download: {filename}")
            except Exception as e:
                logger.error(f"Erro durante download de {filename}: {e}")
    
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"Processo concluído. {success_count}/{total_files} arquivos baixados com sucesso em {elapsed:.2f} segundos.")
    return success_count == total_files

def main():
    """Função principal para execução automática."""
    logger.info("\n" + "="*60)
    logger.info(f"Iniciando atualização automática - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60 + "\n")
    
    # Limpa arquivos antigos
    cleanup_old_files()
    
    # Executa downloads
    success = download_all_files()
    
    # Log final
    logger.info("\nArquivos na pasta raiz após atualização:")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if any(f.lower().endswith(ext) for ext in ['.m3u', '.m3u', '.gz', '.xml.gz']):
            size_kb = os.path.getsize(os.path.join(OUTPUT_DIR, f)) / 1024
            logger.info(f"- {f.ljust(25)} {size_kb:8.2f} KB")
    
    logger.info("\n" + "="*60)
    logger.info("Atualização automática concluída")
    logger.info("="*60 + "\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())