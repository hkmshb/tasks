from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import os, random


REPO_URL = 'https://github.com/hkmshb/tasks.git'



def deploy_live(site_name, project_name):
    _deploy(site_name, project_name, REPO_URL, False)

def deploy_vbox(site_name, project_name, repo_url):
    _deploy(site_name, project_name, repo_url, True)

def _deploy(site_name, project_name, repo_url, to_vbox):
    site_folder = '/home/%s/webapps/%s' % (env.user, site_name)
    source_folder = site_folder + '/source'
    
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder, repo_url or REPO_URL)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)
    _update_config_wsgi(source_folder, site_name, project_name)
    
    if to_vbox:
        _append_config_directives(source_folder, site_name, project_name)

def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database', 'static', 'virtualenv', 'source'):
        run('mkdir -p %s/%s' % (site_folder, subfolder))

def _get_latest_source(source_folder, repo_url=None):
    print repo_url
    if exists(source_folder + '/.git'):
        run('cd %s && git fetch' % (source_folder,))
    else:
        run('git clone %s %s' % (repo_url, source_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (source_folder, current_commit))

def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/tasks/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path,
        'ALLOWED_HOSTS = .+$',
        'ALLOWED_HOSTS = ["%s"]' % (site_name,)
    )
    secret_key_file = source_folder + '/tasks/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '%s'" % (key,))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')

def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run('virtualenv --python=python3.4 %s' % (virtualenv_folder,))
    run('%s/bin/pip install -r %s/requirements.txt' % (
        virtualenv_folder, source_folder
    ))
    
def _update_static_files(source_folder):
    run('cd %s && ../virtualenv/bin/python3 manage.py collectstatic --noinput' % (
        source_folder,
    ))    
    
def _update_database(source_folder):
    run('cd %s && ../virtualenv/bin/python manage.py migrate --noinput' % (
        source_folder,
    ))    

def _update_config_wsgi(source_folder, site_name, project_name):
    local_dir = os.path.dirname(__file__)
    conf_extra = local_dir + '\\httpd-wsgi-extra.template.conf'
    lines = open(conf_extra, 'r').readlines()
    
    run('cd %s && cp httpd.conf httpd.conf.orig' % (
        source_folder + '/../apache2/conf'
    ))
    
    conf_file = source_folder + '/../apache2/conf/httpd.conf'
    for line in lines:
        key, value = line.strip().split(' ', 1)
        sed(conf_file,
            '%s .+$' % (key,),
            '%s %s' % (key, value.replace('$USR', env.user)
                                 .replace('$SITENAME', site_name)
                                 .replace('$PJTNAME', project_name))
        )

def _append_config_directives(source_folder, site_name, project_name):
    local_dir = os.path.dirname(__file__)
    conf_append = local_dir + '\\httpd-local-extra.template.conf'
    lines = open(conf_append, 'r').readlines()
    
    entire_file = (''.join(lines)).replace('$USR', env.user) \
                                  .replace('$SITENAME', site_name) \
                                  .replace('$PJTNAME', project_name)
    
    conf_file = source_folder + '/../apache2/conf/httpd.conf'
    append(conf_file, '\n%s' % (entire_file,))
    