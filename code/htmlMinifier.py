import htmlmin

html_file = '../results/digitalAtlas.html'
HtmlFile = open(html_file, 'r', encoding='utf-8')
source_code = HtmlFile.read()

minified = htmlmin.minify(source_code, remove_comments=True)

output_file = html_file.replace('.html', '_minified.html')
Html_file = open(output_file, 'w')
Html_file.write(minified)
Html_file.close()
