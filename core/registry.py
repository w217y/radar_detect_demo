class SignalRegistry:
    _registry = {}

    @classmethod
    def register(cls,name):
        def decorator(signal_class):
            cls._registry[name] = signal_class
            return signal_class
        return decorator
    

    @classmethod
    def get_signal_class(cls,name):
        if name not in cls._registry:
            raise ValueError(f"未知的信号信号类型：{name}，已注册的类型有：{list[cls._registry.keys()]}")
        return cls._registry[name]
    
    