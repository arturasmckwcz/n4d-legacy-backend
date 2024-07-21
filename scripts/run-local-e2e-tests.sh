if [ -f .env ] && [ -f manage.py ]; then
  while IFS== read -r name value
  do
    export "$name"="$value"
  done < .env

  python manage.py makemigrations
  python manage.py migrate
  python manage.py clear_data
  python manage.py seed_data

  # needed to finish seeding
  sleep 5

  pytest -vvv ./tests_e2e
else
  echo "please run the script from project root dir."
fi

