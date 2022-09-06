# Pi In The Sky - API

[![Python package](https://github.com/philcali/pits-api/actions/workflows/python-package.yml/badge.svg)](https://github.com/philcali/pits-api/actions/workflows/python-package.yml)
[![CodeQL](https://github.com/philcali/pits-api/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/philcali/pits-api/actions/workflows/codeql-analysis.yml)

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

## Deploy to AWS Lambda

The service is geared towards an AWS API Gateway V2 HTTP API. The surrounding infrastructure
must support the following:

1. `TABLE_NAME`: name of the DynamoDB Table resource to store things
1. `DATA_ENDPOINT`: AWS IoT data endpoint tied to the account
