"""
Adiciona a coluna "Classificação Prova Escrita" ao index.html
com base nos dados cruzados com os PDFs de resultado da FEPESE.
"""

import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ── Classificações obtidas pelo cruzamento com os PDFs de resultado ───────────
CLASSIFICACOES = {
    # Ambiental
    "MARIA AUGUSTA DOS SANTOS DOIN VIEIRA": "14",
    "ANTHONY DE OLIVEIRA SILVEIRA": "31",
    "LAURA ADRIANO CORREA": "33",
    "JULIANA MERLIN VIANA": "34",
    "RICARDO QUEIROZ MELLO DA SILVEIRA": "68",
    "HADJA MARIA RADTKE NUNES": "70",
    "RITA DE CASSIA CARDOSO DA LUZ": "72",
    "FERNANDA GALLOTTI GOTELIP": "83",
    "PRISCILA SEBASTIANA GRIGORE DE AMORIM": "84",
    "TAIS BERNAL BALCONI": "138",
    "RAFAEL ANTONIO PARIZZI": "158",
    "NATHALIA CRISTINA GONZALEZ RIBEIRO": "170",
    "ANA CAROLINA BOGO DA ROSA": "183",
    "GEOVANA VENDRUSCOLO": "206",
    "HIUKARY MARIA ALVES BORGES": "243",
    "WILLIAN CARLOS NORI DOS SANTOS": "247",
    "JULIANE GONCALVES": "266",
    "CAMILA MACHADO CIESCA": "276",
    "FRANCIELLE BATISTA DUARTE FERREIRA": "285",
    "SUELEN PAULA CIZINANDE": "337",
    "KAREN ANDRINEIA DE OLIVEIRA": "388",
    "GENIANE SCHNEIDER": "414",
    "RENATO CARVALHO FERREIRA": "443",
    "TOZELLI JOAO PASCHOAL FILHO": "467",
    "CARLA FABIANA BONFANTI": "513",
    "ROMELL ALVES RIBEIRO DIAS": "533",
    "ALLAN MARTINS ALVES": "628",
    "SERENA RAMOS": "813",
    # Ciências Biológicas
    "SABRINA PEREIRA SANTOS": "1",
    "NATALIA VIEIRA SEGATTO": "3",
    "NICOLAS GABRIEL MARTINS SILVA": "11",
    "LUISA VIANNA MESQUITA": "67",
    "GIVAGO NODARY DA SILVA CORREA": "110",
    "LENA RIBEIRO LEITAO PINTER": "145",
    "CLEDINA DE OLIVEIRA STIEGEMAIER DOS SANTOS": "153",
    "JESSICA CAMPESTRINI": "181",
    "JULIANA CRISTINA PEREIRA HEINZ": "197",
    "JANAINA CARRION WICKERT": "227",
    "ANA KELLY PITLOVANCIV": "234",
    "IRAPUAN FRANCISCO BUSSMANN FILHO": "296",
    "VANESSA ZANELLA": "298",
    "MARCELO LUIZ SCHIAVINI": "348",
    "GABRIELA PROENCO": "426",
    "ANA RUBIA RAMOS FRITSCHE ZANELLA": "447",
    "BRUNO CEZAR SENA SANTOS": "500",
    "ALESSANDRA BORTOLUZZI COSTA": "637",
    "MONICA BECKER COELHO WORDELL": "651",
    # Ciências Sociais Aplicadas
    "LEANDRO QUINTELA WOITYNA": "52",
    "LUIZ ANTONIO SIMM VIANA": "92",
    "EMMANUELLE DE CARVALHO SANTIAGO": "115",
    "ALINE BRAZ": "121",
    "CHRISTIAN NUNES DE MORAES": "129",
    "NAYARA JULIO ROCHA": "136",
    "NADJARA DAS NEVES PIRES": "141",
    "ELEAKIN DE ALMEIDA SCREMIN": "168",
    "MIRIANA BORGHEZAN GONCALVES": "227",
    "CARLOS RICARDO DE MELO": "245",
    "RONI COELHO ROSSO": "250",
    "LUIZ ERNANDES WESCHE": "262",
    "MICHELLY ALVES PEREIRA": "282",
    "RAFAEL SILVA MARTINS": "288",
    "ALINE CECHETTO BECK": "434",
    "AMANDA ANTUNES VIEIRA": "447",
    "JOAO ROBERTO ARAUJO ANDRADE": "478",
    "CLAUDIO LUIS BITTELBRUN": "486",
    "FERNANDO RAMOS DAMASCO": "491",
    # Engenharia Civil
    "BRUNO VITALI ISOPPO": "12",
    "MARLON VENICIUS WASEM": "23",
    "MAGALI BARDINI SIMON": "42",
    "RENAN MATSUDA BENEDITO": "122",
    "ELTON JORGE DA SILVA": "185",
    "ESTELA BORTOLANZA DALAZEN": "215",
    "CAIO BONETTI MENDES": "229",
    "ALEXANDRE VON FRUHAUF": "279",
    "GUILHERME HENRIQUE ROSSO": "346",
    "MATHEUS MARION ROVANI": "403",
    # Geologia/Minas
    "JAIME REGO DE MENEZES NETO": "40",
    # Informática
    "ERICK LAGO FREITAS": "59",
    "ALECIO HENRIQUE DIONIZIO": "70",
    "MAURICIO DARABAS RONZANI": "89",
    "VICTOR LOUSAN DO NASCIMENTO POUBEL": "114",
    "CAROLINA ROCHA BARBOSA": "163",
    "EDUARDO DOMANSKI DOS SANTOS": "171",
    # Mecânica/Mecatrônica/Materiais
    "LEONARDO DE SOUZA PIRES": "17",
    "GUILHERME FRANZOI": "48",
    "NAGILA LUCIETTI SCHMIDT MELLO": "51",
    "GABRIEL FONTANELLE PEREIRA": "109",
    "PATRICK NIKSON RUBBO": "110",
    "ANDRE LUIZ DOS SANTOS": "163",
    # Medicina Legal
    "VICTOR HUGO DE CAMPOS": "7",
    "DANIEL JOSE RESENDE SAGGIN": "23",
    "GEOVAN FABIO DE OLIVEIRA": "82",
    # Medicina Legal (Psiquiatria)
    "ARTHUR BONETTI MENDES": "12",
    # Medicina Veterinária
    "BEATRIZ PAVEI BEZ BATTI": "2",
    "BEATRIZ SUZANA MACHADO": "5",
    "VANESSA FARINHA NUNES DA SILVA": "70",
    "MARIO CESAR CORREA JUNIOR": "256",
    # Química
    "ELLEN MARCELINA SPILLERE SCHEEREN": "10",
    "GABRIEL MODERNELL ZANOTTO": "21",
    "CARLOS WESTRUP PIRES DA SILVA": "23",
    "MYLENA FERNANDES": "75",
    "MONICA CRISTINE THIBES": "82",
    "PRISCILLA DE LIMA NUNES": "93",
    "LUIZ PHILIPI CALEGARI": "111",
    "GISELA ANGELICA DIAS FAVRETTO": "116",
    "SURYA DE JESUS CANTARINO": "158",
    "BETHANIA LUIZA HORST": "190",
    "KETTULIN ZOMER REZIN": "233",
    "JESSICA GIOVANNA BERNARDINI SANTIN": "267",
    "MAIARA VENANCIO": "356",
    "SIRLENE MARTINS MAZZUCO": "358",
    "JULIANA MONTAGNA HARTWIG": "368",
    "DEBORA BIASI": "486",
    "MARCELA FERRAZ DICKOW": "520",
    "RODRIGO BONELI LIDORIO": "637",
    # Áudio e Imagem
    "PIETRO OLIVEIRA MORAIS GUESSER": "20",
    "FELIPP BITTENCOURT FRASSETTO": "79",
    "GUSTAVO DA SILVA POLETTO": "91",
}


def main():
    html_path = "index.html"

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # ── 1. Extrai o JSON embutido ─────────────────────────────────────────────
    m = re.search(r"const data = (\[.*?\]);", html, re.DOTALL)
    if not m:
        print("ERRO: não encontrei 'const data = [...]' no index.html")
        sys.exit(1)

    data = json.loads(m.group(1))
    print(f"Registros encontrados: {len(data)}")

    # ── 2. Adiciona a coluna de classificação ─────────────────────────────────
    encontrados = 0
    for rec in data:
        nome = rec.get("Nome", "").strip().upper()
        classif = CLASSIFICACOES.get(nome, "—")
        rec["Classif. Prova Escrita"] = classif
        if classif != "—":
            encontrados += 1

    print(f"Classificações preenchidas: {encontrados}/{len(data)}")

    novo_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    # ── 3. Substitui o JSON no HTML ───────────────────────────────────────────
    html = html[:m.start(1)] + novo_json + html[m.end(1):]

    # ── 4. Adiciona cabeçalho da nova coluna na <thead> ───────────────────────
    # Adiciona antes do último </tr> do thead
    html = html.replace(
        '<th onclick="sortTable(4)">Arquivo PDF ↕</th>',
        '<th onclick="sortTable(4)">Arquivo PDF ↕</th>\n'
        '        <th onclick="sortTable(5)">Class. Prova Escrita ↕</th>',
    )

    # ── 5. Adiciona campo de filtro ───────────────────────────────────────────
    html = html.replace(
        '<div class="filter-group">\n'
        '          <label for="searchArquivo">Arquivo PDF</label>\n'
        '          <input type="text" id="searchArquivo" placeholder="Filtrar...">',
        '<div class="filter-group">\n'
        '          <label for="searchArquivo">Arquivo PDF</label>\n'
        '          <input type="text" id="searchArquivo" placeholder="Filtrar...">\n'
        '        </div>\n'
        '        <div class="filter-group">\n'
        '          <label for="searchClassif">Class. Prova Escrita</label>\n'
        '          <input type="text" id="searchClassif" placeholder="Filtrar...">',
    )

    # ── 6. Atualiza o JavaScript de renderização para incluir a nova coluna ───
    # Substitui o trecho que gera as <td> da linha
    old_render = (
        "tr.innerHTML = `\n"
        "                <td>${row['Nome'] || ''}</td>\n"
        "                <td class=\"${estadoClass}\">${row['Cargo Atual'] || ''}</td>\n"
        "                <td>${row['Lotacao (Unidade Exercicio)'] || ''}</td>\n"
        "                <td>${row['Cargo Concurso'] || ''}</td>\n"
        "                <td>${arquivoLink}</td>\n"
        "              `;"
    )
    new_render = (
        "tr.innerHTML = `\n"
        "                <td>${row['Nome'] || ''}</td>\n"
        "                <td class=\"${estadoClass}\">${row['Cargo Atual'] || ''}</td>\n"
        "                <td>${row['Lotacao (Unidade Exercicio)'] || ''}</td>\n"
        "                <td>${row['Cargo Concurso'] || ''}</td>\n"
        "                <td>${arquivoLink}</td>\n"
        "                <td style=\"text-align:center;font-weight:bold;color:${row['Classif. Prova Escrita'] && row['Classif. Prova Escrita'] !== '—' ? '#38bdf8' : '#64748b'}\">"
        "${row['Classif. Prova Escrita'] || '—'}</td>\n"
        "              `;"
    )
    if old_render in html:
        html = html.replace(old_render, new_render)
        print("Bloco de renderização atualizado.")
    else:
        print("AVISO: bloco de renderização não encontrado — tentando abordagem alternativa.")
        html = html.replace(
            "<td>${arquivoLink}</td>",
            "<td>${arquivoLink}</td>\n"
            "                <td style=\"text-align:center;font-weight:bold;color:"
            "${row['Classif. Prova Escrita'] && row['Classif. Prova Escrita'] !== '—' ? '#38bdf8' : '#64748b'}\">"
            "${row['Classif. Prova Escrita'] || '—'}</td>",
        )

    # ── 7. Atualiza o filtro para incluir a nova coluna ───────────────────────
    # Adiciona searchClassif ao objeto inputs e ao filtro
    html = html.replace(
        "arquivo: document.getElementById('searchArquivo')",
        "arquivo: document.getElementById('searchArquivo'),\n"
        "    classif: document.getElementById('searchClassif')",
    )
    html = html.replace(
        "(item['Arquivo PDF Origem'] || '').toLowerCase().includes(terms.arquivo)",
        "(item['Arquivo PDF Origem'] || '').toLowerCase().includes(terms.arquivo) &&\n"
        "      (item['Classif. Prova Escrita'] || '').toLowerCase().includes(terms.classif)",
    )

    # ── 8. Atualiza o mapeamento de colunas no sortTable ─────────────────────
    html = html.replace(
        "const mapIndexToKey = { 0: 'Nome', 1: 'ESTADO', 2: 'Cargo Concurso', 3: 'Arquivo PDF Origem' };",
        "const mapIndexToKey = { 0: 'Nome', 1: 'Cargo Atual', 2: 'Lotacao (Unidade Exercicio)', 3: 'Cargo Concurso', 4: 'Arquivo PDF Origem', 5: 'Classif. Prova Escrita' };",
    )

    # ── 9. Atualiza o título ──────────────────────────────────────────────────
    html = html.replace(
        "Servidores Encontrados - Concurso 2026",
        "Servidores Encontrados - Concurso 2026",
    )
    html = html.replace(
        "Análise cruzada entre FEPESE (Concurso 2025) e Portal da Transparência SC",
        "Análise cruzada entre FEPESE (Concurso 2025) e Portal da Transparência SC · "
        "Classificação Preliminar da Prova Escrita",
    )

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nindex.html atualizado com sucesso!")

    # ── 10. Atualiza também o CSV principal ───────────────────────────────────
    import csv, pathlib
    csv_path = pathlib.Path("servidores_concurso_encontrados.csv")
    if csv_path.exists():
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter=";"))

        for row in rows:
            nome = row.get("Nome", "").strip().upper()
            row["Classif. Prova Escrita"] = CLASSIFICACOES.get(nome, "—")

        fieldnames = list(rows[0].keys()) if rows else []
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(rows)
        print(f"CSV '{csv_path}' atualizado com {len(rows)} registros.")

    csv_det = pathlib.Path("servidores_concurso_encontrados_detalhado.csv")
    if csv_det.exists():
        with open(csv_det, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter=";"))
        for row in rows:
            nome = row.get("Nome", "").strip().upper()
            row["Classif. Prova Escrita"] = CLASSIFICACOES.get(nome, "—")
        if rows:
            fieldnames = list(rows[0].keys())
            with open(csv_det, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
                writer.writeheader()
                writer.writerows(rows)
            print(f"CSV '{csv_det}' atualizado com {len(rows)} registros.")


if __name__ == "__main__":
    main()
