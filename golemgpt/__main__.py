import argparse
import readline  # noqa

from golemgpt.actions import GeneralActions
from golemgpt.golems.general import GeneralGolem
from golemgpt.memory.localfiles import LocalFilesMemory
from golemgpt.settings import Settings
from golemgpt.utils import chdir, console, genkey


def main():
    settings = Settings()
    console.set_debug(settings.GOLEM_DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-j",
        "--job-key",
        metavar="JOB_KEY",
        type=str,
        default=genkey(),
        required=False,
    )
    args = parser.parse_args()

    job_key = args.job_key
    console.info(f"Job key: {job_key}")

    workdir = settings.WORKDIR.absolute()
    outdir = workdir / job_key / "output"
    outdir.mkdir(parents=True, exist_ok=True)

    memory = LocalFilesMemory(workdir)
    memory.load(job_key)
    goals = memory.goals

    goals = [
        "Get weather in Batumi, Georgia. Use Celsius. "
        "Save results in human readable format."
    ]

    # goals = [
    #     "Get best offers for dedicated servers in the USA, need at least 1 Tb "
    #     "of storage and 1 Gbps of bandwidth. Save results in human readable format."
    # ]

    # goals = [
    #     "Get the price for LEGO collection 75342 (Star Wars). "
    #     "Verify the offers found via search are valid. "
    #     "Real numbers needed, not just links to websites. "
    #     "Skip unavailable resources. "
    #     "Summarize results in human readable format with pricing details in a single file."
    # ]

    goals = [
        "Find funny chess meme images about, use some creativity "
        "in search queries. Get at least 10 images, and please avoid "
        "downloading non-relevant images. Also avoid SVG and GIF files, "
        "prefer PNG ad JPEG. If download failed just look for other sources. "
        "Download images themselves and also put URLs it text file."
    ]

    while not goals:
        goal = input("Enter a goal for the Golem-GPT:\n?> ").strip()
        if goal:
            goals.append(goal)

    golem = GeneralGolem(
        goals=goals,
        job_key=job_key,
        memory=memory,
        settings=settings,
        actions=GeneralActions.get_actions(),
    )

    with chdir(outdir):
        console.info(f"Working directory: {outdir}")
        golem.start_job()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
