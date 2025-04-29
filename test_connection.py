import pymysql

try:
    connection = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='root123',
        database='agromarketplace',
        port=3306
    )
    print("Conexão bem sucedida!")
    connection.close()
except Exception as e:
    print(f"Erro ao conectar: {e}") 