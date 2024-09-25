from toolbox.data.hub.abstract_hub_id import AbstractHubId
from toolbox.util.override import overrides


class CM1HubId(AbstractHubId):
    """
    Describes the CM1 project reader.
    """

    @overrides(AbstractHubId)
    def get_url(self) -> str:
        """
        :return: Returns URL to CM1 on the SAFA bucket containing definition file.
        """
        return "https://safa-datasets-open.s3.amazonaws.com/datasets/open-source/cm1.zip"
