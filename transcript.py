import os
import base64
import whisper


class Transcript:
    
    def __init__(self, save_dir="audio"):
        # Diretório para salvar os áudios
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    # Função para corrigir o padding da string Base64
    def fix_base64_padding(self, base64_string):
        missing_padding = len(base64_string) % 4
        if missing_padding != 0:
            base64_string += "=" * (4 - missing_padding)
        return base64_string
            
    def transcribe_audio_with_whisper(self, audio_file):
        """
        Transcreve o áudio usando Whisper.
        """
        try:
            model = whisper.load_model("base")  # Escolha o modelo: tiny, base, small, medium, large
            result = model.transcribe(audio_file)
            return result["text"]
        except Exception as e:
            print(f"Erro durante a transcrição: {e}")
            return None
    
    def get_text(self, data) -> str:
        try:
            # Corrigir o padding da string Base64
            code_base64 = self.fix_base64_padding(data.audio_base64_bytes)

            # Decodificar a string Base64 para bytes de áudio
            audio_data = base64.b64decode(data.audio_base64_bytes)

            # Caminho do arquivo de saída
            output_file = os.path.join(self.save_dir, "output_audio.wav")
            
            # Salvar o arquivo no diretório especificado
            with open(output_file, "wb") as audio_file:
                audio_file.write(audio_data)

            print(f"Áudio salvo com sucesso em {output_file}")
            
            # Transcrever o áudio
            transcription = self.transcribe_audio_with_whisper(output_file)

            # (Opcional) Remover o arquivo temporário
            os.remove(output_file)

            return transcription

        except base64.binascii.Error as e:
            print(f"Erro de decodificação Base64: {e}")
            return None
        except Exception as e:
            print(f"Erro geral: {e}")
            return None


