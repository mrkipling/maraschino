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
    try:
        logger.log('UPDATER :: Looking for new comits on GitHub', 'DEBUG')
        L = list((c.id) for c in gh.commits.forBranch(Owner, Repo, Branch))
    except:
        logger.log('UPDATER :: Failed to fetch branch info from gitgub', 'ERROR')
        return render_template('updater.html',
            github_fail = True,
        )

    try:
        logger.log('UPDATER :: Attempting to get hash from version file', 'DEBUG')
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
    try:
        logger.log('UPDATER :: Downloading update file', 'DEBUG')
        url = urllib2.urlopen(GitHubURL)
        f = open('%s.tar.gz' % Repo,'wb')
        f.write(url.read())
        f.close()
    except:
        logger.log('UPDATER :: Failed to download update file', 'ERROR')
        return jsonify({'error': 'Update failed, please check the log'})

    # Write new hash to file
    try:
        logger.log('UPDATER :: Writing new hash to version file', 'DEBUG')
        WriteHashToFile(GetHashFromGitHub()[1])
    except:
        logger.log('UPDATER :: Faied to write new has to version file', 'ERROR')

    # Extract to temp folder
    try:
        logger.log('UPDATER :: Extracting update file', 'DEBUG')
        tar = tarfile.open('%s.tar.gz' % Repo)
        tar.extractall(BaseUrl + '/%s-update' % Repo)
        tar.close()
    except:
        logger.log('Failed to extract update file', 'ERROR')
        return jsonify({'error': 'Update failed, please check the log'})

    # Overwrite old files with new ones
    try:
        root_src_dir = BaseUrl + "/%s-update/%s-%s-%s" % (Repo, Owner, Repo, GetHashFromGitHub()[0])
    except:
        logger.log('UPDATER :: Could not get hash from GitHub', 'ERROR')
        return jsonify({'error': 'Update failed, please check the log'})
    root_dst_dir = BaseUrl

    try:
        logger.log('UPDATER :: Overwriting old files', 'DEBUG')
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
    except:
        logger.log('UPDATER :: Failed to overwrite old files', 'ERROR')
        return jsonify({'error': 'Update failed, please check the log'})

    try:
        logger.log('UPDATER :: Removing update files', 'DEBUG')
        os.remove("%s.tar.gz" % Repo)
        shutil.rmtree(BaseUrl + "/%s-update" % Repo)
    except:
        logger.log('UPDATER :: Could not remove update files', 'ERROR')

    logger.log('UPDATER :: Update complete', 'INFO')
    return jsonify({'status': 'Update complete'})

