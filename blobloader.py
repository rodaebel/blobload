#!/usr/bin/env python

from cStringIO import StringIO
from optparse import OptionParser
import cookielib
import logging
import urllib
import urllib2
import mimetools
import mimetypes
import os
import stat


DESCRIPTION = 'Program to upload files to the blobload app.'
USAGE = 'usage: %prog [options] file...'

LOG_FORMAT = '%(levelname)-8s %(asctime)s %(filename)s:%(lineno)s] %(message)s'

MAX_BYTES = 1024**3


class MultipartPostHandler(urllib2.BaseHandler):
    handler_order = urllib2.HTTPHandler.handler_order - 10

    def http_request(self, request):
        data = request.get_data()
        if data is not None and type(data) != str:
            files = []
            fields = []

            for key, value in data.items():
                if type(value) == file:
                    files.append((key, value))
                else:
                    fields.append((key, value))

            if len(files) == 0:
                data = urllib.urlencode(fields, 1)
            else:
                boundary, data = self.multipart_encode(fields, files)
                contenttype = 'multipart/form-data; boundary=%s' % boundary
                request.add_unredirected_header('Content-Type', contenttype)

            request.add_data(data)
        
        return request

    def multipart_encode(fields, files, boundary=None, buf=None):
        if boundary is None:
            boundary = mimetools.choose_boundary()

        if buf is None:
            buf = StringIO()

        for key, value in fields:
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; name="%s"' % key)
            buf.write('\r\n\r\n%s\r\n' % value)

        for key, fd in files:
            file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
            filename = fd.name.split('/')[-1]
            contenttype = (mimetypes.guess_type(filename)[0] or
                           'application/octet-stream')
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; '
                      'name="%s"; filename="%s"\r\n' % (key, filename))
            buf.write('Content-Type: %s\r\n' % contenttype)
            fd.seek(0)
            buf.write('\r\n%s\r\n' % fd.read())

        buf.write('--%s--\r\n\r\n' % boundary)
        buf = buf.getvalue()

        return boundary, buf

    class Callable:
        def __init__(self, anycallable):
            self.__call__ = anycallable

    multipart_encode = Callable(multipart_encode)

    https_request = http_request


def upload(address, upload_path, file_path):
    size = os.path.getsize(file_path)
    if size < MAX_BYTES:
        logging.info("preparing upload...")
        result = urllib2.urlopen("http://%s/%s" % (address, upload_path))
        upload_url = result.readline()

        logging.info("uploading blob...")
        cookies = cookielib.CookieJar()
        opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(cookies), MultipartPostHandler)

        params = {"file" : open(file_path, "rb")}
        results = opener.open(upload_url, params).read()
        if urllib.unquote(results) == os.path.basename(file_path):
            logging.info("successfully uploaded '%s'" % file_path)
        else:
            logging.error("unknown error when uploading '%s'" % file_path)
    else:
        logging.error("upload file is too big")


if __name__ == "__main__":
    parser = OptionParser(description=DESCRIPTION, usage=USAGE)

    parser.add_option("--address", dest="address", metavar="ADDR:PORT",
                  help="the address where the app is hosted",
                  default='localhost:8080')

    parser.add_option("--upload_path", dest="upload_path", metavar="PATH",
                  help="the upload URL path",
                  default='upload')

    (options, args) = parser.parse_args()  

    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)

    for file_path in args:
        if not os.path.isfile(file_path):
            logging.error("'%s': not a valid file" % file_path)
            continue
        try:
            upload(options.address, options.upload_path, file_path)
        except Exception, e:
            logging.error("failed to upload '%s' (%s)" % (file_path, e))
