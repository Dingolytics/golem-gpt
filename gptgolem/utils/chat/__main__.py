# import os
import argparse
# import binascii
import time
from .history import History
from .settings import Settings
from .dialog import Dialog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-k', '--chat-key', metavar='CHAT_KEY',
        type=str, default='', required=False
    )
    args = parser.parse_args()
    #
    key = args.chat_key or hex(int(time.time()))[2:]
    print(f"Chat key: {key}")
    #
    settings = Settings()
    history = History(key=key)
    history.load()
    history.print_all_messages()
    #
    while True:
        try:
            message = input("Ask ChatGPT: ")
            message = message.strip()
        except (KeyboardInterrupt, EOFError):
            message = ''
        #
        dialog = Dialog(settings=settings, history=history)
        if message:
            dialog.send_message(message)
            history.print_last_message()
            history.dump_message(-2)  # Save user's prompt message
            history.dump_message(-1)  # Save plain-text reply message
        dialog.save()
        #
        if not message:
            break


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        print("")
        print("Thanks for chatting!")
