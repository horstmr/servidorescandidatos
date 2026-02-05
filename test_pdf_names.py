from cross_reference_multi import *
import os

pdf_file = "ed_1_lst_homologacao_1_15.pdf"
filepath = os.path.join(BASE_DIR, pdf_file)
raw_text = extract_text_from_pdf(filepath)
norm_text = normalize(raw_text)

print("Primeiras 2000 caracteres do texto normalizado do PDF:")
print(norm_text[:2000])
print("\n" + "="*80)
print("Procurando por padrões de nomes...")

# Procurar linhas que parecem nomes (maiúsculas, múltiplas palavras)
lines = raw_text.split('\n')
name_lines = [line.strip() for line in lines if len(line.strip()) > 10 and line.strip().isupper() and ' ' in line.strip()]

print(f"\nEncontradas {len(name_lines)} linhas que parecem nomes:")
for i, line in enumerate(name_lines[:20]):
    print(f"  {i+1}. {line}")
