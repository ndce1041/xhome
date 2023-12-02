import template as tp


template = tp.Template("{{ title }}",{"title":"登录"}).render()


print(template)