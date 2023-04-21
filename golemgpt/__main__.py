import os
import argparse
import contextlib
import readline  # noqa

from golemgpt.settings import Settings
from golemgpt.golems.director import Director
from golemgpt.utils.memory.localfiles import LocalFilesMemory
from golemgpt.utils import console, genkey


@contextlib.contextmanager
def cd(path: str):
   old = os.getcwd()
   os.chdir(path)
   try:
       yield
   finally:
       os.chdir(old)


def main():
    settings = Settings()
    console.set_debug(settings.GOLEM_DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-j', '--job-key', metavar='JOB_KEY',
        type=str, default=genkey(),
        required=False
    )
    args = parser.parse_args()

    job_key = args.job_key
    console.info(f"Job key: {job_key}")

    workdir = settings.WORKDIR.absolute()
    outdir = workdir / job_key / 'output'
    outdir.mkdir(parents=True, exist_ok=True)

    memory = LocalFilesMemory(workdir)
    memory.load(job_key)
    goals = memory.goals

    while not goals:
        goal = input("Enter a goal for the Golem-GPT:\n?> ").strip()
        if goal:
            goals.append(goal)

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
