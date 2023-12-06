# Real Time Cards Testing Flows

## Local Dev Setup 
### Install metaflow in your python environment 

1. Clone Metaflow somewhere on your computer: `git clone -b valay/real-time-cards git@github.com:valayDave/metaflow.git` ; you don't need to run this step if you already have metaflow running. 
2. Setup the python environment: 
    ```sh
    conda create -n metaflow-testing-package python=3.11 ipython
    conda activate metaflow-testing-package
    ```
3. Install the metaflow package : `pip install -e <path-to-where-metaflow-is-cloned>`


## Run the flow 

1. Run the flow in the terminal: `python realtimecardflow.py --datastore local --metadata local run`
2. Run the card viewer to see the status of the flow [In another terminal window]: `python realtimecardflow.py --datastore local --metadata local card server`
3. Go to the browser on `http://localhost:8324/` to see the cards
