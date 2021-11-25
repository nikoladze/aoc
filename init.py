import os
from glob import glob1
import sys
from shutil import copyfile
import requests
from datetime import date
import logging
from argparse import ArgumentParser

logging.basicConfig(
    level=logging.INFO, format="%(levelname)-8s %(funcName)s: %(message)s",
)
logger = logging.getLogger(__name__)

lang_files = {
    "cpp": ["*.cpp", "*.hpp", "*.h", "Makefile"],
}


def setup_dir(day, languages):
    newdir = f"day{day:02d}"
    if not os.path.exists(newdir):
        os.mkdir(newdir)
        logger.info(f"created a new directory {newdir}")
    for lang in languages:
        # check if there are multiple filetypes for that language, otherwise
        # we just copy everything that matches *.lang
        wildcards = lang_files.get(lang, [f"*.{lang}"])
        for wc in wildcards:
            for t in glob1("templates", wc):
                if t in os.listdir(newdir):
                    logger.warning(f"{newdir} already contains {t}, skipping")
                else:
                    copyfile(os.path.join("templates", t), os.path.join(newdir, t))
    logger.info(f"done copying templates to {newdir}")


def get_input(day, year):
    if not "AOC_SESSION" in os.environ:
        logger.warning("no environment variable 'AOC_SESSION' found! skipping download")
        return
    else:
        cookie = os.environ["AOC_SESSION"]

    url = "https://adventofcode.com/{}/day/{}/input".format(year, day)
    dayfolder = f"day{day:02d}"
    if "input.txt" in os.listdir(dayfolder):
        logger.warning(f"{dayfolder}/input.txt already exists, skip download")
        return

    logger.info("download input from {}... ".format(url))
    try:
        response = requests.get(
            url=url,
            cookies={"session": cookie},
            headers={"User-Agent": "get_input_script"},
        )
        if response.ok:
            data = response.text
            f = open(os.path.join(dayfolder, "input.txt"), "w+")
            f.write(data.rstrip("\n"))
            f.close()
            logger.info("... done!")
        else:
            logger.error("server response not ok")
    except:
        logger.error("something went wrong")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-d", "--day", default=date.today().day, type=int)
    parser.add_argument("-y", "--year", default=date.today().year, type=int)
    parser.add_argument("-l", "--language", default=["py"], nargs="+")
    parser.add_argument("--no-download", dest="skip_download", action="store_true")
    args = parser.parse_args()

    setup_dir(args.day, args.language)
    if not args.skip_download:
        get_input(args.day, args.year)
