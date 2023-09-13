# Copyright (c) OpenMMLab. All rights reserved.
from typing import Callable, Union

from mmlmtools.parsers import DefaultParser
from mmlmtools.schema import ToolMeta
from mmlmtools.types import ImageIO
from mmlmtools.utils import load_or_build_object, require
from ..base import BaseTool


class HumanBodyPose(BaseTool):
    DEFAULT_TOOLMETA = ToolMeta(
        name='Human Body Pose Detection On Image',
        description='This tool can estimate the pose or keypoints of '
        'human in an image and draw the human pose image',
        inputs=['image'],
        outputs=['image'],
    )

    @require('mmpose')
    def __init__(self,
                 toolmeta: Union[dict, ToolMeta] = DEFAULT_TOOLMETA,
                 parser: Callable = DefaultParser,
                 model='human',
                 device: str = 'cuda'):
        super().__init__(toolmeta=toolmeta, parser=parser)
        self.model_name = model
        self.device = device

    def setup(self):
        from mmpose.apis import MMPoseInferencer
        self._inferencer = load_or_build_object(
            MMPoseInferencer, pose2d=self.model_name, device=self.device)

    def apply(self, image: ImageIO) -> ImageIO:
        image = image.to_array()[:, :, ::-1]
        vis_params = self.adaptive_vis_params(*image.shape[:2])
        results = next(
            self._inferencer(
                inputs=image,
                skeleton_style='openpose',
                black_background=True,
                return_vis=True,
                **vis_params,
            ))
        skeleton_image = results['visualization'][0][:, :, ::-1]
        return ImageIO(skeleton_image)

    @staticmethod
    def adaptive_vis_params(width, height) -> dict:
        scale = (width * height)**0.5

        radius = max(round((3 / 256) * scale), 3)
        thickness = max(round((1 / 256) * scale), 3)

        return dict(radius=int(radius), thickness=int(thickness))
