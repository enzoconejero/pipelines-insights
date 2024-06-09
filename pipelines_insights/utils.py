def basic_equals(obj1, obj2):
    """Check if objects are the same class and the attributes are equals"""
    return obj1.__class__ == obj2.__class__ and obj1.__dict__ == obj2.__dict__
