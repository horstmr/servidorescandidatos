import csv
import os
import unicodedata
import pypdf
import sys
import re

# Configuration
csv_path = r"d:/Google Drive/Meu Drive/ACAPE/CONCURSO 2026/ListaServidores04022026185303-6983958f4503d.csv"
pdf_dir = r"d:/Google Drive/Meu Drive/ACAPE/CONCURSO 2026/fepese_pci_perito_pdfs"

def normalize(text):
    if not isinstance(text, str):
        text = str(text)
    # Normalize unicode characters to decompose combined characters (like ç -> c + ,)
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn').upper()

def load_servidores(path):
    servidores = []
    print(f"Loading CSV from {path}...")
    try:
        with open(path, 'r', encoding='latin-1') as f:
            reader = csv.reader(f, delimiter=';')
            try:
                header = next(reader)
            except StopIteration:
                pass 
            
            for row in reader:
                if len(row) > 0:
                    # Row: Nome;CPF;Cargo;OrgaoExercicio;OrgaoOrigem;UnidadeExercicio;Situacao;ValorBruto
                    # Indices: 0, 1, 2, 3, 4, 5, 6, 7
                    servidores.append({
                        'original_row': row,
                        'name_norm': normalize(row[0]),
                        'lotacao': row[5] if len(row) > 5 else "N/A"
                    })
    except UnicodeDecodeError:
         with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader) 
            for row in reader:
                if len(row) > 0:
                    servidores.append({
                        'original_row': row,
                        'name_norm': normalize(row[0]),
                        'lotacao': row[5] if len(row) > 5 else "N/A"
                    })
    print(f"Loaded {len(servidores)} servidores.")
    return servidores

def extract_text_from_pdf(pdf_path):
    text_content = []
    try:
        reader = pypdf.PdfReader(pdf_path)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_content.append(t)
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return "\n".join(text_content)

def extract_cargo_name(text):
    for line in text.splitlines()[:100]: 
        if "Cargo:" in line:
            # Often "Cargo: Perito Oficial Criminal - Informatica"
            return line.split("Cargo:", 1)[1].strip()
    return "Cargo Desconhecido"

def main():
    servidores = load_servidores(csv_path)
    matches = [] 

    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDFs to process.")

    for filename in pdf_files:
        filepath = os.path.join(pdf_dir, filename)
        
        raw_text = extract_text_from_pdf(filepath)
        cargo_concurso = extract_cargo_name(raw_text)
        
        norm_text = normalize(raw_text)
        
        count_in_pdf = 0
        for serv in servidores:
            # Strict match might be safer for simpler names, but these names seem full.
            # Using simple substring inclusion.
            if serv['name_norm'] in norm_text:
                matches.append({
                    'Nome': serv['original_row'][0],
                    'CargoAtual': serv['original_row'][2] if len(serv['original_row']) > 2 else 'N/A',
                    'Lotacao': serv['lotacao'],
                    'CargoConcurso': cargo_concurso,
                    'PDF': filename
                })
                count_in_pdf += 1
        
        if count_in_pdf > 0:
            print(f"  > matches: {count_in_pdf} | PDF: {filename} | Cargo: {cargo_concurso}")

    # Save to CSV
    output_csv = os.path.join(pdf_dir, "servidores_concurso_encontrados_detalhado.csv")
    print(f"Saving matches to {output_csv}...")
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Nome', 'Cargo Atual', 'Lotacao (Unidade Exercicio)', 'Cargo Concurso', 'Arquivo PDF Origem'])
        for m in matches:
            writer.writerow([m['Nome'], m['CargoAtual'], m['Lotacao'], m['CargoConcurso'], m['PDF']])
    print("Done.")

if __name__ == "__main__":
    main()
