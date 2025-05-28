
from crewai.tools import BaseTool


class ExecutePythonCodeTool(BaseTool):

    name: str = "Ferramenta de execução de código Python"
    description: str = "Executa um bloco de código Python fornecido como uma string e retorna o valor da variável 'resultado'."

    def __init__(self):
        super().__init__()

    def _run(self, python_code: str) -> str:
        local_namespace = {}
        try:
            # Ensure that any required modules for the python_code (e.g. pandas, os)
            # are available in the execution environment where this tool runs.
            # The 'globals()' argument provides access to modules already imported
            # in this file (like BaseTool), but not necessarily all that might be needed.
            exec(python_code, globals(), local_namespace)
            resultado = local_namespace.get('resultado', 'Nenhum resultado capturado. A variável "resultado" não foi definida no código executado.')
            return str(resultado)
        except Exception as e:
            return f"Erro ao executar o código Python: {type(e).__name__}: {e}"
