import os
import pandas as pd
import pypdf
import unicodedata
import json

# Paths
BASE_DIR = r"d:/Google Drive/Meu Drive/ACAPE/CONCURSO 2026/fepese_pci_perito_pdfs"
EXCEL_PATH = os.path.join(BASE_DIR, "servidores igp rs.xlsx")
CSV_OUT = os.path.join(BASE_DIR, "servidores_igp_rs_encontrados.csv")
HTML_OUT = os.path.join(BASE_DIR, "servidores_igp_rs_filter.html")

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

def main():
    print("Loading Excel...")
    try:
        # Load excel, deduplicate by Nome, keep first
        df = pd.read_excel(EXCEL_PATH)
        df.fillna('', inplace=True)
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return

    # Normalize column names just in case
    # Needed columns: Nome, Cargo, Lotação
    # We verify if they exist
    print(f"Columns: {df.columns.tolist()}")

    # Deduplicate and normalize
    df = df.drop_duplicates(subset=['Nome'])
    df['name_norm'] = df['Nome'].apply(normalize)
    
    servidores = df.to_dict('records')
    print(f"Loaded {len(servidores)} unique servers from RS.")

    pdf_files = [f for f in os.listdir(BASE_DIR) if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDFs.")

    matches = []

    for filename in pdf_files:
        filepath = os.path.join(BASE_DIR, filename)
        raw_text = extract_text_from_pdf(filepath)
        norm_text = normalize(raw_text)
        cargo_concurso = extract_cargo_concurso(raw_text)

        count = 0
        for serv in servidores:
            name_n = serv['name_norm']
            # Match condition: Full name must be in PDF text
            if len(name_n) > 5 and name_n in norm_text:
                matches.append({
                    'Nome': serv['Nome'],
                    'ESTADO': 'RS',
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
    <title>Servidores Encontrados - IGP RS</title>
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
        
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>Servidores Encontrados</h1>
        <p class="subtitle">Análise cruzada entre <a href="https://2025pciperito.fepese.org.br/" target="_blank">FEPESE (Concurso 2025)</a> e Servidores IGP RS</p>
    </header>

    <div class="filters">
        <div class="filter-group"><label>Nome</label><input type="text" id="searchNome" placeholder="Filtrar..."></div>
        <div class="filter-group"><label>Estado</label><input type="text" id="searchEstado" placeholder="Filtrar..."></div>
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
                tr.innerHTML = `
                    <td>${row['Nome'] || ''}</td>
                    <td>${row['ESTADO'] || ''}</td>
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
