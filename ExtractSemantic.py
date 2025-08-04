import subprocess
import os
import time

# Define the PowerShell script as a multi-line string
ps_script = r"""
$conn = $null
Write-Host "Creating ADOMD.Connection object..."
$conn = New-Object -ComObject ADOMD.Connection
if ($conn -eq $null) {
    Write-Host "Failed to create ADOMD.Connection object. ADOMD.NET may not be installed or accessible."
    exit
}
Write-Host "ADOMD.Connection object created successfully"

$connStr = "Provider=MSOLAP;Data Source=localhost:<PORT>;Initial Catalog=;Integrated Security=SSPI;"
Write-Host "Connection string: $connStr"
$conn.ConnectionString = $connStr

Write-Host "Attempting to open connection..."
$conn.Open()
Write-Host "Connection state after Open: $($conn.State)"
if ($conn.State -eq 1) {
    Write-Host "Connection is open (State=1)"
    $conn.Close()
    Write-Host "Connection closed"
} else {
    Write-Host "Connection failed to open. State: $($conn.State)"
}
"""

if __name__ == "__main__":
    print("Starting PowerShell script to extract data...")
    # Write the PowerShell script to a temporary file
    ps_file = 'temp_extract.ps1'
    with open(ps_file, 'w') as f:
        f.write(ps_script)
    time.sleep(2)

    try:
        result = subprocess.run(['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', ps_file], capture_output=True, text=True)
        if result.returncode == 0:
            print("Extraction successful. Data saved to C:\\Users\\wongkodsila.theephop\\Desktop\\Projects\\budget_portal\\extracted_data.csv")
            print(result.stdout)
        else:
            print("Error running PowerShell:")
            print(result.stderr)
    except Exception as e:
        print(f"Exception: {e}")

    os.remove(ps_file)

    import csv
    time.sleep(2)
    with open('C:\\Users\\wongkodsila.theephop\\Desktop\\Projects\\budget_portal\\extracted_data.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in list(reader)[:5]:  # Print first 5 rows
            print(row)