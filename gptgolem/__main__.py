import os
import argparse
import contextlib
import time
import readline  # noqa

from gptgolem.settings import Settings
from gptgolem.golems.director import Director
from gptgolem.utils.memory.localfiles import LocalFilesMemory
from gptgolem.utils import console


@contextlib.contextmanager
def cd(path: str):
   old = os.getcwd()
   os.chdir(path)
   try:
       yield
   finally:
       os.chdir(old)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-j', '--job-key', metavar='JOB_KEY',
        type=str, default=hex(int(time.time()))[2:],
        required=False
    )
    args = parser.parse_args()

    job_key = args.job_key
    console.info(f"Job key: {job_key}")

    settings = Settings()
    workdir = settings.WORKDIR.absolute()
    outdir = workdir / job_key / 'output'
    outdir.mkdir(parents=True, exist_ok=True)

    memory = LocalFilesMemory(workdir)
    memory.load(job_key)
    goals = memory.goals

    while True:
        goal = input("Enter a goal for the Golem-GPT:\n?> ").strip()
        if goal:
            goals.append(goal)
            break

    director = Director(
        goals=goals,
        job_key=job_key,
        memory=memory,
        settings=settings,
    )
    with cd(outdir):
        director.start_job()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
