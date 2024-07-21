while IFS== read -r name value
do
  export "$name"="$value"
done < .env

python manage.py makemigrations
python manage.py migrate