#!/usr/bin/env bash

# If the python3 version is < 3.5
if [ `python3 -c 'import sys; print(sys.version_info.major >= 3 and sys.version_info.minor >= 5)'` = "False" ];
then
    curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
    pyenv install 3.5.3
    export PATH="~/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    #eval "$(pyenv virtualenv-init -)"
    pyenv global 3.5.3
fi