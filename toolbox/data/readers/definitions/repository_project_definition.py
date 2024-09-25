from typing import Dict

from toolbox.data.keys.structure_keys import StructuredKeys
from toolbox.data.readers.definitions.abstract_project_definition import AbstractProjectDefinition
from toolbox.data.readers.definitions.tim_project_definition import TimProjectDefinition


class RepositoryProjectDefinition(AbstractProjectDefinition):
    """
    Reads project extracted from GitHub repository.
    """

    @staticmethod
    def read_project_definition(_: str) -> Dict:
        """
        Creates definition for reading GitHub repository composed of commit and issues.
        :return: Project definition for repository.
        """
        return {
            StructuredKeys.ARTIFACTS: {
                "Commit": {
                    StructuredKeys.PATH: "commit.csv",
                    StructuredKeys.COLS: StructuredKeys.ARTIFACTS
                },
                "Issue": {
                    StructuredKeys.PATH: "issue.csv",
                    StructuredKeys.COLS: StructuredKeys.ARTIFACTS
                }
            },
            StructuredKeys.TRACES: {
                "commit2issue": {
                    StructuredKeys.Trace.SOURCE.value: "Commit",
                    StructuredKeys.Trace.TARGET.value: "Issue",
                    StructuredKeys.PATH: "commit2issue.csv",
                    StructuredKeys.COLS: StructuredKeys.TRACES
                }
            },
            StructuredKeys.CONVERSIONS: {
                **TimProjectDefinition.CONVERSIONS[TimProjectDefinition.CSV]
            }
        }
