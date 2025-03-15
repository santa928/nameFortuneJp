from functools import wraps
from flask import has_request_context, copy_current_request_context as flask_copy_current_request_context

def copy_current_request_context(f):
    """
    リクエストコンテキストを新しいスレッドにコピーするデコレータ
    """
    if has_request_context():
        return flask_copy_current_request_context(f)
    return f 