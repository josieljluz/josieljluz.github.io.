# playlists.py
import os
import requests
from hashlib import md5
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import shutil

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT_DIR = os.getcwd()  # Pasta raiz do repositório
TIMEOUT = 15
RETRIES = 3
MAX_WORKERS = 5

def validate_url(url):
    """Valida se a URL é válida."""
    return url.startswith(("http://", "https://"))

def download_file(url, filename, retries=RETRIES):
    """Baixa um arquivo diretamente na pasta raiz."""
    save_path = os.path.join(OUTPUT_DIR, filename)
    
    if not validate_url(url):
        logger.error(f"URL inválida: {url}")
        return False

    for attempt in range(retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de {retries}: Baixando {filename} de: {url}")
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            
            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    file.write(response.content)

                # Verifica se o arquivo foi salvo corretamente
                if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                    file_size = os.path.getsize(save_path)
                    logger.info(f"Sucesso: {filename} ({file_size} bytes) salvo em {save_path}")
                    
                    # Verifica integridade do arquivo
                    try:
                        with open(save_path, 'rb') as file:
                            file_hash = md5(file.read()).hexdigest()
                        logger.info(f"Hash MD5 de {filename}: {file_hash}")
                        
                        # Verificação adicional para arquivos .gz
                        if filename.endswith('.gz'):
                            with gzip.open(save_path, 'rb') as f_in:
                                f_in.read(100)  # Testa leitura parcial
                            logger.info(f"Arquivo {filename} validado como gzip válido")
                            
                        return True
                    except Exception as e:
                        logger.error(f"Erro ao verificar arquivo {filename}: {e}")
                        os.remove(save_path)
                        continue
                else:
                    logger.error(f"Erro: Arquivo {filename} vazio ou não foi salvo corretamente")
                    if os.path.exists(save_path):
                        os.remove(save_path)
            else:
                logger.error(f"Falha ao baixar {filename}. Código HTTP: {response.status_code}")
        except Exception as e:
            logger.error(f"Erro ao baixar {filename}: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)
    return False

def cleanup_old_files():
    """Remove arquivos antigos antes de baixar novos."""
    logger.info("Limpando arquivos antigos na pasta raiz...")
    
    extensions = ['.m3u', '.M3U', '.gz', '.xml.gz']
    for filename in os.listdir(OUTPUT_DIR):
        if any(filename.endswith(ext) for ext in extensions):
            try:
                os.remove(os.path.join(OUTPUT_DIR, filename))
                logger.info(f"Removido: {filename}")
            except Exception as e:
                logger.error(f"Erro ao remover {filename}: {e}")

def get_files_to_download():
    """Retorna os arquivos para download com URLs atualizadas."""
    return {
        "m3u": {
            "epgbrasil.m3u": "http://m3u4u.com/m3u/3wk1y24kx7uzdevxygz7",
            "epgbrasilportugal.m3u": "http://m3u4u.com/m3u/782dyqdrqkh1xegen4zp",			  
            "epgportugal.m3u": "http://m3u4u.com/m3u/jq2zy9epr3bwxmgwyxr5",
            "PiauiTV.m3u": "https://gitlab.com/josieljefferson12/playlists/-/raw/main/PiauiTV.m3u",
            "m3u_proton.m3u": "https://gitlab.com/josieljefferson12/playlists/-/raw/main/m3u4u_proton.me.m3u",
            "playlist.m3u": "https://gitlab.com/josieljefferson12/playlists/-/raw/main/playlist.m3u",
            "playlists.m3u": "https://gitlab.com/josielluz/playlists/-/raw/main/playlists.m3u",
            "pornstars.m3u": "https://gitlab.com/josieljefferson12/playlists/-/raw/main/pornstars.m3u"
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
    logger.info("Iniciando downloads na pasta raiz...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for ext, files in files_to_download.items():
            for filename, url in files.items():
                futures.append(executor.submit(download_file, url.strip(), filename))

        success = 0
        for future in as_completed(futures):
            if future.result():
                success += 1
            else:
                logger.error("Falha em um dos downloads")
        
        logger.info(f"Download concluído. {success}/{len(futures)} arquivos baixados com sucesso.")

def main():
    """Função principal."""
    logger.info(f"Download iniciado. Pasta de destino: {OUTPUT_DIR}")
    
    # Limpa arquivos antigos
    cleanup_old_files()
    
    # Baixa todos os arquivos
    download_all_files()
    
    # Lista arquivos baixados
    logger.info("Arquivos na pasta raiz após download:")
    for f in os.listdir(OUTPUT_DIR):
        if any(f.endswith(ext) for ext in ['.m3u', '.M3U', '.gz', '.xml.gz']):
            logger.info(f"- {f} ({os.path.getsize(os.path.join(OUTPUT_DIR, f))} bytes)")

if __name__ == "__main__":
    main()