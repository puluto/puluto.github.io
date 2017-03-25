#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

AUTHOR = u'Puluto'
SITENAME = u'Thinking'
SITEURL = 'http://puluto.github.io'
SITETITLE = AUTHOR

TIMEZONE = 'Asia/Shanghai'
DEFAULT_DATE_FORMAT = '%Y-%m-%d(%a)'
DEFAULT_DATE = 'fs'
DEFAULT_LANG = 'zh'
THEME = 'flex'
PYGMENTS_STYLE = 'monokai'
# DISQUS_SITENAME = ""
GOOGLE_ANALYTICS = "UA-63906522-1"

PATH = 'content'
LINKS = (('Pelican', 'http://getpelican.com/'),
	)
SOCIAL = (('GITHUB', 'https://github.com/puluto'),
          ('微博', 'http://weibo.com/u/1871671127'),)

DEFAULT_PAGINATION = 8

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = False

STATIC_PATHS = [
    'extra/CNAME',
    'images'
    ]
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}

SITESUBTITLE='更新很慢的博客，关于自己研究的一些东西'
# SITEDESCRIPTION = '%s\'s Thoughts and Writings' % AUTHOR
# SITELOGO = '//s.gravatar.com/avatar/5dc5ba59a94eeab2106ad9d397361b2c?s=120'
# FAVICON = '/images/favicon.ico'
# BROWSER_COLOR = '#333333'
# ROBOTS = 'index, follow'
I18N_TEMPLATES_LANG = 'zh'
# OG_LOCALE = 'en_US'
# LOCALE = 'en_US'

#DATE_FORMATS = {
#    'en': '%B %d, %Y',
#}

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

USE_FOLDER_AS_CATEGORY = False
MAIN_MENU = True
HOME_HIDE_TAGS = True

MENUITEMS = (('Archives', '/archives.html'),
             ('Categories', '/categories.html'),
             ('Tags', '/tags.html'),)

CC_LICENSE = {
    'name': 'Creative Commons Attribution-ShareAlike',
    'version': '4.0',
    'slug': 'by-sa'
}

COPYRIGHT_YEAR = 2016

PLUGIN_PATHS = ['../pelican-plugins']
PLUGINS = ['sitemap', 'post_stats', 'i18n_subsites']

JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.6,
        'indexes': 0.6,
        'pages': 0.5,
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly',
    }
}

CUSTOM_CSS = 'static/custom.css'

USE_LESS = False
