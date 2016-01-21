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
    1. [pre_deploy](#pre_deploy)
    2. [deploy](#deploy)
    3. [rollback](#rollback)
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
        assets:
            enabled: false
            symlink: true
            relative: false
            target_path: '/path/to/target/path'
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
- `assets` manages the `assets:install` task. If its `enabled` key is true, it installs the assets, with the
corresponding options specified, that are the same as the Symfony2 command. 

========================

## Tasks

The tasks that may be called from the command line are the following.

### `pre_deploy`

Locally checkouts the specified branch for server and execute the tests, if defined.

Execution example:

```bash
fab --set server=prod pre_deploy
```

### `deploy`

It deploys the application by updating the source to the last commit of the specified git branch, executes a
composer update, installs assets —if specified— executes database migrations —if specified— and clears the cache
for the _production_ environment.

Note that the project must already be configured at the specified host as it only updates the source code, it
 does not install it.
 
Deploy to a server named _prod_ in `hosts.yml` file:

```bash
fab --set server=prod deploy
```

### `rollback`

It rollbacks the code to a specified commit or to a number of revisions back. It requires a parameter, revision,
that may be a number —rolling back that number of commits— or a string —rolling back to that revision.

To rollback 3 revisions in a server named _prod_ in `hosts.yml` file:

```bash
fab --set server=prod rollback:3
```

To rollback to a specified commit in a server named _prod_ in `hosts.yml` file:

```bash
fab --set server=prod rollback:ab3ba
```

========================

## Execution

These are the execution options that may be passed to command line:
- `server`: required. It is the name of the server defined in `hosts.yml` file where you want to execute the task.
Example: 

```bash
fab --set server=server_name deploy
```

- `verbose`: optional. If defined, it shows the output of command executions instead of informative messages. Example:

```bash
fab --set server=server_name,verbose deploy
```


========================

## TODO

- File backup, for user files, such as images.
- Ship as a bundle or git submodule.
- Add more post-deployment tasks~~, such as installing assets~~.
- Checking `hosts.yml` file integrity.
- Backup the database prior to any migration.
- Allowing not only to update the project, but also to install it.
- Check compatibility for Symfony3.
- ~~Silent mode.~~
- Tests.




[1]: https://symfony.com/
[2]: http://www.fabfile.org/
[3]: http://capifony.org/
[4]: http://pyyaml.org/
[5]: https://pip.pypa.io/en/stable/quickstart/
[6]: http://symfony.com/doc/current/bundles/DoctrineMigrationsBundle/index.html