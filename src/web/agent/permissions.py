from ciberonline.exceptions import BadRequest, Forbidden


class AgentMustHaveValidCode:
    def __init__(self, agent, message='The agent must have the code valid!'):
        if not agent.code_valid:
            raise BadRequest(message)