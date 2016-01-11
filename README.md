# Symfony2 deployer

This is a simple [Symfony2][1] application deployer using [Fabric][2]. I spent some time trying to configure
[Capyfony][3] for my Symfony2 projects, but it did not fully meet my needs that, in fact, are really simple: I
deploy using git to different servers that may —or may not— be on the same git branch, and I need to execute some
tasks after deploy. Therefore, I needed something easy to use, easy to configure and easy to extend, so I decided to
write my own tool using [Fabric][2].

Right now, this is a alpha version and I intend to implement [some features](#todo), but feel
free to suggest anything or to improve it by yourself.

========================

## Usage

1. [Requirements.](#requirements)
2. [Configuration.](#configuration)
3. [Tasks.](#tasks)
    1. [checkout](#checkout)
    2. [tests](#tests)
    3. [pre_deploy](#pre_deploy)
    4. [deploy](#deploy)
    4. [rollback](#rollback)
4. [Execution.](#execution)

========================

## Requirements

There are two Python packages required to use this deployer, and both can be installed system-wide using [pip][5]. The
packages are:

1. [Fabric][2] (obviously). To install it:

    ```bash
    sudo pip install fabric
    ```

2. [PyYAML][4] for parsing configuration files. To install it:

    ```bash
    sudo pip install PyYAML
    ```

========================

## Configuration

The file `fabfile.py` must be placed at the root of your project. You may commit it if you want, and do not forget
to add to your `.gitignore` files with extension `*.pyc`.

The configuration file `hosts.yml` must be placed within the `app/config` folder of your Symfony2 application, and you
may commit it with your source code, as it does not contain any secret information such as passwords. Its format 
is as follows:

```yml
hosts:
    server_name: 
        hosts:
            - 'username@host:port'
        path: '/path/to/source'
        composer_bin: '/path/to/composer'
        php_bin: '/path/to/php'
        phpunit_bin: '/path/to/local/phpunit'
        branch: 'master'
        tests: false
        repo: 'git@repo.org'
        database_migrations: false
        forward_agent: true
```

Some things to take into account:
- `server_name` will be the name that will be used for invoking the tasks from the command line, so it must be unique.
You can have as many servers defined as you want, and that is the great thing about using this configuration file: you
may add a new server simply by adding it to the `hosts.yml` file.
- `hosts` within `server_name` may be a list of servers, and the task will be executed on all of them. Note that
the different paths defined and the branch must be the same for all of them.
- `phpunit_bin` is the path of the local `phpunit` binary, in case you want to execute tests in local before deploying.
- `tests` if true, it locally executes application tests.
- `database_migrations` if true, it executes any database migration required using the [DoctrineMigrationsBundle][6].
- `forward_agent` indicates whether the local SSH agent must be forwarded, so the authentication against the host
can be done using a private key. It is extremely recommended to use it, so you do not have to enter the password
each time you deploy the application.

========================

## Tasks

The tasks that may be called from the command line are the following.

### `checkout`

It locally checks out the specified branch, so it is verifiable that it does not have any thing that you do not want
to deploy. It is also the previous step to executing the tests.

### `tests`

It locally executes the tests.

### `pre_deploy`

It calls the tasks `checkout` and `tests` —if defined. It is useful when you want to verify that everything is right
before deploying to production.

### `deploy`

It deploys the application by updating the source to the last commit of the specified git branch, executes a
composer update, executes database migrations —if specified— and clears the cache for the _production_ environment.

Note that the project must already be configured at the specified host as it only updates the source code, it
 does not install it.

### `rollback`

It rollbacks the code to a specified commit or to a number of revisions back. It requires a parameter, revision,
that may be a number —rolling back that number of commits— or a string —rolling back to that revision.

========================

## Execution

You can call any task to be executed from the command line. The most useful are `pre_deploy`, `deploy` and `rollback`:

```bash
fab --set server=server_name pre_deploy
```

```bash
fab --set server=server_name deploy
```

To rollback 3 revisions:

```bash
fab --set server=server_name rollback:3
```

To rollback to a specified commit:

```bash
fab --set server=server_name rollback:ab3ba
```

`server_name` is the name defined in your configuration file.

========================

## TODO

- Ship as a bundle.
- Add more post-deployment tasks, such as installing assets.
- Checking `hosts.yml` file integrity.
- Backup the database prior to any migration.
- Allowing not only to update the project, but also to install it.
- Check compatibility for Symfony3.
- Silent mode.




[1]: https://symfony.com/
[2]: http://www.fabfile.org/
[3]: http://capifony.org/
[4]: http://pyyaml.org/
[5]: https://pip.pypa.io/en/stable/quickstart/
[6]: http://symfony.com/doc/current/bundles/DoctrineMigrationsBundle/index.html