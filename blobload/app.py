"""Blobload app for uploading files to the Blobstore with an external script."""


from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
import urllib


class MainHandler(webapp.RequestHandler):
    """Provides the index.html page."""

    def get(self):
        blobs = reversed(blobstore.BlobInfo.all().fetch(10))
        output = template.render('index.html', {'blobs': blobs})
        self.response.out.write(output)


class UploadUrlRequestHandler(webapp.RequestHandler):
    """Provides the file upload URL."""

    def get(self):
        """Handles get."""

        upload_url = blobstore.create_upload_url('/upload')

        self.response.headers['content-type'] = 'text/plain'
        self.response.out.write(upload_url)


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    """Handles upload of blobs."""

    def post(self):
        """Handles post."""

        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        self.redirect('/')


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    """Serves blobs."""

    def get(self, resource):
        """Handles get."""

        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


app = webapp.WSGIApplication([
    ('/', MainHandler),
    ('/prepare', UploadUrlRequestHandler),
    ('/upload', UploadHandler),
    ('/serve/([^/]+)?', ServeHandler),
], debug=True)


def main():
    """The main function."""

    util.run_wsgi_app(app)


if __name__ == '__main__':
    main()
