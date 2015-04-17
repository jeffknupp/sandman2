from sandman2 import AutomapModel


class User(AutomapModel):

    """A user of the blogging application."""

    __tablename__ = 'user'

    def __unicode__(self):
        return self.name


class Blog(AutomapModel):

    """An online weblog."""

    __tablename__ = 'blog'

    def __unicode__(self):
        return self.name

class Post(AutomapModel):

    """An individual blog post."""

    __tablename__ = 'post'

    def __unicode__(self):
        return self.title
