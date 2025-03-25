from smb.SMBConnection import SMBConnection
import smbprotocol

# Server and share details
server_ip = "169.254.146.220"
share_name = "CMFX_Results"
username = "Control Room"
password = "cmfx1234"
domain = ""  # Use an empty string if no domain is required

##
# Initialize SMB connection
conn = SMBConnection(username, password, "client", "server", domain=domain, use_ntlm_v2=True)
conn.connect(server_ip, 445)  # Port 139 is commonly used for SMB, use 445 if needed

# List files and directories
try:
    shares = conn.listShares()
    for share in shares:
        if share.name == share_name:
            print(f"Listing contents of share: {share_name}")
            files = conn.listPath(share_name, '/')
            for file in files:
                print(file.filename)
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    conn.close()
