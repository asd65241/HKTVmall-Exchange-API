# HKTVmall Exchange API

This API used to interact with the HKTVmall Exchange backend.

## Current Features

- This API support retriveing sales of n-day before today
- This API support retriveing sales of a particular date
- This API support custom login

## Preparing Work

Create a `.env` file to fill in your default HKTVmall Exchange login credential. Please follow the format below:

```
HKTV_USERNAME=XXXXXXXX      # Your Exchange Username
HKTV_PWD=YYYYYYYY           # Your Exchange Password
HKTV_MERCHANT_CODE=HXXXXXXX # Your HKTVmall Storecode
```

## Run using Docker

Build the image using:
```bash
$ docker build -t hktvmall-api . 
```

Run the image using:
```
$ sudo docker run --env-file .env -d --name hktv-api -p 8000:80 hktvmall-api

```

Then, go to http://127.0.0.1:8000 to see the documentation of the API

## Using Docker Compose

Fill in the docker-compose.yml

Then, do the following command:
```
$ sudo docker-compose --env-file .env up 
```

This will copy your environment variable to the container.

## Development

It is suggested to use pipenv to initialize your dev environment

```
$ pipenv shell
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)