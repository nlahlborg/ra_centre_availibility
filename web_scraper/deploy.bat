ECHO OFF
DEL deployment.zip
POWERSHELL "Compress-Archive -Path '..\.linux_venv\lib\python3.13\site-packages\*' -DestinationPath 'deployment.zip'"
POWERSHELL "Compress-Archive -Update -Path 'lambda_function.py' -DestinationPath 'deployment.zip'"
POWERSHELL "Compress-Archive -Update -Path '.env' -DestinationPath 'deployment.zip'"
POWERSHELL "Compress-Archive -Update -Path 'src' -DestinationPath 'deployment.zip'"
POWERSHELL "Compress-Archive -Update -Path 'main.py' -DestinationPath 'deployment.zip'"
POWERSHELL "Compress-Archive -Update -Path 'tests' -DestinationPath 'deployment.zip'"