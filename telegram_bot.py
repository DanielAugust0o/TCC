import telebot

# Substitua pelo token do seu bot
TOKEN = '7552093490:AAG_7ho97BYEQjoZ67BKeNTnIgX7VKKFcBQ'
CHAT_ID = '1184444451'  #  # Substitua pelo chat ID do grupo ou usuário


bot = telebot.TeleBot(token=TOKEN)

def send_telegram_message(text):
    try:
        bot.send_message(chat_id=CHAT_ID, text=text)
        print("Mensagem enviada com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar mensagem pelo Telegram: {e}")

# Testando o envio de mensagem
if __name__ == "__main__":
    send_telegram_message("Teste de mensagem: O bot está funcionando corretamente!")