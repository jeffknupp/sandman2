from flask import jsonify

def register_index(router, root = "/"):
    """Creates a root endpoint for the API

    This takes a list of :class:`ModelView` classes and creates an endpoint that simply lists them.
    The function uses the :attr:`__name__` and a :attr:`__url__` attributes of the :class:`ModelView` to list the API endpoints.

    :param router: A Flask application or blueprint
    :param root: The root URI for the Sandman index
    :return: A response whose body lists the routes setup by the model views
    """
    @router.route(root)
    def index():
        """Return a list of routes to the registered classes."""
        routes = {}
        for view in router.model_views:
            routes[view.__model__.__name__] = '{}{{/{}}}'.format(
                view.__model__.__url__,
                view.__model__.primary_key())
        return jsonify(routes)
