import pyodbc
import os
import time
import sys


def conexao_bd():
    servidor, banco, usuario, senha, path = '', '', '', '', ''

    servidor = input('\nQual o servidor que você deseja conectar?\n=> ')

    if not servidor:
        volta = input('\nNotei que você não preencheu os dados do servidor.\nDeseja voltar e preencher os parâmetros novamente? Responda S para Sim e N para Não.\n=>').upper()
        if volta == 'S':
            os.system('cls||clear')
            conexao_bd()
        else:
            sys.exit('\nA aplicação foi encerrada!')

    banco = input('\nQual o banco de dados a ser acessada no servidor ' +
                  servidor + '?\n=> ').upper()

    if not banco:
        volta = input('\nNotei que você não preencheu os dados do banco de dados.\nDeseja voltar e preencher os parâmetros novamente? Responda S para Sim e N para Não.\n=>').upper()
        if volta == 'S':
            os.system('cls||clear')
            conexao_bd()
        else:
            sys.exit('\nA aplicação foi encerrada!')

    usuario = input('\nQual o seu usuário no banco ' + banco + '?\n=> ')

    if not usuario:
        volta = input('\nNotei que você não digitou os dados de usuário.\nDeseja voltar e preencher os parâmetros novamente? Responda S para Sim e N para Não.\n=>').upper()
        if volta == 'S':
            os.system('cls||clear')
            conexao_bd()
        else:
            sys.exit('\nA aplicação foi encerrada!')

    senha = input('\nQual a senha do usuário ' + usuario + ' no banco ' + banco + '?\n=> ')

    if not senha:
        volta = input('\nNotei que você não digitou a senha do seu usuário.\nDeseja voltar e preencher os parâmetros novamente? Responda S para Sim e N para Não.\n=>').upper()
        if volta == 'S':
            os.system('cls||clear')
            conexao_bd()
        else:
            sys.exit('\nA aplicação foi encerrada!')
        
    path = input('\nQual o caminho para salvar os arquivos que serão gerados?\n*** FAVOR NÃO ENVIAR COM \\ NO FINAL *** - Modelo: C:\\Teste \n=> ')
    
    if not path:
        volta = input('\nNotei que você não digitou o caminho onde os arquivos serão salvos.\nDeseja voltar e preencher os parâmetros novamente? Responda S para Sim e N para Não.\n=>').upper()
        if volta == 'S':
            os.system('cls||clear')
            conexao_bd()
        else:
            sys.exit('\nA aplicação foi encerrada!')
        
    os.system('cls||clear')

    try:
        conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                              'Server='+servidor+';'
                              'Database='+banco+';'
                              'UID='+usuario+';'
                              'PWD='+senha+';'
                              'Trusted_Connection=no;')

        print('\nConexão com o servidor ' + servidor + ', banco ' + banco +
              ' para o usuário ' + usuario + ' foi realizada com sucesso!\n')
        print('========================================================================================================================\n')

        create_temporary_table(conexao=conn, path=path)
    except Exception as ex:
        print('\n')
        print(ex)
        print('\n')
        volta = input('\nAlguma informação que você digitou está incorreta.\nVocê deseja voltar e preencher os parâmetros novamente? Responda S para Sim e N para Não.\n=>').upper()
        if volta == 'S':
            os.system('cls||clear')
            conexao_bd()
        else:
            sys.exit('\nA aplicação foi encerrada!')


def create_temporary_table(conexao, path):
    cursor = conexao.cursor()

    sql_p = 'SELECT '
    sql_p += 'ROW_NUMBER() OVER (ORDER BY B.NAME) SEQUENCIAL, '
    sql_p += "CONCAT(C.NAME, '.', B.NAME) DS_OBJETO "
    sql_p += 'INTO #PROCEDURES '
    sql_p += 'FROM '
    sql_p += 'SYS.SQL_MODULES A WITH(NOLOCK) '
    sql_p += 'JOIN SYS.OBJECTS B WITH(NOLOCK) ON A.[OBJECT_ID] = B.[OBJECT_ID] '
    sql_p += 'JOIN SYS.SCHEMAS C WITH(NOLOCK) ON B.[SCHEMA_ID] = C.[SCHEMA_ID] '
    sql_p += "WHERE B.[TYPE] = 'P'"

    cursor.execute(sql_p)
    
    path += '\\'

    if not os.path.exists(r'' + path + 'ERRO\\'):
        os.mkdir(r'' + path + 'ERRO\\')

    _file_ERRO = open(r'' + path + 'ERRO\\LOG_ERRO.txt',
                      'w+', encoding="utf-8")

    print('##########################################################################################')
    print('#                                                                                        #')
    print('######### Aguarde! O sistema está convertendo todas as procedures para arquivos. #########')
    print('#                                                                                        #\n')
    print(f'### Diretório onde esses arquivos estão sendo salvos => {path} ')
    print('#                                                                                        #')
    print('##########################################################################################')

    control_recursion(0, 500, conexao, _file_ERRO,
                      path, max_temp_procedure(conexao))


def max_temp_procedure(conexao):
    _cursor = conexao.cursor()
    sql = 'SELECT MAX(SEQUENCIAL) MAXIMO FROM #PROCEDURES'

    _cursor.execute(sql)
    maximo = _cursor.fetchall()
    data = [list(rows) for rows in maximo]

    for row in data:
        _max = row[0]

    return(_max)


def filter_temp_procedure(init, end, conexao):
    list_all_procedures = list()
    _cursor = conexao.cursor()
    sql = 'SELECT DS_OBJETO '
    sql += 'FROM #PROCEDURES '
    sql += 'WHERE SEQUENCIAL >= ' + \
        str(init) + ' AND SEQUENCIAL < ' + str(end) + ''

    _cursor.execute(sql)
    all_procedures = _cursor.fetchall()
    data = [list(rows) for rows in all_procedures]

    for row in data:
        list_all_procedures.append(row[0])

    return(list_all_procedures)


def create_procedure_file(list_p, position, conexao, _file, path):
    if position < len(list_p):
        cursor = conexao.cursor()

        sql = "sp_helptext '" + list_p[position] + "'"
        try:
            cursor.execute(sql)
            row = cursor.fetchall()
            data = [list(rows) for rows in row]
            _file = open(
                r'' + path + list_p[position] + '.txt', 'w+', encoding="utf-8")

            for row in data:
                _file.write(row[0].replace('\r\n', '\n'))

            create_procedure_file(list_p, position + 1, conexao, _file, path)
        except:
            _file.write(sql + '\n')
            create_procedure_file(list_p, position + 1, conexao, _file, path)


def control_recursion(init, interval, conexao, _file, path, _max):
    if init < _max:
        create_procedure_file(filter_temp_procedure(
            init, interval, conexao), 0, conexao, _file, path)
        
        control_recursion(init + 500, interval + 500,
                          conexao, _file, path, _max)
    else:
        os.system('cls||clear')

        time.sleep(1)

        print('##########################################################################################')
        print('#                                                                                        #')
        print('####################### Arquivos de procedures criados com sucesso #######################')
        print('#                                                                                        #')
        print('######## Aguarde, o sistema esta executando um script para converta .txt para .sql #######')
        print('#                                                                                        #')
        print('##########################################################################################')

        os.chdir(r'' + path)
        os.system('ren *.txt *.sql')

        time.sleep(1)

        close_bd(conexao)
        sys.exit('\nA aplicação foi encerrada!')


def close_bd(conexao):
    conexao.close()


if __name__ == '__main__':
    conexao_bd()
