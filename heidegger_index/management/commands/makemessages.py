from django.core.management.commands import makemessages
from django.conf import settings


# makemessages command with some default arguments
class Command(makemessages.Command):
    def handle(self, *args, **options):
        locale = options.pop("locale", [])
        ignore_patterns = options.pop("ignore_patterns", [])
        super(Command, self).handle(
            *args,
            **options,
            locale=[*locale, *settings.SUPPORTED_LOCALES],
            ignore_patterns=[*ignore_patterns, *settings.LOCALE_IGNORE_PATTERNS]
        )
