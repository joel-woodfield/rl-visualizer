from enum import Enum
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


class FrameType(Enum):
    GRAYSCALE = 1
    COLOR = 2
    GRID = 3


class RLVisualizer(metaclass=SingletonMeta):
    _screens: list[str] = []
    _screen_frame_types = dict[str, FrameType]
    _frames: dict[str, list[torch.Tensor]] = {}
    _is_recording: bool = False
    # the number of complete frames added by calling add() and end_step()
    _frame_count: int = 0

    _border_width = 1
    _border_color = (0, 191, 255)
    _grid_scale_factor = 5
    _grid_binary = False

    def reset(self):
        self._screens = []
        self._screen_frame_types = {}
        self._frames = {}
        self._is_recording = False
        self._frame_count = 0

    def set_grid_scale_factor(self, factor):
        self._grid_scale_factor = factor

    def set_grid_binary(self, use_binary: bool):
        self._grid_binary = use_binary

    def init_screens(self, names: list[str], frame_types: list[FrameType] = None):
        if len(self._screens) != 0:
            raise ValueError("Screens have already being set. Please call reset().")
        if len(names) == 0:
            raise ValueError("Please provide at least one screen name.")
        if frame_types is None:
            frame_types = [FrameType.GRAYSCALE] * len(names)
        if len(names) != len(frame_types):
            raise ValueError("Names and frame types must have the same length.")
        if len(set(names)) != len(names):
            raise ValueError("Names must not have any duplicates.")

        self._screens = names
        self._screen_frame_types = {name: frame_type for name, frame_type in zip(names, frame_types)}
        self._frames = {screen: [] for screen in self._screens}

    def start_recording(self):
        if self._is_recording:
            raise ValueError("Visualizer is already recording.")
        self._is_recording = True

    def pause_recording(self):
        if not self._is_recording:
            raise ValueError("Visualizer is not recording.")
        self._is_recording = False

    def unpause_recording(self):
        if self._is_recording:
            raise ValueError("Visualizer is already recording.")
        self._is_recording = True

    def add(self, frame: torch.Tensor, screen: str):
        if self._is_recording:
            self._add(frame, screen)
        # else ignore
        
    def _add(self, frame: torch.Tensor, screen: str):
        if screen not in self._screens:
            raise ValueError(
                f"The screen {screen} was not initialized.\n"
                f"Please call reset() and include this screen to init_screens()."
            )
        if len(self._frames[screen]) == self._frame_count + 1:
            raise ValueError(f"The frame for screen {screen} has already been added for this step.")

        if self._screen_frame_types[screen] == FrameType.GRAYSCALE:
            if len(frame.shape) != 2:
                raise ValueError(
                    f"Screen {screen} with frame type {FrameType.GRAYSCALE} must have dimensions "
                    f"HxW, but was given {frame.shape}"
                )
        elif self._screen_frame_types[screen] == FrameType.COLOR:
            if len(frame.shape) != 3 or frame.shape[2] != 3:
                raise ValueError(
                    f"Screen {screen} with frame type {FrameType.COLOR} must have dimensions "
                    f"HxWx3, but was given {frame.shape}"
                )
        elif self._screen_frame_types[screen] == FrameType.GRID:
            if len(frame.shape) != 3:
                raise ValueError(
                    f"Screen {screen} with frame type {FrameType.GRID} must have dimensions "
                    f"CxHxW, but was given {frame.shape}"
                )

        self._frames[screen].append(frame)
    
    def end_step(self):
        for name, frames in self._frames.items():
            if len(frames) != self._frame_count + 1:
                self._frames[name].append(torch.zeros_like(frames[-1]))

        self._frame_count += 1

    def end_recording(self, video_path: str):
        if not self._is_recording:
            raise ValueError("Visualizer has not yet started recording.")
        if self._frame_count == 0:
            raise ValueError("No frames have been added yet. Please use add() and end_step()")

        self._save_video(video_path)
        self.reset()
    
    def _save_video(self, video_path):
        processed_frames = {}
        for name, frames in self._frames.items():
            processed_frames[name] = self._process_frames(frames, self._screen_frame_types[name])

        video = []
        for i in range(self._frame_count):
            combined_frame = self._combine_frames(
                {name: frames[i] for name, frames in processed_frames.items()}
            )
            video.append(combined_frame)

        imageio.mimsave(video_path, video)

    def _process_frames(self, frames: list[torch.Tensor], frame_type: FrameType) -> np.ndarray:
        frames = np.array([frame.numpy() for frame in frames])
        frames = normalize(frames)
        frames = (frames * 255).astype(np.uint8)

        if frame_type != FrameType.COLOR:
            frames = colorize(frames)
        if frame_type == FrameType.GRID:
            frames = gridify(
                frames,
                self._border_width,
                self._border_color,
                scale_factor=self._grid_scale_factor,
                binary=self._grid_binary,
            )

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
                frame = np.array(Image.fromarray(frame).resize((new_width, max_height), Image.NEAREST))
            
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


def gridify(frames: np.ndarray, border_width: int, border_color: tuple[int, int, int], scale_factor: int = 1, binary: bool = False) -> np.ndarray:
    if len(frames.shape) != 5:
        raise ValueError("Input frames should be TxCxHxWx3")

    T, C, H, W, _ = frames.shape  # Time, Channels, Height, Width, Color
    H *= scale_factor
    W *= scale_factor

    if binary:
        frames = (frames > 0).astype(np.uint8)

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


def start_recording():
    RLVisualizer().start_recording()


def end_recording(filename: str):
    RLVisualizer().end_recording(filename)


def pause_recording():
    RLVisualizer().pause_recording()


def unpause_recording():
    RLVisualizer().unpause_recording()


def add(frame: torch.Tensor, screen: str):
    RLVisualizer().add(frame, screen)


def end_step():
    RLVisualizer().end_step()


def reset():
    RLVisualizer().reset()


def init_screens(screens: list[str], frame_types: list[FrameType] = None):
    RLVisualizer().init_screens(screens, frame_types)


def set_grid_binary(grid_binary: bool):
    RLVisualizer().set_grid_binary(grid_binary)
