import argparse
from os.path import isfile
from json import load
from args import parser
from commands.commands import SHELL_COMMANDS, CommandFailedException

SERVER_DATA = []

if not isfile("servers.json"):
    raise FileNotFoundError("Server config not existing")

with open("servers.json", "r") as read_file:
    SERVER_DATA = load(read_file)

args = parser.parse_args()
if args.cmd is None:
    raise Exception("No cmd given")

for server in args.server:
    config = args.config
    env = {
        "server_data": SERVER_DATA,
        "server": None,
        "server_config": None
    }
    env["server"] = server
    if config is not None:
        env["server_config"] = config
    if args.cmd not in SHELL_COMMANDS:
        raise Exception(f"command {args.cmd} not found")
    result = SHELL_COMMANDS[args.cmd](env, args.args)
    if not result:
        raise CommandFailedException()
