import time
import subprocess

def restart_bot():
    while True:
        # Попробуем запустить бота
        process = subprocess.Popen(['python3', 'main.py'])
        process.wait()  # ждем, пока бот не завершится
        print("Bot stopped, restarting...")
        time.sleep(5)  # небольшой перерыв перед перезапуском

if __name__ == "__main__":
    restart_bot()
