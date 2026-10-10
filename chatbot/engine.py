"""Retrieval-based chatbot (spec §3.1, Option B).

Queries are matched against the curated KnowledgeEntry table, so every answer is
grounded in local data and carries its source. The match score blends:
  * word TF-IDF on Porter-stemmed text (scheme/schemes, grower/growers),
  * character n-gram TF-IDF, which tolerates misspellings (fertizer, yeild),
  * a boost for entries whose intent matches the intent detected in the query,
    so "schemes for rice growers" prefers scheme answers over rice fertilizer ones,
  * a boost for entries about the crop the query names, so "schemes for paddy farmers"
    prefers the paddy-specific entry over the generic schemes list.
"""
import re
from dataclasses import dataclass

from django.db.models import Count, Max
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import KnowledgeEntry

MATCH_THRESHOLD = 0.2
WORD_WEIGHT, CHAR_WEIGHT = 0.6, 0.4
INTENT_BOOST = 0.15
CROP_BOOST = 0.1
# Synonym groups; a question naming a crop prefers entries about that crop over generic ones.
CROP_TERMS = {
    'rice': {'rice', 'paddy', 'dhan'}, 'wheat': {'wheat', 'gehu', 'gehun'}, 'maize': {'maize', 'corn', 'makka'},
    'cotton': {'cotton', 'kapas'}, 'tomato': {'tomato', 'tamatar'}, 'potato': {'potato', 'aloo'},
    'chilli': {'chilli', 'chili', 'mirchi'},
}

INTENT_KEYWORDS = {
    'greeting': ['hello', 'hi', 'hey', 'greetings', 'namaste', 'namaskar', 'namaskara', 'good morning'],
    'market': ['price', 'prices', 'rate', 'rates', 'mandi', 'bhav', 'market'],
    'weather': ['weather', 'rain', 'forecast', 'temperature', 'humidity', 'wind'],
    'fertilizer': ['fertilizer', 'fertiliser', 'urea', 'dap', 'npk', 'manure', 'compost', 'potash'],
    'pest': ['pest', 'insect', 'disease', 'fungus', 'blight', 'spray', 'worm', 'aphid', 'whitefly', 'thrips', 'mite', 'borer', 'leaf spot', 'rot'],
    'scheme': ['scheme', 'subsidy', 'msp', 'pmfby', 'kcc', 'benefit', 'pm-kisan', 'pm kisan', 'insurance', 'loan', 'credit', 'government', 'yojana'],
    'irrigation': ['irrigation', 'water', 'drip', 'sprinkler'],
    'soil': ['soil', 'ph', 'health card', 'nutrient'],
    'crop_selection': ['which crop', 'what crop', 'grow', 'sow', 'season', 'kharif', 'rabi', 'variety'],
}

GREETING_REPLY = (
    'Namaste! I can help with crop selection, fertilizers, pests and diseases, irrigation, '
    'soil health and government schemes. What would you like to know?'
)
FALLBACK_REPLY = (
    "Sorry, I don't have a reliable answer for that yet. Please try rephrasing, or contact the "
    'Kisan Call Centre (toll-free 1800-180-1551) for expert advice.'
)


@dataclass
class BotReply:
    text: str
    intent: str
    confidence: float = 0.0
    entry: KnowledgeEntry | None = None

    def as_dict(self):
        return {
            'reply': self.text,
            'intent': self.intent,
            'confidence': round(self.confidence, 3),
            'source': self.entry.source if self.entry else None,
            'source_url': (self.entry.source_url or None) if self.entry else None,
        }


_stemmer = PorterStemmer()


def normalize(text):
    return re.sub(r'[^a-z0-9\s-]', ' ', text.lower()).strip()


def stem_text(text):
    return ' '.join(_stemmer.stem(w) for w in normalize(text).split() if w not in ENGLISH_STOP_WORDS)


def crops_in(text):
    words = set(normalize(text).split())
    return {crop for crop, terms in CROP_TERMS.items() if words & terms}


def detect_intent(text):
    text = f' {normalize(text)} '
    scores = {
        intent: sum(1 for kw in kws if f' {kw} ' in text or (len(kw) > 4 and kw in text))
        for intent, kws in INTENT_KEYWORDS.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] else 'general'


class _Index:
    """TF-IDF index over active knowledge entries, rebuilt when the table changes."""

    def __init__(self):
        self.version = None
        self.entries = []
        self.entry_crops = []
        self.word_vec = self.char_vec = None
        self.word_matrix = self.char_matrix = None

    def _current_version(self, qs):
        agg = qs.aggregate(n=Count('id'), last=Max('updated_at'))
        return (agg['n'], agg['last'])

    def get(self):
        qs = KnowledgeEntry.objects.filter(is_active=True)
        version = self._current_version(qs)
        if version != self.version:
            self.entries = list(qs)
            self.entry_crops = [crops_in(f'{e.question} {e.keywords}') for e in self.entries]
            docs = [normalize(f'{e.question} {e.question} {e.keywords}') for e in self.entries]
            if docs:
                self.word_vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True,
                                                preprocessor=stem_text)
                self.word_matrix = self.word_vec.fit_transform(docs)
                self.char_vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), sublinear_tf=True)
                self.char_matrix = self.char_vec.fit_transform(docs)
            self.version = version
        return self

    def scores(self, message, intent):
        text = normalize(message)
        word = cosine_similarity(self.word_vec.transform([text]), self.word_matrix)[0]
        char = cosine_similarity(self.char_vec.transform([text]), self.char_matrix)[0]
        scores = WORD_WEIGHT * word + CHAR_WEIGHT * char
        if intent != 'general':
            scores += [INTENT_BOOST if e.intent == intent else 0 for e in self.entries]
        if crops := crops_in(message):
            scores += [CROP_BOOST if crops & self.entry_crops[i] else 0 for i in range(len(self.entries))]
        return scores


_index = _Index()


def answer(message):
    message = (message or '').strip()
    if not message:
        return BotReply(FALLBACK_REPLY, 'general')

    intent = detect_intent(message)
    if intent == 'greeting' and len(message.split()) <= 4:
        return BotReply(GREETING_REPLY, 'greeting', 1.0)
    if intent == 'weather':
        return BotReply(
            'For a localized 5-day forecast and farm advisory, open the Weather page from the menu '
            '(it uses the location in your profile).',
            'weather', 1.0,
        )

    if intent == 'market' and not re.search(r'\b(sell|online|enam|e-nam)\b', normalize(message)):
        return BotReply(
            'Open the Market Prices page from the menu to see the latest published mandi prices for major crops '
            'in your state, with green/red arrows showing the change from the previous day.',
            'market', 1.0,
        )

    index = _index.get()
    if not index.entries:
        return BotReply(FALLBACK_REPLY, intent)

    sims = index.scores(message, intent)
    best = int(sims.argmax())
    score = min(float(sims[best]), 1.0)
    if score < MATCH_THRESHOLD:
        return BotReply(FALLBACK_REPLY, intent, score)

    entry = index.entries[best]
    return BotReply(entry.answer, entry.intent, score, entry)
