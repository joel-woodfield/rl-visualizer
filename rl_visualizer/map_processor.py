import imageio
import numpy as np

from PIL import Image
from tqdm import tqdm


def make_map_grid(
    saliency_maps, grid_height, grid_width, border_width=3, border_color=(128, 128, 128)
):
    if len(saliency_maps.shape) != 5:
        raise ValueError("saliency_maps must have 5 dimensions: timesteps, feature_channels, height, width, color_channels.")
    if saliency_maps.shape[1] > grid_height * grid_width:
        raise ValueError("Grid height and width too small to fit all channels in saliency map.")

    timesteps, num_channels, cell_height, cell_width, color_channels = saliency_maps.shape

    grid_height_pixels = cell_height * grid_height + border_width * (grid_height + 1)
    grid_width_pixels = cell_width * grid_width + border_width * (grid_width + 1)
    grid = np.zeros((timesteps, grid_height_pixels, grid_width_pixels, color_channels), dtype=saliency_maps.dtype)

    # top and left border of the grid
    grid[:, :border_width, :] = border_color
    grid[:, :, :border_width] = border_color

    for channel_num in range(num_channels):
        map = saliency_maps[:, channel_num]

        cell_i = int(channel_num / grid_width)
        cell_j = channel_num % grid_width

        pixel_i = cell_i * cell_height + (1 + cell_i) * border_width
        pixel_j = cell_j * cell_width + (1 + cell_j) * border_width

        # add map
        grid[:, pixel_i:pixel_i+cell_height, pixel_j:pixel_j+cell_width] = map

        # add border
        pixel_i = pixel_i + cell_height
        pixel_j = pixel_j + cell_width
        grid[:, pixel_i:pixel_i+border_width, :] = border_color
        grid[:, :, pixel_j:pixel_j+border_width] = border_color

    return grid


def combine_frames_and_saliency_grid(frames, saliency_grids, verbose=False):
    num_frames, frame_height, frame_width, channels = frames.shape
    _, grid_height, grid_width, _ = saliency_grids.shape

    grid_scale_factor = frame_height / grid_height
    scaled_grid_width = int(grid_width * grid_scale_factor)
    combined_frames = np.zeros((num_frames, frame_height, frame_width + scaled_grid_width, channels), dtype=saliency_grids.dtype)

    if verbose:
        loop = tqdm(enumerate(zip(frames, saliency_grids)), desc="Combining video", unit=" frames", total=len(frames))
    else:
        loop = enumerate(zip(frames, saliency_grids))

    for i, (frame, grid) in loop:
        resized_grid = np.array(Image.fromarray(grid).resize((scaled_grid_width, frame_height), Image.Resampling.NEAREST))
        combined_frame = np.concatenate([frame, resized_grid], axis=1)
        combined_frames[i] = combined_frame
    return combined_frames


def min_max_normalize(saliency_maps):
    return (saliency_maps - np.min(saliency_maps)) / (np.ptp(saliency_maps) + 1e-8)


def grayscale_to_rgb(frames):
    return np.stack([frames, frames, frames], axis=-1)


def save_video(frames, filename, fps=60):
    print('Writing %d frames to %s at fps=%d...' % (len(frames), filename, fps))
    imageio.mimsave(filename, frames, fps=fps)
