## Microwave Bias Calculator for New York City Local Law 144

Microwave is a Jupyter notebook designed to help companies comply with the auditing requirements of New York City’s Local Law 144. Specifically, Microwave performs the bias tests on model outputs required by the law, as specified by the municipal Department of Consumer and Worker Protection’s December 2022 proposed rules available [here](https://rules.cityofnewyork.us/wp-content/uploads/2022/12/DCWP-NOH-AEDTs-1.pdf). Read the instructions below to learn more about using the Microwave notebook.

### Freely available web-based example

If you are not familiar with Python, Jupyter, and virtual environments, consider using our freely available cloud-based Microwave example available [here](https://colab.research.google.com/github/bnh-ai/labs-microwave/blob/main/colab/Microwave.ipynb), which requires no installation.

The freely available cloud-based Microwave example relies on Google Colab and Workspaces, which require you to be logged into your Google account. If you would like to try the example, but do not have a Google account, you may follow instructions to create an account for free [here](https://support.google.com/accounts/answer/27441?hl=en). Once you are logged into your Google account, you may access the freely available web-based example at the link above. If you are prompted with a warning that "This notebook was not authored by Google," click "Run anyway" to continue to the Colab notebook.

### Local installation

For users who are familiar with Python, Jupyter, and virtual environments and plan to install the Microwave notebook locally, please follow the installation and usage instructions below or in `Microwave_Documentation.pdf` which is available in the docs folder or by clicking on "Documentation for v1.23.1 of the notebook can be accessed here" from the [Luminos portal](https://luminos.ai). **The installation steps below are required for the notebook to function properly.**

**Basic install instructions**:

* Unzip the downloaded zip file.
* Run the setup file. 
  * On Mac or Linux:
    * Open a terminal window. Change directories into the unzipped folder.
    * Change directories into the scripts folder: `cd scripts`
    * To start the notebook (for the first time and in the future), run: `./setup.sh` (You may need to run the following command to enable execution of the setup.sh file: `chmod +x ./setup.sh`)
  * On Windows: 
    * Open a PowerShell window. Change directories into the unzipped folder.
    * Change directories into the scripts folder: `cd scripts`
    * To start the notebook (for the first time and in the future), run: `.\Setup.ps1` (You may need to enable PowerShell scripts to run and to unblock `Setup.ps1`: `PowerShell -ExecutionPolicy Bypass -File Setup.ps1`)
* Running the setup script should install a virtual Python environment based on `requirements.txt`, start a Jupyter notebook server, and open a browser tab.
* In that browser tab, click on `microwave`, then `Microwave.ipynb`.
  * The setup should sign the notebook so that it is trusted by Jupyter, but if Jupyter indicates the notebook is not trusted, click on `Not Trusted`, then click on `Trust`.
* Click on: `Kernel`. Then click on: `Restart & Run All`.
* The notebook should now be ready - just follow the directions in the notebook to use it! 

**Support Note:** Python 3.9 with associated distutils package installed is preferred. 

**Support Note:** If you are familiar with Python virtual environments, in place of running the setup script you may instead create a virtual environment, activate it, use `requirements.txt` to install the required dependencies, and start the `Microwave.ipynb` notebook. You may also need to trust the notebook, restart the kernel, and run all cells.

### Directory contents

```
.
├── LICENSE.txt
├── README.md
├── requirements.txt
├── data
│   ├── sample_candidate_scoring_data.csv
│   └── sample_candidate_selection_data.csv
├── docs
│   └── Microwave_Documentation.pdf
├── jupyter_config
│   └── jupyter_notebook_config.py
├── microwave
│   └── Microwave.ipynb
├── scripts
│   ├── Setup.ps1
│   └── setup.sh
└── util
    ├── bias_testing.py
    ├── display.py
    └── exceptions.py
```

### License  

**Disclaimer**: This notebook is being provided under the CC BY-NC-ND 4.0
license. For more information about the restrictions associated with this
license, see [here](https://creativecommons.org/licenses/by-nc-nd/4.0).
