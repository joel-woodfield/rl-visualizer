import warnings
from enum import Enum
from threading import Lock

import h5py
import imageio
import numpy as np
import torch
from PIL import Image
import pickle


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


class RlvizType(Enum):
    GRAYSCALE = 1
    COLOR = 2
    GRID = 3
    LOGGRID = 4
    TEXT = 5


class RlVisualizer(metaclass=SingletonMeta):
    _attributes: set[str] = set()
    _types: dict[str, RlvizType] = {}
    _step_number: int = 0
    _is_recording: bool = False
    _is_paused: bool = False

    _data: dict[str, list[object]] = {}
    _step_buffer: dict[str, object] = {}

    def reset(self) -> None:
        self._data.clear()
        self._attributes.clear()
        self._types.clear()
        self._reset_recording()

    def _reset_recording(self) -> None:
        for attribute_data in self._data.values():
            attribute_data.clear()

        self._step_buffer.clear()
        self._is_recording = False
        self._is_paused = False
        self._step_number = 0

    def init_attributes(self, names: list[str], types: list[RlvizType]) -> None:
        self.reset()

        if len(names) != len(types):
            raise ValueError("names must have the same length as types.")

        self._attributes = set(names)
        if len(self._attributes) != len(names):
            raise ValueError("names must not contain duplicates")

        self._types = dict(zip(names, types))
        self._data = {name: [] for name in names}

    def start_recording(self) -> None:
        if self._is_recording:
            warnings.warn("start_recording() is called when Rlviz is already recording.", stacklevel=2)
        self._reset_recording()
        self._is_recording = True

    def pause(self) -> None:
        if self._is_paused:
            warnings.warn("pause() is called when Rlviz is already paused.", stacklevel=2)
        if not self._is_recording:
            warnings.warn("pause() is called when Rlviz is not recording. Ignoring.", stacklevel=2)
            return
        self._is_paused = True

    def unpause(self) -> None:
        if not self._is_paused:
            warnings.warn("unpause() is called when Rlviz is not already paused.", stacklevel=2)
        if not self._is_recording:
            warnings.warn("unpause() is called when Rlviz is not recording. Ignoring.", stacklevel=2)
            return
        self._is_paused = False

    def add(self, name: str, data: object) -> None:
        if not self._is_recording or self._is_paused:
            return

        self._validate_attribute(name)
        self._validate_compatibility(name, data)
        self._validate_duplicate(name)

        self._step_buffer[name] = self._process_data(data)

    def end_step(self):
        if self._step_number == 0 and any(attr not in self._step_buffer for attr in self._attributes):
            raise ValueError("Must add all attributes in the first step.")

        for attribute in self._attributes:
            if attribute not in self._step_buffer:
                step_data = self._get_default_value(attribute)
            else:
                step_data = self._step_buffer[attribute]
            self._data[attribute].append(step_data)

        self._step_buffer.clear()
        self._step_number += 1

    def end_recording(self, output_path: str):
        if not self._is_recording:
            raise ValueError("Rlviz must be recording to call end_recording()")

        self._save_data(output_path)

    def _save_data(self, output_path: str):
        with h5py.File(output_path, "w") as f:
            for attribute, data in self._data.items():
                f.create_dataset(attribute, data=self._process_data_h5py(attribute, data))

            # Store metadata about data types
            dtype_group = f.create_group("_dtypes")  # Create a group to store data types
            for attribute, rlviz_type in self._types.items():
                dtype_group.attrs[attribute] = str(rlviz_type)  # Store type as string

    def _process_data_h5py(self, attribute: str, data: list[object]):
        rlviz_type = self._types[attribute]

        if rlviz_type == RlvizType.TEXT:
            return np.array(data, dtype=h5py.special_dtype(vlen=str))
        else:
            return np.stack(data)

    def _get_default_value(self, attribute: str):
        if self._step_number == 0:
            raise ValueError("default value cannot be obtained on the first step.")

        type = self._types[attribute]
        if type == RlvizType.TEXT:
            return "MISSING"
        else:
            return np.zeros_like(self._data[attribute][-1])

    def _validate_attribute(self, name: str) -> None:
        if name not in self._attributes:
            raise ValueError(f"The attribute {name} was not initialized.")

    def _validate_compatibility(self, name: str, data: object) -> None:
        if not self._is_compatible(data, self._types[name]):
            raise ValueError(f"data is not compatible with {name}'s type {self._types[name]}.")

    def _validate_duplicate(self, name: str) -> None:
        if name in self._step_buffer:
            raise ValueError(f"Data for attribute {name} has already been added for this step.")

    def _is_compatible(self, data: object, type: RlvizType) -> bool:
        if type == RlvizType.TEXT:
            return isinstance(data, (int, float, str))
        return isinstance(data, np.ndarray) and data.ndim in {2, 3}

    def _process_data(self, data: object):
        # todo
        return data


def normalize(frames: np.ndarray) -> np.ndarray:
    return (frames - np.min(frames)) / (np.max(frames) - np.min(frames))


def colorize(frames: np.ndarray) -> np.ndarray:
    # TODO test if it works for 4dim array
    if len(frames.shape) not in [3, 4]:
        raise ValueError("Input frames should be TxHxW or TxCxHxW")

    rgb_frames = np.stack([frames] * 3, axis=-1)
    return rgb_frames


def gridify(
    frames: np.ndarray, border_width: int, border_color: tuple[int, int, int], scale_factor: int = 1
) -> np.ndarray:
    if len(frames.shape) != 5:
        raise ValueError("Input frames should be TxCxHxWx3")

    T, C, H, W, _ = frames.shape  # Time, Channels, Height, Width, Color
    H *= scale_factor
    W *= scale_factor

    # work out grid dimensions automatically
    grid_h = np.ceil(np.sqrt(C))
    while C % grid_h != 0 and grid_h >= np.floor(np.sqrt(C)):
        grid_h -= 1
    grid_h = int(grid_h)  # Grid height in cells
    grid_w = int(np.ceil(C / grid_h))   # Grid width in cells

    # Calculate total grid dimensions including borders
    total_h = H * grid_h + border_width * (grid_h + 1)
    total_w = W * grid_w + border_width * (grid_w + 1)
    
    # Initialize grid with border color
    grid = np.full((T, total_h, total_w, 3), border_color, dtype=frames.dtype)

    for c in range(C):
        row = c // grid_w
        col = c % grid_w

        # Calculate top-left corner of current cell
        y = row * (H + border_width) + border_width
        x = col * (W + border_width) + border_width

        # Place the frame in the grid
        if scale_factor != 1:
            frame_cut = np.repeat(np.repeat(frames[:, c], scale_factor, axis=1), scale_factor, axis=2)
        else:
            frame_cut = frames[:, c]
        grid[:, y:y+H, x:x+W] = frame_cut

    return grid


def init_attributes(names: list[str], types: list[RlvizType]):
    RlVisualizer().init_attributes(names, types)


def start_recording():
    RlVisualizer().start_recording()


def end_recording(output_path: str):
    RlVisualizer().end_recording(output_path)


def pause():
    RlVisualizer().pause()


def unpause():
    RlVisualizer().unpause()


def add(name: str, data: object):
    RlVisualizer().add(name, data)


def end_step():
    RlVisualizer().end_step()


def reset():
    RlVisualizer().reset()
