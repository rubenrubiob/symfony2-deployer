from fabric.api import *
from fabric.utils import abort
from fabric.colors import green, red, yellow
import os
import re
import yaml

"""
Set global data before functions
"""

# Set config file that will be used
config_file = 'app/config/hosts.yml'

# Import and parse config file
if not os.path.isfile(config_file):
    abort(red('Config file %s does not exist' % config_file, bold=True))

with open(config_file, 'r') as stream:
    hosts = yaml.load(stream)

# Check that requested server exists
if env.server not in hosts['hosts']:
    abort(red('Server %s does not exist in configuration file' % env.server, bold=True))

# Set server variable as global, as we will use it in all functions
server = hosts['hosts'][env.server]

# Set Fabric env.hosts from the server variable we just defined
env.hosts = server['hosts']

# Forward agent if specified
env.forward_agent = server['forward_agent']


def checkout():
    """
    Checkouts specified branch.
    """
    local('git fetch')
    local('git checkout %s' % server['branch'])
    local('git pull origin %s' % server['branch'])
    print(green('Correctly checked out %s branch in local' % (server['branch']), bold=True))


def tests():
    """
    Executes tests.
    """
    local('%s -c app' % server['phpunit_bin'])
    print(green('Correctly executed tests in local', bold=True))


def pre_deploy():
    """
    Checkouts the specified branch and execute the tests, if specified.
    """
    checkout()
    if server['tests']:
        tests()


def deploy():
    """
    Deploys the application by updating the source to the last commit of the specified
    git branch, executes a composer update, executes database migrations (if specified)
    and clears the cache.
    """

    with cd(server['path']):
        # Execute git pull
        _pull()

        # Execute post deployment tasks
        _post_deployment_tasks()

        print(green('Correctly deployed to %s' % env.server, bold=True))


def rollback(revision='1'):
    """
    Deploys the application by updating the source to the last commit of the specified
    git branch, executes a composer update, executes database migrations (if specified)
    and clears the cache.
    :param revision: if it is a number, it rollbacks N commits back from last one; if it is a string, it rollbacks
    to that commit.
    """

    with cd(server['path']):
        # Pull, so we have all commits
        _pull()

        # Rollback according to version or a number of revisions
        if re.match(r"\d+$", revision) is not None:
            run('git checkout HEAD~%s' % revision)
            revision = run('git rev-parse --short HEAD', quiet=True)
        else:
            result = run('git checkout %s' % revision, quiet=True)
            if result.failed:
                abort(red('Revision %s does not exist' % revision, bold=True))

        # Execute post deployment tasks
        _post_deployment_tasks()

        # Print okay and warning message, informing that the database may be not up to date
        print(green('Correctly rolled back to %s' % revision, bold=True))
        print(yellow('Remember to check your database, because it may be not in sync with your code!!', bold=True))


def _pull():
    """
    Executing regular git pull, updating code to last commit
    """
    run('git fetch')
    run('git checkout %s' % server['branch'])
    run('git pull origin %s' % server['branch'])


def _post_deployment_tasks():
    """
    Executes a composer update, executes database migrations (if specified) and clears the cache
    """
    # Composer update
    run('%s %s update' % (server['php_bin'], server['composer_bin']))

    # Database migrations
    if 'database_migrations' in server and server['database_migrations']:
        run('%s %s/app/console doctrine:migrations:migrate --env=prod --no-interaction' % (
            server['php_bin'], server['path']))

    # Cache clear
    run('%s %s/app/console cache:clear --env=prod' % (server['php_bin'], server['path']))
