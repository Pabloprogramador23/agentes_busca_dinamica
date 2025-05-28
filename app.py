

from flask import Flask, request
from message_sandeco import MessageSandeco as Message
from send_sandeco import SendSandeco
from generate import TextToSpeech
from transcript import Transcript
from dotenv import load_dotenv

import base64

from fluxo_audio import FluxoAudio


load_dotenv()

app = Flask(__name__)

@app.route("/messages-upsert", methods=['POST'])
def webhook():

    send = SendSandeco()
    try:
        data = request.get_json()
                
        msg = Message(data)     
        
        if msg.phone == "556281685163": #Somente sandeco pode requisitar   
        
            if msg.message_type == Message.TYPE_TEXT:
            
                text = msg.get_text()
            
            elif msg.message_type == Message.TYPE_AUDIO:
                
                tsc = Transcript()
                text = tsc.get_text(msg)
                
                                    
            fluxo = FluxoAudio()
            resposta = fluxo.kickoff(inputs={'text':text})

            speech = TextToSpeech()
            speech.synthesize_speech(text=resposta, 
                                        output_file="output.mp3")

            send = SendSandeco()
            send.audio(number=msg.phone, audio_file="output.mp3")
    except Exception as e:
        print(f"Error occurred: {e}")
        send = SendSandeco()
        send.text(number=msg.phone, text="Ocorreu um erro ao processar a mensagem. Por favor, tente novamente.")

    return "resposta"
        

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
