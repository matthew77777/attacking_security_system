import subprocess

command = ["python", "pir_notify.py"]
proc = subprocess.Popen(command)
print("呼び出し中")
proc.communicate()
