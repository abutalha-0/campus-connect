from django.core.exceptions import ValidationError

# Each category's required keys inside Post.details.
# Add a new category here (and in Category seed data) without touching models.py.
CATEGORY_DETAIL_SCHEMAS = {
    'study-partner': {
        'required': ['course_code', 'course_title', 'topic'],
        'optional': ['session_time'],
    },
    'contest-team': {
        'required': ['contest_name', 'tech_stack'],
        'optional': ['required_skills_note'],
    },
    'travel-mate': {
        'required': ['destination', 'travel_date', 'budget'],
        'optional': ['meeting_place'],
    },
}


def validate_post_details(category_slug, details):
    """Validate that Post.details contains the required keys for its category.

    Unknown category slugs are allowed through untouched so new categories
    can be added via the admin/Category table before a schema exists for them.
    """
    schema = CATEGORY_DETAIL_SCHEMAS.get(category_slug)
    if schema is None:
        return

    if not isinstance(details, dict):
        raise ValidationError('Post details must be a JSON object.')

    missing = [key for key in schema['required'] if not details.get(key)]
    if missing:
        raise ValidationError(
            f"Missing required detail fields for '{category_slug}': {', '.join(missing)}"
        )
