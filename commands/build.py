from requests import post, get
from os.path import exists, join
from os import listdir, mkdir
from json import load, loads
import re
from shutil import copyfile, rmtree
import tarfile
from commands import http_api_helper
import io
from wand import image
from wand.drawing import Drawing
from wand.color import Color

team_pattern = r"(?P<name>.+)\s?#(?P<number>\d+)"


def get_final_filename(needle: str, short_name: str, number: str) -> str:
    final_name = f"{short_name}_{number}"
    if "windowsin" in needle or "windowin" in needle:
        final_name = f"{short_name}_{number}WINDOWSIN.dds"
    elif "windowout" in needle or "windowsout" in needle:
        final_name = f"{short_name}_{number}WINDOWSOUT.dds"
    elif "window" in needle:
        final_name = f"{short_name}_{number}WINDOW.dds"
    elif "region" in needle:
        final_name = f"{short_name}_{number}_Region.dds"
    elif ".json" in needle:
        final_name = f"{short_name}_{number}.json"
    elif ".dds" in needle:
        final_name = f"{short_name}_{number}.dds"
    elif "helmet.dds" in needle:
        final_name = f"{short_name}_{number}helmet.dds"
    elif "icon.png" in needle:
        final_name = f"{short_name}_{number}icon.png"
    elif "SMicon.dds" in needle:
        final_name = f"{short_name}_{number}SMicon.dds"
    elif "icon.dds" in needle:
        final_name = f"{short_name}_{number}icon.dds"
    elif "helmet.dds" in needle:
        final_name = f"{short_name}_{number}helmet.png"
    elif "-icon-128x72" in needle:
        final_name = f"{short_name}_{number}-icon-128x72.png"
    elif "-icon-256x144" in needle:
        final_name = f"{short_name}_{number}-icon-256x144.png"
    elif "-icon-1024x576" in needle:
        final_name = f"{short_name}_{number}-icon-1024x576.png"
    elif "-icon-2048x1152" in needle:
        final_name = f"{short_name}_{number}-icon-2048x1152.png"
    elif ".json" in needle:
        final_name = f"{short_name}_{number}.json"
    return final_name


def build_skin_command(env, *args, **kwargs):
    if not env["server"]:
        print("no server set")
    else:
        server_key = env["server"]
        server_data = env["server_data"][server_key]
        url = server_data["url"]
        secret = server_data["secret"]
        file_name = args[0][0]
        if not exists(file_name):
            print("file not existing")
        else:

            # read templates
            build_path = server_data["env"]["build_path"]
            packs_path = server_data["env"]["packs_path"]
            templates_path = server_data["env"]["templates_path"]

            templates = {}
            for file in listdir(templates_path):
                with open(join(templates_path, file)) as file_handle:
                    templates[file.replace(".veh", "")] = file_handle.read()
            with open(file_name, "r") as file:
                data = load(file)
                veh_mods = data["cars"]
                for _, vehicle in veh_mods.items():
                    mod_name = vehicle["component"]["name"]
                    short_name = vehicle["component"]["short"]
                    entries = vehicle["entries"]
                    is_update = vehicle["component"]["update"]
                    if is_update:
                        all_files_in_build = listdir(join(build_path, mod_name))
                        output_filename = join(packs_path, f"server_{mod_name}.tar.gz")
                        with tarfile.open(output_filename, "w:gz") as tar:
                            for raw_file in all_files_in_build:
                                if ".ini" in raw_file:
                                    tar.add(
                                        join(build_path, mod_name, raw_file), raw_file
                                    )
                                    print(f"Adding {raw_file} to archive")
                            for entry in entries:
                                match = re.match(team_pattern, entry)
                                name = match.group("name").strip()
                                number = match.group("number").strip()
                                description = entry
                                # Parse the VEH file
                                raw_template = templates[mod_name]
                                parsed_template = eval(f'f"""{raw_template}\n"""')
                                tar_template = parsed_template.encode("utf8")
                                info = tarfile.TarInfo(
                                    name=f"{short_name}_{number}.veh"
                                )
                                info.size = len(tar_template)

                                file_pattern = r"([^\d]|_)" + number + "[^\d]"
                                # Collect livery files for this car
                                skin_files = []
                                had_custom_file = False
                                for build_file in all_files_in_build:
                                    if (
                                        re.search(file_pattern, build_file) is not None
                                        and ".veh" not in build_file
                                    ):
                                        skin_files.append(build_file)
                                for skin_file in skin_files:
                                    path = join(join(build_path, mod_name), skin_file)
                                    needle = skin_file.lower()
                                    final_name = skin_file
                                    final_name = get_final_filename(
                                        needle, short_name, number
                                    )
                                    had_custom_file = True
                                    tar.add(path, final_name)
                                    print(f"Adding {final_name} to archive")

                                if had_custom_file:
                                    print(f"Adding generated {info.name} to archive")
                                    tar.addfile(info, io.BytesIO(tar_template))

                        got = post(
                            url + "/skins",
                            headers={"authorization": secret},
                            files={"skins": open(output_filename, "rb")},
                            data={"target_path": mod_name},
                        )
                return True


def add_numberplates(
    numberplates: dict,
    skin_file: str,
    region_file: str,
    skin_output_file: str,
    region_output_file: str,
    text=None,
):
    livery = image.Image(filename=skin_file)
    region = image.Image(filename=region_file)
    livery.compression = "dxt5"
    region.compression = "dxt5"
    for numberplate in numberplates:
        x = numberplate["x"]
        y = numberplate["y"]
        rotate = numberplate["rotate"]
        if "file" in numberplate:
            width = numberplate["width"]
            height = numberplate["height"]
            numberplate_img = image.Image(filename=numberplate["file"])
            numberplate_img.resize(width, height)
            numberplate_img.rotate(rotate)
            livery.composite(numberplate_img, left=x, top=y)
        if "text" in numberplate:
            transparency_img = image.Image(filename=numberplate["transparency"])
            with Drawing() as draw:
                draw.fill_color = Color("#c8c8c8")
                draw.font_size = numberplate["size"]
                draw.color = Color("#c8c8c8")
                draw.text(x, y, numberplate["text"] if text is None else text)
                draw(transparency_img)
                transparency_img.rotate(rotate)
                livery.composite(transparency_img, left=0, top=0)

    livery.save(filename=skin_output_file)

    for numberplate in numberplates:
        x = numberplate["x"]
        y = numberplate["y"]
        rotate = numberplate["rotate"]
        if "region" in numberplate:
            width = numberplate["width"]
            height = numberplate["height"]
            region_file = numberplate["region"]
            region_img_stamp = image.Image(filename=region_file)
            region.composite(region_img_stamp, left=x, top=y)
    region.save(filename=region_output_file)


def stamp_command(env, *args, **kwargs):
    config_path = env["server_config"]
    server_key = env["server"]
    server_data = env["server_data"][server_key]
    build_path = server_data["env"]["build_path"]
    with open(config_path, "r") as file:
        config = loads(file.read())
        for workshop_id, vehicle in config["cars"].items():
            short_name = vehicle["component"]["short"]
            vehicle_name = vehicle["component"]["name"]
            if vehicle["component"]["update"]:
                entries = vehicle["entries"]
                numberplates = (
                    []
                    if "numberplates" not in vehicle["component"]
                    else vehicle["component"]["numberplates"]
                )
                for entry in entries:
                    match = re.match(team_pattern, entry)
                    name = match.group("name").strip()
                    number = match.group("number").strip()
                    skin_path = join(
                        build_path,
                        vehicle_name,
                        short_name + "_" + str(number) + ".dds",
                    )
                    region_path = join(
                        build_path,
                        vehicle_name,
                        short_name + "_" + str(number) + "_Region.dds",
                    )
                    if exists(skin_path) and exists(region_path):
                        add_numberplates(
                            numberplates,
                            skin_path,
                            region_path,
                            skin_path,
                            region_path,
                            number,
                        )
    return True


def query_config(env, *args, **kwargs):
    got, text = http_api_helper(env, "config", {}, get)
    print(text)
    return got


def get_config_command(env, *args, **kwargs) -> bool:
    got = query_config(env, args, kwargs)
    print(got)
    return True


def get_ports_command(env, *args, **kwargs) -> bool:
    got = query_config(env, args, kwargs)
    simulation_port = int(got["Multiplayer General Options"]["Simulation Port"])
    http_port = int(got["Multiplayer General Options"]["HTTP Server Port"])
    reciever_port = int(got["reciever"]["port"])
    ports = {
        "TCP": [simulation_port, http_port, reciever_port],
        "UDP": [simulation_port, http_port + 1, http_port + 2],
    }
    print(ports)
    return True
