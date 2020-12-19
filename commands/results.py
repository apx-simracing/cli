from os import listdir
from requests import get
from commands import http_api_helper
from json import loads
import couchdb


def get_results_command(env, *args, **kwargs):
    got, text = http_api_helper(env, "results", {}, get)
    print(text)
    return got


def process_results_command(env, *args, **kwargs):
    got, text = http_api_helper(env, "process_results", {}, get)
    print(text)
    return got


def update_results_command(env, *args, **kwargs):
    got, text = http_api_helper(env, "process_results", {}, get)
    # print(text)
    server = args[0][0]
    couch = couchdb.Server(server)
    if not got:
        raise Exception("Invalid JSON")
    results = loads(text)
    server = env["server"]

    session_db = couch["sessions"]
    laps_db = couch["laps"]
    incidents_db = couch["incidents"]
    for key, value in results.items():
        name = value["name"]
        date = value["date"]
        session = value["session"]
        serverName = value["serverName"]
        trackCourse = value["trackCourse"]
        trackLength = value["trackLength"]
        raceLaps = value["raceLaps"]
        raceTime = value["raceTime"]
        mechFailRate = value["mechFailRate"]
        damageMult = value["damageMult"]
        fuelMult = value["fuelMult"]
        tireMult = value["tireMult"]
        session_data = {
            "server": server,
            "name": name,
            "data": date,
            "session": session,
            "serverName": serverName,
            "trackCourse": trackCourse,
            "trackLength": trackLength,
            "raceLaps": raceLaps,
            "raceTime": raceTime,
            "mechFailRate": mechFailRate,
            "damageMult": damageMult,
            "fuelMult": fuelMult,
            "tireMult": tireMult,
            "vehicleCount": len(value["drivers"])
        }
        query = {
            "selector": {
                "name": {
                    "$eq": name
                },
                "session": {
                    "$eq": session
                },
                "server": {
                    "$eq": server
                },
            }
        }
        if len(list(session_db.find(query))) > 0:
            print(f"Session {name}@{server} already in database")
        else:
            result_data = []
            drivers = value["drivers"]
            for driver in drivers:
                carNumber = driver["CarNumber"]
                teamName = driver["TeamName"]
                swaps = driver["swaps"]
                status = driver["FinishStatus"]
                finish_position = driver["Position"]
                class_finish_position = driver["ClassPosition"]
                grid_position = driver["GridPos"] if "GridPos" in driver else -1
                class_grid_position = driver["ClassGridPos"] if "ClassGridPos" in driver else -1
                carClass = driver["CarClass"]
                drivers_on_car = [
                    driver["Name"].strip()
                ]
                for swap in swaps:
                    if swap["driver"] is not None and swap["driver"].strip() not in drivers_on_car:
                        drivers_on_car.append(swap["driver"].strip())
                result_data.append(
                    {
                        "carNumber": carNumber,
                        "teamName": teamName,
                        "finishPosition": finish_position,
                        "classPosition": class_finish_position,
                        "finishStatus": status,
                        "drivers": drivers_on_car,
                        "gridPosition": grid_position,
                        "classGridPosition": class_grid_position,
                        "carClass": carClass
                    }
                )
            session_data["result"] = result_data
            session_db.save(session_data)
            drivers = value["drivers"]
            incidents = value["incidents"]
            for driver in drivers:
                laps = driver["laps"]
                carNumber = driver["CarNumber"]
                teamName = driver["TeamName"]
                swaps = driver["swaps"]
                status = driver["FinishStatus"]
                finish_position = driver["Position"]
                for lap in laps:
                    lap_driver = driver["Name"]
                    lap_num = int(lap["num"])
                    matching_swaps = list(filter(
                        lambda s: int(s["start"]) <= lap_num and int(s["end"]) >= lap_num, swaps))
                    if len(matching_swaps) > 1:
                        raise Exception(
                            f"Invalid swap amounts found for car {carNumber} in session {name}@{server}")

                    lap_data = lap
                    lap_data["name"] = name
                    lap_data["server"] = server
                    lap_data["driver"] = matching_swaps[0]["driver"] if len(
                        matching_swaps) == 1 else lap_driver
                    lap_data["teamName"] = teamName
                    lap_data["carNumber"] = carNumber
                    lap_data["carState"] = status
                    lap_data["carFinalPosition"] = finish_position
                    driver_incidents = list(
                        filter(lambda i:  i["name1"] == lap_data["driver"], incidents))

                    if len(driver_incidents) > 0:
                        start_time = lap_data["et"]
                        end_time = lap_data["time"]
                        if end_time is not None and start_time != "--.---":
                            lap_incidents = list(
                                filter(lambda i:  i["time"] >= float(
                                    start_time) and i["time"] <= float(
                                    start_time) + end_time, driver_incidents))
                            for lap_incident in lap_incidents:
                                lap_incident_data = {
                                    "name": name,
                                    "other_name": lap_incident["name2"],
                                    "team": teamName,
                                    "carNumber": carNumber,
                                    "server": server,
                                    "driver": lap_data["driver"],
                                    "time": lap_incident["time"],
                                    "lap": lap_data["num"]
                                }
                                incidents_db.save(lap_incident_data)

                    laps_db.save(lap_data)
    return True
