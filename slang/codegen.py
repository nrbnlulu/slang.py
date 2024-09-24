from minijinja import Environment

template = """

class Translations_{{context.name}}:

"""

tem_env = Environment(templates={"translations": template})
