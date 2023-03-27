# Preserve the current working directory for future reference
$cwd = Get-Location 
# We do not need the -ErrorAction parameter for Write-Error calls below because we define $ErrorActionPreference here
$ErrorActionPreference = "Stop"
# Only deactivate if a virual environment is activated; otherwise, we potentially reference the Conda command of the same name
$activated = $false

try {

	Split-Path (Split-Path -Path $PSCommandPath -Parent) -Parent | Set-Location 

	$notebook = Join-Path -Path (Join-Path -Path "." -ChildPath "microwave") -ChildPath "Microwave.ipynb"
	$psd = Get-Location
	if (Test-Path -Path $notebook) {
		if (Test-Path -Path (Join-Path -Path "." -ChildPath "venv")) {
			Write-Error -Message "The Python virtual environment folder venv already exists. If the virtual environment is already installed, you can activate it with the command '.\venv\Scripts\Activate.ps1', then start the notebook with the command 'jupyter notebook' (or, equivalently, 'python -m jupyter notebook')." 
		}
		else {
			Write-Output -InputObject "Setting up Jupyter notebook environment in $psd ..."
			Start-Sleep -Seconds 1.5
		}
	} 
	else {
		Write-Error -Message "The setup script should be run from the Microwave root folder but is currently in the $psd folder, which does not contain the notebook $notebook" 
	}

	Write-Output -InputObject "Creating virtual environment (this might take a few seconds) ..."
	Start-Sleep -Seconds 1.5
	python -m venv venv
	if (-not $?) { Write-Error -Message "Python was not able to create a virtual environment using the venv module." }

	Write-Output -InputObject "Activating virtual environment ..."
	Start-Sleep -Seconds 1.5
	.\venv\Scripts\Activate.ps1
	if (-not $?) { Write-Error -Message "Python was not able to activate the virtual environment using the venv module." }

	$activated = $true

	Write-Output -InputObject "Installing required Python modules (this might take a minute) ..."
	Start-Sleep -Seconds 1.5
	pip install -r .\requirements.txt
	if (-not $?) { Write-Error -Message "The Python pip package manager was not able to install the required modules for the notebook." }

	Write-Output -InputObject "Generating signature for the Jupyter notebook ..."
	Start-Sleep -Seconds 1.5
	python -m jupyter trust .\microwave\Microwave.ipynb
	if (-not $?) { Write-Error -Message "Jupyter encountered a problem signing the notebook so the setup script will terminate." }

	Write-Output -InputObject " "
	Write-Output -InputObject "Jupyter will now be started, after which a browser window will be opened and you "
	Write-Output -InputObject "should navigate to the microwave folder and select the notebook Microwave.ipynb."
	Write-Output -InputObject " "
	Write-Output -InputObject "When you are finished with the notebook, you can shut down the Jupyter server by "
	Write-Output -InputObject "pressing Ctrl-C and deactivate the virtual environment with the command 'deactivate'."
	Write-Output -InputObject " "
	Write-Output -InputObject "Starting Jupyter ..."
	Start-Sleep -Seconds 2.0
	python -m jupyter notebook
	if (-not $?) { Write-Error -Message "Jupyter encountered a problem starting." }

} catch {

	Write-Host " "
	Write-Host "An error occurred trying to install the notebook: " $_
	Write-Host " "
    Write-Host "Please contact BNH.AI customer support at luminos@bnh.ai if you need assistance resolving this error."
	Write-Host " "

} finally {

	if ($activated) { deactivate }
	Set-Location -Path $cwd

}
