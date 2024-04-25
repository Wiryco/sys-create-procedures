import pyodbc
import os
import time
import sys

class createFileProcedure():
    def __init__(self):
        self.servidor = ''
        self.banco = ''
        self.usuario = ''
        self.senha = ''
        self.path = ''

    def databaseConnection(self):
        self.servidor = input('\nQual o servidor que você deseja conectar?\n=> ')

        if not self.servidor:
            volta = input('\nNotei que você não preencheu os dados do servidor.\nDeseja voltar e preencher os parâmetros novamente? Responda S para Sim e N para Não.\n=>').upper()
            if volta == 'S':
                os.system('cls||clear')
                self.databaseConnection()
            else:
                sys.exit('\nA aplicação foi encerrada!')

        self.banco = input('\nQual o banco de dados a ser acessada no servidor ' + self.servidor + '?\n=> ').upper()

        if not self.banco:
            volta = input('\nNotei que você não preencheu os dados do banco de dados.\nDeseja voltar e preencher os parâmetros novamente? Responda S para Sim e N para Não.\n=>').upper()
            if volta == 'S':
                os.system('cls||clear')
                self.databaseConnection()
            else:
                sys.exit('\nA aplicação foi encerrada!')

        self.usuario = input('\nQual o seu usuário no banco ' + self.banco + '?\n=> ')

        if not self.usuario:
            volta = input('\nNotei que você não digitou os dados de usuário.\nDeseja voltar e preencher os parâmetros novamente? Responda S para Sim e N para Não.\n=>').upper()
            if volta == 'S':
                os.system('cls||clear')
                self.databaseConnection()
            else:
                sys.exit('\nA aplicação foi encerrada!')

        self.senha = input('\nQual a senha do usuário ' + self.usuario + ' no banco ' + self.banco + '?\n=> ')

        if not self.senha:
            volta = input('\nNotei que você não digitou a senha do seu usuário.\nDeseja voltar e preencher os parâmetros novamente? Responda S para Sim e N para Não.\n=>').upper()
            if volta == 'S':
                os.system('cls||clear')
                self.databaseConnection()
            else:
                sys.exit('\nA aplicação foi encerrada!')
            
        self.path = input('\nQual o caminho para salvar os arquivos que serão gerados?\n*** FAVOR NÃO ENVIAR COM \\ NO FINAL *** - Modelo: C:\\Teste \n=> ')
        
        if not self.path:
            volta = input('\nNotei que você não digitou o caminho onde os arquivos serão salvos.\nDeseja voltar e preencher os parâmetros novamente? Responda S para Sim e N para Não.\n=>').upper()
            if volta == 'S':
                os.system('cls||clear')
                self.databaseConnection()
            else:
                sys.exit('\nA aplicação foi encerrada!')

        if not os.path.exists(self.path + '\\'):
            print('O caminho informado não existe, mas estamos criando a pasta para dar sequência no script!\nFavor aguardar...')
            os.mkdir(self.path + '\\')
            
        os.system('cls||clear')

        try:
            conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                                'Server='+ self.servidor +';'
                                'Database='+ self.banco +';'
                                'UID='+ self.usuario +';'
                                'PWD='+ self.senha +';'
                                'Trusted_Connection=no;')

            print('\nConexão com o servidor ' + self.servidor + ', banco ' + self.banco +
                ' para o usuário ' + self.usuario + ' foi realizada com sucesso!\n')
            print('========================================================================================================================\n')

            self.createTemporaryTable(conexao=conn)
        except Exception as ex:
            print('\n')
            print(ex)
            print('\n')
            volta = input('\nAlguma informação que você digitou está incorreta.\nVocê deseja voltar e preencher os parâmetros novamente? Responda S para Sim e N para Não.\n=>').upper()
            if volta == 'S':
                os.system('cls||clear')
                self.databaseConnection()
            else:
                sys.exit('\nA aplicação foi encerrada!')


    def createTemporaryTable(self, conexao):
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
        
        self.path += '\\'

        if not os.path.exists(r'' + self.path + 'ERRO\\'):
            os.mkdir(r'' + self.path + 'ERRO\\')

        _file_ERRO = open(r'' + self.path + 'ERRO\\LOG_ERRO.txt', 'w+', encoding="utf-8")

        print('##########################################################################################')
        print('#                                                                                        #')
        print('######### Aguarde! O sistema está convertendo todas as procedures para arquivos. #########')
        print('#                                                                                        #\n')
        print(f'### Diretório onde esses arquivos estão sendo salvos => {self.path} ')
        print('#                                                                                        #')
        print('##########################################################################################')

        self.recursionControl(0, 500, conexao, _file_ERRO, self.maxTempProcedure(conexao))

    def maxTempProcedure(self, conexao):
        _cursor = conexao.cursor()
        sql = 'SELECT MAX(SEQUENCIAL) MAXIMO FROM #PROCEDURES'

        _cursor.execute(sql)
        maximo = _cursor.fetchall()
        data = [list(rows) for rows in maximo]

        for row in data:
            _max = row[0]

        return(_max)

    def filterTempProcedure(self, init, end, conexao):
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

    def createFileProcedure(self, list_p, position, conexao, _file):
        if position < len(list_p):
            cursor = conexao.cursor()

            sql = "sp_helptext '" + list_p[position] + "'"
            try:
                cursor.execute(sql)
                row = cursor.fetchall()
                data = [list(rows) for rows in row]
                _file = open(
                    r'' + self.path + list_p[position] + '.txt', 'w+', encoding="utf-8")

                for row in data:
                    _file.write(row[0].replace('\r\n', '\n'))

                self.createFileProcedure(list_p, position + 1, conexao, _file)
            except:
                _file.write(sql + '\n')
                self.createFileProcedure(list_p, position + 1, conexao, _file)

    def recursionControl(self, init, interval, conexao, _file, _max):
        if init < _max:
            self.createFileProcedure(self.filterTempProcedure(init, interval, conexao), 0, conexao, _file)
            
            self.recursionControl(init + 500, interval + 500, conexao, _file, _max)
        else:
            os.system('cls||clear')

            time.sleep(1)

            print('##########################################################################################')
            print('#                                                                                        #')
            print('####################### Arquivos de procedures criados com sucesso #######################')
            print('#                                                                                        #')
            print('####### Aguarde, o sistema esta executando um script para converter .txt para .sql #######')
            print('#                                                                                        #')
            print('##########################################################################################')

            os.chdir(r'' + self.path)
            os.system('ren *.txt *.sql')

            time.sleep(1)

            self.closeDataBase(conexao)
            sys.exit('\nA aplicação foi encerrada!')


    def closeDataBase(self, conexao):
        conexao.close()


if __name__ == '__main__':
    main = createFileProcedure()
    main.databaseConnection()