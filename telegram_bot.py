import telebot

# Substitua pelo token do seu bot
TOKEN = '7631292504:AAE832UkHj2scbakf6XG5aNMG2L1l5pQMfk'
CHAT_ID = '1271362249'  #  # Substitua pelo chat ID do grupo ou usuário


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