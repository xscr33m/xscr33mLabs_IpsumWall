#######################################################################################################################################
#
# ██╗░░██╗░██████╗░█████╗░██████╗░██████╗░██████╗░███╗░░░███╗██╗░░░░░░█████╗░██████╗░░██████╗
# ╚██╗██╔╝██╔════╝██╔══██╗██╔══██╗╚════██╗╚════██╗████╗░████║██║░░░░░██╔══██╗██╔══██╗██╔════╝
# ░╚███╔╝░╚█████╗░██║░░╚═╝██████╔╝░█████╔╝░█████╔╝██╔████╔██║██║░░░░░███████║██████╦╝╚█████╗░
# ░██╔██╗░░╚═══██╗██║░░██╗██╔══██╗░╚═══██╗░╚═══██╗██║╚██╔╝██║██║░░░░░██╔══██║██╔══██╗░╚═══██╗
# ██╔╝╚██╗██████╔╝╚█████╔╝██║░░██║██████╔╝██████╔╝██║░╚═╝░██║███████╗██║░░██║██████╦╝██████╔╝
# ╚═╝░░╚═╝╚═════╝░░╚════╝░╚═╝░░╚═╝╚═════╝░╚═════╝░╚═╝░░░░░╚═╝╚══════╝╚═╝░░╚═╝╚═════╝░╚═════╝░
#
# ██╗██████╗░░██████╗██╗░░░██╗███╗░░░███╗░██╗░░░░░░░██╗░█████╗░██╗░░░░░██╗░░░░░
# ██║██╔══██╗██╔════╝██║░░░██║████╗░████║░██║░░██╗░░██║██╔══██╗██║░░░░░██║░░░░░
# ██║██████╔╝╚█████╗░██║░░░██║██╔████╔██║░╚██╗████╗██╔╝███████║██║░░░░░██║░░░░░
# ██║██╔═══╝░░╚═══██╗██║░░░██║██║╚██╔╝██║░░████╔═████║░██╔══██║██║░░░░░██║░░░░░
# ██║██║░░░░░██████╔╝╚██████╔╝██║░╚═╝░██║░░╚██╔╝░╚██╔╝░██║░░██║███████╗███████╗
# ╚═╝╚═╝░░░░░╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚══════╝╚══════╝
#
# The fastest way to block suspicious IPs in your Windows Firewall!
#
# This script utilizes the IP blacklist from stamparm's ipsum repository (https://github.com/stamparm/ipsum),
# an open-source project that tracks suspicious IP addresses based on various threat intelligence sources.
# The list is categorized into different "threat levels," with level 1 being the most inclusive (all potential threats),
# and level 8 containing only the most high-risk addresses. This allows users to adjust the level of security
# by selecting which level of threats to block.
#
# It automatically downloads the desired threat level list (defined by the 'block_level' variable),
# processes the IPs, and creates firewall rules in Windows to block both inbound and outbound traffic for these IPs.
#
# Key features:
# - Uses Windows built-in `netsh advfirewall` tool to block IP addresses by creating new firewall rules.
# - Splits the IP list into manageable chunks of 500 IPs per rule to avoid issues with command length limits.
# - Ensures persistent firewall rules across script runs by maintaining a local cache of blocked IPs and rule numbers.
# - Provides logging and a summary report that tracks the number of blocked IPs and the time taken for each execution.
# - Can be run periodically or as part of a security automation pipeline to maintain an updated firewall blacklist.
#
# IMPORTANT:
# - The script requires admin privileges to modify the Windows Firewall rules.
# - Avoid manually deleting cache files (blocked_ips.txt and rule_number_cache.txt), as this could lead to duplicate firewall rules.
#   If necessary, clear the existing rules in Windows Firewall before running the script again without the cache files.
#
# To run:
# 1. Set the desired 'block_level' (1 for maximum protection, 8 for high-risk threats only).
# 2. Run the launch_script.bat with an double-click and let the magic happen.
#
# Created by: xscr33mLabs 2024
#######################################################################################################################################
import ctypes
import logging
import subprocess
import sys
import os
import time
import webbrowser
from datetime import datetime
from threading import Timer

# Script Configuration
block_level = 1  # 1 = all IPs, 8 = high-risk only
ips_per_rule = 500  # Number of IPs per rule.
max_logs = 5  # Number of logs to retain
skip_prompt = False  # Set to True to skip Y/N prompt for deleting firewall rules
log_level = logging.ERROR  # Define log level: DEBUG, INFO, WARNING, ERROR, CRITICAL

ipsum_url = f"https://raw.githubusercontent.com/stamparm/ipsum/refs/heads/master/levels/{
    block_level}.txt"

# Cache files !!Do not delete - leads to duplicate rules!!
cache_dir = "cache"
results_dir = "results"
logs_dir = "logs"

blocked_ips_file = os.path.join(cache_dir, "blocked_ips.txt")
rule_number_file = os.path.join(cache_dir, "rule_number_cache.txt")
summary_file = os.path.join(results_dir, "summary.txt")

os.makedirs(cache_dir, exist_ok=True)
os.makedirs(results_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)

log_filename = os.path.join(
    logs_dir, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
logging.basicConfig(level=log_level,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger()

current_log_level = logging.getLevelName(logger.getEffectiveLevel())

file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))

logger.addHandler(file_handler)


def manage_logs(logs_dir, max_logs):
    """ Remove the oldest logs if there are more than max_logs files """
    log_files = [os.path.join(logs_dir, f) for f in os.listdir(
        logs_dir) if os.path.isfile(os.path.join(logs_dir, f))]
    log_files.sort(key=os.path.getmtime)

    if len(log_files) > max_logs:
        logs_to_remove = log_files[:-max_logs]
        for log_file in logs_to_remove:
            print(f"Deleting old log file: {log_file}")
            logger.debug(f"Deleting old log file: {log_file}")
            os.remove(log_file)


manage_logs(logs_dir, max_logs)


def check_admin():
    """ Enforce running as admin """
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("No admin rights, restarting as admin.")
            logger.warning("No admin rights, restarting as admin.")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, __file__, None, 1)
            sys.exit(0)
        else:
            print("Admin rights confirmed.")
            logger.debug("Admin rights confirmed.")
    except Exception as e:
        print(f"Admin check failed: {e}")
        logger.error(f"Admin check failed: {e}")
        sys.exit(1)


def install_packages():
    """ Install required packages """
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "requests"])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install required packages: {e}")
        logger.error(f"Failed to install required packages: {e}")
        sys.exit(1)


def check_for_packages():
    """ Check for needed packages """
    try:
        import requests # type: ignore
    except ImportError:
        print("requests not found. Installing now...")
        logger.warning("requests not found. Installing now...")
        install_packages()
        print("Restarting script after package installation...")
        logger.debug("Restarting script after package installation...")
        os.execv(sys.executable, ['python'] + sys.argv)


def check_python_installed():
    """ Check if Python is installed """
    try:
        version = subprocess.check_output(
            [sys.executable, '--version'], stderr=subprocess.STDOUT)
        print(f"Python {version.decode().strip()} found.")
        logger.debug(f"Python {version.decode().strip()} found.")
    except FileNotFoundError:
        print(
            "Python is not installed. Opening the Python download page...")
        logger.error(
            "Python is not installed. Opening the Python download page...")
        webbrowser.open("https://www.python.org/downloads/")
        sys.exit(1)


def download_ips():
    """ Function to download IP addresses """
    try:
        import requests # type: ignore
        print("Downloading IP addresses...")
        logger.debug("Downloading IP addresses...")
        response = requests.get(ipsum_url)
        response.raise_for_status()
        ips = [line.strip() for line in response.text.splitlines()
               if line and not line.startswith("#")]
        print(f"{len(ips)} IP addresses successfully downloaded.")
        logger.debug(f"{len(ips)} IP addresses successfully downloaded.")
        return ips
    except requests.RequestException as e:
        print(f"Error downloading IPs: {e}")
        logger.error(f"Error downloading IPs: {e}")
        return []


def load_blocked_ips():
    """ Function to load already blocked IPs from file """
    if os.path.exists(blocked_ips_file):
        with open(blocked_ips_file, 'r') as f:
            blocked_ips = {line.strip() for line in f}
        print(f"{len(blocked_ips)} already blocked IPs loaded.")
        logger.debug(f"{len(blocked_ips)} already blocked IPs loaded.")
        return blocked_ips
    else:
        print("No blocked IPs found.")
        logger.debug("No blocked IPs found.")
        return set()


def save_blocked_ip(ip):
    """ Function to save blocked IPs to cache """
    with open(blocked_ips_file, 'a') as f:
        f.write(ip + '\n')


def load_rule_number():
    """ Load the last rule number """
    if os.path.exists(rule_number_file):
        with open(rule_number_file, 'r') as f:
            return int(f.read().strip())
    return 1


def save_rule_number(rule_number):
    """ Save the rule number to the cache file """
    with open(rule_number_file, 'w') as f:
        f.write(str(rule_number))


def count_existing_rules():
    """ Count the existing firewall rules with the xL-Block prefix """
    try:
        result = subprocess.run(
            'netsh advfirewall firewall show rule name=all | findstr /C:"xL-Block-"', shell=True, capture_output=True, text=True
        )
        rule_count = len(result.stdout.splitlines())
        print(f"Found {rule_count} existing xL-Block rules.")
        logger.debug(f"Found {rule_count} existing xL-Block rules.")
        return rule_count
    except Exception as e:
        print(f"Failed to count existing firewall rules: {e}")
        logger.error(f"Failed to count existing firewall rules: {e}")
        return 0


def delete_firewall_rules():
    """ Delete existing xL-Block firewall rules after user confirmation """
    rule_count = count_existing_rules()
    if rule_count == 0:
        print("No xL-Block rules to delete.")
        return

    if skip_prompt or prompt_user(f"Do you want to delete the {rule_count} existing xL-Block firewall rules? (Y/N): "):
        print("Deleting existing xL-Block firewall rules...")
        logger.debug("Deleting existing xL-Block firewall rules...")
        try:
            subprocess.run(
                'netsh advfirewall firewall delete rule name="xL-Block-*"', shell=True)
            print("All xL-Block rules have been deleted.")
            logger.debug("All xL-Block rules have been deleted.")
        except Exception as e:
            print(f"Failed to delete firewall rules: {e}")
            logger.error(f"Failed to delete firewall rules: {e}")


def prompt_user(prompt_message):
    """ Prompt for Y/N input with a 60-second timeout """
    response = None

    def timeout():
        nonlocal response
        response = "N"
        print("No response received in time. Defaulting to 'N'.")
        logger.debug("No response received in time. Defaulting to 'N'.")

    timer = Timer(60.0, timeout)
    timer.start()

    response = input(prompt_message).strip().upper()
    timer.cancel()

    return response == "Y"


def block_ips(ip_list, rule_number, total_ips, blocked_so_far):
    """ Function to block a list of IPs """
    try:
        print(f"Blocking {len(ip_list)} IPs...")
        logger.debug(f"Blocking {len(ip_list)} IPs...")
        in_rule_name = f"xL-Block-{rule_number}"
        out_rule_name = f"xL-Block-{rule_number}"
        subprocess.run(f'netsh advfirewall firewall add rule name="{
                       in_rule_name}" dir=in action=block remoteip={",".join(ip_list)}', shell=True)
        subprocess.run(f'netsh advfirewall firewall add rule name="{
                       out_rule_name}" dir=out action=block remoteip={",".join(ip_list)}', shell=True)

        for ip in ip_list:
            save_blocked_ip(ip)

        blocked_so_far += len(ip_list)
        print(f"Blocking successful. Progress: {
            blocked_so_far}/{total_ips} ({(blocked_so_far / total_ips) * 100:.2f}%)")
        logger.debug(f"Blocking successful. Progress: {
            blocked_so_far}/{total_ips} ({(blocked_so_far / total_ips) * 100:.2f}%)")
    except Exception as e:
        print(f"Error blocking IPs: {e}")
        logger.error(f"Error blocking IPs: {e}")

    return blocked_so_far


def main():
    print("Starting xscr33mLabs xL_IpsumWall...")
    logger.debug("Starting xscr33mLabs xL_IpsumWall...")

    print(f"Current log level: {current_log_level}")
    logger.debug(f"Current log level: {current_log_level}")

    check_python_installed()
    check_admin()
    check_for_packages()

    ips = download_ips()
    blocked_ips = load_blocked_ips()

    ips_to_block = [ip for ip in ips if ip not in blocked_ips]
    if not ips_to_block:
        print("All IPs are already blocked.")
        logger.debug("All IPs are already blocked.")
        with open(summary_file, 'a') as summary:
            summary.write(f"No new IPs to block found at {
                          datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        return

    print(f"{len(ips_to_block)} new IPs need to be blocked.")
    logger.debug(f"{len(ips_to_block)} new IPs need to be blocked.")
    start_time = time.time()

    delete_firewall_rules()

    rule_number = load_rule_number()
    total_ips = len(ips_to_block)
    blocked_so_far = 0

    for i in range(0, total_ips, ips_per_rule):
        blocked_so_far = block_ips(
            ips_to_block[i:i + ips_per_rule], rule_number, total_ips, blocked_so_far)
        rule_number += 1

    save_rule_number(rule_number)
    duration = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))

    with open(summary_file, 'a') as summary:
        summary.write(f"{len(ips_to_block)} IPs blocked in {duration} at {
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(f"Done! {len(ips_to_block)} IPs were blocked in {duration}.")
    logger.debug(f"Done! {len(ips_to_block)} IPs were blocked in {duration}.")


if __name__ == "__main__":
    main()
