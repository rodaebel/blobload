========
Blobload
========

A simple Google App Engine Blobstore app + blobloader script.

In order to upload one or more files to your locally running (dev_appserver.py)
blobload app, run the blobloader.py script by typing:

  $ python blobloader.py /path/to/myimage.jpg

The blobloader.py script takes a number of command line options:

  Usage: blobloader.py [options] file...

  Options:
    -h, --help           show this help message and exit
    --address=ADDR:PORT  the address where the app is hosted
