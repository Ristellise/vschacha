import typing
import vapoursynth
import functools

output_mix_frame = None


class Mframe:

    def __init__(self, source, final:vapoursynth.VideoNode=None, **sources: vapoursynth.VideoNode):
        """
        A class to hold multiple vapoursynth VideoNodes
        :param sources:
        """
        self.sources = sources

    def set_source(self, source: vapoursynth.VideoNode):
        self.sources["source"] = source

    def set_final(self, source: vapoursynth.VideoNode):
        self.sources["final"] = source

    def get(self, name):
        return self.sources[name]

    def set_global(self):
        global output_mix_frame
        output_mix_frame = self

    @staticmethod
    def get_global():
        return output_mix_frame
