import csv
import json
import os

csv_path = r'd:\Google Drive\Meu Drive\ACAPE\CONCURSO 2026\fepese_pci_perito_pdfs\servidores_concurso_encontrados_detalhado.csv'
html_path = r'd:\Google Drive\Meu Drive\ACAPE\CONCURSO 2026\fepese_pci_perito_pdfs\servidores_concurso_filter.html'

data = []
try:
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            data.append(row)
except Exception as e:
    print(f"Error reading CSV: {e}")
    # Fallback for different encoding if needed, though utf-8 is standard
    try:
        with open(csv_path, 'r', encoding='latin-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            data = []
            for row in reader:
                data.append(row)
    except Exception as e2:
         print(f"Error reading CSV with latin-1: {e2}")

json_data = json.dumps(data, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Servidores Encontrados - Concurso 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent-color: #38bdf8;
            --accent-hover: #0ea5e9;
            --border-color: rgba(148, 163, 184, 0.1);
            --gradient-start: #0f172a;
            --gradient-end: #1e293b;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Outfit', sans-serif;
        }}

        body {{
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
        }}

        .container {{
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
        }}

        header {{
            margin-bottom: 2rem;
            text-align: center;
        }}

        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(to right, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}

        p.subtitle {{
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}

        .filters {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .filter-group {{
            display: flex;
            flex-direction: column;
        }}

        label {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            font-weight: 500;
        }}

        input {{
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            color: var(--text-primary);
            font-size: 0.95rem;
            transition: all 0.3s ease;
        }}

        input:focus {{
            outline: none;
            border-color: var(--accent-color);
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
        }}

        .table-container {{
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}

        thead {{
            background: rgba(15, 23, 42, 0.8);
        }}

        th {{
            padding: 1rem;
            font-weight: 600;
            color: #818cf8;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
            cursor: pointer;
            user-select: none;
            position: sticky;
            top: 0;
            background: rgba(15, 23, 42, 0.95); /* Fix sticky header transparency overlap */
            z-index: 10;
        }}
        
        th:hover {{
            color: var(--accent-color);
        }}

        td {{
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-secondary);
            font-size: 0.9rem;
            transition: color 0.2s;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr:hover {{
            background: rgba(56, 189, 248, 0.05); /* Very subtle hover effect */
        }}
        
        tr:hover td {{
            color: var(--text-primary);
        }}

        tr {{
            transition: background-color 0.2s ease;
        }}

        /* New CSS for links */
        a {{
            color: var(--accent-color);
            text-decoration: none;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }}

        a:hover {{
            color: var(--accent-hover);
            text-decoration: underline;
        }}

        .external-link-icon {{
            width: 14px;
            height: 14px;
            fill: currentColor;
            opacity: 0.7;
        }}

        .stats {{
            margin-top: 1rem;
            color: var(--text-secondary);
            font-size: 0.875rem;
            text-align: right;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Scrollbar styling */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: rgba(15, 23, 42, 0.4);
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(148, 163, 184, 0.3);
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(148, 163, 184, 0.5);
        }}
        
        .no-results {{
            text-align: center;
            padding: 3rem;
            color: var(--text-secondary);
            font-style: italic;
            display: none;
        }}
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>Servidores Encontrados</h1>
        <p class="subtitle">Análise cruzada entre <a href="https://2025pciperito.fepese.org.br/" target="_blank">FEPESE (Concurso 2025)</a> e <a href="https://www.transparencia.sc.gov.br/remuneracao-servidores" target="_blank">Portal da Transparência SC</a></p>
    </header>

    <div class="filters">
        <div class="filter-group">
            <label for="searchNome">Nome</label>
            <input type="text" id="searchNome" placeholder="Filtrar por nome...">
        </div>
        <div class="filter-group">
            <label for="searchCargoAtual">Cargo Atual</label>
            <input type="text" id="searchCargoAtual" placeholder="Filtrar por cargo atual...">
        </div>
        <div class="filter-group">
            <label for="searchLotacao">Lotação</label>
            <input type="text" id="searchLotacao" placeholder="Filtrar por lotação...">
        </div>
        <div class="filter-group">
            <label for="searchCargoConcurso">Cargo Concurso</label>
            <input type="text" id="searchCargoConcurso" placeholder="Filtrar por cargo concurso...">
        </div>
        <div class="filter-group">
            <label for="searchArquivo">Arquivo Origem</label>
            <input type="text" id="searchArquivo" placeholder="Filtrar por arquivo...">
        </div>
    </div>

    <div class="table-container">
        <table id="dataTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Nome ↕</th>
                    <th onclick="sortTable(1)">Cargo Atual ↕</th>
                    <th onclick="sortTable(2)">Lotação ↕</th>
                    <th onclick="sortTable(3)">Cargo Concurso ↕</th>
                    <th onclick="sortTable(4)">Arquivo PDF ↕</th>
                </tr>
            </thead>
            <tbody id="tableBody">
                <!-- Rows will be injected here -->
            </tbody>
        </table>
        <div id="noResults" class="no-results">
            Nenhum registro encontrado para os filtros selecionados.
        </div>
    </div>
    
    <div class="stats" id="stats">
        Mostrando <span id="shownCount">0</span> de <span id="totalCount">0</span> registros
    </div>
</div>

<script>
    const data = {json_data};
    
    // SVG icon for external link
    const linkIcon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="external-link-icon"><path d="M14 3h7v7h-2V6.41L9.41 16 8 14.59 17.59 5H14V3zm-2 9v2H6V6h2v2h2v2H8v4h6v-2h-2zm6 8V12h2v10H2V8h10v2H4v10h16z"/></svg>`;

    const tableBody = document.getElementById('tableBody');
    const shownCountEl = document.getElementById('shownCount');
    const totalCountEl = document.getElementById('totalCount');
    const noResultsEl = document.getElementById('noResults');
    const tableEl = document.getElementById('dataTable');

    // Input elements
    const inputs = {{
        nome: document.getElementById('searchNome'),
        cargoAtual: document.getElementById('searchCargoAtual'),
        lotacao: document.getElementById('searchLotacao'),
        cargoConcurso: document.getElementById('searchCargoConcurso'),
        arquivo: document.getElementById('searchArquivo')
    }};

    function renderTable(filteredData) {{
        tableBody.innerHTML = '';
        
        if (filteredData.length === 0) {{
            noResultsEl.style.display = 'block';
            tableEl.style.display = 'none';
        }} else {{
            noResultsEl.style.display = 'none';
            tableEl.style.display = 'table';
            
            filteredData.forEach(row => {{
                const tr = document.createElement('tr');
                const arquivo = row['Arquivo PDF Origem'] || '';
                // Create link if archive exists
                const arquivoLink = arquivo ? `<a href="${{arquivo}}" target="_blank">${{arquivo}}${{linkIcon}}</a>` : '';

                tr.innerHTML = `
                    <td>${{row['Nome'] || ''}}</td>
                    <td>${{row['Cargo Atual'] || ''}}</td>
                    <td>${{row['Lotacao (Unidade Exercicio)'] || ''}}</td>
                    <td>${{row['Cargo Concurso'] || ''}}</td>
                    <td>${{arquivoLink}}</td>
                `;
                tableBody.appendChild(tr);
            }});
        }}
        
        shownCountEl.textContent = filteredData.length;
        totalCountEl.textContent = data.length;
    }}

    function filterData() {{
        const terms = {{
            nome: inputs.nome.value.toLowerCase(),
            cargoAtual: inputs.cargoAtual.value.toLowerCase(),
            lotacao: inputs.lotacao.value.toLowerCase(),
            cargoConcurso: inputs.cargoConcurso.value.toLowerCase(),
            arquivo: inputs.arquivo.value.toLowerCase()
        }};

        const filtered = data.filter(item => {{
            return (
                (item['Nome'] || '').toLowerCase().includes(terms.nome) &&
                (item['Cargo Atual'] || '').toLowerCase().includes(terms.cargoAtual) &&
                (item['Lotacao (Unidade Exercicio)'] || '').toLowerCase().includes(terms.lotacao) &&
                (item['Cargo Concurso'] || '').toLowerCase().includes(terms.cargoConcurso) &&
                (item['Arquivo PDF Origem'] || '').toLowerCase().includes(terms.arquivo)
            );
        }});

        renderTable(filtered);
    }}

    // Attach event listeners
    Object.values(inputs).forEach(input => {{
        input.addEventListener('input', filterData);
    }});
    
    // Sort functionality
    let currentSort = {{ column: null, direction: 'asc' }};
    
    window.sortTable = function(columnIndex) {{
        const mapIndexToKey = {{
            0: 'Nome',
            1: 'Cargo Atual',
            2: 'Lotacao (Unidade Exercicio)',
            3: 'Cargo Concurso',
            4: 'Arquivo PDF Origem'
        }};
        
        const key = mapIndexToKey[columnIndex];
        
        if (currentSort.column === key) {{
            currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
        }} else {{
            currentSort.column = key;
            currentSort.direction = 'asc';
        }}
        
        // Visual indicator logic could be added here (updating arrows)
        
        // Initial filter to get current set
        const terms = {{
            nome: inputs.nome.value.toLowerCase(),
            cargoAtual: inputs.cargoAtual.value.toLowerCase(),
            lotacao: inputs.lotacao.value.toLowerCase(),
            cargoConcurso: inputs.cargoConcurso.value.toLowerCase(),
            arquivo: inputs.arquivo.value.toLowerCase()
        }};
        
        let filtered = data.filter(item => {{
            return (
                (item['Nome'] || '').toLowerCase().includes(terms.nome) &&
                (item['Cargo Atual'] || '').toLowerCase().includes(terms.cargoAtual) &&
                (item['Lotacao (Unidade Exercicio)'] || '').toLowerCase().includes(terms.lotacao) &&
                (item['Cargo Concurso'] || '').toLowerCase().includes(terms.cargoConcurso) &&
                (item['Arquivo PDF Origem'] || '').toLowerCase().includes(terms.arquivo)
            );
        }});
        
        filtered.sort((a, b) => {{
            const valA = (a[key] || '').toLowerCase();
            const valB = (b[key] || '').toLowerCase();
            
            if (valA < valB) return currentSort.direction === 'asc' ? -1 : 1;
            if (valA > valB) return currentSort.direction === 'asc' ? 1 : -1;
            return 0;
        }});
        
        renderTable(filtered);
    }};

    // Initial render
    renderTable(data);

</script>

</body>
</html>
"""

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML file created at: {html_path}")
