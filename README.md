# Launch development environment

To launch the development environment you must have:

- Python >=3.11
- pip
- Python 3.11 development libraries

Install the requirements:
```
pip install -r requirements.txt
```

Prepare the environment variables, the following must be set:

```
DATABASE_URL                # Database URL
SECRET_KEY                  # Secret Key for token generation
ALGORITHM                   # Algorithm used for token generation: (HS256)
ACCESS_TOKEN_EXPIRE_MINUTE  # Token duration (30)
EMAIL_HOST                  # SMTP server host
EMAIL_PORT                  # SMTP server port
EMAIL_USERNAME              # SMTP server username
EMAIL_PASSWORD              # SMTP server password
EMAIL_FROM                  # Email address used to send mails.
HIBP_API_KEY                # Have I been Pwned API Key
SITE                        # URL to the frontend
API                         # URL to the backend
USER_AGENT                  # User agent used for HIBP API calls
```

Launch the environment:

```
uvicorn app.main:app --host MY_HOST_IP --port MY_PORT
```


## Launch development environment with Docker

### Build the image locally

```
docker build -t duckpass-backend .
```

### Run the container

Run the image (please set environment variables):
```
docker run -d \
    -e DATABASE_URL= \
    -e SECRET_KEY= \
    -e ALGORITHM= \
    -e ACCESS_TOKEN_EXPIRE_MINUTES= \
    -e EMAIL_HOST= \
    -e EMAIL_PORT= \
    -e EMAIL_USERNAME= \
    -e EMAIL_PASSWORD= \
    -e EMAIL_FROM= \
    -e HIBP_API_KEY= \
    -e SITE= \
    -e API= \
    -e USER_AGENT= \
    --name backend -p MY_PORT:80 duckpass-backend
```
