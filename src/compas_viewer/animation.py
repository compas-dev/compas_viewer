"""Animation recording presets."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnimationPreset:
    """Settings for a common animation output target.

    Parameters
    ----------
    width
        Frame width in pixels.
    height
        Frame height in pixels.
    fps
        Frames per second.
    colors
        Maximum number of colors used for GIF output.
    quality
        WebP output quality from 0 to 100.
    optimize
        Whether to optimize animated GIF output.

    """

    width: int
    height: int
    fps: int
    colors: int
    quality: int
    optimize: bool = True


ANIMATION_PRESETS: dict[str, AnimationPreset] = {
    "preview": AnimationPreset(width=640, height=360, fps=15, colors=128, quality=70),
    "documentation": AnimationPreset(width=960, height=540, fps=24, colors=256, quality=85),
    "presentation": AnimationPreset(width=1280, height=720, fps=30, colors=256, quality=95, optimize=False),
}

__all__ = ["ANIMATION_PRESETS", "AnimationPreset"]
