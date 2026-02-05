from cross_reference_multi import *
import os

# Carregar alguns servidores
print("Carregando servidores...")
servidores = load_pr_data()[:1000] + load_sp_data()[:1000] + load_ms_data()[:1000]  # Apenas primeiros 1000 de cada
print(f"Servidores para teste: {len(servidores)}")

# Normalizar
servidores_por_nome = {}
for serv in servidores:
    name_norm = serv['name_norm']
    if name_norm not in servidores_por_nome:
        servidores_por_nome[name_norm] = []
    servidores_por_nome[name_norm].append(serv)

servidores_validos = []
for name_norm, grupo in servidores_por_nome.items():
    if len(grupo) == 1:
        servidores_validos.extend(grupo)
    else:
        nomes_originais_norm = [normalize(serv['Nome']) for serv in grupo]
        if all(nome == name_norm for nome in nomes_originais_norm):
            servidores_validos.extend(grupo)

print(f"Servidores válidos: {len(servidores_validos)}")

# Testar em um PDF
pdf_files = [f for f in os.listdir(BASE_DIR) if f.lower().endswith('.pdf')]
if pdf_files:
    test_pdf = pdf_files[0]
    print(f"\nTestando no PDF: {test_pdf}")
    filepath = os.path.join(BASE_DIR, test_pdf)
    raw_text = extract_text_from_pdf(filepath)
    norm_text = normalize(raw_text)
    cargo_concurso = extract_cargo_concurso(raw_text)
    
    print(f"Cargo encontrado: {cargo_concurso}")
    print(f"Tamanho do texto normalizado: {len(norm_text)} caracteres")
    
    # Testar primeiros 10 servidores
    matches = []
    for serv in servidores_validos[:10]:
        name_n = serv['name_norm']
        if check_match_strict(name_n, norm_text):
            matches.append(serv['Nome'])
            print(f"  MATCH: {serv['Nome']} ({name_n})")
    
    if not matches:
        print("\nNenhum match encontrado nos primeiros 10 servidores.")
        print("Testando busca simples...")
        # Testar busca simples
        for serv in servidores_validos[:10]:
            name_n = serv['name_norm']
            if name_n in norm_text:
                print(f"  Nome encontrado no texto (busca simples): {serv['Nome']} ({name_n[:50]}...)")
                break
        else:
            print("  Nenhum nome encontrado nem com busca simples.")
