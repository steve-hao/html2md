from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication

from bs4 import Tag, NavigableString,  Comment, BeautifulSoup 

import argparse
import os

import urllib.request

def html2md(html, **options):
    """Simple API"""
    proc = Processor(html,
                     **options)
    return proc.get_output()

_process_tag = ['a', 'b', 'strong', 'blockquote', 'br', 'center', 'code', 'dl', 'dt', 'dd', 'div', 'em', 'i','cite',
                   'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'img', 'li', 'ol', 'ul', 'p', 'pre', 'tt','table','s','del']
_ignore_tag = ['html','body', 'article', 'aside', 'footer', 'header', 'main', 'section', 'span','figure','dfn']  #该标签被忽略
_skip_tag = ['head', 'nav', 'menu', 'menuitem','script'] #标签所包含内容完全抛弃

LF = os.linesep

class Processor(object):
    def __init__(self, html, **kwargs):
        """
        Supported options:
        attrs:
        footnotes:
        """
        self.html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        ### self._clear_soup()


        self._processed = False
        self._options = {
            'ignore_emphasis': False,   
            'ignore_images': False, 
            'ignore_links': False,
            'ignore_footnotes':False, 
            'def_list': True,   
            'table': True, 
            'strikethrough': True, 
            'attrs': False, 
            'ul_style_dash': False, 
            'em_style_asterisk': False, 

        }
        self._options.update(kwargs)
    
        if self._options['ignore_emphasis']:
            self.removeAttrs(_process_tag,'b','strong','i','em','cite')
            _ignore_tag.extend(['b','strong','i','em','cite'])
        else:
            if self._options['strikethrough']:
                _process_tag.extend(['s','del'])

        if self._options['ignore_images']:
            self.removeAttrs(_process_tag,'img')
            _ignore_tag.extend(['img'])
 
        if self._options['ignore_links']:
            self.removeAttrs(_process_tag,'a')
            _ignore_tag.extend(['a'])
 
        if not self._options['def_list']:
            self.removeAttrs(_process_tag,'dl','dt','dd')
 
        if not self._options['table']:
            self.removeAttrs(_process_tag,'table')
 
        self.ul_item_mark = '-' if self._options['ul_style_dash'] else '*'
        self.emphasis_mark = '*' if self._options['em_style_asterisk'] else '_'
        self.strong_mark = '__' if self._options['em_style_asterisk'] else '**'

    '''
    def _clear_soup(self):
        for tag in self.soup(lambda t: isinstance(t, Comment)):
            tag.decompose()
        for ele in _skip_tag:
            for tag in self.soup(ele):
                tag.decompose()
        for ele in _ignore_tag:
            for tag in self.soup(ele):
                tag.unwrap()
    ''' 
    def get_output(self):
        
        mdtxt=self._process(self.soup)
        

        return mdtxt.strip()

    def _process(self, element):

        if isinstance(element,Comment):
            return ''

        if isinstance(element, NavigableString):
            mdtxt=''
            if element.strip(' \t\n\r'):  
                mdtxt = str(element).replace('>','&gt;').replace('<','&lt;').replace(u'\xa0', u'&nbsp;')
            return mdtxt

        mdtxtlist = []
        lastendLF=0
        for t in element.contents:  # 否则则对子元素进行遍历处理
            mdtxt = self._process_tag(t) if isinstance(t, Tag) else self._process(t)
            if mdtxt:
                if  mdtxt.startswith(LF*2):
                    mdtxt=mdtxt[len(LF)*lastendLF:]
                else:
                    if mdtxt.startswith(LF) and lastendLF == 2:
                        mdtxt=mdtxt[len(LF):]
                mdtxtlist.append(mdtxt)
                if mdtxt.endswith(LF*2):
                    lastendLF = 2
                else:
                    if mdtxt.endswith(LF):
                        lastendLF = 1
                    else:
                        lastendLF = 0
        return ''.join(mdtxtlist).strip()

    def _process_tag(self, tag):

        if tag.name in _process_tag:       # 可处理的进行处理
            func = eval('self._tag_'+tag.name)
            return func(tag)
            
        if tag.name in _skip_tag:
            return ''

        if tag.name in _ignore_tag:
            return self._process(tag)
            
        return str(tag)          # 暂无处理的，保持原样


    def _tag_a(self, tag):
        
        if tag.get('href'):  

            attrs = tag.attrs.copy()
            mdtxt='[' + self._process(tag) + '](' + attrs['href']
            title = attrs.get('title') if attrs.get('title') else ''
            self.removeAttrs(attrs, 'href', 'title')
            attrs_str = self.simpleAttrs(attrs)  if self._options['attrs'] else ''   # 对属性进行处理，返回一个其他属性字符串
            s=(title + ' ' + attrs_str).strip()

            if s:
                mdtxt += ' "' + s + '"'

            mdtxt += ')'
        else:
            mdtxt = self._process(tag)

        return mdtxt

    def _tag_strong(self, tag): 

        return self.strong_mark + self._process(tag) + self.strong_mark

    _tag_b = _tag_strong
    
    def _tag_em(self, tag):
        return self.emphasis_mark + self._process(tag) + self.emphasis_mark

    _tag_i = _tag_em

    _tag_cite = _tag_em

    def _tag_s(self, tag):
        return '~~' + self._process(tag) + '~~'

    _tag_del = _tag_s

    def _tag_blockquote(self, tag):
        
        return  LF*2 + '> ' + '> '.join(self._process(tag).splitlines(True)) + LF * 2

    def _tag_br(self, tag):

        return "  " + LF

    def _tag_code(self, tag):

        return '`' +  tag.get_text() + '`'
        
    _tag_tt = _tag_code 

    def _tag_center(self, tag):

        return '<p style = "text-align:center">' + self._process(tag) + '</p>'  if self._options['attrs'] else self._process(tag)

    def _tag_div(self, tag):
        
        return LF*2 + self._process(tag) + LF*2

    def _tag_dl(self, tag):

        return LF*2 + self._process(tag) + LF*2

    def _tag_dt(self, tag):

        return LF*2 + self._process(tag) + LF

    def _tag_dd(self, tag):

        mdtxt = '&nbsp;' if not tag.find_previous_sibling(['dd','dt'])  else ''

        mdtxt +=  '' if tag.previous_sibling and tag.previous_sibling.name in ['dd' , 'dt']  else LF

        mdtxt += ':    ' + '    '.join(self._process(tag).splitlines(True)) + LF

        mdtxt += '' if tag.next_sibling and tag.next_sibling.name == 'dd' else LF

        return  mdtxt
    
    def _tag_table(self, tag):

        caption = tag.find('caption')
        mdtxt = LF*2 + caption.get_text() if caption else ''

        trlist = tag.find_all('tr')
        mdtxt += LF*2 + '|'
        tl = LF + '|'

        if trlist[0].find_parent('thead'):
            thlist = trlist[0].find_all(['td','th'])
            for th in thlist:
                txt = self._process(th)
                txt = txt if txt else ' ' 
                mdtxt += ' ' + txt.replace(LF,'<br>') + ' |'
                tl += '-' + '-'*len(txt) + '-|'
            del trlist[0]
        else:
            maxnum = 0
            for tr in trlist:
                num = len(tr.find_all(['td','th']))
                if num > maxnum:
                    maxnum = num
            mdtxt += '   |' * maxnum
            tl += '---|' * maxnum
        
        mdtxt += tl

        for tr in trlist:
            tdlist = tr.find_all(['td','th'])
            mdtxt += LF + '|'
            for td in tdlist:
                txt = self._process(td)
                txt = txt if txt else ' ' 
                mdtxt += ' ' + txt.replace(LF,'<br>') + ' |'

        return mdtxt + LF*2

    def _tag_h(self, tag):
        
        return LF*2 + '#' * int(tag.name[1]) + ' ' + self._process(tag) + LF*2

    _tag_h1 =_tag_h
    _tag_h2 =_tag_h
    _tag_h3 =_tag_h
    _tag_h4 =_tag_h
    _tag_h5 =_tag_h
    _tag_h6 =_tag_h


    def _tag_hr(self, tag):
        
        return LF*2 + '---' + LF * 2

    def _tag_img(self, tag): 

        attrs = tag.attrs.copy()
        title = attrs.get('title') if attrs.get('title') else ''
        mdtxt='![' + (tag.get('alt') or title)  + '](' + tag['src']

        self.removeAttrs(attrs, 'src', 'title', 'alt')
        attrs_str = self.simpleAttrs(attrs) if self._options['attrs'] else '' 

        s = title + ' ' + attrs_str.strip()

        if s:
            mdtxt += ' "' + s + '"'

        mdtxt += ')'

        return mdtxt


    def _tag_li(self, tag):

        parent = tag.find_parent(['ul','ol'])

        indentation = self.ul_item_mark + '  ' if parent.name == 'ul' else str(parent.find_all('li',recursive=False).index(tag) + 1) + '.  '

        return   indentation + '    '.join(self._process(tag).rstrip().splitlines(True)) + LF  # if tag.find_next_sibling('li') else LF*2)

    
    def _tag_ul(self, tag):

        return (LF*2 if tag.previous_sibling and not tag.previous_sibling.name in ['ul','ol'] else '') + self._process(tag) + LF*2

    _tag_ol = _tag_ul 

    def _tag_p(self, tag):

        return LF*2 + self._process(tag) + LF*2

    def _tag_pre(self, tag):

        return LF*2 + '``` ' + (' '.join(tag['class']) if self._options['attrs'] and tag.has_attr('class') else '' )+ LF + tag.get_text().strip() + LF + '```' + LF*2


    def simpleAttrs(self, attrs):
        if not attrs:
            return u""

        attr_arr = []
        lattrs = attrs.copy()
        if 'id' in lattrs:
            attr_arr.append("#%s" % lattrs['id'])
            del lattrs['id']
        if 'class' in lattrs:
            [attr_arr.append(sv) for sv in lattrs['class']]
            del lattrs['class']

        for k, v in lattrs.items():
            use_sep = False
            if isinstance(v,list):
               v=' '.join([str(s) for s in v])
            for c in (' ', ':', '-', ';'):
                if v.find(c) > -1:
                    use_sep = True
                    break
            if use_sep:
                attr_arr.append("%s='%s'" % (k, v))
            else:
                attr_arr.append("%s=%s" % (k, v))
        return u"{{%s}}" % " ".join(attr_arr)


    def removeAttrs(self, attrs, *keys):
        if not attrs:
            return
        for k in keys:
            try:
                del attrs[k]
            except KeyError:
                pass

def output():

    if options.output_file == 'clipboard':
        clipboard.setText(text)
    else:
        fp=open(options.output_file, 'w')
        fp.write(text)
        fp.close()


def monitor_clipboard():

    global text

    data = clipboard.mimeData()
    if  text != data.text() and data.hasHtml(): 
        text=html2md(data.html(),**vars(options))
        output()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Transform HTML  to Markdown')
    parser.add_argument('-e', '--ignore-emphasis', dest='ignore_emphasis', action='store_true',
        default=False, help='not include any formatting for emphasis')
    parser.add_argument('-i', '--ignore-images', dest='ignore_images', action='store_true',
        default=False, help='not include any formatting for images')
    parser.add_argument('-l', '--ignore-links', dest='ignore_links', action='store_true',
        default=False, help='not include any formatting for links')
    parser.add_argument('-f', '--ignore_footnotes', dest='ignore_footnotes', action='store_true', 
        default=False, help='Disable element attributes in the output (custom Markdown extension)')
    parser.add_argument('-d', '--def_list',  dest='def_list', action='store_false',
        default=True, help='Disable conversion of definition lists')
    parser.add_argument('-t', '--table', dest='table',  action='store_false',
        default=True, help='Disable conversion of table')
    parser.add_argument('-s', '--strikethrough', dest='strikethrough', action='store_true',
        default=True, help='Disable strike-through text')
    parser.add_argument('-a', '--attrs', dest='attrs', action='store_true', 
        default=False, help='Disable element attributes in the output (custom Markdown extension)')
    parser.add_argument('-D', '--dash-unordered-list', dest='ul_style_dash', action='store_true',
        default=False, help='use a dash rather than a star for unordered list items')
    parser.add_argument('-E', '--asterisk-emphasis', dest='em_style_asterisk', action='store_true',
        default=False, help='use an asterisk rather than an underscore for emphasized text')
    parser.add_argument('-o', '--output_file', nargs='+', dest='output_file', type=str, action='store', 
        default='clipboard', help='give output filename,default is out to clipbord')
    parser.add_argument('in_file', nargs='?', action='store', type=str, default="clipboard")
    options = parser.parse_args()
  

    app = QApplication([])
    clipboard = app.clipboard()

    text=''

    if options.in_file == 'clipboard':
        timer_clipboard = QTimer()  # 声明定时器
        timer_clipboard.timeout.connect(monitor_clipboard) # 定时器触发monitor_clipboard方法
        timer_clipboard.start(3000)  # 定时器触发间隔为3秒
        app.exec_()
    else:
        if options.in_file.startswith('http://') or options.in_file.startswith('https://'):
            response = urllib.request.urlopen(options.in_file)
            data = response.read()
        else:
            data = open(options.in_file, 'rb').read()

        text=html2md(data,**vars(options))
        output()