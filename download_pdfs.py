import re
import os
import urllib.request
import urllib.parse
import html

file_path = "d:/Google Drive/Meu Drive/ACAPE/CONCURSO 2026/fepese_pci_perito_pdfs/page_content.html"
output_dir = "d:/Google Drive/Meu Drive/ACAPE/CONCURSO 2026/fepese_pci_perito_pdfs"
base_url = "https://2025pciperito.fepese.org.br/"

# Read HTML
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find hrefs
raw_links = re.findall(r'href=["\'](.*?)["\']', content)

unique_urls = set()

print("Parsing links...")
for link in raw_links:
    clean_link = html.unescape(link.strip())
    
    if ('go=download' in clean_link) or clean_link.lower().endswith('.pdf'):
        if clean_link.startswith('http'):
            full_url = clean_link
        else:
            if clean_link.startswith('/'):
                full_url = "https://2025pciperito.fepese.org.br" + clean_link
            else:
                full_url = "https://2025pciperito.fepese.org.br/" + clean_link
        
        unique_urls.add(full_url)

print(f"Found {len(unique_urls)} unique download links.")

# Download
for i, url in enumerate(unique_urls):
    try:
        # Try to extract filename from URL (query param 'arquivo')
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        filename = f"document_{i}.pdf" # Default
        if 'arquivo' in params:
            filename = params['arquivo'][0]
        elif url.lower().endswith('.pdf'):
            filename = os.path.basename(parsed.path)
            
        # Clean filename
        filename = re.sub(r'[\\/*?:"<>|]', "", filename)
        save_path = os.path.join(output_dir, filename)
        
        print(f"Downloading: {filename} from {url}")
        
        # User agent might be needed if they block scripts, but let's try simple first
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        
        with urllib.request.urlopen(req) as response, open(save_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
            
        print("Done.")
        
    except Exception as e:
        print(f"Failed to download {url}: {e}")
