#!/usr/bin/env python

from cStringIO import StringIO
from optparse import OptionParser
import cookielib
import urllib
import urllib2
import mimetools
import mimetypes
import os
import stat


class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable


class MultipartPostHandler(urllib2.BaseHandler):
    handler_order = urllib2.HTTPHandler.handler_order - 10

    def http_request(self, request):
        data = request.get_data()
        if data is not None and type(data) != str:
            files = []
            vars = []

            for key, value in data.items():
                if type(value) == file:
                    files.append((key, value))
                else:
                    vars.append((key, value))

            if len(files) == 0:
                data = urllib.urlencode(vars, 1)
            else:
                boundary, data = self.multipart_encode(vars, files)
                contenttype = 'multipart/form-data; boundary=%s' % boundary
                request.add_unredirected_header('Content-Type', contenttype)

            request.add_data(data)
        
        return request

    def multipart_encode(vars, files, boundary=None, buf=None):
        if boundary is None:
            boundary = mimetools.choose_boundary()

        if buf is None:
            buf = StringIO()

        for key, value in vars:
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; name="%s"' % key)
            buf.write('\r\n\r\n' + value + '\r\n')

        for key, fd in files:
            file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
            filename = fd.name.split('/')[-1]
            contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename))
            buf.write('Content-Type: %s\r\n' % contenttype)
            fd.seek(0)
            buf.write('\r\n' + fd.read() + '\r\n')

        buf.write('--' + boundary + '--\r\n\r\n')
        buf = buf.getvalue()

        return boundary, buf

    multipart_encode = Callable(multipart_encode)

    https_request = http_request


def uploader(file_path):
    size = os.path.getsize(file_path)
    if size < 1073741824:
        print "preparing upload..."
        result = urllib2.urlopen("http://localhost:8080/prepare")
        upload_url = result.readline()

        print "uploading blob..."
        cookies = cookielib.CookieJar()
        opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(cookies), MultipartPostHandler)

        params = {"file" : open(file_path, "rb")}
        results = opener.open(upload_url, params).read()
            
        print "done."
    else:
        print "upload file is too big"


if __name__ == "__main__":
    parser = OptionParser()
    (options, args) = parser.parse_args()  

    if os.path.isfile(args[0]):
        uploader(args[0])
    else:
        print "not a valid file"
