# Original code by Mikie (https://github.com/Mikie-Ghost/)
from flask import Flask, render_template, jsonify
from Maraschino import app
from Maraschino import rundir
from maraschino.noneditable import *
import maraschino.logger as logger
import maraschino

from pygithub import github
import urllib2, zipfile, tarfile, os, shutil

Owner = "mrkipling"
Repo = "maraschino"
Branch = "master"
GitHubURL = "https://github.com/%s/%s/tarball/%s" % (Owner, Repo, Branch)

BaseUrl = rundir

def GetHashFromFile():
    VersionFile = open('Version.txt','r')
    LocalHash = VersionFile.read()
    VersionFile.close()
    return LocalHash

def WriteHashToFile(RemoteHash):
    VersionFile = open('Version.txt', 'w')
    VersionFile.write(RemoteHash)
    VersionFile.close()

def GetHashFromGitHub():
    gh = github.GitHub()

    for c in reversed(gh.commits.forBranch(Owner, Repo, Branch)):
        short = (c.id[:7])
        long = (c.id)

    shorthash = short.splitlines()[0]
    longhash = long.splitlines()[0]

    return (shorthash, longhash)

@app.route('/xhr/updater/check')
@requires_auth
def xhr_updater_check():
    logger.log('UPDATER :: Checking for updates', 'INFO')
    gh = github.GitHub()
    L = list((c.id) for c in gh.commits.forBranch(Owner, Repo, Branch))

    try:
		i = L.index(GetHashFromFile())
    except:
		i = -1 # no match, file empty

    if i == -1: # unknown version
        logger.log('UPDATER :: Unknown version', 'INFO')
        return render_template('updater.html',
            unknown_version = True,
        )
    elif i == 0: # already has latest version
        logger.log('UPDATER :: Maraschino is up to date', 'INFO')
        return render_template('updater.html',
            latest_version = True,
        )
    else: # updates are available
        logger.log('UPDATER :: Maraschino is %s commits behind' % i, 'INFO')
        compare_url = 'https://github.com/%s/%s/compare/%s...%s' % (Owner, Repo, GetHashFromFile(), L[0])
        return render_template('updater.html',
            update_available = True,
            commits = i,
            compare_url = compare_url,
        )

@app.route('/xhr/updater/update')
@requires_auth
def xhr_updater_update():
    logger.log('UPDATER :: Updating Maraschino...', 'INFO')
    # Download repo
    url = urllib2.urlopen(GitHubURL)
    f = open('%s.tar.gz' % Repo,'wb')
    f.write(url.read())
    f.close()

    # Write new hash to file
    WriteHashToFile(GetHashFromGitHub()[1])

    # Extract to temp folder
    tar = tarfile.open('%s.tar.gz' % Repo)
    tar.extractall(BaseUrl + '/%s-update' % Repo)
    tar.close()

    # Delete .tar.gz
    os.remove("%s.tar.gz" % Repo)

    # Overwrite old files with new ones
    root_src_dir = BaseUrl + "/%s-update/%s-%s-%s" % (Repo, Owner, Repo, GetHashFromGitHub()[0])
    root_dst_dir = BaseUrl

    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir)
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)

    try:
        shutil.rmtree(BaseUrl + "/%s-update" % Repo)
    except:
        pass

    logger.log('UPDATER :: Update complete', 'INFO')
    return jsonify({'status': 'Update complete'})

