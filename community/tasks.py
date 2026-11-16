"""Slow community work done in the background (see jobs app)."""
import hashlib

from django.tasks import task

# Languages offered by the post "Translate" button.
TRANSLATE_LANGS = ('hi', 'kn', 'mr')


def _source_hash(post):
    return hashlib.sha256('\n'.join([post.title, post.description, post.tags or '']).encode()).hexdigest()


def get_or_create_translation(post, lang):
    """Saved translation of a post (translated now and saved if missing or outdated)."""
    from .models import PostTranslation
    from .translator import translate_text
    digest = _source_hash(post)
    saved = PostTranslation.objects.filter(post=post, lang=lang, source_hash=digest).first()
    if saved:
        return saved
    fields = {'source_hash': digest,
              'title': translate_text(post.title, lang),
              'description': translate_text(post.description, lang),
              'tags': [translate_text(tag, lang) for tag in post.get_tags()]}
    if fields['title'] == post.title and fields['description'] == post.description:
        # The translation service failed (translate_text falls back to the original text).
        # Never save English as a "translation"; show the original this time.
        return PostTranslation(post=post, lang=lang, **fields)
    translation, _ = PostTranslation.objects.update_or_create(post=post, lang=lang, defaults=fields)
    return translation


class TranslationUnavailable(Exception):
    pass


@task
def translate_post(post_id):
    """Translate a new post into the offered languages ahead of time."""
    from .models import CommunityPost
    post = CommunityPost.objects.filter(pk=post_id).first()
    if post is None:
        return
    for lang in TRANSLATE_LANGS:
        if get_or_create_translation(post, lang).pk is None:
            # Not translated (service down / out of credits): fail so the job queue retries later.
            raise TranslationUnavailable(f'Translation to {lang} failed for post {post_id}')
