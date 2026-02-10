def executar_maqhipo(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r') as f:
            instrucoes = [linha.strip() for linha in f.readlines()]
    except FileNotFoundError:
        print("Arquivo nao encontrado")
        return

    memoria = [0.0] * 1000  
    pilha_dados = []       
    pilha_retorno = []      
    ip = 0                  


    while ip < len(instrucoes):
        linha = instrucoes[ip]
        if not linha: 
            ip += 1
            continue
            
        partes = linha.split()
        comando = partes[0]
        
        #print(f"{ip} | {linha:} | {pilha_dados}")

        if comando == "INPP":
            pass

        elif comando == "ALME":
            pass 

        elif comando == "CRCT":
            pilha_dados.append(float(partes[1]))

        elif comando == "CRVL":
            endereco = int(partes[1])
            pilha_dados.append(memoria[endereco])

        elif comando == "ARMZ":
            endereco = int(partes[1])
            valor = pilha_dados.pop()
            memoria[endereco] = valor

        elif comando == "SOMA":
            v2 = pilha_dados.pop()
            v1 = pilha_dados.pop()
            pilha_dados.append(v1 + v2)

        elif comando == "SUBT":
            v2 = pilha_dados.pop()
            v1 = pilha_dados.pop()
            pilha_dados.append(v1 - v2)

        elif comando == "MULT":
            v2 = pilha_dados.pop()
            v1 = pilha_dados.pop()
            pilha_dados.append(v1 * v2)

        elif comando == "DIVI":
            v2 = pilha_dados.pop()
            v1 = pilha_dados.pop()
            pilha_dados.append(v1 / v2)

        elif comando == "INVE":
            v = pilha_dados.pop()
            pilha_dados.append(-v)
        # == 
        elif comando == "CPIG": 
            v2 = pilha_dados.pop()
            v1 = pilha_dados.pop()
            pilha_dados.append(1.0 if v1 == v2 else 0.0)

        # !=
        elif comando == "CPNE": 
            v2 = pilha_dados.pop()
            v1 = pilha_dados.pop()
            pilha_dados.append(1.0 if v1 != v2 else 0.0)

        # >=
        elif comando == "CPMI":
            v2 = pilha_dados.pop()
            v1 = pilha_dados.pop()
            pilha_dados.append(1.0 if v1 >= v2 else 0.0)

        # <=
        elif comando == "CMAI": 
            v2 = pilha_dados.pop()
            v1 = pilha_dados.pop()
            pilha_dados.append(1.0 if v1 <= v2 else 0.0)

        # <
        elif comando == "CPMA": 
            v2 = pilha_dados.pop()
            v1 = pilha_dados.pop()
            pilha_dados.append(1.0 if v1 < v2 else 0.0)
        # >
        elif comando == "CPME":
            v2 = pilha_dados.pop()
            v1 = pilha_dados.pop()
            pilha_dados.append(1.0 if v1 > v2 else 0.0)

        elif comando == "DSVI":
            ip = int(partes[1])
            continue 

        elif comando == "DSVF":
            endereco_pulo = int(partes[1])
            condicao = pilha_dados.pop()
            if condicao == 0.0:
                ip = endereco_pulo
                continue

        elif comando == "CHAM":
            pilha_retorno.append(ip + 1) 
            ip = int(partes[1])
            continue

        elif comando == "RTRN":
            if pilha_retorno:
                ip = pilha_retorno.pop()
                continue
            else:
                print("Erro: RTRN sem endereço de retorno!")
                break

        elif comando == "IMPR":
            valor = pilha_dados.pop()
            print(f"[SAÍDA]: {valor}")

        elif comando == "LEIT":
            valor = float(input("Digite um numero real: "))
            pilha_dados.append(valor)

        elif comando == "PARA":
            break

        ip += 1
