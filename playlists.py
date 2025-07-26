import os
import requests
from hashlib import md5
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT_DIR = os.getcwd()
TIMEOUT = 10
RETRIES = 3
MAX_WORKERS = 5

def validate_url(url):
    return url.startswith(("http://", "https://"))

def download_file(url, save_path, retries=RETRIES):
    if not validate_url(url):
        logger.error(f"URL inválida: {url}")
        return False

    for attempt in range(retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de {retries}: Baixando de: {url}")
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            
            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    file.write(response.content)

                if os.path.getsize(save_path) > 0:
                    logger.info(f"Sucesso: {save_path} ({os.path.getsize(save_path)} bytes)")
                    with open(save_path, 'rb') as file:
                        file_hash = md5(file.read()).hexdigest()
                    logger.info(f"Hash MD5: {file_hash}")
                    return True
                else:
                    logger.error(f"Erro: Arquivo vazio ou corrompido: {save_path}")
            else:
                logger.error(f"Falha ao baixar {url}. Código: {response.status_code}")
        except Exception as e:
            logger.error(f"Erro ao baixar {url}: {e}")
    return False

def main():
    logger.info(f"Diretório de trabalho: {OUTPUT_DIR}")
    logger.info("Removendo arquivos antigos...")
    
    target_files = ["epgbrasil.m3u", "epgbrasil.xml.gz", "epgbrasilportugal.m3u", "epgbrasilportugal.xml.gz", "epgportugal.m3u", "epgportugal.xml.gz", "m3u@proton.me.m3u", "PiauiTV.m3u", "playlist.m3u", "playlists.m3u", "pornstars.m3u"]
    
    for filename in target_files:
        file_path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Removido: {filename}")
            except Exception as e:
                logger.error(f"Erro ao remover {filename}: {e}")

    files_to_download = {
        "m3u": {
            "epgbrasil.m3u": "http://m3u4u.com/m3u/3wk1y24kx7uzdevxygz7",
            "epgbrasilportugal.m3u": "http://m3u4u.com/m3u/782dyqdrqkh1xegen4zp",			  
            "epgportugal.m3u": "http://m3u4u.com/m3u/jq2zy9epr3bwxmgwyxr5",
            "PiauiTV.m3u": "https://gitlab.com/josieljefferson12/playlists/-/raw/main/PiauiTV.m3u",
            "m3u@proton.me.m3u": "https://gitlab.com/josieljefferson12/playlists/-/raw/main/m3u4u_proton.me.m3u",
            "playlist.m3u": "https://gitlab.com/josieljefferson12/playlists/-/raw/main/playlist.m3u",
            "playlists.m3u": "https://gitlab.com/josielluz/playlists/-/raw/main/playlists.m3u",
            "pornstars.m3u": "https://gitlab.com/josieljefferson12/playlists/-/raw/main/pornstars.m3u"
        },
        "xml.gz": {
            "epgbrasil.xml.gz": "http://m3u4u.com/epg/3wk1y24kx7uzdevxygz7",
            "epgbrasilportugal.xml.gz": "http://m3u4u.com/epg/782dyqdrqkh1xegen4zp",
            "epgportugal.xml.gz": "http://m3u4u.com/epg/jq2zy9epr3bwxmgwyxr5"
        }
    }

    logger.info("Iniciando downloads...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for ext, files in files_to_download.items():
            for filename, url in files.items():
                save_path = os.path.join(OUTPUT_DIR, filename)
                futures.append(executor.submit(download_file, url.strip(), save_path))

        for future in as_completed(futures):
            if not future.result():
                logger.error("Erro em um dos downloads.")

    logger.info("Downloads concluídos.")

if __name__ == "__main__":
    main()