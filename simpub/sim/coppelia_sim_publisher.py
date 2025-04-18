import numpy as np

from ..parser.coppelia_sim import CoppeliasSimParser
from ..simdata import SimObject, SimScene, SimTransform, SimVisual
from ..simdata import SimMaterial, SimTexture, SimMesh
from ..simdata import VisualType
from ..core.log import logger


from mujoco import mj_name2id, mjtObj
from typing import List, Dict, Tuple, Optional
import numpy as np

from ..core.simpub_server import SimPublisher
from ..parser.mj import MjModelParser
from ..simdata import SimObject


class CoppeliaSimPublisher(SimPublisher):

    def __init__(
        self, sim,
        host: str = "127.0.0.1",
        no_rendered_objects: Optional[List[str]] = None,
        no_tracked_objects: Optional[List[str]] = None,
        visual_layer_list: Optional[List[int]] = None,
    ) -> None:
        # self.mj_model = mj_model
        # self.mj_data = mj_data
        self.sim = sim
        self.parser = CoppeliasSimParser(sim, visual_layer_list)
        sim_scene = self.parser.parse()

        self.tracked_obj_trans: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
        super().__init__(
            sim_scene,
            host,
            no_rendered_objects,
            no_tracked_objects,
        )
        # self.set_update_objects(self.sim_scene.root)

    def set_update_objects(self, obj: Optional[SimObject]):
        if obj is None:
            return
        if obj.name in self.no_tracked_objects:
            return
        body_id = str(obj.name)
        pos = self.sim.getObjectPosition(body_id, self.sim.handle_world)
        rot = self.sim.getObjectQuaternion(body_id, self.sim.handle_world)

        trans: Tuple[np.ndarray, np.ndarray] = (pos, rot)
        self.tracked_obj_trans[obj.name] = trans
        for child in obj.children:
            self.set_update_objects(child)

    def get_update(self) -> Dict[str, List[float]]:
        state = {}
        for name, trans in self.tracked_obj_trans.items():
            pos, rot = trans
            state[name] = [
                -pos[1], pos[2], pos[0], rot[2], -rot[3], -rot[1], rot[0]
            ]
        return state
