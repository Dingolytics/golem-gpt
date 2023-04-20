import argparse
import time
from typing import List
from pathlib import Path
from ..http import http_request
from .settings import Settings
from .prompt import Prompt


def save_result(
    key: str, message: str, urls: List[str] = [],
    root_dir=Path('./history')
) -> None:
    """Save the generated result to the history directory."""
    chat_dir = root_dir / f'{key}-image'
    chat_dir.mkdir(parents=True, exist_ok=True)
    message_path = chat_dir / '0.txt'
    with open(message_path, "w") as file:
        file.write(message)
    for i, url in enumerate(urls):
        image_path = chat_dir / f'generated_{i}.png'
        print(url, '->', image_path)
        data = http_request('GET', url)
        with open(image_path, "wb") as file:
            file.write(data)


def main():
    """Generate images from a prompt message."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n', '--images-number', metavar='IMAGES_NUMBER',
        type=int, default=1, required=False
    )
    parser.add_argument(
        '-s', '--image-size', metavar='IMAGE_SIZE',
        type=str, default='', required=False
    )
    args = parser.parse_args()
    #
    key = hex(int(time.time()))[2:]
    print(f"Prompt key: {key}")
    #
    try:
        message = input("Prompt for image by ChatGPT: ")
        message = message.strip()
    except (KeyboardInterrupt, EOFError):
        return
    #
    settings = Settings()
    prompt = Prompt(settings)
    result = prompt.send_message(
        message, n=args.images_number, size=args.image_size
    )
    #
    urls = [item['url'] for item in result.get('data', [])]
    save_result(key, message, urls, root_dir=Path(settings.HISTORY_ROOT))


if __name__ == '__main__':
    main()
