class ActiveRecord:
    """
    base class for active record pattern
    """
    def save(self):
        raise NotImplementedError("Subclasses must implement save method")