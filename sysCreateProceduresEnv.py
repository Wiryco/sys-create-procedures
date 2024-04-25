import pyodbc
import os
import time
import sys
import dotenv

dotenv.load_dotenv()

class createFileProcedure():
    def __init__(self):
        self.serverName = os.getenv('serverName')
        self.dataBase = os.getenv('dataBase')
        self.userName = os.getenv('userName')
        self.password = os.getenv('password')
        self.drive = os.getenv('driveConnection')
        self.path = os.getenv('pathSaveFiles')

    def databaseConnection(self):
        """
        Em caso de não preenchimento dos campos userName e password no .env, a função usa autenticação do Windows para conectar ao banco de dados
        """
        if self.userName and self.password:
            connection_string = (
                'Driver={' + self.drive + '};'
                f'Server=' + self.serverName + ';'
                f"Database=" + self.dataBase + ';'
                f'UID=' + self.userName + ';'
                f'PWD=' + self.password + ';'
                f"Trusted_Connection=no;"
            )

            try:
                conn = pyodbc.connect(connection_string)
                self.createTemporaryTable(conexao=conn)
            except Exception as ex:
                print(ex)
                print('\n')
                sys.exit('\nA aplicação foi encerrada!')
        else:
            connection_string = (
                'Driver={' + self.drive + '};'
                f'Server=' + self.serverName + ';'
                f"Database=" + self.dataBase + ';'
                f"Trusted_Connection=yes;"
            )

            try:
                conn = pyodbc.connect(connection_string)
                self.createTemporaryTable(conexao=conn)
            except Exception as ex:
                print(ex)
                print('\n')
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
        
        self.path += self.dataBase + '\\'

        if not os.path.exists(r'' + self.path):
            os.mkdir(r'' + self.path)  

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