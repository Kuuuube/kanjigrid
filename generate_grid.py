from functools import reduce
import urllib.parse
import re

from . import util, data

def generate(mw, config, units, export = False):
    def kanjitile(char, bgcolor, count = 0, avg_interval = 0):
        tile = ""
        color = "#000"

        context_menu_events = f" onmouseenter=\"bridgeCommand('h:{char}');\" onmouseleave=\"bridgeCommand('l:{char}');\"" if not export else ""

        if config.tooltips:
            tooltip = "Character: %s" % util.safe_unicodedata_name(char)
            if avg_interval:
                tooltip += " | Avg Interval: " + str("{:.2f}".format(avg_interval)) + " | Score: " + str("{:.2f}".format(util.scoreAdjust(avg_interval / config.interval)))
            tile += "\t<div class=\"grid-item\" style=\"background:%s;\" title=\"%s\"%s>" % (bgcolor, tooltip, context_menu_events)
        else:
            tile += "\t<div style=\"background:%s;\"%s>" % (bgcolor, context_menu_events)

        if config.copyonclick:
            tile += "<a style=\"color:" + color + ";cursor: pointer;\">" + char + "</a>"
        elif config.browseonclick and not export:
            tile += "<a href=\"" + util.get_browse_command(char) + "\" style=\"color:" + color + ";\">" + char + "</a>"
        else:
            tile += "<a href=\"" + util.get_search(config, char) + "\" style=\"color:" + color + ";\">" + char + "</a>"

        tile += "</div>\n"

        return tile

    deckname = "*"
    if config.did != "*":
        deckname = mw.col.decks.name(config.did).rsplit('::', 1)[-1]

    result_html  = "<!doctype html><html lang=\"%s\"><head><meta charset=\"UTF-8\" /><title>Anki Kanji Grid</title>" % config.lang
    result_html += "<style type=\"text/css\">body{text-align:center;}.grid-container{display:grid;grid-gap:2px;grid-template-columns:repeat(auto-fit,23px);justify-content:center;" + util.get_font_css(config) + "}.key{display:inline-block;width:3em}a,a:visited{color:#000;text-decoration:none;}</style>"
    result_html += "</head>\n"
    if config.copyonclick:
        result_html += "<script>function copyText(text) {const range = document.createRange();const tempElem = document.createElement('div');tempElem.textContent = text;document.body.appendChild(tempElem);range.selectNode(tempElem);const selection = window.getSelection();selection.removeAllRanges();selection.addRange(range);document.execCommand('copy');document.body.removeChild(tempElem);}document.addEventListener('click', function(e) {e.preventDefault();if (e.srcElement.tagName == 'A') {copyText(e.srcElement.textContent);}}, false);</script>"
    result_html += "<body>\n"
    result_html += "<div style=\"font-size: 3em;color: #888;\">Kanji Grid - %s</div>\n" % deckname
    result_html += "<p style=\"text-align: center\">Key</p>"
    result_html += "<p style=\"text-align: center\">Weak&nbsp;"
    # keycolors = (hsvrgbstr(n/6.0) for n in range(6+1))
    for c in [n/6.0 for n in range(6+1)]:
        result_html += "<span class=\"key\" style=\"background-color: %s;\">&nbsp;</span>" % util.hsvrgbstr(c/2)
    result_html += "&nbsp;Strong</p></div>\n"
    result_html += "<hr style=\"border-style: dashed;border-color: #666;width: 100%;\">\n"
    result_html += "<div style=\"text-align: center;\">\n"

    unitsList = {
        util.SortOrder.NONE:      sorted(units.values(), key=lambda unit: (unit.idx, unit.count)),
        util.SortOrder.UNICODE:   sorted(units.values(), key=lambda unit: (util.safe_unicodedata_name(unit.value), unit.count)),
        util.SortOrder.SCORE:     sorted(units.values(), key=lambda unit: (util.scoreAdjust(unit.avg_interval / config.interval), unit.count), reverse=True),
        util.SortOrder.FREQUENCY: sorted(units.values(), key=lambda unit: (unit.count, util.scoreAdjust(unit.avg_interval / config.interval)), reverse=True),
    }[util.SortOrder(config.sortby)]

    if config.groupby > 0:
        groups = data.groups[config.groupby - 1]
        kanji = [u.value for u in unitsList]
        for i in range(1, len(groups.data)):
            result_html += "<h2 style=\"color:#888;\">%s Kanji</h2>\n" % groups.data[i][0]
            table = "<div class=\"grid-container\">\n"
            count_found = 0
            count_known = 0

            sorted_units = []
            if config.sortby == 0:
                sorted_units = [units[c] for c in groups.data[i][1] if c in kanji]
            else:
                sorted_units = [units[c] for c in kanji if c in groups.data[i][1]]

            for unit in sorted_units:
                if unit.count != 0 or config.unseen:
                    count_found += 1
                    bgcolor = util.get_background_color(unit.avg_interval, config.interval, unit.count, missing = False)
                    if unit.count != 0 or bgcolor not in ["#E62E2E", "#FFF"]:
                        count_known += 1
                    table += kanjitile(unit.value, bgcolor, count_found, unit.avg_interval)
            table += "</div>\n"
            total_count = len(groups.data[i][1])
            if config.unseen:
                unseen_kanji = []
                count = 0
                for char in [c for c in groups.data[i][1] if c not in kanji]:
                    count += 1
                    bgcolor = "#EEE"
                    unseen_kanji.append(kanjitile(char, bgcolor))
                if count != 0:
                    table += "<details><summary>Missing kanji</summary><div class=\"grid-container\">\n"
                    for element in unseen_kanji:
                        table += element
                table += "</div></details>\n"
            result_html += "<h4 style=\"color:#888;\">" + str(count_found) + " of " + str(total_count) + " Found - " + "{:.2f}".format(round(count_found / (total_count if total_count > 0 else 1) * 100, 2)) + "%, " + str(count_known) + " of " + str(total_count) + " Known - " + "{:.2f}".format(round(count_known / (total_count if total_count > 0 else 1) * 100, 2)) + "%</h4>\n"
            result_html += table

        chars = reduce(lambda x, y: x+y, dict(groups.data).values())
        result_html += "<h2 style=\"color:#888;\">" + str(groups.data[0][0]) + "</h2>" #label for "not in group" groups
        table = "<div class=\"grid-container\">\n"
        total_count = 0
        count_known = 0
        for unit in [u for u in unitsList if u.value not in chars]:
            if unit.count != 0 or config.unseen:
                total_count += 1
                bgcolor = util.get_background_color(unit.avg_interval, config.interval, unit.count, missing = False)
                if unit.count != 0 or bgcolor not in ["#E62E2E", "#FFF"]:
                    count_known += 1
                table += kanjitile(unit.value, bgcolor, total_count, unit.avg_interval)
        table += "</div>\n"
        result_html += "<h4 style=\"color:#888;\">" + str(count_known) + " of " + str(total_count) + " Known - " + "{:.2f}".format(round(count_known / (total_count if total_count > 0 else 1) * 100, 2)) + "%</h4>\n"
        result_html += table
        result_html += "<style type=\"text/css\">.datasource{font-style:italic;font-size:0.75em;margin-top:1em;overflow-wrap:break-word;}.datasource a{color:#1034A6;}</style><span class=\"datasource\">Data source: " + ' '.join("<a href=\"{}\">{}</a>".format(w, urllib.parse.unquote(w)) if re.match("https?://", w) else w for w in groups.source.split(' ')) + "</span>"
    else:
        table = "<div class=\"grid-container\">\n"
        total_count = 0
        count_known = 0
        for unit in unitsList:
            if unit.count != 0 or config.unseen:
                total_count += 1
                bgcolor = util.get_background_color(unit.avg_interval,config.interval, unit.count)
                if unit.count != 0 or bgcolor not in ["#E62E2E", "#FFF"]:
                    count_known += 1
                table += kanjitile(unit.value, bgcolor, total_count, unit.avg_interval)
        table += "</div>\n"
        if total_count != 0:
            result_html += "<h4 style=\"color:#888;\">" + str(count_known) + " of " + str(total_count) + " Known - " + "{:.2f}".format(round(count_known / (total_count if total_count > 0 else 1) * 100, 2)) + "%</h4>\n"
        else:
            result_html += "<h4 style=\"color:#888;\">" + str(count_known) + " of " + str(total_count) + " Known - 0%</h4>\n"
        result_html += table
    result_html += "</div></body></html>\n"
    return result_html
