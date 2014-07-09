# -*- encoding: utf-8 -*-
#
# This decadent code is a tribute to the "good" old PHP times of doing
# everything yourself in one file. Enjoy!
#

import util
import core


CSS = """div.release, div.repo, div.branches { padding: 0; margin: 9px 30px; }
h2.package, h3.release, h4.repo { margin: 0; padding: 0.3em 0 0.2em 8px; }

div.package { margin-bottom: 3em; }
h2.package { font-size: 36px; color: #034769; padding-left: 0px; }

div.release { margin-bottom: 1em; }
h3.release { font-size: 24px; color: #086FA1; }

h4.repo { font-size: 18px; color: #04819E; }

code { font-weight: normal }

table.branches { margin-left: 30px; }
table.branches td { padding: 0 0.5em 0.2em; vertical-align: top; }
table.branches td.branch { font-weight: bold; text-align: right; }
table.branches td.version { font-weight: bold; padding-left: 0.4em; }

.ver-old, .ver-unknown { color: #CC9900; }
.ver-new { color: #336633; }
.ver-error { color: #A60000; }
.ver-sep { color: #9A9A9A; font-weight: normal; }
.ver-extra { color: #444444; font-weight: normal; }
"""


PAGE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<title>%(title)s</title>
<style type="text/css">
body { padding: 0; margin: 0; }

%(css)s
</style>
</head>

<body>
%(body)s
</body>
</html>
"""


def render_version_html(ver, max_ver=None, show_error=False):
    s = ''
    if 'version' in ver:
        if 'epoch' in ver:
            s += ('<span class="ver-epoch ver-extra">%s</span>'
                  '<span class="ver-sep">:</span>' % ver['epoch'])
        v = ver['version']
        if max_ver and v == max_ver:
            s += '<span class="ver-new">%s</span>' % v
        else:
            s += '<span class="ver-old">%s</span>' % v
        if 'release' in ver:
            s += ('<span class="ver-sep">-</span>'
                  '<span class="ver-release ver-extra">%s</span>'
                  % ver['release'])
    else:
        if show_error:
            try:
                err_msg = ver['error']
            except KeyError:
                err_msg = ("BUG: No version fetched but fetcher didn't return "
                           "error. Fetcher bug!")
        else:
            err_msg = '!!'
        s += '<span class="ver-error">%s</span>' % err_msg
    if 'next' in ver:
        next_ver = ver['next']
        if not util.is_same_version(ver, next_ver):
            s += ' &nbsp; &rarr; &nbsp; ' + \
                 render_version_html(next_ver, max_ver)
    return s


def render_versions_html(pkg_conf, vers, repo_links=True, show_commands=False):
    first = True
    pkgs = pkg_conf['packages']
    html = "<div class='versions'>\n"
    for pkg in pkgs:
        rlss = pkg['releases']
        pkg_name = pkg['name']
        if first:
            first = False
        else:
            html += "\n"
        html += ("<div class=\"package\" id=\"pkg-%s\"><h2 class=\"package\">"
                 "%s</h2>\n" % (pkg_name, pkg_name))
        for rls in rlss:
            html += "<div class=\"release\"><h3 class=\"release\">%s</h3>\n" \
                    % rls['name']
            max_ver = util.release_latest_version(rls, vers, pkg_name)
            # print all release versions
            for repo in rls['repos']:
                tags = core.repo_tags(repo, pkg_conf)
                repo_name = repo['repo']
                repo_title = util.get_repo_title(pkg_conf, repo_name)
                if repo_links:
                    repo_link = util.get_repo_link(pkg_conf, repo_name)
                    if repo_link:
                        repo_title += " <a href=\"%s\">&rarr;</a>" % repo_link
                cls = ["repo"] + map(lambda x: "repo-%s" % x, tags)
                html += "<div class=\"%s\">\n<h4 class=\"repo\">%s</h4>\n" \
                        % (" ".join(cls), repo_title)
                html += "<table class=\"branches\">\n"
                for branch in repo['branches']:
                    try:
                        ver = vers[pkg_name][repo_name][branch]
                        ver_str = render_version_html(ver, max_ver)
                        if show_commands and 'cmd' in ver:
                            ver_str += '<br><code>$ %s</code>' % ver['cmd']
                    except KeyError:
                        ver_str = '<span class="ver-unknown">??</span>'
                    html += ("<tr><td class=\"branch\">%s:</td>"
                             "<td class=\"version\">%s</td></tr>\n"
                             % (branch, ver_str))
                html += "</table>\n</div>\n"
            html += "</div>\n"
        html += "</div>\n"
    html += "</div>\n"
    return html


def render_versions_html_page(pkg_conf, vers, title="verwatch versions",
                              css=None):
    if css:
        _css = "%s\n%s" % (css, CSS)
    else:
        _css = CSS
    page = PAGE_TEMPLATE % {
        'css': _css,
        'body': render_versions_html(pkg_conf, vers),
        'title': title
    }
    return page
