from jinja2 import Template, Environment, FileSystemLoader
import html_css
import pkgutil

def render_template(path_template, output=None, filters={}, **kw):

    # print('Jinja rendered received template path:',path_template)

    template_str = html_css.html

    '''
    try:
        template_str = open('res/template.html','r+',encoding='UTF-8').read()

    except FileNotFoundError:
        print('No file found at res/template.html')
        print('Trying to access res with pkgutil')
        template_binarystr = pkgutil.get_data('res','template.html')
        if template_binarystr:
            print('Template fetched from resource')
            template_str = template_binarystr.decode('UTF-8','ignore')
            print('Length of decoded template:',len(template_str),template_str[:20])
        else:
            template_str = open('template.html','r+').read()
    '''
    env = Environment()
    for key,value in filters.items():
        env.filters[key] = value

    template = env.from_string(template_str)
    return template.render(**kw)

    ################

    env = Environment(loader=FileSystemLoader('./'))

    for key,value in filters.items():
        env.filters[key] = value
    
    template = env.get_template('template.html')
    rendered_html = template.render(**kw)

    if output is not None:
        with open(output, 'w+', encoding='UTF-8') as file:
            file.write(rendered_html)

    return rendered_html
