import sys

import colorlog
import argparse

from prism_launcher_sync import config
from prism_launcher_sync import utils
from prism_launcher_sync import base

from prism_launcher_sync import gdrive
from prism_launcher_sync import prismlauncher

utils.set_logger_config()
logger = colorlog.getLogger(__name__)

try:
    args = utils.parse_arguments()
    if args.debug is True:
        config.DEBUG_MODE = True
    if args.cmd is True:
        logger.info("Opening in new window...")
        utils.launch_in_new_window()

    gd_manager = gdrive.DriveFileManager(
        _root=gdrive.DriveFile(config.DRIVE_FOLDER),
        _api=gdrive.DriveApi.build()
    )
    gd_manager.map_from_drive()

    mc_instance = prismlauncher.MinecraftInstance.from_src(args.instance)

    # Ask the user if they want to sync their instance
    last_backup = gd_manager.last_backup_for_instance(mc_instance)
    logger.info(
        utils.build_user_message(
            instance_name=gd_manager.last_backup_for_instance(mc_instance),
            instance_date=mc_instance.dt_modified.strftime("%Y-%m-%d %H:%M:%S"),
            last_backup_date=last_backup.dt_modified.strftime("%Y-%m-%d %H:%M:%S") if last_backup else "None",
        )
    )
    if input().lower().strip() != "y":
        sys.exit()

    logger.info("Sync process starting...")
    gd_manager.sync_instance(mc_instance)

    logger.info("Cleaning up temp files...")
    zip_dir = base.BaseFile.from_src(config.ZIPFILES_DIR)
    zip_dir.clean_dir()

    logger.info("Sync complete!")


except (argparse.ArgumentError, gdrive.DriveFileManagerError, gdrive.DriveApiError, base.BaseFileError) as e:
    logger.error(e, exc_info=config.DEBUG_MODE)
