#!/usr/bin/env python3
import requests
import json
from time import sleep
import sys
import os
from pathlib import Path
import subprocess

# --- CONFIGURATION ---
CONFIG_FILE = os.path.expanduser("~/dotfiles/.bin/we_usage.json")
BASE_URL = "https://my.te.eg"
LOGIN_URL = (
    f"{BASE_URL}/echannel/service/besapp/base/rest/busiservice/v1/auth/userAuthenticate"
)
USAGE_URL = (
    f"{BASE_URL}/echannel/service/besapp/base/rest/busiservice/cz/cbs/bb/queryFreeUnit"
)


def load_config():
    """Load configuration from file"""
    try:
        argConf = sys.argv[1:]
        if len(argConf) != 0:
            confFile = argConf[0]
        else:
            confFile = CONFIG_FILE

        with open(confFile) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found at {CONFIG_FILE}")
        print("Please create it with your credentials in this format:")
        print(
            """{
    "username": "FBB0211122233",
    "password": "your_password"
}"""
        )
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in config file {CONFIG_FILE}")
        sys.exit(1)


def get_usage(session, config):
    """Fetch usage data from TE portal"""
    try:
        # --- LOGIN ---
        login_response = session.post(
            LOGIN_URL,
            headers={
                "Content-Type": "application/json",
                "channelId": "702",
                "clientType": "Firefox",
                "isCoporate": "false",
                "isMobile": "false",
                "isSelfcare": "true",
                "languageCode": "ar-EG",
                "Host": "my.te.eg",
            },
            json={
                "acctId": config["username"],
                "appLocale": "ar-EG",
                "isMobile": "N",
                "isSelfcare": "Y",
                "password": config["password"],
                "recaptchaToken": "",
            },
        )

        login_response.raise_for_status()
        login_data = login_response.json()

        if login_data.get("header", {}).get("retCode") != "0":
            return None, "Login failed"

        auth_token = login_data["body"]["token"]
        subscriber_id = login_data["body"]["subscriber"]["subscriberId"]

        session.headers.update(
            {
                "Authorization": f"Bearer {auth_token}",
                "csrftoken": auth_token,
            }
        )

        sleep(1)  # Brief delay

        # --- GET USAGE ---
        usage_response = session.post(
            USAGE_URL,
            headers={
                "Content-Type": "application/json",
                "channelId": "702",
                "clientType": "Firefox",
                "isCoporate": "false",
                "isMobile": "false",
                "isSelfcare": "true",
                "languageCode": "ar-EG",
                "Host": "my.te.eg",
                "csrftoken": auth_token,
                "delegatorSubsId": "",
                "X-Requested-With": "XMLHttpRequest",
            },
            json={
                "mainOfferId": "820048",
                "needQueryPoint": True,
                "subscriberId": subscriber_id,
            },
        )

        usage_response.raise_for_status()
        return usage_response.json(), None

    except Exception as e:
        return None, str(e)


def format_output(usage_data, simple=False):
    """Format the output for Polybar"""
    if not usage_data or "body" not in usage_data or not usage_data["body"]:
        return "No data"

    item = usage_data["body"][0]
    used = float(item["used"])
    total = float(item["total"])
    remain = float(item["remain"])
    pct_used = (used / total) * 100
    remainingDays = item["freeUnitBeanDetailList"][0]["remainingDaysForRenewal"]
    glyph = "🌐"  # You can change this to any other glyph

    if simple:
        return f"{used:.1f}/{total:.0f}GB ({remain:.1f} left)"

    # Define color thresholds
    if remain < 20:
        color = "#FF0000"  # Red for low value
    elif remain < 50:
        color = "#FFA500"  # Orange for medium value
    else:
        color = "#adff00"  # Green for high value

    if remain <10:
        subprocess.run(["notify-send", "WE Usage", "Usage is below 10GB"])

    return f"%{{F{color}}}{glyph} {remain:.1f}GB ({remainingDays})%{{F-}}"


def main():
    config = load_config()

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Origin": BASE_URL,
            "DNT": "1",
            "Referer": f"{BASE_URL}/echannel/",
        }
    )

    # Initial request to get cookies
    session.get(f"{BASE_URL}/echannel/")

    usage_data, error = get_usage(session, config)

    if error:
        print(f"WE: Error ({error})")
        sys.exit(1)

    # Simple output for Polybar (remove --simple for full output)
    simple_output = "--simple" not in sys.argv
    print(format_output(usage_data, simple=simple_output))


if __name__ == "__main__":
    main()
