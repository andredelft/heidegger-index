from django.core.management.commands import compilemessages
from django.conf import settings


# compilemessages command with some default arguments
class Command(compilemessages.Command):
    def handle(self, *args, **options):
        locale = options.pop("locale", [])
        super(Command, self).handle(
            *args, **options, locale=[*locale, *settings.SUPPORTED_LOCALES]
        )
