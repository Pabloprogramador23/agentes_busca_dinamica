import os
import requests
from dotenv import load_dotenv

class TextToSpeech:
    def __init__(self, chunk_size=1024):
        """
        Inicializa a classe TextToSpeech com a chave da API e o tamanho do chunk para download.
        :param api_key: Chave da API ElevenLabs (se não fornecida, será carregada do .env).
        :param chunk_size: Tamanho dos blocos para o download do áudio.
        """
        load_dotenv()
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("SANDECO_VOICE_ID")
        self.chunk_size = 1024
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"
        
        self.data_template = {
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 1
            }
        }
        
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }


    def synthesize_speech(self, text, output_file):
        """
        Gera um arquivo de áudio a partir de um texto utilizando a API ElevenLabs.
        
        :param text: Texto que será convertido em áudio.
        :param output_file: Nome do arquivo de saída para salvar o áudio.
        """

        url = f"{self.base_url}/{self.voice_id}"


        # Atualizando o template com o texto
        data = self.data_template.copy()
        data["text"] = text

        response = requests.post(url, json=data, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Erro na requisição: {response.status_code} - {response.text}")

        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=self.chunk_size):
                if chunk:
                    f.write(chunk)

        print(f"Áudio gerado com sucesso e salvo em: {output_file}")
