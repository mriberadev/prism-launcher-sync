import os
import sys
import subprocess
import argparse
from pathlib import Path

import colorlog


# Checks if program is a pyinstaller compiled executable or a python script
def is_compiled_executable() -> bool:
    if getattr(sys, 'frozen', False) and hasattr(sys, "_MEIPASS"):
        return True
    return False


def get_root_dir() -> Path:
    if is_compiled_executable():
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def set_logger_config() -> None:
    os.environ["FORCE_COLOR"] = "True"
    colorlog.basicConfig(
        level=colorlog.INFO,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "light_blue",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red,bg_bold_white",
        },
        format=("%(white)s[%(asctime)s]"
                " %(log_color)s[%(levelname)s]"
                " %(green)s[%(module)s:%(lineno)d]"
                " %(light_white)s%(message)s%(reset)s"),
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_arguments() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        prog="main",
        description="Sync Prism Launcher instances to Google Drive",
        exit_on_error=False
    )
    arg_parser.add_argument(
        "-i", "--instance",
        type=str,
        required=True
    )
    optional = {"ask", "debug", "cmd"}
    for arg in optional:
        arg_parser.add_argument(
            f"--{arg}",
            action=argparse.BooleanOptionalAction,
            required=False
        )
    return arg_parser.parse_args()


def launch_in_new_window() -> None:
    # Execute in a new cmd window
    sys.argv.remove("--cmd")
    subprocess_args = ["cmd.exe", "/c", "start", "/wait"]
    if not is_compiled_executable():
        subprocess_args.append(sys.executable)
    subprocess_args.extend(sys.argv)
    subprocess.call(subprocess_args)
    sys.exit()


def build_user_message(
        instance_name: str,
        instance_date: str,
        last_backup_date: str
) -> str:
    return (
        "\n"
        f"-- {instance_name} --\n"
        f"Most recent savefile: {instance_date}\n"
        f"Most recent backup: {last_backup_date}\n"
        "Would you like to sync this instance with your Google Drive? (y/N):"
    )
