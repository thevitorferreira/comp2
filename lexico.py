class Lexico:
    
    def __init__(self, arquivo):
        with open(arquivo, 'r') as f:
            self.texto = f.read()
        self.posicao = 0
        self.linha = 1

    def prox_token(self):

        self._ignora_vazio_e_comentarios()

        if self.posicao >= len(self.texto):
            return None 
        
        if self.texto.startswith('<?php', self.posicao):
            self.posicao += 5
            return '<?php', 'T_PHP_OPEN', self.linha  
            
        if self.texto.startswith('?>', self.posicao):
            self.posicao += 2
            return '?>', 'T_PHP_CLOSE', self.linha
        
        
        if self.texto.startswith('floatval(readline())', self.posicao):
            token = 'floatval(readline())'
            self.posicao += len(token)
            return token, 'T_READLINE', self.linha

        char_atual = self.texto[self.posicao]

        if char_atual.isalpha() or char_atual == '$' or char_atual == '_':
            inicio = self.posicao 
            while self.posicao < len(self.texto) and (self.texto[self.posicao].isalnum() or self.texto[self.posicao] in '$_'):
                self.posicao += 1
            token = self.texto[inicio:self.posicao]
            if token in ['function', 'if', 'else', 'while', 'echo', '<?php', '?>']:
                return token, 'PALAVRA_RESERVADA', self.linha
            return token, 'IDENT', self.linha
        
        if char_atual.isdigit():
            inicio = self.posicao
            while self.posicao < len(self.texto) and (self.texto[self.posicao].isdigit() or self.texto[self.posicao] == '.'):
                self.posicao += 1
            return self.texto[inicio:self.posicao], 'NUMERO', self.linha
        
        if self.texto[self.posicao:self.posicao+2] in ['>=', '<=', '!=', '==']:
            token = self.texto[self.posicao:self.posicao+2]
            self.posicao += 2
            return token, 'REL_OP', self.linha
        
        if char_atual in "+-*/=();{},.":
            self.posicao += 1
            return char_atual, 'SIMBOLO', self.linha
        
        self.posicao += 1
        return char_atual, 'T_ERRO', self.linha
        

    def _ignora_vazio_e_comentarios(self):
        while self.posicao < len(self.texto):
            if self.texto[self.posicao] == '\n':
                self.linha += 1
                self.posicao += 1
            elif self.texto[self.posicao].isspace():
                self.posicao += 1
            elif self.texto[self.posicao:self.posicao+2] == '/*':
                while self.posicao < len(self.texto) and self.texto[self.posicao:self.posicao+2] != '*/':
                    self.posicao += 1
                self.posicao +=2 
            elif self.texto[self.posicao:self.posicao+2] == '//':
                while self.posicao < len(self.texto) and self.texto[self.posicao] != '\n':
                    self.posicao += 1
            else:
                break 