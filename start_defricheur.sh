#!/bin/bash

set -efaou pipefail

source .env_defricheur > /dev/null 2>&1

if [ "$SECRET_KEY" ]
then

    echo "SECRET_KEY is set to '$SECRET_KEY'"
else
    echo "SECRET_KEY is not set, if you continue, no output will be saved"
    read -p "Continue? [ y / $(tput setaf 1)N$(tput sgr0) ] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        echo "Aborting"
        exit 1
    else
        echo "Caution, no output will be saved"
    fi
fi

set +a

cd "${FOLDER:=`pwd`/}"

# Ensure pwd has worked
if [ -z "${FOLDER%/*}" ]
then
    echo "The pwd command failed, leading to cd to $FOLDER"
    exit 1
fi

# git pull origin master --quiet || exit

if [ ! -d "venv" ]
then
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

source "$FOLDER""venv/bin/activate"

# Ensure that we have everything we need
set +e
sed "s/\(.*\)\(--\|#\).*/\1/g" "requirements.txt" | grep -v '^ *#' | while IFS= read -r package
do
    if [[ "git" == *"$package"* ]]
    then
      package_name=$(echo "$package" | cut -d'@' -f1)
      package_url=$(echo "$package" | cut -d'@' -f2)
      if ! pip show "$package_name" > /dev/null
      then
          echo "Missing $package, trying to install it..."
          pip install git+"$package_url"@master
      fi
    else
      if ! pip show "$package" > /dev/null
      then
          echo "Missing $package, trying to install it..."
          pip install "$package"
      fi
    fi
done
set -e

python3 src/init.py

COMMAND="source $FOLDER""venv/bin/activate; python -m uvicorn src.main:app --host ${DEFRICHEUR_HOST:-'0.0.0.0'} --port ${DEFRICHEUR_PORT:-'8000'} --root-path ${ROOT_PATH:-'/'} --workers 1 --timeout-keep-alive 1000 --log-config log.conf"

printf "Starting defricheur with command:\n"
echo "$COMMAND"

set +ue
IS_RUNNING=`screen -ls | grep Defricheur`
if [ -z "$IS_RUNNING" ]
then
    set -ue
    echo "defricheur service currently not running, starting..."
    screen -S Defricheur -dm bash -c "$COMMAND"
else
    set -ue
    echo "defricheur already running, restarting..."
    screen -S Defricheur -X quit
    screen -S Defricheur -dm bash -c "$COMMAND"
fi

cd -
