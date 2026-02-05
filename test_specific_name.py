from cross_reference_multi import *
import os

# Pegar um nome do PDF
pdf_file = "ed_1_lst_homologacao_1_15.pdf"
filepath = os.path.join(BASE_DIR, pdf_file)
raw_text = extract_text_from_pdf(filepath)
norm_text = normalize(raw_text)

# Extrair nomes do PDF (linhas que parecem nomes após o cabeçalho)
lines = raw_text.split('\n')
pdf_names = []
for line in lines:
    line = line.strip()
    # Procurar padrão: número número NOME MAIUSCULO CIDADE
    parts = line.split()
    if len(parts) >= 4:
        # Tentar identificar nomes (partes que são todas maiúsculas e têm mais de 2 caracteres)
        name_parts = []
        for part in parts[2:]:  # Pular número de inscrição e número sequencial
            if part.isupper() and len(part) > 2 and part.isalpha():
                name_parts.append(part)
            elif name_parts:  # Se já começamos a coletar nome e encontramos algo diferente, para
                break
        if len(name_parts) >= 2:  # Pelo menos nome e sobrenome
            name = ' '.join(name_parts)
            pdf_names.append(name)

print(f"Encontrados {len(pdf_names)} nomes no PDF:")
for i, name in enumerate(pdf_names[:10]):
    print(f"  {i+1}. {name}")

# Normalizar nomes do PDF
pdf_names_norm = [normalize(name) for name in pdf_names[:10]]

# Carregar servidores
print("\nCarregando servidores...")
servidores = load_pr_data() + load_sp_data() + load_ms_data()
servidores_dict = {serv['name_norm']: serv for serv in servidores}

print(f"Total servidores: {len(servidores_dict)}")

# Procurar matches
print("\nProcurando matches...")
matches_found = []
for pdf_name_norm in pdf_names_norm:
    if pdf_name_norm in servidores_dict:
        serv = servidores_dict[pdf_name_norm]
        matches_found.append((pdf_name_norm, serv['Nome'], serv['ESTADO']))
        print(f"  MATCH: {pdf_name_norm} -> {serv['Nome']} ({serv['ESTADO']})")

if not matches_found:
    print("Nenhum match encontrado.")
    print("\nTestando busca parcial...")
    # Testar busca parcial (primeiro nome + sobrenome)
    for pdf_name_norm in pdf_names_norm[:5]:
        # Pegar primeiras duas palavras
        words = pdf_name_norm.split()
        if len(words) >= 2:
            partial = ' '.join(words[:2])
            for serv_norm, serv in servidores_dict.items():
                if partial in serv_norm or serv_norm.startswith(partial):
                    print(f"  Match parcial: {partial} -> {serv['Nome']} ({serv['ESTADO']})")
                    break
