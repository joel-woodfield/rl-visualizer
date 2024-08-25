from threading import Lock

import imageio
import numpy as np
import torch
from PIL import Image


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


class RLVisualizer(metaclass=SingletonMeta):
    _names: list[str]
    _frames: dict[str, list[torch.Tensor]]
    _is_recording: bool = False
    # the number of complete frames added by calling add() and end_step()
    _frame_count: int = 0

    BORDER_WIDTH = 1
    BORDER_COLOR = [0, 191,255]

    def reset(self):
        self._names = None
        self._frames = None
        self._is_recording = False
        self._frame_count = 0  

    def init_names(self, names: list[str]):
        if self._names is not None:
            raise ValueError("Names have already being set. Please call reset().")
        self._names = names
        self._frames = {name: [] for name in self._names}

    def start_recording(self):
        if self._is_recording:
            raise ValueError("Visualizer is already recording.")
        self._is_recording = True

    def add(self, frame: torch.Tensor, name: str):
        if self._is_recording:
            self._add(frame, name)
        # else ignore
        
    def _add(self, frame: torch.Tensor, name: str):
        if name not in self._names:
            raise ValueError(
                f"The name {name} was not initialized.\n"
                f"Please call reset() and include this name to init_names()."
            )

        if len(self._frames[name]) == self._frame_count + 1:
            raise ValueError(f"The frame for name {name} has already been added for this step.")

        self._frames[name].append(frame)
    
    def end_step(self):
        for name, frames in self._frames.items():
            if len(frames) != self._frame_count + 1:
                raise ValueError(f"The frame for name {name} has not been added for this step.")

        self._frame_count += 1

    def end_recording(self, video_path: str):
        if not self._is_recording:
            raise ValueError("Visualizer has not yet started recording.")
        if self._frame_count == 0:
            raise ValueError("No frames have been added yet. Please use add() and end_step()")

        self._save_video(video_path)
        self.reset()
    
    def _save_video(self, video_path):
        processed_frames = {
            name: self._process_frames(frames) for name, frames in self._frames.items()
        }

        video = []
        for i in range(self._frame_count):
            combined_frame = self._combine_frames(
                {name: frames[i] for name, frames in processed_frames.items()}
            )
            video.append(combined_frame)

        imageio.mimsave(video_path, video)

    def _process_frames(self, frames: list[torch.Tensor]) -> list[np.ndarray]:
        frames = np.ndarray([frame.numpy() for frame in frames])
        frames = normalize(frames)
        frames = colorize(frames)
        if len(frames.shape) == 5:
            frames = gridify(frames, self.BORDER_WIDTH, self.BORDER_COLOR)

        return frames

    def _combine_frames(self, frames: dict[str, np.ndarray]) -> np.ndarray:
        for frame in frames.values():
            if len(frame.shape) != 3:
                raise ValueError("All frames must have shape HxWx3")

        max_height = max(frame.shape[0] for frame in frames.values())
        
        resized_frames = []
        total_width = 0
        
        for _, frame in frames.items():
            height, width = frame.shape[:2]
            if height != max_height:
                # Resize the frame to match the max_height while maintaining aspect ratio
                new_width = int(width * (max_height / height))
                frame = np.array(Image.fromarray(frame).resize((new_width, max_height)))
            
            resized_frames.append(frame)
            total_width += frame.shape[1]
        
        # Create a new image with the size of all resized frames combined
        combined = np.zeros((max_height, total_width, 3), dtype=np.uint8)
        
        # Paste the resized frames side by side
        x_offset = 0
        for frame in resized_frames:
            combined[:, x_offset:x_offset+frame.shape[1]] = frame
            x_offset += frame.shape[1]
        
        return combined
        

def normalize(frames: np.ndarray) -> np.ndarray:
    return (frames - np.min(frames)) / (np.max(frames) - np.min(frames))


def colorize(frames: np.ndarray) -> np.ndarray:
    # TODO test if it works for 4dim array
    if len(frames.shape) not in [3, 4]:
        raise ValueError("Input frames should be TxHxW or TxCxHxW")

    rgb_frames = np.stack([frames] * 3, axis=-1)
    return rgb_frames


def gridify(frames: np.ndarray, border_width: int, border_color: tuple[int, int, int]) -> np.ndarray:
    if len(frames.shape) != 5:
        raise ValueError("Input frames should be TxCxHxWx3")

    T, C, H, W, _ = frames.shape  # Time, Channels, Height, Width, Color
    grid_h = int(np.floor(np.sqrt(C)))  # Grid height in cells
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
        grid[:, y:y+H, x:x+W] = frames[:, c]

    return grid


def start_recording():
    RLVisualizer().start_recording()


def end_recording(filename: str):
    RLVisualizer().end_recording(filename)


def add(name: str, frame: torch.Tensor):
    RLVisualizer().add(name, frame)


def end_step():
    RLVisualizer().end_step()


def save(filename: str):
    RLVisualizer().save(filename)


def reset():
    RLVisualizer().reset()


def is_recording() -> bool:
    return RLVisualizer().is_recording()


def init_names(names: list[str]):
    RLVisualizer().init_names(names)

