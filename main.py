import sys
from lexico import Lexico
from sintatico_semantico import Sintatico

from maqhipo import executar_maqhipo 

def main():
    if len(sys.argv) < 2:
        return

    arquivo_entrada = sys.argv[1]
    arquivo_objeto = "codigo_objeto.txt"

    try:
        lex = Lexico(arquivo_entrada)
        sin = Sintatico(lex)
        
        sin.programa()
        sin.salvar_arquivo(arquivo_objeto)
        
        executar_maqhipo(arquivo_objeto)

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()