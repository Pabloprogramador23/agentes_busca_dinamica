import os
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class TalkingCrew:
    def __init__(self, verbose=True, memory=True):
        """
        Inicializa a configuração do agente de transcrição.
        
        :param api_key: Chave da API OpenAI.
        :param verbose: Define se o agente deve ser detalhista nos logs.
        :param memory: Define se o agente deve ter memória ativa.
        """
        
        self.llm = "gpt-4o-mini"
        
        self.agent = Agent(
            role="Processador de transcrições",
            goal="Receber uma transcrição de áudio como texto e produzir uma resposta relevante e coerente.",
            backstory="Especialista em compreender contextos e responder com clareza.",
            memory=memory,
            verbose=verbose,
            llm=self.llm
        )

        self.task = Task(
            description=(
                "Analise o seguinte texto de transcrição e forneça uma resposta com base nas informações apresentadas: "
                "{transcription_text}. A resposta deve ser clara e objetiva. Responda sempre com 'Oi chefe' ou 'Fala professor' ou 'Oi professor' ou 'Aqui está chefe'"
            ),
            expected_output="Um texto com uma resposta coerente e relevante.",
            agent=self.agent
        )

        self.crew = Crew(
            agents=[self.agent],
            tasks=[self.task],
            process=Process.sequential  # Processo sequencial
        )

    def kickoff(self, transcription):
        """
        Processa o texto da transcrição e retorna a resposta.
        
        :param transcription_text: O texto da transcrição de áudio.
        :return: Resposta gerada pelo agente.
        """
        result = self.crew.kickoff(inputs={"transcription_text":transcription})
        return result.raw


