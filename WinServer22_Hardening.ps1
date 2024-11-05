# Script for basic configuration of a Windows Server

# Define a function to handle console output with timestamps
function Write-Log {
    param ([string]$Message)
    Write-Output "$(Get-Date -Format "yyyy-MM-dd HH:mm:ss") - $Message"
}

# Function to verify if the script is running with administrator privileges
function EnsureAdminRights {
    if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        Write-Log "Script is not running with Administrator privileges."

        # Timer countdown for re-execution prompt
        $timerSeconds = 10
        Write-Log "The script will re-launch with Administrator privileges in $timerSeconds seconds."
        Write-Log "Press 'Y' to confirm the restart or 'N' to exit the script."

        # Countdown loop for user response
        for ($i = $timerSeconds; $i -gt 0; $i--) {
            if ($host.UI.RawUI.KeyAvailable) {
                $key = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
                if ($key.Character -eq 'y' -or $key.Character -eq 'Y') {
                    Write-Log "Restarting script with Administrator privileges..."
                    Start-Process powershell.exe -ArgumentList "-File `"$PSCommandPath`"" -Verb RunAs
                    exit
                }
                elseif ($key.Character -eq 'n' -or $key.Character -eq 'N') {
                    Write-Log "Script execution terminated by user."
                    exit
                }
            }
            Start-Sleep -Seconds 1
            Write-Log "$i seconds remaining..."
        }

        # If no user response, restart the script automatically
        Write-Log "No response received. Restarting script with Administrator privileges..."
        Start-Process powershell.exe -ArgumentList "-File `"$PSCommandPath`"" -Verb RunAs
        exit
    }
}

# Set the console output encoding to UTF-8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Validate administrator rights for script execution
EnsureAdminRights

Write-Log "Starting basic configuration of Windows Server..."

# Step 1: Disable the scheduled task for Server Manager launch on startup
Write-Log "Disabling Server Manager startup task..."
$serverManagerTaskPath = "\Microsoft\Windows\Server Manager\"
$serverManagerTaskName = "ServerManager"

try {
    $task = Get-ScheduledTask -TaskPath $serverManagerTaskPath -TaskName $serverManagerTaskName -ErrorAction Stop
    Disable-ScheduledTask -TaskPath $serverManagerTaskPath -TaskName $serverManagerTaskName
    Write-Log "Server Manager startup task successfully disabled."
}
catch {
    Write-Log "Server Manager task could not be found or disabled: $_"
}

# Step 2: Disable specified services for optimized server performance
$servicesToDisable = @(
    "InstallService", "Spooler", "WPDBusEnum", "fdPHost",
    "ShellHWDetection", "TrkWks", "bthserv", "NcbService",
    "SensrSvc", "WiaRpc", "upnphost", "AudioEndpointBuilder", "FrameServer"
)

Write-Log "Disabling unnecessary services..."
foreach ($serviceName in $servicesToDisable) {
    try {
        $service = Get-Service -Name $serviceName -ErrorAction Stop
        if ($service.Status -ne 'Stopped') {
            Stop-Service -Name $serviceName -Force
        }
        Set-Service -Name $serviceName -StartupType Disabled
        Write-Log "Service $serviceName successfully disabled."
    }
    catch {
        Write-Log "Service $serviceName could not be disabled or does not exist: $_"
    }
}

# Step 3: Uninstall Internet Explorer for improved security
Write-Log "Uninstalling Internet Explorer..."
$ieCapability = "Browser.InternetExplorer~~~~0.0.11.0"
try {
    $dismResult = dism /online /Remove-Capability /CapabilityName:$ieCapability
    if ($dismResult -match "The operation completed successfully.") {
        Write-Log "Internet Explorer successfully uninstalled."
    }
    else {
        Write-Log "Internet Explorer could not be uninstalled."
    }
}
catch {
    Write-Log "Error encountered while uninstalling Internet Explorer: $_"
}

# Step 4: Disable pre-enabled firewall rules for additional security
Write-Log "Disabling default enabled firewall rules..."

$firewallRules = @(
    "AllJoyn Router (TCP-In)", "AllJoyn Router (TCP-Out)", 
    "AllJoyn Router (UDP-In)", "AllJoyn Router (UDP-Out)", 
    "Captive Portal Flow", "Cast to Device functionality (qWave-TCP-In)", 
    "Cast to Device functionality (qWave-TCP-Out)", 
    "Cast to Device functionality (qWave-UDP-In)", 
    "Cast to Device functionality (qWave-UDP-Out)", 
    "Cast to Device SSDP Discovery (UDP-In)", 
    "Cast to Device streaming server (HTTP-Streaming-In)", 
    "Cast to Device streaming server (RTCP-Streaming-In)", 
    "Cast to Device streaming server (RTP-Streaming-Out)", 
    "Cast to Device streaming server (RTSP-Streaming-In)", 
    "Cast to Device UPnP Events (TCP-In)", 
    "Connected User Experiences and Telemetry", 
    "Desktop App Web Viewer", 
    "DIAL protocol server (HTTP-In)", 
    "Email and accounts", 
    "mDNS (UDP-In)", 
    "mDNS (UDP-Out)", 
    "Microsoft Media Foundation Network Source IN [TCP 554]", 
    "Microsoft Media Foundation Network Source IN [UDP 5004-5009]", 
    "Microsoft Media Foundation Network Source OUT [TCP ALL]", 
    "Narrator", "Start", 
    "Windows Default Lock Screen", 
    "Windows Feature Experience Pack", 
    "Work or school account", 
    "Your account"
)

foreach ($rule in $firewallRules) {
    try {
        # Find and disable rules matching the specified names
        $firewallRulesToDisable = Get-NetFirewallRule -DisplayName "*$rule*" -ErrorAction Stop
        foreach ($firewallRule in $firewallRulesToDisable) {
            if ($firewallRule.Enabled -eq 'True') {
                Disable-NetFirewallRule -DisplayName $firewallRule.DisplayName
                Write-Log "Firewall rule '$($firewallRule.DisplayName)' successfully disabled."
            }
            else {
                Write-Log "Firewall rule '$($firewallRule.DisplayName)' is already disabled."
            }
        }
    }
    catch {
        Write-Log "No firewall rule found for '$rule'."
    }
}

# Step 5: Block outbound RDP sessions to restrict remote desktop access
Write-Log "Blocking outbound RDP sessions..."
$rdpOutboundRuleName = "Block Outbound RDP (TCP 3389)"

# Check if the RDP blocking rule already exists, create if not
$existingRule = Get-NetFirewallRule -DisplayName $rdpOutboundRuleName -ErrorAction SilentlyContinue

if (-not $existingRule) {
    New-NetFirewallRule -DisplayName $rdpOutboundRuleName `
        -Direction Outbound `
        -Protocol TCP `
        -LocalPort 3389 `
        -Action Block `
        -Profile Any `
        -Enabled True
    Write-Log "Outbound RDP blocking rule created and enabled."
}
else {
    Write-Log "Outbound RDP blocking rule already exists."
}

Write-Log "Windows Server basic configuration completed."

# Await user input before terminating the script
Write-Log "Press ENTER to exit the script."
Read-Host -Prompt " "
