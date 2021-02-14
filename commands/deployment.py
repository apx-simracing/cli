from requests import post, get
from os.path import exists
from json import loads
from commands import http_api_helper


def deploy_command(env, *args, **kwargs) -> bool:
    server_key = env["server"]
    server_data = env["server_data"][server_key]
    url = server_data["url"]
    secret = server_data["secret"]

    is_running_command, running_text = http_api_helper(env, "status", {}, get)
    if not is_running_command:
        raise Exception("Status check failed")

    status_json = loads(running_text)
    if "not_running" not in status_json:
        raise Exception("Server is running, deploy failed")
    file_name = args[0][0]
    rfm_filename = args[0][1]
    result = False
    upload_files = {}
    with open(file_name, "r") as file:
        data = file.read()
        # add grip, if possible
        json_data = loads(data)
        if "conditions" in json_data:
            for session_key, gripfile in json_data["conditions"].items():
                upload_files[session_key] = open(gripfile, "rb").read()

        got = post(
            url + "/deploy",
            headers={"authorization": secret},
            data={"config": data, "rfm_config": open(rfm_filename, "r").read()},
            files=upload_files,
        )

        result = got.status_code == 200
    return result


def install_command(env, *args, **kwargs) -> bool:

    is_running_command, running_text = http_api_helper(env, "status", {}, get)
    if not is_running_command:
        raise Exception("Status check failed")

    status_json = loads(running_text)
    if "not_running" not in status_json:
        raise Exception("Server is running, install failed")
    got, text = http_api_helper(env, "install", {}, get)
    print(text)
    return got


def unlock_command(env, *args, **kwargs):
    if not env["server"]:
        print("no server set")
    else:
        server_key = env["server"]
        server_data = env["server_data"][server_key]
        url = server_data["url"]
        secret = server_data["secret"]
        file = args[0][0]
        got = post(
            url + "/unlock",
            headers={"authorization": secret},
            files={"unlock": open(file, "rb")},
        )
        return True


def get_lockfile_command(env, *args, **kwargs):
    if not env["server"]:
        print("no server set")
    else:
        server_key = env["server"]
        server_data = env["server_data"][server_key]
        url = server_data["url"]
        secret = server_data["secret"]
        target_file = args[0][0]
        got = get(url + "/lockfile", headers={"authorization": secret})
        with open(target_file, "wb") as f:
            f.write(got.content)
        return True


def get_log_command(env, *args, **kwargs):
    if not env["server"]:
        print("no server set")
    else:
        server_key = env["server"]
        server_data = env["server_data"][server_key]
        url = server_data["url"]
        secret = server_data["secret"]
        target_file = args[0][0]
        got = get(url + "/log", headers={"authorization": secret})
        with open(target_file, "wb") as f:
            f.write(got.content)
        return True