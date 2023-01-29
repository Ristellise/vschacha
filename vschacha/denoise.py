import typing
import vapoursynth
import vsdenoise, vstools

def bm3d(
        in_clip: vapoursynth.VideoNode,
        ref: vapoursynth.VideoNode = None,
        sigma: typing.Union[float, typing.List[float], typing.List[typing.List[float]]] = 3,
        radius: typing.Union[typing.Optional[int], typing.List[typing.Optional[int]]] = 1,
        profile: vsdenoise.Profile = vsdenoise.Profile.LOW_COMPLEXITY,
        cuda: int = 1
):
    """Denoise with Block-matching and 3D filtering

    It is in general, a well rounded denoising tool that can be applied to most* modern animation.
    However, it struggles for artistic anime that uses static grain for certain effects.
                    
    Args:
        in_clip (vs.VideoNode): The input clip.

        ref (vs.VideoNode): Referance clip. 
            - This can be good if you use DFTTest or something to tell BM3D what to lookout for. Something like that.

        sigma (A list or a single value representing all 3 planes): The denoising strength.
            - Defaults to 3 -> [3, 3, 3]. *You should probable change this!*

        radius (A list or a single value representing all 3 planes): The number of frames to look ahead/behind for referance.
            - Higher values for a larger range.

        cuda (int) : Enable the use of cuda. Defaults to cuda enabled. 0 for CPU, 1 for CUDA, 2 for CUDA+RTC (Runtime Code Compilation. Slightly faster but slight overhead).

    Returns:
        VideoNode: VapourSynth Video node. You don't need anything else right?
    """
    modes = [vsdenoise.BM3DCPU, vsdenoise.BM3DCuda, vsdenoise.BM3DCudaRTC]
    matrix = vstools.Matrix.from_video(in_clip, strict=True)
    # Sigma passes though correctly but pylance is flagging out due to it because "Nooo i want to use special types!!!"
    return modes[cuda](in_clip, ref=ref, sigma=sigma, profile=profile, radius=radius, matrix=matrix).clip

def ccd(
        in_clip: vapoursynth.VideoNode,
        thr: float = 4,
        mode=0
):
    """Camcorder Color denoise (CCD)

    A chroma only denoiser. Reading from vsdenoise: "works great on old sources such as VHSes and DVDs."
    Although it's right in a sense, from my experience, CCD works well for modern anime as well.

    This method is a dumbbed down version from vsdenoise, and yes it just calls vsdenoise.ccd().

    Args:
        in_clip (vs.VideoNode): The input clip.

        thr (float): The Euclidean distance threshold for including pixel in the matrix.
            - Higher = Stronger denoising

        mode (int): The mode in which the video is processed. 1-4 all procceses the clip in 444.
            - [0] (default) Processes as-is, without any pre/post processing.
            - [1] Downscales luma to match chroma with bicubic.
            - [2] Upscale chroma to match luma with bicubic.
            - [3] Upscale chroma to match luma with NNedi3, downscale with bicubic.
            - [4] Upscale chroma to match luma with NNedi3, downscale with SSIM.


    Returns:
        VideoNode: VapourSynth Video node.
    """
    return vsdenoise.ccd(in_clip, thr, mode=mode)