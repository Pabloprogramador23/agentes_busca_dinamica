
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv



# Carregar variáveis de ambiente
load_dotenv()

class FacadeCrew:
    def __init__(self):
        # Configuração da chave de API
        self.agent = None
        self.task = None
        self.crew = None
        self.llm = "gpt-4o-mini"
        
        self._setup_crew()

    def _setup_crew(self):
        # Configurar o agente
        self.agent = Agent(
            role="Classificador de Texto",
            goal=(
                "Classificar um texto em duas categorias: "
                "'Vendas' ou 'trivialidades'"
            ),
            backstory=(
                "Você é um especialista em análise de linguagem, capaz de interpretar textos "
                "e classificá-los de acordo com o contexto: vendas ou trivialidades. A palavra deve estar em minúsculas."
            ),
            memory=False,
            verbose=True,
            llm=self.llm
        )

        # Configurar a tarefa
        self.task = Task(
            description=(
                r"""Determine se o texto delimitado por <texto> ele fala sobre: 
                'vendas' (assuntos relacionados a produtos, clientes, etc.), 
                
                'trivialidades' (qualquer outro tema). 
                Forneça uma classificação com somente uma palavra: 'vendas' ou 'trivialidades. A palavra deve estar em minúsculas.'.
                <texto>
                    {text}
                </texto>
                """
            ),
            expected_output=(
                "Retorne somente uma das categorias: 'vendas' ou 'trivialidades'. Não precisa retornar as aspas."
            ),
            agent=self.agent
        )

        # Configurar o crew
        self.crew = Crew(
            agents=[self.agent],
            tasks=[self.task],
            process=Process.sequential
        )

    def kickoff(self, text):
        """
        Classifica o texto fornecido em uma das três categorias: 
        'Vendas', 'Base de Dados de Vendas', ou 'Outro Assunto'.

        :param text: Texto a ser classificado.
        :return: Classificação e justificativa.
        """
        result = self.crew.kickoff(inputs={"text": text})
        return result.raw

