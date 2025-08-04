import os
import re

base_path = r"C:\\Users\\wongkodsila.theephop\\Microsoft\\Power BI Desktop Store App\\AnalysisServicesWorkspaces"

workspaces = [os.path.join(base_path, d) for d in os.listdir(base_path) if d.startswith('AnalysisServicesWorkspace')]
latest_workspace = max(workspaces, key=os.path.getmtime)
log_path = os.path.join(latest_workspace, 'Data', 'msmdsrv.port.txt')

if __name__ == "__main__":
    # Parse log for port
    with open(log_path, 'r') as f:
        log_content = f.read()
    
    if log_content:
        
        print(f"Local port: {log_content}")
    else:
        print("Port not found. Ensure Power BI Desktop is open with the model loaded.")