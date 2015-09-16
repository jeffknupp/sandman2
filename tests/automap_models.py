from sandman2 import AutomapModel


class User(AutomapModel):

    """A user of the blogging application."""

    __tablename__ = 'user'

    def __str__(self):
        return self.name

    __unicode__ = __str__


class Blog(AutomapModel):

    """An online weblog."""

    __tablename__ = 'blog'

    def __str__(self):
        return self.name

    __unicode__ = __str__

class Post(AutomapModel):

    """An individual blog post."""

    __tablename__ = 'post'

    def __str__(self):
        return self.title

    __unicode__ = __str__
