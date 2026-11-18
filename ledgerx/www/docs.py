no_cache = 1
sitemap = 0


def get_context(context):
	from ledgerx import __version__

	context.ledgerx_version = __version__
	context.no_header = 1
	context.show_sidebar = 0
