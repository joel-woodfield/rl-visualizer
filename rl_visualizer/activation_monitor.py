import warnings
from threading import Lock


class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    Code from: https://refactoring.guru/design-patterns/singleton/python/example#example-1
    """

    _instances = {}

    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        # Now, imagine that the program has just been launched. Since there's no
        # Singleton instance yet, multiple threads can simultaneously pass the
        # previous conditional and reach this point almost at the same time. The
        # first of them will acquire lock and will proceed further, while the
        # rest will wait here.
        with cls._lock:
            # The first thread to acquire the lock, reaches this conditional,
            # goes inside and creates the Singleton instance. Once it leaves the
            # lock block, a thread that might have been waiting for the lock
            # release may then enter this section. But since the Singleton field
            # is already initialized, the thread won't create a new object.
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class ActivationMonitor(metaclass=SingletonMeta):
    _activations: dict = {}
    ACTIVATION_INDEX = 0
    GRADIENT_INDEX = 1
    REQUIRES_GRAD_FLAG_INDEX = 2

    def monitor_activation(self, activation, name, requires_grad=False):
        self._activations[name] = [activation, None, requires_grad]

        if requires_grad:
            if activation.requires_grad:
                warnings.warn(
                    "The activation being registered already requires grad. "
                    "It will be detached from the computational graph."
                )
            activation = activation.detach()
            activation.requires_grad = True
            activation.register_hook(lambda gradient: self.set_gradient(name, gradient))

        return activation

    def set_activation(self, name, activation):
        self._activations[name][self.ACTIVATION_INDEX] = activation

    def set_gradient(self, name, gradient):
        self._activations[name][self.GRADIENT_INDEX] = gradient

    def get_activation(self, name):
        if name not in self._activations:
            raise ValueError(f"Activation {name} was not monitored.")
        return self._activations[name][self.ACTIVATION_INDEX]

    def get_gradient(self, name):
        if not self._activations[name][self.REQUIRES_GRAD_FLAG_INDEX]:
            raise ValueError(f"The gradient for activation {name} was not monitored. Set requires_grad=True in activation_monitor.monitor_activation().")
        return self._activations[name][self.GRADIENT_INDEX]


def monitor_activation(activation, name, requires_grad=False):
    return ActivationMonitor().monitor_activation(activation, name, requires_grad)


def get_activation(name):
    return ActivationMonitor().get_activation(name)


def get_gradient(name):
    return ActivationMonitor().get_gradient(name)
