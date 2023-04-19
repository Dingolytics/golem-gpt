import argparse
import pathlib
import time

from gptgolem.settings import Settings
from gptgolem.directors.general import Director
from gptgolem.utils.memory.localfiles import LocalFilesMemory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-j', '--job-key', metavar='JOB_KEY',
        type=str, default='', required=False
    )
    args = parser.parse_args()
    #
    job_key = args.job_key or hex(int(time.time()))[2:]
    print(f"Job key: {job_key}")
    #
    settings = Settings()
    memory = LocalFilesMemory(pathlib.Path('workdir'))
    director = Director(
        job_key=job_key,
        memory=memory,
        settings=settings,
    )
    director.start_job()


if __name__ == '__main__':
    main()
