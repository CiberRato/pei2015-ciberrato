from competition.views.simplex import RoundSimplex
from os.path import basename, getsize, getmtime
from hurry.filesize import size
from django.core.files.storage import default_storage


class AgentSimplex:
    def __init__(self, ag):
        self.agent_name = ag.agent_name
        self.user = ag.user
        self.is_local = ag.is_local
        self.language = ag.language
        self.competitions = [cp_agent.competition for cp_agent in ag.competitionagent_set.all()]

        self.rounds = []
        for r in [cp_agent.round for cp_agent in ag.competitionagent_set.all()]:
            self.rounds += [RoundSimplex(r)]

        self.team_name = ag.team.name
        self.validation_result = ag.validation_result
        self.code_valid = ag.code_valid
        self.created_at = ag.created_at
        self.updated_at = ag.updated_at


class AgentFileSimplex:
    def __init__(self, file_obj):
        self.file = basename(file_obj.original_name)
        self.last_modification = getmtime(default_storage.path(file_obj.file))
        self.size = size(getsize(default_storage.path(file_obj.file)))
        self.url = "/api/v1/agents/file/" + file_obj.agent.agent_name + "/" + self.file + "/"