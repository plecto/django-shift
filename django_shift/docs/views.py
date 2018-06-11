from django.views.generic import TemplateView


class DocumentationRoot(TemplateView):
    template_name = 'django_shift/docs/docs_root.html'
    router = None

    def get_context_data(self, **kwargs):
        ctx = super(DocumentationRoot, self).get_context_data(**kwargs)

        # Apparently templates does not work when passing raw classes, so we're making an instance for now
        ctx.update({
            'resources': [resource for resource in [cls(self.request) for cls in self.router.get_objects()]],
            'changelog': [[
                version, changelogs
            ] for version, changelogs in self.router.versions.items()]
        })
        return ctx