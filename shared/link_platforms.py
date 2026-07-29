# Platforms a user may only link once. Anything else (e.g. "website") can be
# added any number of times.
SINGLE_INSTANCE_LINK_PLATFORMS = {'github', 'linkedin', 'facebook'}

# Domains a link must belong to for these platforms — prevents e.g. a random
# URL being saved under "github". No restriction for "website".
PLATFORM_DOMAINS = {
    'github': ('github.com',),
    'linkedin': ('linkedin.com',),
    'facebook': ('facebook.com', 'fb.com'),
}
