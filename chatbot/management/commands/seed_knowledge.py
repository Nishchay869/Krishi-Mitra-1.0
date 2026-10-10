import json

from django.conf import settings
from django.core.management.base import BaseCommand

from chatbot.models import KnowledgeEntry


class Command(BaseCommand):
    help = 'Load curated agricultural FAQs into the chatbot knowledge base (idempotent).'

    def add_arguments(self, parser):
        parser.add_argument('--file', default=str(settings.BASE_DIR / 'data' / 'knowledge_base.json'))

    def handle(self, *args, **opts):
        with open(opts['file'], encoding='utf-8') as fh:
            items = json.load(fh)
        created = 0
        for item in items:
            _, was_created = KnowledgeEntry.objects.update_or_create(
                question=item['question'],
                defaults={k: v for k, v in item.items() if k != 'question'},
            )
            created += was_created
        self.stdout.write(self.style.SUCCESS(f'{len(items)} entries loaded ({created} new).'))
