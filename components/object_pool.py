class ObjectPool:
    def __init__(self, factory_func, initial_size=10):
        self.factory_func = factory_func
        self.active_objects = []
        self.inactive_objects = []
        
        # Create initial objects
        for _ in range(initial_size):
            obj = factory_func()
            obj.active = False
            self.inactive_objects.append(obj)
    
    def get_object(self, *args, **kwargs):
        """Get an object from the pool or create new one"""
        if self.inactive_objects:
            obj = self.inactive_objects.pop()
        else:
            obj = self.factory_func()
            
        # Initialize with args
        obj.initialize(*args, **kwargs)
        obj.active = True
        self.active_objects.append(obj)
        return obj
    
    def release_object(self, obj):
        """Return object to pool"""
        if obj in self.active_objects:
            self.active_objects.remove(obj)
            obj.active = False
            self.inactive_objects.append(obj)
    
    def update(self, *args, **kwargs):
        """Update all active objects"""
        for obj in list(self.active_objects):
            if not obj.active:
                self.release_object(obj)
            else:
                obj.update(*args, **kwargs)
