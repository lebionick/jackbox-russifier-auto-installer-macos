import logging
import os
import re
import shutil
import subprocess
from pathlib import Path

import click
from tqdm import tqdm

# Control log level via environment variable
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))

logger = logging.getLogger("jackbox_auto_russifier")


UNARCH_DIR_NAME = "unarchived"

pack_version_re = re.compile(r"JPP([0-9]+)ru.+")


def check_unar() -> None:
    try:
        ret_unar = subprocess.run(["unar", "-v"], capture_output=True, text=True)
    except FileNotFoundError:
        logger.warning("unar not found, trying to install it")
        try:
            _ = subprocess.run(["brew", "-v"], capture_output=True, text=True)
        except FileNotFoundError as e:
            msg = 'install brew first: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            raise RuntimeError(msg) from e
        _ = subprocess.run(["brew", "install", "unar"], capture_output=True, text=True)
        ret_unar = subprocess.run(["unar", "-v"], capture_output=True, text=True)
    if ret_unar.returncode == 0:
        logger.info("You have Unarchiver installed")
    return


def unzip_to_dir(zip_path: Path, out_dir: Path | None = None) -> Path | None:
    out_dir = out_dir or zip_path.with_suffix("")
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = ["unar", "-f", "-q", "-o", str(out_dir), str(zip_path)]
    ret = subprocess.run(cmd, capture_output=True, text=True)
    if ret.returncode == 0:
        out_unarch = out_dir / zip_path.stem
        assert out_unarch.is_dir(), out_unarch
        return out_unarch
    return None


def create_out_dir(root_dir: Path, clear: bool = True) -> Path:
    path = root_dir / UNARCH_DIR_NAME
    if clear and path.exists():
        shutil.rmtree(path)
    path.mkdir(exist_ok=True)
    return path


def patch_game(unarchived_rus: Path, app_path: Path) -> None:
    dest = app_path / "Contents/Resources/macos"
    shutil.copytree(unarchived_rus, dest, dirs_exist_ok=True)


def get_app_path(pack_ver: str) -> Path | None:
    steam_home = Path.home() / "Library/Application Support/Steam/steamapps/common/"
    assert steam_home.exists(), f"{steam_home} does not exist"
    suffix = f" {pack_ver}" if pack_ver != "1" else ""
    party_pack_path = steam_home / f"The Jackbox Party Pack{suffix}/The Jackbox Party Pack{suffix}.app"
    if party_pack_path.exists():
        return party_pack_path


def get_archive_paths(zip_dir: str) -> list[Path]:
    dir_path = Path(zip_dir).expanduser()
    assert dir_path.exists(), f"{dir_path} does not exist"
    assert dir_path.is_dir(), f"{dir_path} is not a directory"
    zip_paths: list[Path] = []
    for zip_path in dir_path.iterdir():
        if zip_path.suffix != ".zip" or zip_path.name.startswith("."):
            continue
        zip_paths.append(zip_path)
    assert len(zip_paths), f"{dir_path} does not contain any zip archives"
    return zip_paths


def check_input_output_dir(zip_dir: str) -> None:
    for arch_path in get_archive_paths(zip_dir):
        pack_ver: str = pack_version_re.match(arch_path.stem).groups()[0]
        app_path = get_app_path(pack_ver)
        if app_path is None:
            logger.warning(f"you have russifier {arch_path}, but no game installed")


@click.command()
@click.option(
    "-i",
    "--rus-zip-folder",
    required=True,
    help="Path to directory where you put all archived russifiers that you want to install",
)
@click.option("--dry-run", is_flag=True, help="Disables actual copying into game files")
def main(rus_zip_folder: str, dry_run: bool):
    check_input_output_dir(rus_zip_folder)
    check_unar()
    unarch_dir = create_out_dir(Path(rus_zip_folder).expanduser(), clear=True)
    zip_paths = get_archive_paths(rus_zip_folder)
    for zip_path in tqdm(zip_paths, desc="Iterating over archived russifiers", unit="archive"):
        pack_ver: str = pack_version_re.match(zip_path.stem).groups()[0]
        app_path = get_app_path(pack_ver)
        if app_path is None:
            continue
        logging.info(f"Unzipping: {zip_path} into {unarch_dir}")
        unarch_path = unzip_to_dir(zip_path, unarch_dir)
        logging.info(f"Successul, files are under: {unarch_path}, detected version of party pack is {pack_ver}")
        assert unarch_path
        if not dry_run:
            patch_game(unarch_path, app_path)
            logger.info(f"{app_path.stem} is patched successfully!")
        else:
            logger.info(f'{app_path.stem} is not patched, due to flag "--dry-run"')
    logger.info("All packs are patched successfully!")


if __name__ == "__main__":
    main()
