import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from chatbot.models import KnowledgeEntry


class Command(BaseCommand):
    help = 'Load curated agricultural FAQs and official Package of Practices (CIARI, TNAU, UAS Dharwad, MANAGE) into chatbot knowledge base.'

    def add_arguments(self, parser):
        parser.add_argument('--file', default=None, help='Explicit file to load')

    def handle(self, *args, **opts):
        files_to_load = []
        if opts['file']:
            files_to_load.append(opts['file'])
        else:
            default_files = [
                'knowledge_base.json',
                'ciari_rag_knowledge.json',
                'cpg2012_rag_knowledge.json',
                'horticulture_rag_knowledge.json',
                'uas_dharwad_rag_knowledge.json',
                'farmerbook_rag_knowledge.json',
            ]
            for fname in default_files:
                fpath = os.path.join(settings.BASE_DIR, 'data', fname)
                if os.path.exists(fpath):
                    files_to_load.append(fpath)

        total_loaded = 0
        total_created = 0

        for filepath in files_to_load:
            with open(filepath, encoding='utf-8') as fh:
                items = json.load(fh)
            for item in items:
                # Handle keywords list or string
                kw_val = item.get('keywords', '')
                if isinstance(kw_val, list):
                    kw_str = ', '.join(str(k) for k in kw_val)
                else:
                    kw_str = str(kw_val or '')

                source_str = item.get('source', 'Krishi Mitra Verified Guide')[:255]

                # Map fields to KnowledgeEntry model
                defaults = {
                    'answer': item.get('answer', ''),
                    'intent': item.get('topic') or item.get('intent') or 'general',
                    'keywords': kw_str[:255],
                    'source': source_str,
                    'source_url': item.get('source_url', '')[:200],
                    'language': item.get('language', 'en'),
                    'is_active': True,
                }
                # Ensure intent fits choices
                valid_intents = {'crop_selection', 'fertilizer', 'pest', 'scheme', 'irrigation', 'soil', 'general'}
                if defaults['intent'] not in valid_intents:
                    intent_low = defaults['intent'].lower()
                    if any(k in intent_low for k in ['pest', 'disease', 'protection']):
                        defaults['intent'] = 'pest'
                    elif any(k in intent_low for k in ['fertilizer', 'nutrient', 'organic', 'biostimulant']):
                        defaults['intent'] = 'fertilizer'
                    elif any(k in intent_low for k in ['variety', 'season', 'intercrop', 'sowing', 'propagation']):
                        defaults['intent'] = 'crop_selection'
                    elif 'irrigation' in intent_low or 'water' in intent_low:
                        defaults['intent'] = 'irrigation'
                    elif 'soil' in intent_low:
                        defaults['intent'] = 'soil'
                    else:
                        defaults['intent'] = 'general'

                _, was_created = KnowledgeEntry.objects.update_or_create(
                    question=item['question'],
                    source=source_str,
                    defaults=defaults,
                )
                total_created += was_created
                total_loaded += 1

        self.stdout.write(self.style.SUCCESS(f'{total_loaded} entries loaded ({total_created} new).'))
