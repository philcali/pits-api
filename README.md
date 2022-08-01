# Pi In The Sky - API

This is the API backend for the `pinthesky` console. In effect, this is a resource server
authenticated by an AWS Cognito User Pools.

## Run the Tests

Install the current directory:

```
python3 -m pip install -e .
pytest
```

Run the conventention analysis:

```
flake8
```

## Build a zip

Obtain the latest archive to use for AWS Lambda deployment:

```
./dev.make-zip.sh | tail -1
```
