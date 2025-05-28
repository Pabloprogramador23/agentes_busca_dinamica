
import os
from crewai import Agent, Task, Crew, Process
from custom_tool_vendas import QueryCSV

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

        self.tool_file_path = os.path.join('vendas_ficticias_brasil.csv')
        self.crew = None
        #self.llm = "deepseek/deepseek-reasoner"
        self.llm = "gpt-4o-mini"
        
        self._setup_crew()

    def _setup_crew(self):
        # Inicializa a ferramenta de vendas
        vendas_tool = QueryCSV(file_path=self.tool_file_path)




        # Define o agente Analista de Dados
        analista_dados = Agent(
            role="Analista de Dados",
            goal="Criar códigos em Python que executam uma consulta em um determinado CSV",
            backstory=(
                """Você é um analista de dados experiente, capaz de escrever códigos em Python 
                capazes de extrair informações solicitadas de conjuntos de dados estruturados como arquivos CSV."""
            ),
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
        task_csv = Task(
                description=(
                """
                Dada a solicitação delimitada por <query>, crie um código python que 
                irá ler o arquivo exatamente o código delimitado em <abertura>. Você 
                deve completar o código que começou em abertura de modo a atender
                a <query>. Chame a ferramenta QueryCSV para executar o código. Em <exemplo>
                tem um exemplo de um código que você deve gerar. Veja que o exemplo ja tem <abertura> nele. 
                
                <query>
                colunas=(Data da Venda,ID da Venda,ID do Cliente,Nome do Cliente,Produto,ID do Produto,Categoria,Preço Unitário,Quantidade,Valor Total,Meio de Pagamento,Vendedor,Região,Status da Venda)
                Com base nas colunas do CSV vendas_ficticias_brasil.csv escreva um código pandas para essa solicitação:\n\n
                {query}
                </query>
                
                <abertura>
                csv = os.path.join('vendas_ficticias_brasil.csv')
                df = pd.read_csv(csv)
                <abertura>
                
                <exemplo>
                import os
                import pandas as pd

                csv = os.path.join('vendas_ficticias_brasil.csv')
                # Carregue o arquivo CSV no DataFrame
                df = pd.read_csv(csv)
                
                # Verificar se o arquivo existe antes de tentar carregá-lo
                if not os.path.exists(csv):
                    raise FileNotFoundError(f"O arquivo vendas_ficticias_brasil.csv não foi encontrado. Verifique o caminho!")


                # Agrupar os dados por 'Região' e somar o 'Valor Total' para cada grupo
                vendas_por_regiao = df.groupby('Região')['Valor Total'].sum()

                # Identificar a região com maior valor total de vendas
                regiao_mais_vendeu = vendas_por_regiao.idxmax()
                valor_total_mais_vendeu = vendas_por_regiao.max()

                resultado = f'A região que mais vendeu foi' + regiao_mais_vendeu + 'com um total de R$' + valor_total_mais_vendeu.'
                <exemplo>
                
                no código, sempre atribua o resultado da a variável "resultado" como mostra o <exemplo>
                        
                """
                ),
                expected_output="Um texto em um parágrafo sobre: {query}.",
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
                context=[task_csv]
            )
        

        # Configura o Crew
        self.crew = Crew(
            agents=[analista_dados, redator],
            tasks=[task_csv, write_task],
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
