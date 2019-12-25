# [html2md](https://github.com/steve-hao/html2md)

html2md is a Python script that converts HTML from clipboard/File/URL into Markdown code  (default use GFM and surpport extend syntax).

``` 
Usage: html2md.py [-h] [-e] [-i] [-l] [-f] [-d] [-t] [-s] [-a] [-D] [-E]
                  [-o OUTPUT_FILE ]
                  [in_file]

Transform HTML to Markdown

positional arguments:
  in_file

optional arguments:
  -h, --help            show this help message and exit
  -e, --ignore-emphasis
                        not include any formatting for emphasis, default is False 
  -i, --ignore-images   not include any formatting for images, default is False 
  -l, --ignore-links    not include any formatting for links, default is False
  -d, --def_list        Disable conversion of definition lists, default is True
  -t, --table           Disable conversion of table, default is True
  -s, --strikethrough   Disable strike-through text, default is True
  -a, --attrs           Enable element attributes in the link, default is False
  -D, --dash-unordered-list
                        use a dash rather than a star for unordered list items, default is False
  -E, --asterisk-emphasis
                        use an asterisk rather than an underscore for emphasized text , default is False
  -o OUTPUT_FILE , --output_file OUTPUT_FILE 
                        give output filename ,default is out to clipbord
```
On default, this script will monitor syste clipboard,  when it find the HTML contents has been changed (not text contents in clipboard) ,it will convert and place Markdown Text into clipboard Text buffer. Then you can directly paste the Markdown code into any Editor

You can simply press Ctrl+C and Ctrl+V ,then the transformation work automaticlly. 

Of cause, you can make an URL or HTML file as input, and make a file as output.

You can use it from within Python:

``` 
from html2hd import html2hd
markdown = html2md("<p>Hello, world.</p>")

the method call as html2md(html, **kwargs)

kwargs:

    'ignore_emphasis': False,   
    'ignore_images': False, 
    'ignore_links': False,
    'def_list': True,   
    'table': True, 
    'strikethrough': True, 
    'attrs': False, 
    'ul_style_dash': False, 
    'em_style_asterisk': False, 
```

_html2md was inspired by Aaron Swartz's [html2text](https://github.com/aaronsw/html2text) and al3xandru's [htm2md](https://github.com/al3xandru/html2md)_