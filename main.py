import argparse
import os
from datetime import datetime
from time import sleep
import re

# Função para determinar o ano do diário a partir do arquivo
def determinar_ano_diario(nome_arquivo):
    formatos_data = ['%m/%d/%y, %H:%M', '%d/%m/%Y %H:%M']  # Adicionar os formatos de data conhecidos
    with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
        for linha in arquivo:
            if linha.strip():  # Verificar se a linha não está vazia
                data = linha.split(' - ')[0].strip()  # Extrair a data do início da linha e remover espaços em branco
                for formato in formatos_data:
                    try:
                        data_parseada = datetime.strptime(data, formato)
                        return data_parseada.year, formato  # Retornar o ano e o formato da data
                    except ValueError:
                        continue  # Se a data não puder ser parseada, continuar para a próxima tentativa
    # Se não for possível determinar o ano, retornar None
    return None, None

# Função para ler o arquivo de texto e retornar um dicionário onde as chaves são os dias
# e os valores são tuplas contendo a data e os textos do diário
def ler_diario(nome_arquivo, formato_data):
    with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
        linhas = arquivo.readlines()
        diario = {}
        dia = None
        data_hora_atual = None
        texto = []

        for linha in linhas:
            if 'Dia #' in linha:
                if dia is not None:
                    diario[dia] = (data_hora_atual, processar_texto('\n'.join(texto)))
                data_hora_atual = linha.split(' - ')[0].strip()  # Extrair a data e hora da linha
                data_hora_atual = datetime.strptime(data_hora_atual, formato_data)  # Converter a data e hora para datetime
                dia = int(linha.split('Dia #', 1)[1].split(' ')[0])  # Extrair o número do dia
                texto = [linha.split(': ', 1)[1].strip()]  # Inicializar o texto com a primeira linha
            elif dia is not None:
                texto.append(linha.strip())

        if dia is not None:
            diario[dia] = (data_hora_atual, processar_texto('\n'.join(texto)))

        return diario

# Função para substituir hashtags (exceto a primeira) por "(hashtag)"
def processar_texto(texto):
    partes = re.split(r'(#)', texto)  # Divide o texto por '#'
    novo_texto = []
    encontrou_primeira_hashtag = False

    for parte in partes:
        if parte == '#' and not encontrou_primeira_hashtag:
            encontrou_primeira_hashtag = True
            novo_texto.append(parte)
        elif parte == '#':
            novo_texto.append('(hashtag)')
        else:
            novo_texto.append(parte)

    return ''.join(novo_texto)

# Função para criar um arquivo Markdown com o título e conteúdo do diário referente ao dia especificado
def criar_arquivo_markdown(diario, numero_dia, caminho_base):
    if numero_dia in diario:
        data_hora_diario, texto = diario[numero_dia]
        nome_arquivo = f"Dia {numero_dia} ({data_hora_diario.strftime('%d-%m-%Y %H-%M')}).md"  # Substituir ':' por '-'
        nome_pasta = f"Dia {numero_dia} ({data_hora_diario.strftime('%d-%m-%Y %H-%M')})"  # Nome da pasta
        caminho_pasta = os.path.join(caminho_base, nome_pasta)
        
        os.makedirs(caminho_pasta, exist_ok=True)  # Criar a pasta
        
        caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
        
        with open(caminho_completo, 'w', encoding='utf-8') as arquivo:
            arquivo.write(f"{texto}")  # Escrever título e conteúdo no arquivo
        print(f"Arquivo Markdown '{caminho_completo}' criado com sucesso.")
    else:
        print("Dia não encontrado no diário.")

def main():
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description='Cria arquivos Markdown a partir de um diário em texto.')
    parser.add_argument('--arquivo', type=str, required=True, help='Nome do arquivo de diário em texto')
    parser.add_argument('--caminho', type=str, required=True, help='Caminho onde os arquivos Markdown serão salvos')
    parser.add_argument('--nome_pasta', type=str, required=True, help='Nome da pasta onde os arquivos Markdown serão salvos')
    args = parser.parse_args()

    # Determinar o ano e o formato do diário
    ano_diario, formato_data = determinar_ano_diario(args.arquivo)

    if ano_diario is None:
        print("Não foi possível determinar o ano do diário.")
        return

    # Criar diretório base com o nome especificado
    caminho_base = os.path.join(args.caminho, args.nome_pasta)
    os.makedirs(caminho_base, exist_ok=True)

    # Ler o diário do arquivo
    diario = ler_diario(args.arquivo, formato_data)

    # Criar arquivo Markdown para cada dia do diário
    for numero_dia in diario.keys():
        criar_arquivo_markdown(diario, numero_dia, caminho_base)
        sleep(0.1)  # Atraso de 0,1 segundos entre a criação de cada arquivo

if __name__ == "__main__":
    main()
