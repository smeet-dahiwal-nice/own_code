import json
from datetime import datetime, timedelta
import pytz
from ruamel.yaml import YAML

# ---------- CONFIG ----------
JSON_FILE = "cr_info.json"
YAML_FILE = "cr_info.yaml"

IST_TZ = pytz.timezone("Asia/Kolkata")
US_MT_TZ = pytz.timezone("US/Mountain")

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
# ----------------------------

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def load_yaml(path):
    with open(path, "r") as f:
        return yaml.load(f)


def save_yaml(path, data):
    with open(path, "w") as f:
        yaml.dump(data, f)


def main():
    json_data = load_json(JSON_FILE)
    yaml_data = load_yaml(YAML_FILE)

    window_hours = json_data["deployment_window_hours"]

    for phase in yaml_data["deploymentPhase"]:
        phase_name = phase.get("name")

        if phase_name not in json_data["phases"]:
            continue

        for env_group, env_data in json_data["phases"][phase_name].items():

            # Skip env-groups removed from YAML
            if env_group not in phase:
                continue

            ist_time_str = env_data["start_time"]
            deployer_name = env_data.get("deployer")

            # ---- IST start ----
            start_dt_ist = IST_TZ.localize(
                datetime.strptime(ist_time_str, DATETIME_FORMAT)
            )

            end_dt_ist = start_dt_ist + timedelta(hours=window_hours)

            # ---- Convert to US Mountain ----
            start_dt_us = start_dt_ist.astimezone(US_MT_TZ)
            end_dt_us = end_dt_ist.astimezone(US_MT_TZ)

            # ---- Update dates ----
            phase[env_group]["startDate"] = start_dt_us.strftime(DATETIME_FORMAT)
            phase[env_group]["endDate"] = end_dt_us.strftime(DATETIME_FORMAT)

            # ---- Update deployer ----
            if deployer_name:
                phase[env_group]["deployer"] = deployer_name

            print(f"✔ Updated {phase_name} → {env_group}")
            print(f"  Start (US MT): {phase[env_group]['startDate']}")
            print(f"  End   (US MT): {phase[env_group]['endDate']}")
            if deployer_name:
                print(f"  Deployer     : {deployer_name}")

    save_yaml(YAML_FILE, yaml_data)
    print("\n✅ cr_info.yaml updated successfully")


if __name__ == "__main__":
    main()
