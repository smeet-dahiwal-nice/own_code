import json
import yaml
from datetime import datetime, timedelta
import pytz

# ---------- CONFIG ----------
JSON_FILE = "cr_info.json"
YAML_FILE = "cr_info.yaml"

IST_TZ = pytz.timezone("Asia/Kolkata")
US_MT_TZ = pytz.timezone("US/Mountain")

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
# ----------------------------


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def save_yaml(path, data):
    with open(path, "w") as f:
        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            default_flow_style=False
        )


def main():
    json_data = load_json(JSON_FILE)
    yaml_data = load_yaml(YAML_FILE)

    window_hours = json_data["deployment_window_hours"]

    for phase in yaml_data["deploymentPhase"]:
        phase_name = phase["name"]

        if phase_name not in json_data["phases"]:
            continue

        for env_group, ist_time_str in json_data["phases"][phase_name].items():

            if env_group not in phase:
                continue

            # ---- IST start ----
            start_dt_ist = IST_TZ.localize(
                datetime.strptime(ist_time_str, DATETIME_FORMAT)
            )

            end_dt_ist = start_dt_ist + timedelta(hours=window_hours)

            # ---- Convert to US Mountain ----
            start_dt_us = start_dt_ist.astimezone(US_MT_TZ)
            end_dt_us = end_dt_ist.astimezone(US_MT_TZ)

            # ---- Write into YAML ----
            phase[env_group]["startDate"] = start_dt_us.strftime(DATETIME_FORMAT)
            phase[env_group]["endDate"] = end_dt_us.strftime(DATETIME_FORMAT)

            print(f"✔ Updated {phase_name} → {env_group}")
            print(f"  Start (US MT): {phase[env_group]['startDate']}")
            print(f"  End   (US MT): {phase[env_group]['endDate']}")

    save_yaml(YAML_FILE, yaml_data)


if __name__ == "__main__":
    main()
