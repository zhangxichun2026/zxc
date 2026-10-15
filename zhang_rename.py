#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 HTML 里的 CSS 类名、id 名、JS 变量统一加 zhang_ 前缀。

定向替换四处，不做全文裸替换（避免误伤正文里的 box / text / main 等普通单词）：
  1. class="..." 属性值
  2. id="..."    属性值
  3. <style> 与独立 .css 里「选择器区段」的 .class / #id
     —— 花括号感知，声明块内部（十六进制颜色 #fff 等）绝不触碰，递归处理 @media/@keyframes
  4. <script> 里声明的变量，以及字符串中对 class/id 的引用（'.foo' / '#foo' / 'foo'）
"""
import re
import os
import sys
import glob

PREFIX = "zhang_"

JS_KEYWORDS = {
    "break", "case", "catch", "class", "const", "continue", "debugger", "default",
    "delete", "do", "else", "export", "extends", "finally", "for", "function", "if",
    "import", "in", "instanceof", "new", "return", "super", "switch", "this", "throw",
    "try", "typeof", "var", "void", "while", "with", "yield", "let", "static",
    "true", "false", "null", "undefined", "await", "async", "of",
    "document", "window", "Math", "Array", "Object", "String", "Number", "Boolean",
    "JSON", "console", "requestAnimationFrame", "setTimeout", "setInterval",
    "parseInt", "parseFloat", "isNaN", "alert", "Date", "RegExp", "Error", "Promise",
}

RE_CLASS_ATTR = re.compile(r'class\s*=\s*(["\'])([^"\']*)\1')
RE_ID_ATTR = re.compile(r'(?<![-\w])id\s*=\s*(["\'])([^"\']*)\1')
RE_SELECTOR = re.compile(r'([.#])([A-Za-z_][\w-]*)')
RE_STYLE_BLOCK = re.compile(r'(<style[^>]*>)(.*?)(</style>)', re.S)
RE_SCRIPT_BLOCK = re.compile(r'(<script(?![^>]*\bsrc=)[^>]*>)(.*?)(</script>)', re.S)


def rename(name):
    if not name or name.startswith(PREFIX):
        return name
    return PREFIX + name


# ---------------- CSS：花括号感知 ----------------
def mask_comments(css):
    store = []

    def rep(m):
        store.append(m.group(0))
        return "\x00%d\x00" % (len(store) - 1)

    return re.sub(r'/\*.*?\*/', rep, css, flags=re.S), store


def unmask_comments(css, store):
    for i, c in enumerate(store):
        css = css.replace("\x00%d\x00" % i, c)
    return css


def _walk_css(css, repl):
    out = []
    pos = 0
    i = 0
    n = len(css)
    while i < n:
        if css[i] == '{':
            sel = css[pos:i]
            depth = 1
            j = i + 1
            while j < n and depth > 0:
                if css[j] == '{':
                    depth += 1
                elif css[j] == '}':
                    depth -= 1
                j += 1
            inner = css[i + 1:j - 1]
            if '{' in inner:                       # @media / @keyframes 等嵌套规则
                out.append(repl(sel))
                out.append('{')
                out.append(_walk_css(inner, repl))  # 内层继续按规则处理
                out.append('}')
            else:                                   # 普通声明块：内部原样保留
                out.append(repl(sel))
                out.append('{')
                out.append(inner)
                out.append('}')
            pos = j
            i = j
        else:
            i += 1
    out.append(css[pos:])
    return "".join(out)


def css_selectors(css):
    """取出所有选择器文本。注释已换成占位符且不还原，因此注释里的 #f00 / .box 不会被采集。"""
    masked, _ = mask_comments(css)
    found = []

    def collect(sel):
        found.append(sel)
        return sel

    _walk_css(masked, collect)
    return "".join(found)


def proc_css(css, cmap, imap):
    masked, store = mask_comments(css)

    def repl(sel):
        def one(m):
            sym, nm = m.group(1), m.group(2)
            if sym == '.' and nm in cmap:
                return "." + cmap[nm]
            if sym == '#' and nm in imap:
                return "#" + imap[nm]
            return m.group(0)
        return RE_SELECTOR.sub(one, sel)

    return unmask_comments(_walk_css(masked, repl), store)


# ---------------- HTML / JS ----------------
def sub_tokens(val, mapping):
    return re.sub(r'\S+', lambda t: mapping.get(t.group(0), t.group(0)), val)


def proc_class_attrs(text, cmap):
    return RE_CLASS_ATTR.sub(
        lambda m: 'class=%s%s%s' % (m.group(1), sub_tokens(m.group(2), cmap), m.group(1)),
        text)


def proc_id_attrs(text, imap):
    return RE_ID_ATTR.sub(
        lambda m: 'id=%s%s%s' % (m.group(1), sub_tokens(m.group(2), imap), m.group(1)),
        text)


def proc_js(js, cmap, imap):
    decls = set()
    for m in re.finditer(r'\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)', js):
        decls.add(m.group(1))
    for m in re.finditer(r'\bfunction\s+([A-Za-z_$][\w$]*)', js):
        decls.add(m.group(1))
    for m in re.finditer(r'\bfunction\s*[\w$]*\s*\(([^)]*)\)', js):
        for a in m.group(1).split(','):
            a = a.strip()
            if re.fullmatch(r'[A-Za-z_$][\w$]*', a):
                decls.add(a)
    for m in re.finditer(r'\(([^()]*)\)\s*=>', js):     # 箭头函数参数
        for a in m.group(1).split(','):
            a = a.strip()
            if re.fullmatch(r'[A-Za-z_$][\w$]*', a):
                decls.add(a)

    vmap = {d: rename(d) for d in decls if d not in JS_KEYWORDS}

    # 先改字符串里对 class / id 的引用，再改变量名（避免变量名先被改后破坏字符串匹配）
    for n in sorted(set(cmap) | set(imap), key=len, reverse=True):
        new = rename(n)
        js = re.sub(r'(["\'])([.#]?)' + re.escape(n) + r'(["\'])',
                    lambda m: m.group(1) + m.group(2) + new + m.group(3), js)

    for d in sorted(vmap, key=len, reverse=True):
        js = re.sub(r'(?<![\w$.])' + re.escape(d) + r'\b', vmap[d], js)
    return js, vmap


def collect(html):
    classes, ids = set(), set()
    for m in RE_CLASS_ATTR.finditer(html):
        classes.update(m.group(2).split())
    for m in RE_ID_ATTR.finditer(html):
        ids.update(m.group(2).split())
    for m in RE_STYLE_BLOCK.finditer(html):
        sel_text = css_selectors(m.group(2))
        for sm in RE_SELECTOR.finditer(sel_text):
            sym, nm = sm.group(1), sm.group(2)
            (classes if sym == '.' else ids).add(nm)
    return classes, ids


def process(html):
    classes, ids = collect(html)
    cmap = {c: rename(c) for c in classes}
    imap = {i: rename(i) for i in ids}
    out, pos, vmap_all = [], 0, {}
    for m in re.finditer(r'<style[^>]*>.*?</style>|<script(?![^>]*\bsrc=)[^>]*>.*?</script>',
                         html, re.S):
        out.append(proc_id_attrs(proc_class_attrs(html[pos:m.start()], cmap), imap))
        block = m.group(0)
        sm = re.match(r'(<style[^>]*>)(.*?)(</style>)', block, re.S)
        km = re.match(r'(<script[^>]*>)(.*?)(</script>)', block, re.S)
        if sm:
            out.append(sm.group(1) + proc_css(sm.group(2), cmap, imap) + sm.group(3))
        else:
            new_js, vmap = proc_js(km.group(2), cmap, imap)
            vmap_all.update(vmap)
            out.append(km.group(1) + new_js + km.group(3))
        pos = m.end()
    out.append(proc_id_attrs(proc_class_attrs(html[pos:], cmap), imap))
    return "".join(out), cmap, imap, vmap_all


def main():
    src_dir, dst_dir = sys.argv[1], sys.argv[2]
    os.makedirs(dst_dir, exist_ok=True)
    allc, alli, allv = set(), set(), 0
    for path in sorted(glob.glob(os.path.join(src_dir, "*.html"))):
        name = os.path.basename(path)
        raw = open(path, encoding="utf-8", newline="").read()   # 保留原 CRLF
        new, cmap, imap, vmap = process(raw)
        open(os.path.join(dst_dir, name), "w", encoding="utf-8", newline="").write(new)
        allc |= set(cmap)
        alli |= set(imap)
        allv += len(vmap)
        print("=" * 62)
        print("【%s】" % name)
        if cmap:
            print("  class(%d): %s" % (len(cmap), ", ".join(sorted(cmap))))
        if imap:
            print("  id(%d)   : %s" % (len(imap), ", ".join(sorted(imap))))
        if vmap:
            print("  jsvar(%d): %s" % (len(vmap), ", ".join(sorted(vmap))))
    print("=" * 62)
    print("合计：类名 %d 个、id %d 个、JS 变量 %d 个" % (len(allc), len(alli), allv))
    for path in glob.glob(os.path.join(src_dir, "*.css")):
        name = os.path.basename(path)
        raw = open(path, encoding="utf-8", newline="").read()
        open(os.path.join(dst_dir, name), "w", encoding="utf-8", newline="").write(
            proc_css(raw, {}, {}))


if __name__ == "__main__":
    main()
