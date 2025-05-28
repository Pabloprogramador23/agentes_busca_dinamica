import mysql.connector
import pandas as pd
import os
from db_config import get_db_connection_params

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS vendas (
    `Data da Venda` DATE,
    `ID da Venda` VARCHAR(255) PRIMARY KEY,
    `ID do Cliente` VARCHAR(255),
    `Nome do Cliente` VARCHAR(255),
    `Produto` VARCHAR(255),
    `ID do Produto` VARCHAR(255),
    `Categoria` VARCHAR(255),
    `Preço Unitário` DECIMAL(10, 2),
    `Quantidade` INT,
    `Valor Total` DECIMAL(10, 2),
    `Meio de Pagamento` VARCHAR(255),
    `Vendedor` VARCHAR(255),
    `Região` VARCHAR(255),
    `Status da Venda` VARCHAR(255)
);
"""

def create_vendas_table(cursor):
    """Creates the 'vendas' table if it doesn't exist."""
    try:
        cursor.execute(CREATE_TABLE_SQL)
        print("Tabela 'vendas' verificada/criada com sucesso.")
    except mysql.connector.Error as err:
        print(f"Erro ao criar tabela 'vendas': {err}")
        raise

def insert_data_from_csv(cursor, csv_filepath):
    """Reads data from a CSV file and inserts it into the 'vendas' table."""
    try:
        if not os.path.exists(csv_filepath):
            print(f"Erro: Arquivo CSV '{csv_filepath}' não encontrado.")
            return

        df = pd.read_csv(csv_filepath)

        # Replace NaN with None for SQL NULL
        df = df.where(pd.notnull(df), None)

        # Define the column order as in the table for the INSERT statement
        # (Assuming CSV column names match table column names)
        table_columns = [
            "Data da Venda", "ID da Venda", "ID do Cliente", "Nome do Cliente",
            "Produto", "ID do Produto", "Categoria", "Preço Unitário",
            "Quantidade", "Valor Total", "Meio de Pagamento", "Vendedor",
            "Região", "Status da Venda"
        ]
        
        # Ensure all expected columns are in the DataFrame
        for col in table_columns:
            if col not in df.columns:
                print(f"Erro: Coluna '{col}' esperada não encontrada no arquivo CSV '{csv_filepath}'.")
                return

        insert_sql = f"""
        INSERT INTO vendas ({', '.join(f"`{col}`" for col in table_columns)})
        VALUES ({', '.join(['%s'] * len(table_columns))})
        ON DUPLICATE KEY UPDATE `ID da Venda`=`ID da Venda`; 
        """
        # The ON DUPLICATE KEY UPDATE part is a simple way to ignore inserts 
        # if the primary key (ID da Venda) already exists.
        # More sophisticated handling might be needed for other columns.

        rows_inserted = 0
        rows_skipped = 0
        for index, row in df.iterrows():
            try:
                # Convert data types if necessary
                # Pandas usually handles dates well when reading CSV, but ensure format is YYYY-MM-DD
                # For 'Data da Venda', if it's not already a string in 'YYYY-MM-DD' or a datetime object:
                if row["Data da Venda"] is not None and not isinstance(row["Data da Venda"], str):
                     # Assuming it might be a pandas Timestamp
                    row["Data da Venda"] = pd.to_datetime(row["Data da Venda"]).strftime('%Y-%m-%d')
                
                # Ensure numeric types are correct, pandas usually handles this for DECIMAL and INT
                # when reading CSV, but explicit conversion can be added if issues arise.
                # Example: row['Preço Unitário'] = Decimal(row['Preço Unitário']) if needed

                data_tuple = tuple(row[col] for col in table_columns)
                cursor.execute(insert_sql, data_tuple)
                if cursor.rowcount > 0: # rowcount is 1 for insert, 2 for update on duplicate
                    rows_inserted +=1
                else: # rowcount is 0 if ON DUPLICATE KEY did nothing (no update needed)
                    rows_skipped +=1 # Or handle as an update if values could change

            except mysql.connector.Error as err:
                print(f"Erro ao inserir linha {index + 2}: {row.to_dict()}")
                print(f"  Erro MySQL: {err}")
            except Exception as e:
                print(f"Erro inesperado ao processar linha {index + 2}: {row.to_dict()}")
                print(f"  Erro: {e}")


        print(f"Inserção de dados do CSV concluída. {rows_inserted} linhas inseridas, {rows_skipped} linhas ignoradas/atualizadas.")

    except pd.errors.EmptyDataError:
        print(f"Erro: O arquivo CSV '{csv_filepath}' está vazio.")
    except Exception as e:
        print(f"Erro ao processar o arquivo CSV '{csv_filepath}': {e}")
        raise

if __name__ == "__main__":
    db_connection = None
    cursor = None
    try:
        print("Iniciando configuração do banco de dados...")
        db_params = get_db_connection_params()

        if not all(db_params.values()):
            print("Erro: Parâmetros de conexão com o banco de dados não estão totalmente configurados no arquivo .env.")
            exit(1) # Exit if DB params are not set

        # Establish MariaDB connection
        db_connection = mysql.connector.connect(
            host=db_params['host'],
            user=db_params['user'],
            password=db_params['password'],
            database=db_params['database']
        )
        cursor = db_connection.cursor()
        print("Conexão com o banco de dados estabelecida.")

        # Create 'vendas' table
        create_vendas_table(cursor)

        # Define CSV file path and insert data
        csv_file_path = 'vendas_ficticias_brasil.csv'
        if not os.path.exists(csv_file_path):
            print(f"AVISO: Arquivo CSV '{csv_file_path}' não encontrado. A tabela 'vendas' foi criada, mas nenhum dado foi inserido.")
        else:
            print(f"Iniciando inserção de dados do arquivo '{csv_file_path}'...")
            insert_data_from_csv(cursor, csv_file_path)
            db_connection.commit()
            print("Dados do CSV inseridos e transação commitada.")

        print("Configuração do banco de dados concluída com sucesso.")

    except mysql.connector.Error as err:
        print(f"Erro de banco de dados durante a configuração: {err}")
        if db_connection and db_connection.is_connected():
            db_connection.rollback() # Rollback changes if any error occurs
            print("Rollback da transação realizado.")
    except Exception as e:
        print(f"Um erro inesperado ocorreu durante a configuração: {e}")
        if db_connection and db_connection.is_connected():
            db_connection.rollback()
            print("Rollback da transação realizado devido a erro inesperado.")
    finally:
        if cursor:
            cursor.close()
            print("Cursor fechado.")
        if db_connection and db_connection.is_connected():
            db_connection.close()
            print("Conexão com o banco de dados fechada.")
