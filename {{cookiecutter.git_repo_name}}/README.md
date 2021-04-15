# {{cookiecutter.git_repo_name}}

## Overview
This project is created with [fast-api-starter-kit](https://github.com/rwhitten577/fast-api-starter-kit)

### Getting Started
1. Install [poetry](https://python-poetry.org/), used for managing dependencies and virtual environments.
1. Install dependencies with `poetry install`. 
1. Run tests with `pytest`.
1. Set environment and run server: `PROJECT_ENV=dev python src/main.py`

#### Configuration
Configuration variables are stored in [settings.toml](./settings.toml).

Certain secrets (e.g. passwords) that should not be checked into Git can be interpolated from
environment variables. If you declared an item as `my_var = "${EXAMPLE_VALUE}"`, you will
need to have an environment variable `EXAMPLE_VALUE` defined. You may use a `.env` file to store these 
environment variables and they will automatically be loaded using `dotenv`. To avoid
passing secrets in plaintext in the run environment, you can also define variables in AWS Systems Manager
Parameter Store (SSM). To do so, simply prefix the value with `ssm:/` and the code will automatically
fetch and decode the param at runtime (as long as valid AWS credentials are available).

These configuration files are parsed by the [TOML Kit](https://github.com/sdispater/tomlkit) library, 
and then stored as attributes on an object called [Settings](#Settings). 

Every settings.toml file must have a `default` table. These default values are shared across all environments.

```
[default]
project_name = "my_project"
```

After the `default` table, a table for each environment should exist, e.g. "local", "dev", and "prod". These tables override
any values that exist in the `default` table with the same name; in other words - environment settings take precedence over default settings.
Below we have two environments, `local` and `dev`, each with a custom `database_username` variable. 
In `local`, we also override the default `slack_enabled` param to disable sending Slack messages.
```
[default]
project_name = "my_project"
slack_enabled = true

[local]
database_username = "local_user"
slack_enabled = false

[dev]
database_username = "dev_user"
```

Since TOML and TOML Kit support nested tables/sections, we use them within the context of an environment. 
To declare a group of settings for a given environment, prefix the table name with the name of the environment, e.g. `local.mysql`.

```
[default]
project_name = "my_project"

[local]
    [local.mysql]
    username = "local_user"
    password = "secret password"
```

Read more below for how these values are accessed in Settings.

#### Settings
The [Settings](./src/core/settings.py) class reads `settings.toml` files, and sets attributes on itself for 
every item in the config file. However, it will only ever load settings from the `default` table and the table (and its children) matching 
the current environment, e.g., `local`. 

The environment **must** be set with a variable `PROJECT_ENV`, otherwise the fallback 
is `local` so nothing will ever touch production by accident. The value of this variable needs to match a corresponding section in your `settings.toml` file,
but you are free to name environments as you wish. There's no difference if you call an environment `dev` or `development` or `test`, so long as
you set `PROJECT_ENV=dev` or `PROJECT_ENV=development` or `PROJECT_ENV=test`.

Initialization:
```
from src.core import Settings
settings = Settings(config_filepath=custom_path + "settings.toml")
```

By default, it extracts the environment from the `PROJECT_ENV` variable, but you can override if needed by passing an `env` argument:
```
settings = Settings(config_filepath=custom_path + "settings.toml", env="dev")
```

We also initialize a global `settings` variable in [settings.py](./src/core/settings.py), so feel free to use it throughout the project without 
initializing it manually. 

After your config file is read, the default and environment-specific values are set to be accessible from the Settings object
in either dict-notation, or dot-notation. Inspired by [Dynaconf](https://www.dynaconf.com/), this means you can do the following:
```
# Get
settings.user
settings.get("user")
settings["user"]

# Get nested settings e.g. from [local.mysql] section of settings.toml
settings.mysql.user
settings.get("mysql").user
settings["mysql"]["user"]

# Set
settings.user = "TestUser"
settings["user"] = "TestUser"

# Iterate
for x in settings.items()
for x in settings.keys()
for x in settings.values()
```

This flexibility makes it easier to access settings vs always having to use dict-notation, get environment variables every time, 
or use ConfigParser and pass the section for every variable. 

Because Settings is a dict-like object, you can also set values to update config or store state as your process progresses. 
This can however introduce side effects since you are sharing global state across requests, but it can be handy to throw variables in here
instead of passing them down a large tree of functions as standard arguments.

#### Logging
This project provides a function `init_logging` which initializes handlers, formatters, and loggers with Python's logging.config.dictConfig.
Similar to Settings, you can pass a custom `env` argument but the default is your `PROJECT_ENV` environment variable.
We set the root log level based on your environment (local, dev = DEBUG, all others = INFO), but you can also pass this as an
override with the `root_level` argument, OR by setting an environment variable `ROOT_LOG_LEVEL`. We also expose the logging.config option
`disable_existing_loggers` as an argument, defaulted to False. 

##### Customizing module loggers: 
You can customize the log level for any module by passing a dictionary where keys are module names, and values are log levels. 
Example as read from `settings.toml`:

```
# settings.toml
[logging]
boto3 = "DEBUG"
botocore = "ERROR"

# main.py
init_logging(loggers=settings.logging)
```

#### Running in AWS Lambda
By default, this project will run FastAPI with uvicorn. Uvicorn is a production-ready ASGI server 
which should cover most needs. However, an interesting way to make FastAPI serverless is to use 
[Mangum](https://github.com/jordaneremieff/mangum) and run it with AWS Lambda.

Steps to run this project in Lambda:
1. Change `init_logging(is_lambda=False...)` in [main.py](./src/main.py) to `init_logging(is_lambda=True...)`
    * Since AWS Lambda controls the logging environment, we can't/shouldn't set any custom formatters or logging config. What 
    we can do though is set the overall log level. When running in Lambda, use the `is_lambda` option when, which when set to True
    will skip the dictConfig initialization and just call `logging.getLogger().setLevel(log_level)` with either the default
    environment level, or a custom level passed in like `init_logging(level="DEBUG")`.
1. Uncomment `handler = Mangum(app)` in [main.py](./src/main.py). This initializes Mangum, which will 
intercept incoming Lambda event and context, and conver them to HTTP request objects that ASGI servers
can understand. Just point your Lambda function to this variable as the handler. 
1. This step is optional, but if using AWS Cognito for authentication, and API Gateway with Lambda, 
you can have API Gateway verify JWT tokens before it invokes the Lambda function. This provides a few 
benefits, the main one being that requests (i.e., Lambda invocations) are not charged for 
authorization and authentication failures. Lambda is pretty cheap already, but this adds a first layer of 
protection from running up your invocation count if unauthorized users try to gain access to your API.
    * To set this up, just comment out `jwks = JWKS.parse_obj(...)` in [deps](./src/api/deps.py) and
      make sure to set the initialization of `auth = JWTBearer(jwks)` to receive either `None` 
      for the `jwks` arg, or remove it comepletely, e.g. `auth = JWTBearer()`. Optionally, you can
      leave all this enabled, but will just have duplicate token verification since API Gateway already did that step.
    * This will skip validating the token but return JWTAuthorizationCredentials so you can extract
      any required info from the token.
