import re
test='<area shape="rect" coords="9,160,108,182" href="http://store.dangdang.com/282/list.html?sort_type=sort_xsellcount_desc&amp;inner_cat=002820060000" target="_blank" title="励志" alt="励志" ddt-src="http://store.dangdang.com/282/list.html?sort_type=sort_xsellcount_desc&amp;inner_cat=002820060000">'
url=re.findall("href=(.*?)target",test)
print()