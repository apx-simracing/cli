from requests import post

from commands.env import stop_command, list_command, oneclick_start_command
from commands.status import get_status_command, get_drivers_command, get_states_command
from commands.chat import (
    chat_command,
    kick_command,
    add_bot_command,
    restart_weekend_command,
    restart_race_command,
    restart_race_command,
    next_session_command,
    rejoin_driver_command,
)
from commands.deployment import (
    deploy_command,
    install_command,
    unlock_command,
    get_lockfile_command,
)
from commands.build import (
    build_skin_command,
    get_config_command,
    get_ports_command,
    stamp_command,
)
from commands.util import (
    get_rfcmp_info_command,
    get_components_in_directory_command,
    check_config_command,
)

SHELL_COMMANDS = {
    "status": get_status_command,
    "states": get_states_command,
    "chat": chat_command,
    "rejoin": rejoin_driver_command,
    "kick": kick_command,
    "addbot": add_bot_command,
    "new_weekend": restart_weekend_command,
    "restart": restart_race_command,
    "advance": next_session_command,
    "deploy": deploy_command,
    "start": oneclick_start_command,
    "stop": stop_command,
    "list": list_command,
    "drivers": get_drivers_command,
    "build_skins": build_skin_command,
    "config": get_config_command,
    "ports": get_ports_command,
    "install": install_command,
    "unlock": unlock_command,
    "lockfile": get_lockfile_command,
    "rfcmpinfo": get_rfcmp_info_command,
    "rfcmpdir": get_components_in_directory_command,
    "checkconfig": check_config_command,
    "stamp": stamp_command,
}


class CommandFailedException(Exception):
    pass
