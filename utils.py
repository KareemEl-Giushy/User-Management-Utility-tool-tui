import subprocess

def get_system_users() -> list:
    return [
        ("Username", "uid", "Groups", "Comments", "Locked"),
        ("Kareem", "123123", "ggg", "CC", "No"),
        ("Ahmed", "123123", "gg", "CC", "No"),
        ("Abdallah", "123123", "ggg", "CC", "No"),
        ("Aziz", "123123", "ggg", "CCS", "No"),
    ]

def get_system_groups() -> list:
    return [
        ("Name", "gid", "Users"),
        ("sudoers", "gid", "Users,dsfadsf"),
        ("gmail", "gid", "Users,sdfsdfa"),
    ]

# ==============================
def list_groups() -> list:
    out = [
        ("Name", "gid", "Users")
    ]
    with open("/etc/group", "r") as f:
        for line in f:
            parts = line.split(":")
            if int(parts[2]) >= 1000 or parts[0] == "wheel" or parts[0] == "sudo":
                out.append((parts[0], parts[2], parts[3]))

    return out

def list_users() -> list:
    out = [
        ("Username", "uid", "Comments", "Home", "Locked"),
    ]

    with open("/etc/passwd", "r") as f:
        for line in f:
            parts = line.split(":")
            if int(parts[2]) >= 1000 and parts[0] != "nobody":
                out.append((parts[0], parts[2], parts[4], parts[5], "No"))
    return out


def run_command(command):
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def add_user(username, password) -> tuple:
    
    success, error = run_command(["sudo", "useradd", "-m", username])
    
    if success:
        proc = subprocess.Popen(['sudo', 'chpasswd'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        proc.communicate(input=f"{username}:{password}")
        return (0, username)
    else:
        return (-1, error)

def delete_user(username) -> tuple:
    success, error = run_command(["sudo", "userdel", "-r", username])
    if success:
        return (0, username)
    else:
        return (-1, error)

def change_user_password(username, new_password) -> tuple:
    command = ['sudo', 'chpasswd']
    
    try:
        proc = subprocess.Popen(
            command, 
            stdin=subprocess.PIPE,  
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True               
        )
        stdout, stderr = proc.communicate(input=f"{username}:{new_password}")
        if proc.returncode == 0:
            return (0, f" Password for '{username}' changed successfully.")
        else:
            return (-1, f" Failed to change password. Error: {stderr}")

    except FileNotFoundError:
        return (-1, " Error: The 'chpasswd' command was not found.")
    except PermissionError:
        return (-1, " Error: You need 'sudo' privileges to run this.")


def add_group(groupname):
    success, error = run_command(["sudo", "groupadd", groupname])
    if success:
        return (0, f" '{groupname}' added successfully.")
    else:
        return (-1, f" Error: {error}")


def delete_group():
    groupname = input("Enter groupname to DELETE: ").strip()
    confirm = input(f"Are you sure you want to delete {groupname} ? (y/n): ")
    
    if confirm.lower() == 'y':
        success, error = run_command(["sudo", "groupdel", groupname])
        if success:
            print(f" group '{groupname}' deleted.")
        else:
            print(f" Error: {error}")



def modify_group(option,value):
    groupname = input("Enter the group name: ").strip()
    success, error = run_command(["sudo", "groupmod", "-"+option , value , groupname])
    
    if success:
        print(f" Successfully updated {groupname} with option -{option}.")
    else:
        print(f" Error: {error}")

def modify_user(option,value):
    username = input("Enter the username: ").strip()
    cmd = ["sudo", "usermod", "-" + option]
    if value:
        cmd.append(value)
    cmd.append(username)
    success, error = run_command(cmd)
    if success:
        print(f" Successfully updated {username} with option -{option}.")
    else:
        print(f" Error: {error}")