from canonicalwebteam.django_views import TemplateFinder


class MaasTemplateFinder(TemplateFinder):
    def get_context_data(self, **kwargs):
        """
        Get context data fromt the database for the given page
        """

        # Get any existing context
        context = super(MaasTemplateFinder, self).get_context_data(**kwargs)

        # Add level_* context variables
        clean_path = self.request.path.strip("/")
        for index, path in enumerate(clean_path.split("/")):
            context["level_" + str(index + 1)] = path

        return context
