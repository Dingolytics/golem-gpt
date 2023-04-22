import argparse
import readline  # noqa

from golemgpt.settings import Settings
from golemgpt.memory.localfiles import LocalFilesMemory
from golemgpt.golems.roles.director import DirectorGolem
from golemgpt.utils import chdir, console, genkey


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

    director = DirectorGolem(
        goals=goals,
        job_key=job_key,
        memory=memory,
        settings=settings,
    )
    with chdir(outdir):
        director.start_job()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
