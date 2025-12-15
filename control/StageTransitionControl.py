from control.AGV import AGV
from control.PathCreationAlgorithm import PathCreationAlgorithm


agv1 = AGV(
    marked_states=[(1, 1), (3, 6), (5, 2), (8, 7), (4, 7), (9, 12), (2, 13)],
    radius=0.5,
    color="#12700EFF",
    path_color="#17D220",
)

agv2 = AGV(
    marked_states=[(1, 7), (4, 10), (7, 7), (10, 4),  (13, 7)],
    radius=0.5,
    color="#12700EFF",
    path_color="#17D220",
)

agv3 = AGV(
    marked_states=[(13, 7), (10, 10), (7, 7), (4, 4), (1, 7)],
    radius=0.5,
    color="#330DCEFF",
    path_color="#2F75CB",
)

class StageTransitionControl:

    def __init__(self, robot):
        # self.agvs = [agv1]
        self.agvs = [agv2, agv3]

        self.path_creator = PathCreationAlgorithm()
        self.create_paths()

    def create_paths(self) -> None:
        for agv in self.agvs:
            path = self.path_creator.create_path(agv.marked_states.copy(), agv.radius)
            print(path)
            agv.path = path

    def get_agvs_number(self) -> int:
        return len(self.agvs)
    