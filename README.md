# xscr33mLabs IpsumWall
 The fastest way to block suspicious IPs in your Windows Firewall!

 This script utilizes the IP blacklist from [stamparm's ipsum repository](https://github.com/stamparm/ipsum),
 an open-source project that tracks suspicious IP addresses based on various threat intelligence sources.
 The list is categorized into different "threat levels," with level 1 being the most inclusive (all potential threats),
 and level 8 containing only the most high-risk addresses. This allows users to adjust the level of security
 by selecting which level of threats to block.

 xscr33mLabs IpsumWall automatically downloads the desired threat level list (defined by the 'block_level' variable),
 processes the IPs, and creates firewall rules in Windows to block both inbound and outbound traffic for these IPs.

 ## Key features
 - Uses Windows built-in `netsh advfirewall` tool to block IP addresses by creating new firewall rules.
 - Splits the IP list into manageable chunks of 500 IPs per rule to avoid issues with command length limits.
 - Ensures persistent firewall rules across script runs by maintaining a local cache of blocked IPs and rule numbers.
 - Provides logging and a summary report that tracks the number of blocked IPs and the time taken for each execution.
 - Can be run periodically or as part of a security automation pipeline to maintain an updated firewall blacklist.

 ## IMPORTANT
 - The script requires admin privileges to modify the Windows Firewall rules.
 - Avoid manually deleting cache files (blocked_ips.txt and rule_number_cache.txt), as this could lead to duplicate firewall rules.
   If necessary, clear the existing rules in Windows Firewall before running the script again without the cache files.

 ## To run
 1. Set the desired 'block_level' (1 for maximum protection, 8 for high-risk threats only).
 2. Run the launch_script.bat with an double-click and let the magic happen.

</br> 
</br> 
</br> 
</br> 
</br> 

# WinServer22_Hardening.ps1


This PowerShell script automates initial configurations for a Windows Server, focusing on security and performance optimization. It includes tasks like disabling unnecessary services, removing Internet Explorer, and modifying insecure firewall rules.

## Use Cases

- **Initial Server Setup**: For servers requiring initial configurations for security and optimization.
- **Baseline Configuration**: For organizations needing a standard baseline for Windows Servers.
- **Automated Administration**: Useful for administrators automating initial setup tasks.

## Key features

1. **Disable Server Manager Task**:
   - Prevents the Server Manager from launching automatically on startup.

2. **Disable Unnecessary Services**:
   - Disables non-essential services to improve server performance and security.

3. **Uninstall Internet Explorer**:
   - Removes Internet Explorer to reduce security vulnerabilities.

4. **Disable Default Firewall Rules**:
   - Disables various pre-enabled firewall rules, particularly those related to unnecessary or redundant services.

5. **Block Outbound RDP Sessions**:
   - Adds a firewall rule to prevent outbound Remote Desktop Protocol (RDP) sessions.

## To Run

1. **Open PowerShell as Administrator**:
   - Right-click on the PowerShell icon and select “Run as Administrator.”

2. **Execute the Script**:
   - Run the script by navigating to its location and executing it:
     ```powershell
     .\your_script_name.ps1
     ```

3. **Follow Prompts**:
   - If the script requires elevated permissions, follow the prompts to restart it as an administrator.

## IMPORTANT

- **Compatibility**: This script is designed for Windows Server environments.
- **Script Permissions**: The script must be run as an administrator for full functionality.