# Follow these steps
These steps are for Macbook, pasted in this to GPT to transfer for other OS.

MINICONDA 

1. If you don't have it, best advice is to chatgpt "install miniconda" on whatever hardware you are on
2. Once installed, run conda 'env create -f environment.yml' in the Transit_Dashboard directory
3. That should create the python virtual environment, where you can run 'conda activate transit-env'
4. When working on any notebooks in this repository, make sure to select this environment kernel

PYTHONPATH SETUP

1. Run python setup.py in the main directory to get your path (or just get it manually)
2. Create a string like this with your printed path

export PYTHONPATH="${PYTHONPATH}:/Users/username/Projects/TRANSIT_DASHBOARD/src"

i.e for myself

export PYTHONPATH="${PYTHONPATH}:/Users/user/Documents/Capstone/Transit_Dashboard/src"

3. Run 'nano ~/.zshrc' and add the above string to the bottom of the file
4. Save the file (CTRL + X, Y, then ENTER)
5. Run 'source ~/.zshrc'
6. Run 'echo $PYTHONPATH' to check if python path set correctly

FRONTEND SETUP

1. In a new terminal, 'cd frontend/transit-dashboard/'
2. Run 'bash setup.sh', and follow instructions (download nvm if neccessary)
3. Run 'npm install' 

FRONTEND SETUP

1. Run 'python -m http.server 8080' in the Transit_Dashboard directory
2. In a new terminal, 'cd frontend/transit-dashboard/'
3. Run 'npm start'
