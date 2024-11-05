# xscr33mLabs IpsumWall
 The fastest way to block suspicious IPs in your Windows Firewall!

 This script utilizes the IP blacklist from [stamparm's ipsum repository](https://github.com/stamparm/ipsum),
 an open-source project that tracks suspicious IP addresses based on various threat intelligence sources.
 The list is categorized into different "threat levels," with level 1 being the most inclusive (all potential threats),
 and level 8 containing only the most high-risk addresses. This allows users to adjust the level of security
 by selecting which level of threats to block.

 xscr33mLabs IpsumWall automatically downloads the desired threat level list (defined by the 'block_level' variable),
 processes the IPs, and creates firewall rules in Windows to block both inbound and outbound traffic for these IPs.

 ## Key features:
 - Uses Windows built-in `netsh advfirewall` tool to block IP addresses by creating new firewall rules.
 - Splits the IP list into manageable chunks of 500 IPs per rule to avoid issues with command length limits.
 - Ensures persistent firewall rules across script runs by maintaining a local cache of blocked IPs and rule numbers.
 - Provides logging and a summary report that tracks the number of blocked IPs and the time taken for each execution.
 - Can be run periodically or as part of a security automation pipeline to maintain an updated firewall blacklist.

 ## IMPORTANT:
 - The script requires admin privileges to modify the Windows Firewall rules.
 - Avoid manually deleting cache files (blocked_ips.txt and rule_number_cache.txt), as this could lead to duplicate firewall rules.
   If necessary, clear the existing rules in Windows Firewall before running the script again without the cache files.

 ## To run:
 1. Set the desired 'block_level' (1 for maximum protection, 8 for high-risk threats only).
 2. Run the launch_script.bat with an double-click and let the magic happen.
