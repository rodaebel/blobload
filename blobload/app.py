"""Blobload app for uploading files to the Blobstore with an external script."""


from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
import urllib


class MainHandler(webapp.RequestHandler):
    """A simple main handler."""

    def get(self):
        """Provides the index.html page."""

        upload_info = self.request.GET.get('upload_info')
        if upload_info:
            self.response.headers['content-type'] = 'text/plain'
            self.response.out.write(upload_info)
            return

        blobs = reversed(blobstore.BlobInfo.all().fetch(10))
        output = template.render('index.html', {'blobs': blobs})
        self.response.out.write(output)


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    """Handles upload of blobs."""

    def get(self):
        """Provides an upload URL."""

        upload_url = blobstore.create_upload_url('/upload')

        self.response.headers['content-type'] = 'text/plain'
        self.response.out.write(upload_url)

    def post(self):
        """Stores blob infos for uploaded files."""

        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        self.redirect('/?upload_info=%s' % urllib.quote(blob_info.filename))


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    """Serves blobs."""

    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


app = webapp.WSGIApplication([
    ('/', MainHandler),
    ('/upload', UploadHandler),
    ('/serve/([^/]+)?', ServeHandler),
], debug=True)


def main():
    """The main function."""

    util.run_wsgi_app(app)


if __name__ == '__main__':
    main()
