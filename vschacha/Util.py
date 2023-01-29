import pathlib
import typing

import lvsfunc
import stgfunc
import vapoursynth
import vsmasktools
import vsrgtools
import vsutil
from vapoursynth import core

try:
    import gdown
except ImportError:
    gdown = None

def chamomile_tea(in_clip, ranges, function, debug=False):
    """
    Applies the vapoursynth function to the in_clip with the ranges provided.

    This function is "decently" performant, in that it only applies the function to the list of ranges.
    Any instantiation of the function MUST happen before calling this function, we just run the definition,
    we don't do any instantiation.

    :param in_clip: The base clip to apply the function
    :param ranges: A array of arrays. Such as:
        [
            [0,1000, {"kwargs":"Additional Args"}],
        ]

        The
    :param function: The vapoursynth function or a VideoNode. The first param must accept a vapoursynth VideoNode if it's a function.
    :param debug: Writes a Text number to indicate which range it is.
    :return: A vapoursynth VideoNode with the ranges applied.
    :raises: Any exception. Any uncaught exception may be raised here.
    """

    if isinstance(function, vapoursynth.VideoNode) and function.num_frames == in_clip.num_frames:
        for idx, modify_range in enumerate(ranges):
            clp = function[modify_range[0]:modify_range[1]]
            in_clip = vsutil.insert_clip(in_clip, insert=clp, start_frame=modify_range[0])
            if debug:
                in_clip = in_clip.text.Text(f"{idx}".zfill(2), 2, 7)
    elif isinstance(function, typing.Callable):
        for idx, modify_range in enumerate(ranges):
            clp = function(in_clip[modify_range[0]:modify_range[1]], **modify_range[2])
            in_clip = vsutil.insert_clip(in_clip, insert=clp, start_frame=modify_range[0])
            if debug:
                in_clip = in_clip.text.Text(f"{idx}".zfill(2), 2, 7)
    return in_clip


def mask_replace_square(source_base: vapoursynth.VideoNode,
                        source_replace: vapoursynth.VideoNode,
                        pos: tuple[int, int],
                        size: tuple[int, int],
                        ranges, blur: float = 1,
                        mask: bool = False
                        ):
    """

    Like the function name, replaces an area from a square mask.

    I know you're thinking: "Isn't there a squaremask function on vsmaskutils?"

    Yes. But it's more unweildy compared to just defining a postion,
    size of the mask and the ranges you want.

    Note that this needs lvsfunc.

    :param source_base: The source clip to be replaced.
    :param source_replace: The clip that will be used to replace the base clip
    :param pos: Position of the square mask. In (x, y) from the top left.
    :param size: Size of the mask. In (width, height) notation as well.
    :return: The clip with the area replaced
    """

    maskclp = lvsfunc.BoundingBox(pos, size).get_mask(source_base).bilateral.Gaussian(sigma=blur)

    if mask:
        return maskclp
    return chamomile_tea(source_base, ranges, source_base.std.MaskedMerge(source_replace, maskclp))

def web_source(*src_links, cache_dir: str, depth=16, comb="lehmer", colorspace=None):
    if gdown is None:
        raise ImportError(f"Missing required import: `gdown`. Please install it.")
    
    cache_dir_path = pathlib.Path(cache_dir).resolve()
    if not cache_dir_path.is_dir():
        cache_dir_path.mkdir(parents=True,exist_ok=True)
    gdown.download()


def saucery(*src_input, depth=16, comb="lehmer", colorspace=None):
    """

    Shinon Source function. Boilerplate code when you want to hack and merge 2 different sources without care.

    :param src_input: path inputs. They will be resolved to valid paths before passing onto stgfunc.src
    :param depth: Depth for stgfunc, what else?
    :param comb: merging function. Can be: "avg", "lehmer". "lehmer" is recommended and default.
    :param colorspace: The colorspace using fmtc.resample.
    :return: 1 vapoursynth clip with the merged clip.
    """
    inputs_path = [str(pathlib.Path(inputs).resolve(strict=True)) for inputs in src_input]
    srcs = list(stgfunc.src(inputs, depth=depth, matrix_prop=True) for inputs in inputs_path)
    if comb == "avg":
        if len(src_input) == 2:
            output = core.std.Expr(srcs, 'x y + 2 /')
        elif len(src_input) > 2:
            output = core.average.Mean(*srcs)
        else:
            output = srcs[0]
    elif comb == "lehmer":
        if len(src_input) == 2:
            output = vsrgtools.lehmer_diff_merge(srcs[0], srcs[1])
        elif len(src_input) > 2:
            raise Exception("lehmer merge does not support 2+ srcs!")
        else:
            output = srcs[0]
    else:
        raise Exception(f"Unrecognized combing method: {comb}")
    if colorspace is not None:
        output = output.fmtc.resample(css=colorspace)
    return output


def scale(clip: vapoursynth.VideoNode, percent=0.5):
    """
    Function used for "thresholds" for vsmask.
    :param clip: Input clip to get the bitdepth.
    :param percent: 0.0 to 1.0.
    :return: value that is scaled to the max value possible for the clip's format.
    """
    max_v = 1 << clip.format.bits_per_sample
    return max_v * percent
