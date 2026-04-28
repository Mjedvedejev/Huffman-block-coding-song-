::==============================================================================
:: Creates the development environment for AramMastery
::
:: param: path to python.exe. Defaults to system default
:: param: virtual environment name. Defaults to .venv
::==============================================================================
 
setlocal
 
:: Set the path to python.exe, defaulting to 'python' if not provided
@set python_exe=%1
@if "%python_exe%"=="" @set "python_exe=python"
 
:: Set the virtual environment name, defaulting to '.venv' if not provided
@set venv_name=%2
@if "%venv_name%"=="" @set "venv_name=.venv"
 
:: Update git submodules
git submodule update --init --recursive
 
:: Create the virtual environment
%python_exe% -m pip install virtualenv
%python_exe% -m virtualenv %venv_name%
 
:: Activate the virtual environment
call %venv_name%\Scripts\activate.bat
 
:: Upgrade pip and install dependencies. UV is a super-fast package manager that speeds up the install process
%python_exe% -m pip install --upgrade pip
pip install uv
uv pip install -r requirements.txt
 
endlocal