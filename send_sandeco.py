"""
CLASSE SENDSANDECO - AUTOMATIZAÇÃO DE MENSAGENS WHATSAPP
========================================================

Esta classe permite enviar diferentes tipos de mensagens via WhatsApp usando a Evolution API.
É como um "robô" que automatiza o envio de mensagens, arquivos e mídias.

REQUISITOS:
- Arquivo .env com as credenciais da Evolution API
- Biblioteca evolutionapi instalada
- Biblioteca python-dotenv instalada

EXEMPLO DE USO:
    whatsapp = SendSandeco()
    whatsapp.textMessage("5511999999999", "Olá! Como você está?")
    whatsapp.image("5511999999999", "foto.jpg", "Veja esta imagem!")
"""

import os
import time
from dotenv import load_dotenv
from evolutionapi.client import EvolutionClient
from evolutionapi.models.message import TextMessage, MediaMessage

class SendSandeco:
    """
    Classe principal para envio de mensagens WhatsApp via Evolution API
    
    Esta classe gerencia a conexão com a Evolution API e fornece métodos
    simples para enviar diferentes tipos de conteúdo via WhatsApp.
    """
    
    def __init__(self) -> None:
        """
        CONSTRUTOR DA CLASSE
        ===================
        
        Inicializa a conexão com a Evolution API carregando as credenciais
        do arquivo .env e criando o cliente de conexão.
        
        VARIÁVEIS DE AMBIENTE NECESSÁRIAS NO ARQUIVO .env:
        - EVO_API_TOKEN: Token de autenticação da API
        - EVO_INSTANCE_NAME: Nome da instância do WhatsApp
        - EVO_INSTANCE_TOKEN: Token específico da instância
        - EVO_BASE_URL: URL base da Evolution API
        
        EXEMPLO DO ARQUIVO .env:
            EVO_API_TOKEN=seu_token_aqui
            EVO_INSTANCE_NAME=minha_instancia
            EVO_INSTANCE_TOKEN=token_da_instancia
            EVO_BASE_URL=https://sua-api.com
        """
        # Carregar variáveis de ambiente do arquivo .env
        load_dotenv()
        
        # Obter credenciais das variáveis de ambiente
        self.evo_api_token = os.getenv("EVO_API_TOKEN")
        self.evo_instance_id = os.getenv("EVO_INSTANCE_NAME")
        self.evo_instance_token = os.getenv("EVO_INSTANCE_TOKEN")
        self.evo_base_url = os.getenv("EVO_BASE_URL")
        
        # Inicializar o cliente Evolution com as credenciais
        self.client = EvolutionClient(
            base_url=self.evo_base_url,
            api_token=self.evo_api_token
        )

    def textMessage(self, number, msg, mentions=[]):
        """
        ENVIAR MENSAGEM DE TEXTO
        ========================
        
        Envia uma mensagem de texto simples para um número do WhatsApp.
        Inclui delay de 10 segundos para evitar bloqueios por spam.
        
        PARÂMETROS:
            number (str): Número do WhatsApp com código do país (ex: "5511999999999")
            msg (str): Texto da mensagem a ser enviada
            mentions (list, opcional): Lista de números para mencionar na mensagem
        
        RETORNO:
            response: Resposta da API confirmando o envio
        
        EXEMPLO:
            whatsapp.textMessage("5511999999999", "Olá! Como você está?")
            whatsapp.textMessage("5511999999999", "Oi @fulano!", ["5511888888888"])
        """
        # Criar objeto de mensagem de texto
        text_message = TextMessage(
            number=str(number),  # Converter para string por segurança
            text=msg,
            mentioned=mentions   # Lista de números mencionados
        )

        # Aguardar 10 segundos para evitar spam/bloqueios
        time.sleep(10)

        # Enviar a mensagem através da API
        response = self.client.messages.send_text(
            self.evo_instance_id, 
            text_message, 
            self.evo_instance_token
        )
        return response

    def PDF(self, number, pdf_file, caption=""):
        """
        ENVIAR ARQUIVO PDF
        ==================
        
        Envia um arquivo PDF como documento para um número do WhatsApp.
        Verifica se o arquivo existe antes de tentar enviar.
        
        PARÂMETROS:
            number (str): Número do WhatsApp destinatário
            pdf_file (str): Caminho completo para o arquivo PDF
            caption (str, opcional): Legenda/descrição do arquivo
        
        LEVANTA EXCEÇÃO:
            FileNotFoundError: Se o arquivo PDF não for encontrado
        
        EXEMPLO:
            whatsapp.PDF("5511999999999", "C:/documentos/relatorio.pdf", "Relatório mensal")
        """
        # Verificar se o arquivo existe no sistema
        if not os.path.exists(pdf_file):
            raise FileNotFoundError(f"Arquivo '{pdf_file}' não encontrado.")
        
        # Criar objeto de mensagem de mídia para PDF
        media_message = MediaMessage(
            number=number,
            mediatype="document",           # Tipo: documento
            mimetype="application/pdf",     # Formato: PDF
            caption=caption,                # Legenda opcional
            fileName=os.path.basename(pdf_file),  # Nome do arquivo sem caminho
            media=""                        # Campo obrigatório (vazio para arquivo local)
        )
        
        # Enviar o PDF através da API
        self.client.messages.send_media(
            self.evo_instance_id, 
            media_message, 
            self.evo_instance_token,
            pdf_file
        )

    def audio(self, number, audio_file):
        """
        ENVIAR ARQUIVO DE ÁUDIO
        =======================
        
        Envia um arquivo de áudio (MP3) para um número do WhatsApp.
        O áudio aparecerá como mensagem de voz no chat.
        
        PARÂMETROS:
            number (str): Número do WhatsApp destinatário
            audio_file (str): Caminho completo para o arquivo de áudio
        
        RETORNO:
            str: Mensagem confirmando "Áudio enviado"
        
        LEVANTA EXCEÇÃO:
            FileNotFoundError: Se o arquivo de áudio não for encontrado
        
        EXEMPLO:
            whatsapp.audio("5511999999999", "C:/audios/mensagem.mp3")
        """
        # Verificar se o arquivo de áudio existe
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Arquivo '{audio_file}' não encontrado.")

        # Criar dicionário com dados do áudio
        audio_message = {
            "number": number,
            "mediatype": "audio",        # Tipo: áudio
            "mimetype": "audio/mpeg",    # Formato: MP3
            "caption": ""                # Áudios não têm legenda
        }
        
        # Enviar áudio usando método específico para WhatsApp Audio
        self.client.messages.send_whatsapp_audio(
            self.evo_instance_id,
            audio_message,
            self.evo_instance_token,
            audio_file
        )
                    
        return "Áudio enviado"

    def audioBase64(self, number, audio_file):
        """
        ENVIAR ÁUDIO EM BASE64
        ======================
        
        Método alternativo para envio de áudio, possivelmente para dados em Base64.
        ATENÇÃO: Este método está incompleto e pode não funcionar corretamente.
        
        PARÂMETROS:
            number (str): Número do WhatsApp destinatário
            audio_file: Dados do áudio (formato não especificado)
        
        NOTA: Este método precisa ser revisado e completado.
        """
        # Criar dicionário com dados do áudio
        audio_message = {
            "number": number,
            "mediatype": "audio",
            "mimetype": "audio/mpeg",
            "caption": ""
        }
        
        # Enviar áudio (método possivelmente incompleto)
        self.client.messages.send_whatsapp_audio(
            self.evo_instance_id,
            audio_message,
            self.evo_instance_token,
            audio_file
        )

    def image(self, number, image_file, caption=""):
        """
        ENVIAR IMAGEM
        =============
        
        Envia uma imagem (JPEG) para um número do WhatsApp.
        A imagem pode incluir uma legenda/descrição.
        
        PARÂMETROS:
            number (str): Número do WhatsApp destinatário
            image_file (str): Caminho completo para o arquivo de imagem
            caption (str, opcional): Legenda da imagem
        
        RETORNO:
            str: Mensagem confirmando "Imagem enviada"
        
        LEVANTA EXCEÇÃO:
            FileNotFoundError: Se o arquivo de imagem não for encontrado
        
        EXEMPLO:
            whatsapp.image("5511999999999", "C:/fotos/paisagem.jpg", "Que vista linda!")
        """
        # Verificar se o arquivo de imagem existe
        if not os.path.exists(image_file):
            raise FileNotFoundError(f"Arquivo '{image_file}' não encontrado.")

        # Criar objeto de mensagem de mídia para imagem
        media_message = MediaMessage(
            number=number,
            mediatype="image",              # Tipo: imagem
            mimetype="image/jpeg",          # Formato: JPEG
            caption=caption,                # Legenda da imagem
            fileName=os.path.basename(image_file),  # Nome do arquivo
            media=""                        # Campo obrigatório (vazio para arquivo local)
        )

        # Enviar imagem através da API
        self.client.messages.send_media(
            self.evo_instance_id, 
            media_message, 
            self.evo_instance_token,
            image_file
        )
        
        return "Imagem enviada"

    def video(self, number, video_file, caption=""):
        """
        ENVIAR VÍDEO
        ============
        
        Envia um arquivo de vídeo (MP4) para um número do WhatsApp.
        O vídeo pode incluir uma legenda/descrição.
        
        PARÂMETROS:
            number (str): Número do WhatsApp destinatário
            video_file (str): Caminho completo para o arquivo de vídeo
            caption (str, opcional): Legenda do vídeo
        
        RETORNO:
            str: Mensagem confirmando "Vídeo enviado"
        
        LEVANTA EXCEÇÃO:
            FileNotFoundError: Se o arquivo de vídeo não for encontrado
        
        EXEMPLO:
            whatsapp.video("5511999999999", "C:/videos/apresentacao.mp4", "Veja esta apresentação")
        """
        # Verificar se o arquivo de vídeo existe
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Arquivo '{video_file}' não encontrado.")

        # Criar objeto de mensagem de mídia para vídeo
        media_message = MediaMessage(
            number=number,
            mediatype="video",              # Tipo: vídeo
            mimetype="video/mp4",           # Formato: MP4
            caption=caption,                # Legenda do vídeo
            fileName=os.path.basename(video_file),  # Nome do arquivo
            media=""                        # Campo obrigatório (vazio para arquivo local)
        )

        # Enviar vídeo através da API
        self.client.messages.send_media(
            self.evo_instance_id, 
            media_message, 
            self.evo_instance_token,
            video_file
        )
        
        return "Vídeo enviado"

    def document(self, number, document_file, caption=""):
        """
        ENVIAR DOCUMENTO DO WORD
        ========================
        
        Envia um documento do Microsoft Word (.docx) para um número do WhatsApp.
        O documento pode incluir uma legenda/descrição.
        
        PARÂMETROS:
            number (str): Número do WhatsApp destinatário
            document_file (str): Caminho completo para o arquivo .docx
            caption (str, opcional): Legenda do documento
        
        RETORNO:
            str: Mensagem confirmando "Documento enviado"
        
        LEVANTA EXCEÇÃO:
            FileNotFoundError: Se o arquivo do documento não for encontrado
        
        EXEMPLO:
            whatsapp.document("5511999999999", "C:/docs/contrato.docx", "Contrato para assinatura")
        """
        # Verificar se o arquivo do documento existe
        if not os.path.exists(document_file):
            raise FileNotFoundError(f"Arquivo '{document_file}' não encontrado.")

        # Criar objeto de mensagem de mídia para documento Word
        media_message = MediaMessage(
            number=number,
            mediatype="document",           # Tipo: documento
            # MIME type específico para arquivos Word .docx
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            caption=caption,                # Legenda do documento
            fileName=os.path.basename(document_file),  # Nome do arquivo
            media=""                        # Campo obrigatório (vazio para arquivo local)
        )

        # Enviar documento através da API
        self.client.messages.send_media(
            self.evo_instance_id, 
            media_message, 
            self.evo_instance_token,
            document_file
        )
        
        return "Documento enviado"

"""
RESUMO DOS MÉTODOS DISPONÍVEIS:
==============================

1. textMessage()  - Envia mensagem de texto
2. PDF()         - Envia arquivo PDF
3. audio()       - Envia arquivo de áudio/voz
4. audioBase64() - Envia áudio em Base64 (INCOMPLETO)
5. image()       - Envia imagem JPEG
6. video()       - Envia vídeo MP4
7. document()    - Envia documento Word (.docx)

FORMATOS SUPORTADOS:
- Texto: Qualquer string
- PDF: .pdf
- Áudio: .mp3
- Imagem: .jpg/.jpeg
- Vídeo: .mp4
- Documento: .docx

EXEMPLO DE USO COMPLETO:
=======================

# Instanciar a classe
whatsapp = SendSandeco()

# Enviar diferentes tipos de conteúdo
whatsapp.textMessage("5511999999999", "Olá!")
whatsapp.image("5511999999999", "foto.jpg", "Linda imagem!")
whatsapp.PDF("5511999999999", "documento.pdf", "Documento importante")
whatsapp.audio("5511999999999", "audio.mp3")
whatsapp.video("5511999999999", "video.mp4", "Vídeo explicativo")
whatsapp.document("5511999999999", "contrato.docx", "Contrato")
"""

