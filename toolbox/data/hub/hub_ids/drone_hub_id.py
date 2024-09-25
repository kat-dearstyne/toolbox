from toolbox.data.hub.abstract_hub_id import AbstractHubId
from toolbox.data.hub.hub_ids.multi_task_hub_id import MultiStageHubId
from toolbox.util.override import overrides


class DroneHubId(MultiStageHubId):
    """
    Describes the DroneResponse project reader.
    """

    @overrides(AbstractHubId)
    def get_url(self) -> str:
        """
        :return: Returns URL to DroneResponse on the SAFA bucket containing definition file.
        """
        return "https://safa-datasets-open.s3.amazonaws.com/datasets/open-source/drone.zip"
