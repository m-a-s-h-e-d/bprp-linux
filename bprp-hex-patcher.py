import os
import argparse

# ------------- CONSTANTS ------------- #

REQUIRED_EXE_NAME = "BLUEPROTOCOL-Win64-Shipping.exe"
REQUIRED_DLL_NAME = "xinput1_3.dll"
REPLACED_DLL_NAME = "zinput1_3.dll"

# ------------- CONSTANTS ------------- #

def hex_patch(exe_path):
  try:
    if os.path.basename(exe_path) != REQUIRED_EXE_NAME:
      print(f'[ERROR]: Wrong executable specified, file name must match "{REQUIRED_EXE_NAME}"')
      return

    with open(exe_path, 'r+b') as file:
      offset = 0x7372C4E
      file.seek(offset)
      file.write(b'\x7A') # Replace 'x' with 'z' (0x7A)

    print(f'[SUCCESS] Patched "{exe_path}" at offset 0x7372C4E.')

  except FileNotFoundError:
    print(f'[ERROR]: "{exe_path}" was not found')
  
  except Exception as e:
    print(f'[ERROR]: {e}')

def rename_dll(dll_path):
  try:
    if os.path.basename(dll_path) != REQUIRED_DLL_NAME:
      print(f'[ERROR]: Wrong DLL specified, file name must match "{REQUIRED_DLL_NAME}"')
      return

    old_dll_path = os.path.join(dll_path, "xinput1_3.dll")
    new_dll_path = os.path.join(dll_path, "zinput1_3.dll")

    if os.path.exists(old_dll_path):
      os.rename(old_dll_path, new_dll_path)
      print(f'[SUCCESS] Renamed "{old_dll_path}" to "{new_dll_path}".')
    else:
      print(f'[ERROR]: "{old_dll_path}" was not found')

  except FileNotFoundError:
    print(f'[ERROR]: DLL was not found')
  
  except Exception as e:
    print(f'[ERROR]: {e}')


def main():
  parser = argparse.ArgumentParser(description="BPRP executable hex patcher and dll renamer for Linux users.")
  parser.add_argument("exe_path", help="Path to the BLUEPROTOCOL-Win64-Shipping.exe file.")
  parser.add_argument("dll_path", help="Path to the directory containing xinput1_3.dll.")
  args = parser.parse_args()

  hex_patch(args.exe_path)
  rename_dll(args.dll_path)


if __name__ == "__main__":
  main()
