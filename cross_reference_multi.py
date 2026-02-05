import os
import pandas as pd
import pypdf
import unicodedata
import json

# Paths
BASE_DIR = r"d:/Google Drive/Meu Drive/ACAPE/CONCURSO 2026/fepese_pci_perito_pdfs"
EXCEL_RS = os.path.join(BASE_DIR, "servidores igp rs.xlsx")  # Pode não existir
CSV_PR = os.path.join(BASE_DIR, "servidores-PR.csv")
CSV_PR_XLSX = os.path.join(BASE_DIR, "servidores-PR.xlsx")
CSV_SP = os.path.join(BASE_DIR, "servidores-SP.csv")
CSV_MS = os.path.join(BASE_DIR, "servidores-MS.csv")

# Outputs
CSV_OUT = os.path.join(BASE_DIR, "servidores_multiestado_encontrados.csv")
HTML_OUT = os.path.join(BASE_DIR, "servidores_multiestado_filter.html")

def normalize(text):
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn').upper()

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

def extract_cargo_concurso(text):
    for line in text.splitlines()[:300]: 
        if "Cargo:" in line:
            parts = line.split("Cargo:", 1)
            if len(parts) > 1:
                return parts[1].strip()
    return "Cargo Desconhecido"

def load_rs_data():
    print("Loading RS Excel...")
    try:
        df = pd.read_excel(EXCEL_RS)
        df.fillna('', inplace=True)
        df = df.drop_duplicates(subset=['Nome'])
        
        records = []
        for _, row in df.iterrows():
            records.append({
                'Nome': row['Nome'],
                'Cargo': row.get('Cargo', ''),
                'name_norm': normalize(row['Nome']),
                'ESTADO': 'RS'
            })
        print(f"Loaded {len(records)} RS servers.")
        return records
    except Exception as e:
        print(f"Error loading RS: {e}")
        return []

def load_pr_data():
    print("Loading PR data...")
    records = []
    
    # Try loading CSV
    try:
        try:
            df = pd.read_csv(CSV_PR, sep=';', encoding='utf-8')
        except:
            df = pd.read_csv(CSV_PR, sep=';', encoding='latin-1')

        df.fillna('', inplace=True)
        
        # Filter active
        if 'dt_fim' in df.columns:
            df['dt_fim'] = df['dt_fim'].astype(str)
            df_active = df[df['dt_fim'] > '2025-01-01']
        else:
            df_active = df
        
        df_active = df_active.drop_duplicates(subset=['nome'])
        
        for _, row in df_active.iterrows():
            records.append({
                'Nome': row['nome'],
                'Cargo': row['cargo'],
                'name_norm': normalize(row['nome']),
                'ESTADO': 'PR'
            })
        print(f"Loaded {len(records)} PR servers from CSV.")
    except Exception as e:
        print(f"Error loading PR CSV: {e}")
    
    # Try loading XLSX if exists
    if os.path.exists(CSV_PR_XLSX):
        try:
            df_xlsx = pd.read_excel(CSV_PR_XLSX)
            df_xlsx.fillna('', inplace=True)
            
            # Identify name column
            name_col = next((c for c in df_xlsx.columns if 'nome' in c.lower() or 'Nome' in c), None)
            cargo_col = next((c for c in df_xlsx.columns if 'cargo' in c.lower() or 'Cargo' in c), None)
            
            if name_col:
                df_xlsx = df_xlsx.drop_duplicates(subset=[name_col])
                for _, row in df_xlsx.iterrows():
                    records.append({
                        'Nome': row[name_col],
                        'Cargo': row[cargo_col] if cargo_col else '',
                        'name_norm': normalize(row[name_col]),
                        'ESTADO': 'PR'
                    })
                print(f"Loaded {len([r for r in records if r['ESTADO'] == 'PR'])} total PR servers (CSV + XLSX).")
        except Exception as e:
            print(f"Error loading PR XLSX: {e}")
    
    return records

def load_sp_data():
    print("Loading SP CSV...")
    try:
        try:
            df = pd.read_csv(CSV_SP, sep=';', encoding='utf-8')
        except:
            df = pd.read_csv(CSV_SP, sep=';', encoding='latin-1')
        
        df.fillna('', inplace=True)
        df = df.drop_duplicates(subset=['NOME'])
        
        records = []
        for _, row in df.iterrows():
            records.append({
                'Nome': row['NOME'],
                'Cargo': row['CARGO'],
                'name_norm': normalize(row['NOME']),
                'ESTADO': 'SP'
            })
        print(f"Loaded {len(records)} SP servers.")
        return records
    except Exception as e:
        print(f"Error loading SP: {e}")
        return []

def load_ms_data():
    print("Loading MS CSV...")
    try:
        # Skip first 2 lines (header info), 3rd line is columns
        try:
            df = pd.read_csv(CSV_MS, sep=';', skiprows=2, encoding='utf-8')
        except:
            df = pd.read_csv(CSV_MS, sep=';', skiprows=2, encoding='latin-1')
            
        df.fillna('', inplace=True)
        # Column 'Nome (Nome Social)' likely contains key
        # We need to find the correct column name for Name and Cargo
        # Let's clean column names logic just in case
        
        # Identify columns
        name_col = next((c for c in df.columns if 'Nome' in c), None)
        cargo_col = next((c for c in df.columns if 'Cargo' in c), None)
        
        if not name_col:
            print("Could not identify Name column for MS.")
            return []

        df = df.drop_duplicates(subset=[name_col])
        
        records = []
        for _, row in df.iterrows():
            records.append({
                'Nome': row[name_col],
                'Cargo': row[cargo_col] if cargo_col else '',
                'name_norm': normalize(row[name_col]),
                'ESTADO': 'MS'
            })
        print(f"Loaded {len(records)} MS servers.")
        return records

    except Exception as e:
        print(f"Error loading MS: {e}")
        return []

import re

STOP_WORDS = set([
    "PERITO", "OFICIAL", "CRIMINAL", "MEDICINA", "LEGAL", "ODONTO", 
    "AUXILIAR", "TECNICO", "FORENSE", "QUIMICA", "ENGENHARIA", 
    "AGENTE", "POLICIA", "DELEGADO", "ESCRIVAO", "INVESTIGADOR", 
    "NOTA", "TOTAL", "CLASSIFICACAO", "FINAL", "OBJETIVA", 
    "TITULOS", "DISCURSIVA", "RESULTADO", "APROVADO", "ELIMINADO",
    "INSCRICAO", "DATA", "NASCIMENTO", "JURADO", "NEGRO", "PCD",
    "GERAL", "AMBIENTAL", "MECANICA", "ELETRICA", "INFORMATICA", "CONTABIL",
    "AUDITOR", "FISCAL", "ADMINISTRATIVO", "ANALISTA"
])

def check_match_strict(name, text):
    """Verifica se o nome completo está presente no texto"""
    if len(name) < 5: return False
    
    # Busca simples primeiro - mais rápida
    if name not in text:
        return False
    
    # Se encontrou, verifica se é um match completo (não parte de outro nome)
    # Procura por padrões que indicam fim de nome: quebra de linha, número, ou stop word
    pattern = re.escape(name)
    
    for match in re.finditer(pattern, text):
        start = match.start()
        end = match.end()
        
        # Verifica o que vem antes
        if start > 0:
            char_before = text[start - 1]
            # Se não é espaço, quebra de linha ou início de linha, pode ser parte de outra palavra
            if char_before.isalnum():
                continue
        
        # Verifica o que vem depois
        if end >= len(text):
            return True
        
        remaining = text[end:]
        
        # Se é fim de linha ou quebra de linha, é válido
        if remaining.startswith('\n') or not remaining.strip():
            return True
        
        # Procura próxima palavra
        next_match = re.search(r'\S+', remaining)
        if not next_match:
            return True
        
        next_word = next_match.group(0)
        
        # Se começa com número ou símbolo, é válido (fim de nome)
        if not next_word[0].isalpha():
            return True
        
        # Se é uma stop word, é válido (fim de nome)
        clean_word = next_word.strip('.,-:/').upper()
        if clean_word in STOP_WORDS:
            return True
        
        # Se é uma cidade conhecida, é válido
        cidades = ['FLORIANOPOLIS', 'JOINVILLE', 'BLUMENAU', 'CRICIUMA', 'LAGES', 'PALHOCA', 'CHAPECO']
        if clean_word in cidades:
            return True
        
        # Caso contrário, pode ser parte de um nome maior (ex: "SILVA" em "SILVA JUNIOR")
        # Mas vamos ser mais permissivos - se o nome completo está lá, aceita
        # (isso pode dar alguns falsos positivos, mas é melhor que nenhum match)
        if len(name.split()) >= 2:  # Se tem pelo menos 2 palavras, provavelmente é nome completo
            return True
    
    return False

def names_match_exactly(name1_norm, name2_norm):
    """Verifica se dois nomes normalizados correspondem exatamente (ignorando acentuação)"""
    return name1_norm == name2_norm

def main():
    servidores = load_rs_data() + load_pr_data() + load_sp_data() + load_ms_data()
    print(f"Total servers loaded: {len(servidores)}")

    # Agrupar servidores por nome normalizado
    servidores_por_nome = {}
    for serv in servidores:
        name_norm = serv['name_norm']
        if name_norm not in servidores_por_nome:
            servidores_por_nome[name_norm] = []
        servidores_por_nome[name_norm].append(serv)
    
    # Verificar se todos os nomes em cada grupo correspondem completamente
    # Quando um nome aparece em múltiplos arquivos, só consideramos a mesma pessoa
    # se todos os nomes normalizados corresponderem exatamente
    servidores_validos = []
    nomes_rejeitados = 0
    for name_norm, grupo in servidores_por_nome.items():
        # Se há apenas um servidor com esse nome normalizado, adiciona diretamente
        if len(grupo) == 1:
            servidores_validos.extend(grupo)
        else:
            # Se há múltiplos servidores com o mesmo nome normalizado (de diferentes arquivos),
            # verifica se todos os nomes originais normalizados correspondem exatamente
            nomes_originais_norm = [normalize(serv['Nome']) for serv in grupo]
            # Verifica se todos os nomes normalizados são idênticos
            if all(nome == name_norm for nome in nomes_originais_norm):
                # Todos correspondem completamente, adiciona todos
                servidores_validos.extend(grupo)
            else:
                # Não correspondem completamente - pode haver diferenças além de acentuação
                # (ex: "José Silva" vs "José da Silva" normalizam para valores diferentes)
                # Neste caso, não adicionamos nenhum para evitar falsos positivos
                nomes_rejeitados += len(grupo)
                if nomes_rejeitados <= 10:  # Limita prints para não poluir o output
                    print(f"  > Nomes não correspondem completamente para '{name_norm}': {[serv['Nome'] for serv in grupo[:3]]}")
    
    print(f"Total valid servers after exact name matching: {len(servidores_validos)}")
    if nomes_rejeitados > 0:
        print(f"Servidores rejeitados (nomes não correspondem completamente): {nomes_rejeitados}")

    pdf_files = [f for f in os.listdir(BASE_DIR) if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDFs.")
    print(f"Processing PDFs...")

    matches = []
    pdf_count = 0

    for filename in pdf_files:
        pdf_count += 1
        if pdf_count % 5 == 0:
            print(f"  Processed {pdf_count}/{len(pdf_files)} PDFs... Found {len(matches)} matches so far.")
        
        filepath = os.path.join(BASE_DIR, filename)
        raw_text = extract_text_from_pdf(filepath)
        norm_text = normalize(raw_text)
        cargo_concurso = extract_cargo_concurso(raw_text)

        count = 0
        for serv in servidores_validos:
            name_n = serv['name_norm']
            if check_match_strict(name_n, norm_text):
                matches.append({
                    'Nome': serv['Nome'],
                    'ESTADO': serv['ESTADO'],
                    'Cargo': serv['Cargo'],
                    'Cargo Concurso': cargo_concurso,
                    'Arquivo PDF Origem': filename
                })
                count += 1
        
        if count > 0:
            print(f"  > matches: {count} | {filename} | {cargo_concurso}")

    print(f"Total matches: {len(matches)}")

    # Save to CSV
    matches_df = pd.DataFrame(matches)
    matches_df.to_csv(CSV_OUT, index=False, sep=';', encoding='utf-8')
    print(f"CSV saved to {CSV_OUT}")

    # Generate HTML
    try:
        json_data = matches_df.to_json(orient='records', force_ascii=False)
    except:
        json_data = "[]"

    # HTML Template
    html_template = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Servidores Encontrados - Multiestados</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent-color: #38bdf8;
            --accent-hover: #0ea5e9;
            --border-color: rgba(148, 163, 184, 0.1);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }

        body {
            background-color: var(--bg-color);
            background-image: radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
                              radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
                              radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .container {
            width: 100%;
            max-width: 1400px;
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            border: 1px solid var(--border-color);
            padding: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            animation: fadeIn 0.8s ease-out;
        }

        header { margin-bottom: 2rem; text-align: center; }

        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(to right, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        p.subtitle { color: var(--text-secondary); font-size: 1.1rem; }
        
        a { color: var(--accent-color); text-decoration: none; display: inline-flex; gap: 0.5rem; }
        a:hover { color: var(--accent-hover); text-decoration: underline; }

        .filters { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .filter-group { display: flex; flex-direction: column; }
        label { font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem; }
        input {
            background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border-color);
            border-radius: 8px; padding: 0.75rem 1rem; color: var(--text-primary);
            font-size: 0.95rem; transition: all 0.3s ease;
        }
        input:focus { outline: none; border-color: var(--accent-color); box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2); }

        .table-container { overflow-x: auto; border-radius: 12px; border: 1px solid var(--border-color); }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        thead { background: rgba(15, 23, 42, 0.8); }
        th {
            padding: 1rem; font-weight: 600; color: #818cf8; text-transform: uppercase;
            font-size: 0.75rem; letter-spacing: 0.05em; cursor: pointer; user-select: none;
            position: sticky; top: 0; background: rgba(15, 23, 42, 0.95); z-index: 10;
        }
        th:hover { color: var(--accent-color); }
        td { padding: 1rem; border-bottom: 1px solid var(--border-color); color: var(--text-secondary); font-size: 0.9rem; }
        tr:last-child td { border-bottom: none; }
        tr:hover { background: rgba(56, 189, 248, 0.05); }
        tr:hover td { color: var(--text-primary); }

        .external-link-icon { width: 14px; height: 14px; fill: currentColor; opacity: 0.7; }
        .stats { margin-top: 1rem; color: var(--text-secondary); font-size: 0.875rem; text-align: right; }
        .no-results { text-align: center; padding: 3rem; color: var(--text-secondary); display: none; }
        
        .tag-est-rs { color: #818cf8; font-weight: bold; }
        .tag-est-pr { color: #34d399; font-weight: bold; }
        .tag-est-sp { color: #fbbf24; font-weight: bold; }
        .tag-est-ms { color: #f472b6; font-weight: bold; }
        
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>Servidores Encontrados</h1>
        <p class="subtitle">Análise cruzada: FEPESE (Concurso 2025) x Servidores RS, PR, SP, MS</p>
    </header>

    <div class="filters">
        <div class="filter-group"><label>Nome</label><input type="text" id="searchNome" placeholder="Filtrar..."></div>
        <div class="filter-group"><label>Estado</label><input type="text" id="searchEstado" placeholder="Filtrar (RS, PR, SP, MS)..."></div>
        <div class="filter-group"><label>Cargo Concurso</label><input type="text" id="searchCargoConcurso" placeholder="Filtrar..."></div>
        <div class="filter-group"><label>Arquivo</label><input type="text" id="searchArquivo" placeholder="Filtrar..."></div>
    </div>

    <div class="table-container">
        <table id="dataTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Nome ↕</th>
                    <th onclick="sortTable(1)">Estado ↕</th>
                    <th onclick="sortTable(2)">Cargo Concurso ↕</th>
                    <th onclick="sortTable(3)">Arquivo PDF ↕</th>
                </tr>
            </thead>
            <tbody id="tableBody"></tbody>
        </table>
        <div id="noResults" class="no-results">Nenhum registro encontrado.</div>
    </div>
    <div class="stats">Mostrando <span id="shownCount">0</span> de <span id="totalCount">0</span> registros</div>
</div>

<script>
    const data = __JSON_DATA_PLACEHOLDER__;
    const linkIcon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="external-link-icon"><path d="M14 3h7v7h-2V6.41L9.41 16 8 14.59 17.59 5H14V3zm-2 9v2H6V6h2v2h2v2H8v4h6v-2h-2zm6 8V12h2v10H2V8h10v2H4v10h16z"/></svg>`;

    const tableBody = document.getElementById('tableBody');
    const shownCountEl = document.getElementById('shownCount');
    const totalCountEl = document.getElementById('totalCount');
    const noResultsEl = document.getElementById('noResults');
    const tableEl = document.getElementById('dataTable');

    const inputs = {
        nome: document.getElementById('searchNome'),
        estado: document.getElementById('searchEstado'),
        cargoConcurso: document.getElementById('searchCargoConcurso'),
        arquivo: document.getElementById('searchArquivo')
    };

    function renderTable(filteredData) {
        tableBody.innerHTML = '';
        if (filteredData.length === 0) {
            noResultsEl.style.display = 'block';
            tableEl.style.display = 'none';
        } else {
            noResultsEl.style.display = 'none';
            tableEl.style.display = 'table';
            filteredData.forEach(row => {
                const tr = document.createElement('tr');
                const arquivo = row['Arquivo PDF Origem'] || '';
                const arquivoLink = arquivo ? `<a href="${arquivo}" target="_blank">${arquivo}${linkIcon}</a>` : '';
                
                let estadoClass = '';
                if (row['ESTADO'] === 'RS') estadoClass = 'tag-est-rs';
                else if (row['ESTADO'] === 'PR') estadoClass = 'tag-est-pr';
                else if (row['ESTADO'] === 'SP') estadoClass = 'tag-est-sp';
                else if (row['ESTADO'] === 'MS') estadoClass = 'tag-est-ms';
                
                tr.innerHTML = `
                    <td>${row['Nome'] || ''}</td>
                    <td class="${estadoClass}">${row['ESTADO'] || ''}</td>
                    <td>${row['Cargo Concurso'] || ''}</td>
                    <td>${arquivoLink}</td>
                `;
                tableBody.appendChild(tr);
            });
        }
        shownCountEl.textContent = filteredData.length;
        totalCountEl.textContent = data.length;
    }

    function filterData() {
        const terms = {
            nome: inputs.nome.value.toLowerCase(),
            estado: inputs.estado.value.toLowerCase(),
            cargoConcurso: inputs.cargoConcurso.value.toLowerCase(),
            arquivo: inputs.arquivo.value.toLowerCase()
        };

        const filtered = data.filter(item => {
            return (
                (item['Nome'] || '').toLowerCase().includes(terms.nome) &&
                (item['ESTADO'] || '').toLowerCase().includes(terms.estado) &&
                (item['Cargo Concurso'] || '').toLowerCase().includes(terms.cargoConcurso) &&
                (item['Arquivo PDF Origem'] || '').toLowerCase().includes(terms.arquivo)
            );
        });
        renderTable(filtered);
    }

    Object.values(inputs).forEach(input => input.addEventListener('input', filterData));
    
    let currentSort = { column: null, direction: 'asc' };
    window.sortTable = function(columnIndex) {
        const mapIndexToKey = { 0: 'Nome', 1: 'ESTADO', 2: 'Cargo Concurso', 3: 'Arquivo PDF Origem' };
        const key = mapIndexToKey[columnIndex];
        if (currentSort.column === key) currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
        else { currentSort.column = key; currentSort.direction = 'asc'; }
        
        const terms = {
            nome: inputs.nome.value.toLowerCase(),
            estado: inputs.estado.value.toLowerCase(),
            cargoConcurso: inputs.cargoConcurso.value.toLowerCase(),
            arquivo: inputs.arquivo.value.toLowerCase()
        };
        
        let filtered = data.filter(item => {
            return (
                (item['Nome'] || '').toLowerCase().includes(terms.nome) &&
                (item['ESTADO'] || '').toLowerCase().includes(terms.estado) &&
                (item['Cargo Concurso'] || '').toLowerCase().includes(terms.cargoConcurso) &&
                (item['Arquivo PDF Origem'] || '').toLowerCase().includes(terms.arquivo)
            );
        });
        
        filtered.sort((a, b) => {
            const valA = (a[key] || '').toLowerCase();
            const valB = (b[key] || '').toLowerCase();
            if (valA < valB) return currentSort.direction === 'asc' ? -1 : 1;
            if (valA > valB) return currentSort.direction === 'asc' ? 1 : -1;
            return 0;
        });
        renderTable(filtered);
    };

    renderTable(data);
</script>
</body>
</html>
"""
    final_html = html_template.replace("__JSON_DATA_PLACEHOLDER__", json_data)

    with open(HTML_OUT, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"HTML saved to {HTML_OUT}")

if __name__ == "__main__":
    main()
