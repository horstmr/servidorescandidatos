from cross_reference_multi import *

print("Carregando servidores...")
servidores = load_pr_data() + load_sp_data() + load_ms_data()
print(f"Total servidores carregados: {len(servidores)}")

# Agrupar por nome normalizado
servidores_por_nome = {}
for serv in servidores:
    name_norm = serv['name_norm']
    if name_norm not in servidores_por_nome:
        servidores_por_nome[name_norm] = []
    servidores_por_nome[name_norm].append(serv)

print(f"Grupos únicos por nome normalizado: {len(servidores_por_nome)}")

# Verificar validação
servidores_validos = []
nomes_rejeitados = 0
grupos_multiplos = 0

for name_norm, grupo in servidores_por_nome.items():
    if len(grupo) == 1:
        servidores_validos.extend(grupo)
    else:
        grupos_multiplos += 1
        nomes_originais_norm = [normalize(serv['Nome']) for serv in grupo]
        if all(nome == name_norm for nome in nomes_originais_norm):
            servidores_validos.extend(grupo)
        else:
            nomes_rejeitados += len(grupo)
            if grupos_multiplos <= 5:
                print(f"  Rejeitado '{name_norm}': {[serv['Nome'] for serv in grupo[:3]]}")

print(f"\nGrupos com múltiplos servidores: {grupos_multiplos}")
print(f"Servidores válidos após validação: {len(servidores_validos)}")
print(f"Servidores rejeitados: {nomes_rejeitados}")
