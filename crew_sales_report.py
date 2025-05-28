
import os
from crewai import Agent, Task, Crew, Process
from custom_tool_vendas import ExecutePythonCodeTool

from dotenv import load_dotenv



# Carregar variáveis de ambiente
load_dotenv()

class SalesReportCrew:
    
    def __init__(self):
        """
        Inicializa o Crew responsável por gerar relatórios baseados em dados de vendas.

        :param api_key: Chave de API necessária para o CrewAI.
        :param tool_file_path: Caminho para o arquivo CSV usado pela ToolVendas.
        :param verbose: Define se os agentes devem executar no modo detalhado.
        """

        self.crew = None
        #self.llm = "deepseek/deepseek-reasoner"
        self.llm = "gpt-4o-mini"
        
        self._setup_crew()

    def _setup_crew(self):
        # Inicializa a ferramenta de vendas
        vendas_tool = ExecutePythonCodeTool()




        # Define o agente Analista de Dados
        analista_dados = Agent(
            role="Analista de Dados",
            goal="Criar scripts Python concisos para interagir com um banco de dados MariaDB (usando `mysql.connector` e `db_config.get_db_connection_params()`) para extrair e processar informações da tabela 'vendas', com base na solicitação do usuário. O script deve atribuir o resultado final (uma string ou representação de string dos dados) a uma variável chamada `resultado`.",
            backstory="Você é um programador Python experiente, especialista em automação de tarefas de dados e interação com bancos de dados SQL. Você é proficiente em escrever scripts Python que usam `mysql.connector` para se conectar a MariaDB, buscar detalhes de conexão de `db_config.get_db_connection_params()`, executar consultas SQL e processar os resultados. Seus scripts são limpos, eficientes e sempre definem uma variável `resultado` com a saída final.",
            memory=True,
            verbose=True,
            llm=self.llm
        )

        # Define o agente Redator
        redator = Agent(
            role="Redator",
            goal="Escrever um parágrafo baseado no contexto fornecido pelo Analista de Dados e pela solicitação {query}.",
            backstory=(
                """Você é um escritor habilidoso, capaz de transformar dados técnicos e análises 
                em textos claros e cativantes, sempre mantendo um tom formal e direcionado ao chefe."""
            ),
            memory=False,
            verbose=True,
            llm=self.llm
        )

        # Define as tarefas
        task_python_db_query = Task(
            description=(
                """
                Dada a solicitação do usuário delimitada por <query>, crie um script Python para consultar a tabela 'vendas' em um banco de dados MariaDB.

                O script Python gerado DEVE:
                1. Importar `mysql.connector` e `get_db_connection_params` from `db_config`. Podem ser importados outros módulos como `pandas` se for util.
                2. Chamar `db_params = get_db_connection_params()` para obter os detalhes da conexão.
                3. Verificar se todos os `db_params` foram carregados (host, user, password, database). Se não, definir `resultado` como uma mensagem de erro apropriada.
                4. Estabelecer uma conexão com o banco de dados MariaDB usando `mysql.connector.connect(**db_params)`.
                5. Construir a consulta SQL necessária para atender à <query> do usuário. A tabela 'vendas' tem as colunas: `Data da Venda`, `ID da Venda`, `ID do Cliente`, `Nome do Cliente`, `Produto`, `ID do Produto`, `Categoria`, `Preço Unitário`, `Quantidade`, `Valor Total`, `Meio de Pagamento`, `Vendedor`, `Região`, `Status da Venda`.
                6. Executar a consulta SQL.
                7. Buscar os resultados (por exemplo, para uma lista de tuplas ou um DataFrame pandas se a análise for complexa).
                8. Formatar os resultados em uma string clara e concisa.
                9. **Atribuir esta string final à variável `resultado`**. Esta variável é o que será retornado pela ferramenta.
                10. Incluir tratamento de erros (blocos try/except) para operações de banco de dados e outras partes do script. Em caso de erro, `resultado` deve conter uma mensagem de erro descritiva.
                11. Fechar o cursor e a conexão do banco de dados em um bloco `finally`.
                12. Usar `LIMIT` nas consultas SQL para restringir a saída a um máximo de 20 resultados, a menos que a <query> peça explicitamente por todos os dados ou um número diferente.

                <query>
                {query}
                </query>

                <exemplo_solicitacao>
                Qual foi o produto mais vendido em termos de quantidade?
                </exemplo_solicitacao>

                <exemplo_codigo_python>
                import mysql.connector
                from db_config import get_db_connection_params
                import pandas as pd # Opcional, mas pode ser útil

                resultado = ""
                cnx = None
                cursor = None
                try:
                    db_params = get_db_connection_params()
                    if not all(db_params.get(key) for key in ['host', 'user', 'password', 'database']):
                        resultado = "Erro: Parâmetros de conexão com o banco de dados não configurados completamente no .env."
                    else:
                        cnx = mysql.connector.connect(**db_params)
                        cursor = cnx.cursor()
                        
                        query = """
                        SELECT Produto, SUM(Quantidade) AS TotalQuantidade
                        FROM vendas
                        GROUP BY Produto
                        ORDER BY TotalQuantidade DESC
                        LIMIT 1;
                        """
                        cursor.execute(query)
                        data = cursor.fetchall()

                        if data:
                            # Exemplo de formatação do resultado
                            df = pd.DataFrame(data, columns=[i[0] for i in cursor.description])
                            resultado = f"O produto mais vendido em quantidade foi: {df.iloc[0]['Produto']} com {df.iloc[0]['TotalQuantidade']} unidades."
                        else:
                            resultado = "Nenhum produto encontrado."
                    
                except mysql.connector.Error as err:
                    resultado = f"Erro de banco de dados: {err}"
                except Exception as e:
                    resultado = f"Ocorreu um erro inesperado: {e}"
                finally:
                    if cursor is not None:
                        cursor.close()
                    if cnx is not None and cnx.is_connected():
                        cnx.close()
                </exemplo_codigo_python>

                Certifique-se de que seu script Python esteja completo, correto e atribua a saída final à variável `resultado`.
                """
            ),
            expected_output="Um script Python que atenda à solicitação {query} e atribua o resultado a uma variável 'resultado'.",
            agent=analista_dados,
            tools=[vendas_tool]
        )
            
        write_task = Task(
                description=(
                    """
                    Use o contexto fornecido pela pesquisa do agente 'analista_dados' para escrever um parágrafo
                    que responda à solicitação em {query}. O texto deve sempre começar com 'Oi Chefe' e explicar
                    a resposta da maneira mais clara e informativa possível. quando for escrever algum número de valores 
                    em reais, escreva por extenso.
                    """
                ),
                expected_output=(
                    "Um parágrafo começando com 'Oi Chefe', explicando a resposta à solicitação {query}."
                ),
                agent=redator,
                context=[task_python_db_query]
            )
        

        # Configura o Crew
        self.crew = Crew(
            agents=[analista_dados, redator],
            tasks=[task_python_db_query, write_task],
            process=Process.sequential
        )

    def kickoff(self, query):
        """
        Executa o Crew para processar uma consulta e gerar um relatório.

        :param query: Consulta a ser respondida.
        :return: Relatório gerado pelo Crew.
        """
        result = self.crew.kickoff(inputs={"query": query})
        return result.raw
