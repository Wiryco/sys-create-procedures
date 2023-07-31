# Documentação - Cria arquivos de procedures

---

## Descrição

O algoritmo *Cria arquivos de procedures* é responsável por criar arquivos .sql contendo o código de todas as procedures existentes em um banco de dados. Ele solicita ao usuário as informações de conexão com o banco de dados, a pasta onde os arquivos serão salvos e, em seguida, extrai as procedures e as salva individualmente em arquivos .txt. Por fim, o algoritmo utiliza um comando cmd para converter esses arquivos .txt em arquivos .sql prontos para uso.

## Requisitos

Antes de executar o algoritmo, certifique-se de atender aos seguintes requisitos:

1. Ter o Python instalado na versão mais recente. Caso não tenha, você pode baixar o Python em [python.org](https://www.python.org/).

2. Instalar as bibliotecas necessárias através do pip. Caso você ainda não as tenha, utilize os seguintes comandos para instalar individualmente:

```bash
pip install pyodbc
pip install os
pip install time
pip install sys
```

## Permissões no Banco de Dados
O usuário informado para autenticação no banco de dados deve possuir permissões adequadas para acessar as seguintes tabelas de sistema do SQL:

```sql
GRANT SELECT ON SYS.SQL_MODULES TO seu_usuario;
GRANT SELECT ON SYS.OBJECTS TO seu_usuario;
GRANT SELECT ON SYS.SCHEMAS TO seu_usuario;
```

## Funcionamento
Para executar a ferramenta, siga os passos abaixo:
1. Certifique-se de ter atendido aos requisitos mencionados acima, incluindo a instalação das bibliotecas necessárias.
2. Baixe o arquivo *sys_create_procedures.py* para a sua máquina.
3. Abra um terminal ou prompt de comando na pasta onde o arquivo *sys_create_procedures.py* está localizado.
4. Execute o seguinte comando para iniciar a ferramenta:
   ```bash
   python sys_create_procedures.py
   ```
5. Ao executar o script, o algoritmo solicitará as seguintes informações do usuário:
   - Host do banco de dados.
   - Nome de usuário para autenticação.
   - Senha do usuário.
   - Nome do banco de dados a ser acessado.
   - Pasta onde os arquivos .sql serão salvos.
6. Com as informações de conexão fornecidas, o algoritmo se conectará ao banco de dados e extrairá todas as procedures usando o comando *sp_helptext*.
7. As procedures serão salvas individualmente em arquivos .txt na pasta especificada pelo usuário.
8. O algoritmo, então, executará um comando cmd para converter cada arquivo .txt em um arquivo .sql pronto para uso.
9. Ao finalizar a criação dos arquivos .sql, a aplicação será encerrada e o usuário terá acesso a todos os códigos das procedures do banco de dados em arquivos separados.

## Considerações Finais
O algoritmo *sys_create_procesures.py* é uma ferramenta útil para extrair e armazenar as procedures de um banco de dados em arquivos .sql. Certifique-se de atender aos requisitos e de que o usuário possua as permissões necessárias no banco de dados para garantir o correto funcionamento da aplicação.

Esperamos que essa ferramenta seja útil para suas atividades de desenvolvimento e análise de banco de dados!
