if [ -f .env ] && [ -f manage.py ]; then
  while IFS== read -r name value
  do
    export "$name"="$value"
  done < .env

  pytest -vvv
else
  echo "please run the script from project root dir."
fi


