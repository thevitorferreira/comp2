from lexico import Lexico

class Sintatico:
    def __init__(self, lexico):
        self.lexico = lexico
        self.token_atual = self.lexico.prox_token()
        self.tabela_simbolos = {} 
        self.proximo_endereco = 0
        self.codigo_objeto = []

        self.log_debug = open("debug_sintatico.txt", "w")

    def registrar(self, fase, regra, token):
        self.log_debug.write(f"[{fase}] Regra: {regra} | Token: {token}\n")
        self.log_debug.flush()

    def erro(self, mensagem):
        linha = self.token_atual[2] if self.token_atual else "FIM"
        raise Exception(f"Erro Sintático na linha {linha}: {mensagem}")

    def eat(self, esperado):

        if self.token_atual and (self.token_atual[0] == esperado or self.token_atual[1] == esperado):
            self.registrar("CONSUMO", "Terminal", self.token_atual[0])
            self.token_atual = self.lexico.prox_token()
        else:
            encontrado = self.token_atual[0] if self.token_atual else "FIM"
            self.erro(f"Esperava '{esperado}', mas encontrei '{encontrado}'")

    # <programa> -> <?php <corpo> ?>
    def programa(self):
        self.registrar("FIRST", "<programa>", "<?php")
        self.eat('<?php')
        self.codigo_objeto.append("INPP")
        
        self.codigo_objeto.append("") 
        pos_pulo_inicial = len(self.codigo_objeto) - 1
        
        self.corpo()
      
        self.registrar("FOLLOW", "<programa>", "?>")
        self.eat('?>')
        self.codigo_objeto.append("PARA")

    # <corpo> -> <dc> <comandos>
    def corpo(self):
        self.dc()
        self.comandos()

    def dc(self):
        if not self.token_atual: return

        if self.token_atual[1] == 'IDENT':
            self.registrar("FIRST", "<dc>", "dc_v")
            self.dc_v()
            self.dc() 
            
        elif self.token_atual[0] == 'function':
            self.registrar("FIRST", "<dc>", "dc_f")
            self.dc_f()
            self.dc() 
            

    def dc_v(self):
            nome_var = self.token_atual[0]
            self.eat('IDENT')
            
            if nome_var not in self.tabela_simbolos:
                self.tabela_simbolos[nome_var] = self.proximo_endereco
                self.codigo_objeto.append("ALME 1")
                self.proximo_endereco += 1
            
            self.atribuicao_opcional(nome_var)
    # <atribuicao_opcional> -> = <expressao> ; | ;
    def atribuicao_opcional(self, nome_var):
      
        if self.token_atual[0] == '=':
            self.eat('=')
            self.expressao()
            endereco = self.tabela_simbolos[nome_var]
            self.codigo_objeto.append(f"ARMZ {endereco}")
            
        self.eat(';') 

    # <expressao> -> <termo> <outros_termos> | floatval(readline());
    def expressao(self):
        self.registrar("FIRST", "<expressao>", self.token_atual[0])
        
        if self.token_atual[1] == 'T_READLINE':
            self.codigo_objeto.append("LEIT") 
            self.eat('T_READLINE')
        else:
            self.termo()
            self.outros_termos()

    # <outros_termos> -> <op_ad> <termo> <outros_termos> | λ
    def outros_termos(self):
        if self.token_atual and self.token_atual[0] in ['+', '-']:
            op = self.token_atual[0]
            self.eat('SIMBOLO')
            self.termo()
            
            if op == '+': self.codigo_objeto.append("SOMA")
            else: self.codigo_objeto.append("SUBT")
            
            self.outros_termos() # Recursão

    # <termo> -> <op_un> <fator> <mais_fatores>
    def termo(self):
        self.op_un()
        self.fator()
        self.mais_fatores()

    # <op_un> -> - | λ
    def op_un(self):
        if self.token_atual[0] == '-':
            self.eat('SIMBOLO')
            self.codigo_objeto.append("INVE") 

    def mais_fatores(self):
        if self.token_atual and self.token_atual[0] in ['*', '/']:
            op = self.token_atual[0]
            self.eat('SIMBOLO')
            self.fator()
            
            if op == '*': self.codigo_objeto.append("MULT")
            else: self.codigo_objeto.append("DIVI")
            
            self.mais_fatores()

    # <fator> -> $ident | numero_real | ( <expressao> )
    def fator(self):
        val, tipo, lin = self.token_atual
        
        if tipo == 'IDENT':
            if val in self.tabela_simbolos:
                endereco = self.tabela_simbolos[val]
                self.codigo_objeto.append(f"CRVL {endereco}")
            else:
                self.erro(f"Variável {val} não foi declarada.")
            self.eat('IDENT')
            
        elif tipo == 'NUMERO':
            self.codigo_objeto.append(f"CRCT {val}")
            self.eat('NUMERO')
            
        elif val == '(':
            self.eat('SIMBOLO')
            self.expressao()
            self.eat('SIMBOLO')
        else:
            self.erro("Fator inválido na expressão.")

    def dc_f(self):
        self.eat('function')
        nome_funcao = self.token_atual[0]
        self.eat('IDENT')

        pos_pulo = len(self.codigo_objeto)
        self.codigo_objeto.append("") 
        
        self.tabela_simbolos[nome_funcao] = len(self.codigo_objeto)
        
        self.parametros()
        self.eat('{')
        self.corpo_f()
        self.eat('}')
        
        self.codigo_objeto.append("RTRN")
        
        self.codigo_objeto[pos_pulo] = f"DSVI {len(self.codigo_objeto)}"

    def parametros(self):
        self.eat('(')
        if self.token_atual[0] != ')':
            self.lista_par()
        self.eat(')')

    # <lista_par> -> $ident <mais_par>
    def lista_par(self):
        nome_param = self.token_atual[0]
        self.eat('IDENT')
        
        self.tabela_simbolos[nome_param] = self.proximo_endereco
        self.codigo_objeto.append("ALME 1")
        self.proximo_endereco += 1
        
        self.mais_par()

    # <mais_par> -> , $ident <mais_par> | λ
    def mais_par(self):
        if self.token_atual[0] == ',':
            self.eat(',')
            nome_param = self.token_atual[0]
            self.eat('IDENT')
            
            self.tabela_simbolos[nome_param] = self.proximo_endereco
            self.codigo_objeto.append("ALME 1")
            self.proximo_endereco += 1
            
            self.mais_par()
        # FOLLOW de mais_par é ')' -> Lambda

    # <corpo_f> -> <dc_loc> <comandos>
    def corpo_f(self):
        self.dc_loc()
        self.comandos()

    # <dc_loc> -> <dc_v> <mais_dcloc> | λ
    def dc_loc(self):
        # FIRST de dc_loc é $ident
        if self.token_atual and self.token_atual[1] == 'IDENT':
            self.dc_v()
            self.dc_loc() # Recursão para mais_dcloc
        # FOLLOW de dc_loc são os comandos (echo, if, while...)

    # <comandos> -> <comando> <mais_comandos>
    def comandos(self):
        # Enquanto o token atual estiver no FIRST de <comando>
        if self.token_atual and (self.token_atual[0] in ['echo', 'if', 'while'] or self.token_atual[1] == 'IDENT'):
            self.comando()
            self.comandos()
        # FOLLOW de <comandos> = {'}', '?>'} -> Lambda

    def comando(self):
        token = self.token_atual[0]
        
        if token == 'echo':
            self.eat('echo')
            nome_var = self.token_atual[0]
            self.eat('IDENT')
            self.eat('.')
            self.eat('PHP_EOL')
            self.eat(';')
            # Geração de código para imprimir
            if nome_var in self.tabela_simbolos:
                self.codigo_objeto.append(f"CRVL {self.tabela_simbolos[nome_var]}")
                self.codigo_objeto.append("IMPR")
            else: self.erro(f"Variável {nome_var} não declarada.")

        elif token == 'if':
            self.parse_if() # Vamos detalhar abaixo

        elif token == 'while':
            self.parse_while() # Vamos detalhar abaixo

        elif self.token_atual[1] == 'IDENT':
            # Atribuição ou Chamada de Função: $ident <restoIdent> ;
            nome = self.token_atual[0]
            self.eat('IDENT')
            self.restoIdent(nome)
            self.eat(';')
    
    def parse_while(self):
        self.eat('while')
        self.eat('(')
        
        inicio_while = len(self.codigo_objeto)
        self.condicao()
        
        self.eat(')')
        
        # 1. Reserva espaço para o DSVF
        pos_dsvf = len(self.codigo_objeto)
        self.codigo_objeto.append("") # Espaço para preencher

        self.eat('{')
        self.comandos()
        self.eat('}')
        
        # 2. Pulo de volta (DSVI) já sai com o número
        self.codigo_objeto.append(f"DSVI {inicio_while}")
        
        # 3. BACKPATCHING: Preenche o DSVF com o número na mesma linha
        self.codigo_objeto[pos_dsvf] = f"DSVF {len(self.codigo_objeto)}"

    def condicao(self):
        # <condicao> -> <expressao> <relacao> <expressao>
        self.expressao()
        op_rel = self.token_atual[0]
        self.eat('REL_OP')
        self.expressao()
        
        # Gera o código da comparação
        dict_rel = {'==': 'CPIG', '!=': 'CPNE', '>=': 'CPMI', '<=': 'CMAI', '>': 'CPME', '<': 'CPMA'}
        self.codigo_objeto.append(dict_rel[op_rel])
    
    def pfalsa(self):
        # <pfalsa> -> else { <comandos> } | λ
        if self.token_atual and self.token_atual[0] == 'else':
            self.eat('else')
            self.eat('{')
            self.comandos()
            self.eat('}')
        # Se não for 'else', é lambda.
    
    def parse_if(self):
        self.eat('if')
        self.eat('(')
        self.condicao()
        self.eat(')')
        
        # 1. Reserva para o DSVF
        pos_dsvf = len(self.codigo_objeto)
        self.codigo_objeto.append("") 
        
        self.eat('{')
        self.comandos()
        self.eat('}')
        
        # 2. Reserva para o DSVI (pular o else)
        pos_dsvi_pular_else = len(self.codigo_objeto)
        self.codigo_objeto.append("")
        
        # 3. Preenche o DSVF (vai para o início do else ou fim)
        self.codigo_objeto[pos_dsvf] = f"DSVF {len(self.codigo_objeto)}"
        
        self.pfalsa()
        
        # 4. Preenche o DSVI (vai para depois do else)
        self.codigo_objeto[pos_dsvi_pular_else] = f"DSVI {len(self.codigo_objeto)}"

    def restoIdent(self, nome):
        # <restoIdent> -> = <expressao> | <lista_arg>
        if self.token_atual[0] == '=':
            self.eat('=')
            self.expressao()
            if nome in self.tabela_simbolos:
                self.codigo_objeto.append(f"ARMZ {self.tabela_simbolos[nome]}")
            else:
                self.erro(f"Variável {nome} não declarada.")
        else:
            self.lista_arg()
            if nome in self.tabela_simbolos:
                # Chama a função pelo endereço guardado na tabela
                self.codigo_objeto.append(f"CHAM {self.tabela_simbolos[nome]}")
            else:
                self.erro(f"Função {nome} não declarada.")

    def lista_arg(self):
        self.eat('(')
        if self.token_atual[0] != ')':
            self.argumentos()
        self.eat(')')

    def argumentos(self):
        # <argumentos> -> <expressao> <mais_ident>
        self.expressao()
        self.mais_ident()

    def mais_ident(self):
        # <mais_ident> -> , <expressao> <mais_ident> | λ
        if self.token_atual and self.token_atual[0] == ',':
            self.eat(',')
            self.expressao()
            self.mais_ident()
    
    def salvar_arquivo(self, nome="codigo_objeto.txt"):
        try:
            with open(nome, "w") as f:
                for instrucao in self.codigo_objeto:
                    f.write(f"{instrucao}\n")
            print(f"\n[SUCESSO] Código objeto salvo em: {nome}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")
            