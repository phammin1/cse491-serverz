import os
import jinja2

template_dir = './templates'
loader = None
env = None

def init_templates():
    global loader, env

    # calculate the location of the templates directory relative to the
    # directory this file is in
    dirname = os.path.dirname(__file__)
    t_dir = os.path.join(dirname, template_dir)
    t_dir = os.path.abspath(t_dir)

    print 'loading templates from:', t_dir

    loader = jinja2.FileSystemLoader(t_dir)
    env = jinja2.Environment(loader=loader)

def render(template_name, values={}):
    template = env.get_template(template_name)
    return template.render(values)
