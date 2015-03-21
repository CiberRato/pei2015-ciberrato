from competition.views.simplex import RoundSimplex


class AgentSimplex:
    def __init__(self, ag):
        self.agent_name = ag.agent_name
        self.user = ag.user
        self.is_virtual = ag.is_virtual
        self.language = ag.language
        self.competitions = [cp_agent.competition for cp_agent in ag.competitionagent_set.all()]

        self.rounds = []
        for r in [cp_agent.round for cp_agent in ag.competitionagent_set.all()]:
            self.rounds += [RoundSimplex(r)]

        self.group_name = ag.group.name
        self.created_at = ag.created_at
        self.updated_at = ag.updated_at