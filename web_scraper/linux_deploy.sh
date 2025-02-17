cd $LINUX_ENV_PATH
python -m venv .linux_venv
source .linux_venv/bin/activate
cp "$WINDOWS_ENV_PATH/requirements.txt" "$LINUX_ENV_PATH/requirements.txt"
pip install -r requirements.txt
cp -r .linux_venv/. "$WINDOWS_ENV_PATH/.linux_venv"