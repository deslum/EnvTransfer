import urllib2


def function_exception(func):
    def new_func(*args):
        try:
            if func.__name__ in 'upload_file':
                print "Start upload file"
                func(*args)
                print "File successfully uploaded..."
            elif func.__name__ in 'download_file':
                print "Start download file"
                func(*args)
                print "File successfully downloaded..."
            else:
                func(*args)
        except urllib2.URLError as e:
            print "Connection error"
            print e.fp.read()
        except IOError:
            print "File error"
        except TypeError:
            print "Token not found. Please generate token 'envtransfer auth'"

    return new_func
