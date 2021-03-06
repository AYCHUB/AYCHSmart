[![Build Status](https://travis-ci.org/aychsmart.png?branch=master)](https://travis-ci.org/aychsmart)

AYCHSmart is a software for consulting and technology services company to manage:
- commercial leads workflow (from business detection to sales and simple CRM)
- workload schedule to forecast people activity
- operation management: timesheet, margin control, billing

It is written in Python using the Django framework.


# LICENSE

AYCHSmart is available under the GNU Affero Public License v3 or newer (AGPL 3+).
http://www.gnu.org/licenses/agpl-3.0.html

# AUTHOR(S)

Jean Wallet (core@aych.site)


# INSTALLATION

AYCHSmart can be installed as any Django project. Just drop the code somewhere
and setup Apache.

To install all python prerequisites, please do the following: pip install -r requirements.txt. It is strongly advised to use a virtual env.

## Detailed Installation

Drop source code in a directory readable by your apache user
   git clone https://github.com/aychub/AYCHSmart

Create a virtual env in a directory readable by your apache user and activate it
   virtual-env venv
   . venv/bin/activate

Install prerequisites :
   pip install -r <path to AYCHSmart source code>/requirements.txt

Setup your favorite database (mysql/mariaDB or postgresql) and create a schema/base (with UTF-8 character set please) with a valid user that can create/alter/select/delete/update its objects.

Configure your database in AYCHSmart/settings.py. Look at django docs to understand the various database options.

Create tables with :

    ./manage.py migrate

Generate a new secret key with ./manage.py generate_secret_key and put it in AYCHSmart/settings.py

Collect static files with ./manage.py collectstatic

Setup your apache virtual env:

- activate mod_wsgi.
- activate ssl
- active mod_expires
- add Alias to /media and /static
- define auth backend. By default, AYCHSmart is designed to work with an http front end authentication. Look at https://docs.djangoproject.com/en/dev/howto/auth-remote-user/

Setup in cron (or your favorite scheduler) the followings tasks (adapt the schedule and options to your needs):

    5 2  * * *      <path to AYCHSmart>/venv/python -W ignore::DeprecationWarning <path to AYCHSmart>/manage.py clearsessions                    # Purge expired sessions in database
    0 6 1 * *       <path to AYCHSmart>/venv/python -W ignore::DeprecationWarning <path to AYCHSmart>/batch/timesheet_check.py                   # Warn for incomplete and surbooking timesheet for past month
    0 6 2-31 * *    <path to AYCHSmart>/venv/python -W ignore::DeprecationWarning <path to AYCHSmart>/batch/timesheet_check.py -w                # Warn for incomplete timesheet for past month
    0 6 21-31 * *   <path to AYCHSmart>/venv/python -W ignore::DeprecationWarning <path to AYCHSmart>/batch/timesheet_check.py -m current -d 20  # Warn for incomplete timesheet on current month for 20th first days
    0 * * * *       <path to AYCHSmart>/venv/python -W ignore::DeprecationWarning <path to AYCHSmart>/manage.py process_tasks -d 3600            # Process tasks for 1 hour


## Updating an existing installation

After pulling the latest changes, you need to update the database.

There are three possible situations, depending on whether your installation uses Django Migration, uses South or does not use a migration system at all. 
Your installation uses South if there is a `south_migrationhistory`

1. Your installation already uses Django Migration. Run these commands:

        ./manage.py migrate

2. Your installation uses South:

    Firstly you need to checkout the last AYCHSmart version using South "AYCHSmart/master", then run these commands:

        ./manage.py syncdb
        ./manage.py migrate

    After that you can update to to a newer version of AYCHSmart then :

        ./manage.py migrate auth
        ./manage.py migrate contenttypes
        ./manage.py migrate --fake  # for internal aych.crmbstaff apps

    Once this is done, future updates will be handled as situation #1.

3. Your installation does not use Django Migration or South yet.

    Firstly you need to checkout the last AYCHSmart version using South "AYCHSmart/master", then run these commands:

        ./manage.py syncdb
        ./manage.py migrate --all 0001 --fake
        ./manage.py migrate

    After that you can update to to a newer version of AYCHSmart by running:

        ./manage.py migrate --fake

    Once this is done, future updates will be handled just like situation #1.

## Notes about scikit learn
Scikit learn is a machine learning framework for python. It is an optional AYCHSmart deps that can predict leads tags and state.
Some comments:

- You need to install scikit-learn, numpy and scipy (pip install -r requirements-sklearn.txt)
- You might need to add the following directive in your apache virual host file to avoid some nasty deadlock during init when using scikit learn : WSGIApplicationGroup %{GLOBAL}
- For proper model caching, you might need to increase memcached object size (1m => 10m) as well as your python client memcache (hardcoded in lib for python-memcached...sic).

## Notes about javascript tests
If you want to run javascript tests, you need to install node, phantomjs and casperjs. Node may be included in your distribution. For the two others, here's how to install localy, without any root access:

        npm install phantomjs
        npm install casperjs

## Migrate data from environment
On source:

    ./manage.py dumpdata -o dump.json -e contenttypes -e auth.Permission -e admin.LogEntry --natural-foreign

On target:

    create empty database and play migrations
    ./manage.py loaddata dump.json

# Hosting, support, professional services, custom developpement
See https://aychub.blogspot.com/
