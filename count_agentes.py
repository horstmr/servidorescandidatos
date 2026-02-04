import csv

csv_path = r"d:/Google Drive/Meu Drive/ACAPE/CONCURSO 2026/fepese_pci_perito_pdfs/servidores_concurso_encontrados.csv"

def count_agentes():
    unique_agentes = set()
    total_entries = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                cargo = row['Cargo'].upper()
                nome = row['Nome'].strip()
                
                if 'AGENTE' in cargo:
                    unique_agentes.add(nome)
                    total_entries += 1
                    
        print(f"Total de entradas de Agentes encontradas: {total_entries}")
        print(f"Total de Agentes únicos na lista: {len(unique_agentes)}")
        
    except FileNotFoundError:
        print("Arquivo CSV não encontrado.")

if __name__ == "__main__":
    count_agentes()
