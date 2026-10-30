from django.db import migrations


def create_index(apps, schema_editor):
    # Both supported databases (SQLite/PostgreSQL) support expression/partial indexes.
    # Blank addresses on legacy users remain valid until an email is assigned.
    schema_editor.execute('CREATE UNIQUE INDEX accounts_user_email_ci_unique ON auth_user (LOWER(email)) WHERE email <> \'\'')


def drop_index(apps, schema_editor):
    schema_editor.execute('DROP INDEX accounts_user_email_ci_unique')


class Migration(migrations.Migration):
    dependencies = [('accounts', '0003_profile_growing_place_profile_selected_crops'),
                    ('auth', '0012_alter_user_first_name_max_length')]
    operations = [migrations.RunPython(create_index, drop_index)]
