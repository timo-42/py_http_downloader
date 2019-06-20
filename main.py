#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 19:06:30 2019

@author: Timo Haas
"""

from pathlib import Path
import urllib.request
import urllib.parse
import logging
import hashlib
import binascii

class DownloadTask:
    def __init__(self, url, file_path, tmp_path):
        self.url       = url
        self.file_path = file_path
        self.tmp_path  = tmp_path
        
    def download(self):
        try:
            with urllib.request.urlopen(self.url) as req:
                data = req.read()
    
            # open file, if it exists current bytes will be deleted
            with self.tmp_path.open("wb") as f:
                f.write(data)
                f.flush()
                f.close()
            if self.file_path.is_dir():
                logging.warning("Try writing a File to a directory. Url: {}".format(self.url))
                return
            
            # rename is an atomic operation on posix filesystems, so we have a
            # consistent download directory without broken downloaded files
            self.tmp_path.rename(self.file_path)
        except:
            logging.warning("Couldnt download url or store the File on disk. Url: {}".format(self.url))

class Fetch:
    tasks = []
    
    def __init__(self, urls, download_directory, tmp_directory=None, threads=4):
        self.urls = urls
        
        if not type(threads) is int:
            raise Exception("The concurrent paramenter must be an INT")
        self.threads = threads
        
        self.download_directory = Path(download_directory)

        if tmp_directory == None:
            self.tmp_directory = Path(download_directory+"/tmp")
        else:
            self.tmp_directory = Path(tmp_directory)
        
    def prepare(self):
        for url in self.urls:
            
            # parsing url
            parsed_url = urllib.parse.urlsplit(url)
            
            (sanity_check, file_path) = url_sanity_check(url, parsed_url, self.download_directory)
            if sanity_check == False:
                # url cannot pass sanity check
                # skip it
                continue
            
            # create task for download
            logging.info("creating Task for url: {}".format(url))
            
            # now we know the path is secure, we can create the subdirectories
            # for storing the files, we do it here because it is singlethreaded
            # and we dont have to handle race conditions
            file_path.parent.mkdir(parents=True,exist_ok=True)
            
            # we write the temporary file to tmp_dir/hash, because we dont want
            # to replicate a full directory hierachy in it
            # hash over the full url and than as hex
            h = hashlib.sha512()
            h.update(url.encode("utf-8"))
            tmp_path = binascii.hexlify(h.digest()).decode("ascii")
            
            # prepend the tmp_direcory
            tmp_path = self.tmp_directory / Path(tmp_path )
            
            # add the task to the tasks queue
            self.tasks.append(DownloadTask(url, file_path, tmp_path))
            
    def run(self):
        for task in self.tasks:
            task.download()
        pass

def url_sanity_check(url, parsed_url, download_directory):
    # skip urls which are not http(s) or ftp
    if not (parsed_url.scheme == "http" or parsed_url.scheme == "https"):
        logging.warning("Url with unsupported Scheme: {}".format(url))
        return (False, None)
    
    url_file_path = Path(parsed_url.path)
    
    # check urls which end with /
    if url.endswith("/"):
        logging.warning("Url ends with a trailing /. Will not download. Url: {}".format(url))
        return (False,None)
    
    # check for urls without path like http://domain.org or http://domain.org/
    if len(url_file_path.parts) == 0 or len(url_file_path.parts) == 1:
        logging.warning("Url with unsupported Path: {}".format(url))
        return (False,None)

    # adding path from url and domain to our download directory
    try:
        file_path = download_directory / parsed_url.netloc / url_file_path.relative_to("/")
        file_path = file_path.resolve()
    except ValueError:
        logging.warning("couldn't resolve download Filesystem Path. Url: {}".format(url))
        return (False,None)
    
    # sanity check for .. shenanigans
    if ".." in file_path.parts:
        logging.warning("there is .. in the file path, which is not supported. file path: {} Url: {}".format(file_path, url))
        return (False,None)
    
    # check if the filepath begins with the given download directory,
    # otherwise we would try to write outside of given directory
    # which could be a bug or an attack
    try:
        file_path.relative_to(download_directory).resolve()
    except ValueError:
        logging.warning("Wrong base download directory. Download Directory: {} FilePath: {} Url: {}".format(download_directory, file_path, url))
        return (False,None)
    
    # all checks are passed
    return (True,file_path)

if __name__ == "__main__":
    p = Path("tests/urls.txt")
    urls = set()
    with p.open() as f:
        for line in f:
            # remove whitespace and newlines
            line = line.strip()
            urls.add(line)
    fetch = Fetch(urls, "/tmp/dl", "/tmp/tmp")
    fetch.prepare()
    fetch.run()