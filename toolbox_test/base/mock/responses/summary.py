from toolbox.constants.summary_constants import PROJECT_SUMMARY_TAGS, PS_DATA_FLOW_TITLE, PS_ENTITIES_TITLE, PS_FEATURE_TITLE, \
    PS_NOTES_TAG, PS_OVERVIEW_TITLE, PS_SUBSYSTEM_TITLE, SPECIAL_TAGS_ITEMS
from toolbox.summarize.summary import Summary
from toolbox.util.enum_util import EnumDict
from toolbox.util.prompt_util import PromptUtil

# Move to mock_responses
MOCK_PS_RES_MAP = {
    PS_OVERVIEW_TITLE: "project_overview",
    PS_FEATURE_TITLE: "project_features",
    PS_ENTITIES_TITLE: "project_entities",
    PS_SUBSYSTEM_TITLE: "project_subsytem",
    PS_DATA_FLOW_TITLE: "project_data_flow"
}
TEST_PROJECT_SUMMARY = Summary({title: EnumDict({"chunks": ["summary of project"], "title": title})
                                for title in MOCK_PS_RES_MAP.keys()})


def create(title: str, body_prefix: str = None, tag: str = None, body: str = None, n_items: int = 0):
    if body_prefix is None:
        body_prefix = ""
    tag = PROJECT_SUMMARY_TAGS[title] if not tag else tag
    body = MOCK_PS_RES_MAP.get(title, f"project_{title.lower()}") if not body else body
    if title in SPECIAL_TAGS_ITEMS and n_items == 0:
        r = ""
        for i in range(1, 4):
            item_body_prefix = PromptUtil.create_xml("name", body_prefix if body_prefix else f"name{i}")
            item_body = PromptUtil.create_xml(f"descr", body + str(i))
            r += create(title, item_body_prefix, tag, item_body, n_items=i)
        return r
    else:
        r = ""
        r += PromptUtil.create_xml(PS_NOTES_TAG, "notes")
        r += PromptUtil.create_xml(tag, f"{body_prefix}{body}")
        return r


PROJECT_TITLE_TO_RESPONSE = {title: create(title) for title in MOCK_PS_RES_MAP.keys()}

SECTION_TAG_TO_TILE = {
    v: k for k, v in PROJECT_SUMMARY_TAGS.items()
}
PROJECT_SUMMARY_RESPONSES = [
    PROJECT_TITLE_TO_RESPONSE[PS_FEATURE_TITLE],
    PROJECT_TITLE_TO_RESPONSE[PS_ENTITIES_TITLE],
    PROJECT_TITLE_TO_RESPONSE[PS_SUBSYSTEM_TITLE],
    PROJECT_TITLE_TO_RESPONSE[PS_DATA_FLOW_TITLE],
    PROJECT_TITLE_TO_RESPONSE[PS_OVERVIEW_TITLE]
]
