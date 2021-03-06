import lxml.etree as etree


def get_urls_from_sitemap(sitemap_url):
    """Get all the webpage urls we can reach from a sitemap, whether this is a sitemap XML or a sitemap index XML"""
    sitemap = etree.parse(sitemap_url)
    root_tag = sitemap.getroot().tag

    if root_tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}sitemapindex':
        print('Loading sitemap index %s' % sitemap_url)
        return get_urls_from_loaded_sitemapindex(sitemap)
    elif root_tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset':
        print('Loading sitemap %s' % sitemap_url)
        return get_urls_from_loaded_sitemap(sitemap)
    else:
        print('Unrecognized root tag %s in sitemap from %s. Ignoring' % (root_tag, sitemap_url))


def get_urls_from_loaded_sitemap(sitemap):
    urls = set()
    loc_elems = sitemap.findall('//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
    loc_elems_len = len(loc_elems)
    print('Found %d pages to crawl' % loc_elems_len)
    for loc_elem in loc_elems:
        urls.add(loc_elem.text)

    return urls


def get_urls_from_loaded_sitemapindex(sitemapindex):
    """Get all the webpage urls in a retrieved sitemap index XML"""
    urls = set()
    # for loc_elem in sitemapindex_elem.findall('/sitemap/loc'):
    for loc_elem in sitemapindex.findall('//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
        urls.update(get_urls_from_sitemap(loc_elem.text))

    return urls
