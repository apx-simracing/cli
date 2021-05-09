from os.path import isfile
from json import load
from os import getcwd
from sys import path

path.append(getcwd())
from args import parser
from commands.commands import SHELL_COMMANDS, CommandFailedException

SERVER_DATA = []

if not isfile("servers.json"):
    raise FileNotFoundError("Server config not existing")

with open("servers.json", "r") as read_file:
    SERVER_DATA = load(read_file)

parsed_args = parser.parse_args()
if parsed_args.cmd is None:
    raise Exception("No cmd given")

for server in parsed_args.server:
    config = parsed_args.config
    env = {"server_data": SERVER_DATA, "server": None, "server_config": None}
    env["server"] = server
    if config is not None:
        env["server_config"] = config
    if parsed_args.cmd not in SHELL_COMMANDS:
        raise Exception(f"command {args.cmd} not found")
    result = SHELL_COMMANDS[parsed_args.cmd](env, parsed_args.args)
    if not result:
        raise CommandFailedException()
