class ViewSetError(Exception):
    """
        This Error acts as a base for all other viewset based errors
    """

    pass


class ImproperlyConfiguredViewSetError(ViewSetError):
    """
        This error is supposed to be thrown if a viewset is not configured correctly
    """

    pass
