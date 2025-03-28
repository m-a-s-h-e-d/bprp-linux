# BPRP 4 Linux
Authenticator and Hex Patcher for [BPRP](https://playbprp.com/)

# Installation
- Clone the repository

# Usage

## BPRP Hex Patcher
- Run `python bprp-hex-patcher.py "path/to/BLUEPROTOCOL-Win64-Shipping.exe" "path/to/dll/directory"`

## Hoshi Auth
- Run `python hoshi-auth.py` or `./hoshi-auth.sh`
- Authenticate on the login page
- Open with `xdg-open` when prompted by browser
  - This will run the script in the background again with the redirect uri as an argument
  - If you want to see the output, you can modify `hoshi-auth.desktop` to either open in terminal (If you have a default terminal from your DE) or add your tty to the Exec key line and have that execute the python script
- Copy auth.txt to your Win64 directory containing the other Hoshi files
  - If you are using the launcher instead of directly executing `BLUEPROTOCOL-Win64-Shipping.exe`, add auth.txt to your launcher directory as well

# Dependencies
- Python 3.x
- Any Web Browser
- xdg-utils

# To Do
- [ ] Add prompt for Win64 file path
- [ ] Add argument for command to launch game upon authentication

# Bugs & Issues
Create a GitHub issue along with steps to recreate the problem
