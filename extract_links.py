import re
import os

file_path = "d:/Google Drive/Meu Drive/ACAPE/CONCURSO 2026/fepese_pci_perito_pdfs/page_content.html"
base_url = "https://2025pciperito.fepese.org.br/"

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Naive regex to find hrefs
links = re.findall(r'href=["\'](.*?)["\']', content)

found_urls = []
for link in links:
    # Decode HTML entities if necessary using html module, but simple strings first
    clean_link = link.strip()
    
    # Heuristic: verify if it is likely a file download or mentions .pdf
    if ('go=download' in clean_link) or clean_link.lower().endswith('.pdf'):
        if clean_link.startswith('http'):
            full_url = clean_link
        else:
            if clean_link.startswith('/'):
                # base url contains path component? No, pure domain + path
                # https://2025pciperito.fepese.org.br/
                root_url = "https://2025pciperito.fepese.org.br" 
                full_url = root_url + clean_link
            else:
                full_url = "https://2025pciperito.fepese.org.br/" + clean_link
        
        # fix double slash possibility if not http://
        found_urls.append(full_url)

print(f"Extraction complete. Found {len(found_urls)} potential PDF links.")
for u in found_urls:
    print(u)
