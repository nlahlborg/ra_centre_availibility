cd ~/WORKSPACE
python -m venv .linux_venv
source .linux_venv/bin/activate
cp "/mnt/c/Users/nadia/windows repos/ra_centre_availibility/requirements.txt" ~/WORKSPACE/requirements.txt
pip install -r requirements.txt
cp -r .linux_venv/. "/mnt/c/Users/nadia/windows repos/ra_centre_availibility/.linux_venv"
