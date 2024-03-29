from requests import get
from commands import http_api_helper
from json import loads


def oneclick_start_command(env, *args, **kwargs) -> bool:
    is_running_command, running_text = http_api_helper(env, "status", {}, get)
    if not is_running_command:
        raise Exception("Status check failed")
    status_json = loads(running_text)
    if status_json and "not_running" not in status_json:
        raise Exception("Server already running")

    got, text = http_api_helper(env, "oneclick_start_server", {}, get)
    print(text)
    return got


def start_command(env, *args, **kwargs) -> bool:
    is_running_command, running_text = http_api_helper(env, "status", {}, get)
    if not is_running_command:
        raise Exception("Status check failed")
    status_json = loads(running_text)
    if "not_running" not in status_json:
        raise Exception("Server already running")

    got, text = http_api_helper(env, "start", {}, get)
    print(got)
    return got


def stop_command(env, *args, **kwargs) -> bool:
    is_running_command, running_text = http_api_helper(env, "status", {}, get)
    if not is_running_command:
        raise Exception("Status check failed")
    status_json = loads(running_text)
    if "not_running" in status_json:
        raise Exception("Server is not running")
    got, text = http_api_helper(env, "stop", {}, get)
    print(got)
    return got


def list_command(env, *args, **kwargs) -> bool:
    if "server_data" not in env:
        raise Exception("Server data invalid. Check servers.json")
    servers = env["server_data"]
    for key, value in servers.items():
        url = value["url"]
        print(f"{key} => {url}")
    return True


def update_command(env, *args, **kwargs) -> bool:
    is_running_command, running_text = http_api_helper(env, "status", {}, get)
    if not is_running_command:
        raise Exception("Status check failed")
    status_json = loads(running_text)
    if status_json is not None and "not_running" not in status_json:
        raise Exception("Server is running")

    got, text = http_api_helper(env, "update", {}, get)
    print(got, text)
    return got