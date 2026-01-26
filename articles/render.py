from typing import Dict, Tuple, Any
import os
from io import StringIO
from string import Template
from html import escape as html_escape

html_template = Template(
"""
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${title}</title>
        <link rel="stylesheet" href="/style.css">
    </head>
    <body>
        <div id="root">
            <header>
                <h1 id="logo">bagasjs</h1>
                <div class="menu">
                    <div class="menu-item"><a href="/">Home</a></div>
                    <div class="menu-item"><a href="/articles/articles.html">Articles</a></div>
                </div>
            </header>
            <section id="${section_name}">
                ${post}
            </section>
            <footer> Copyright 2026 BagasJS </footer>
        </div>
    </body>
</html>
""")

post_item = Template(
""" 
<div class="post-item">
    <div class="project-name">
        ${date}
    </div>
    <div class="project-excerpt">
        <a href="${url}">${title}</a> 
    </div>
</div>
""")

def translate_line(line: str) -> str:
    if len(line) == 0: return line
    result = StringIO()
    i = 0
    while i < len(line):
        match line[i]:
            case "`":
                i += 1
                start = i
                while i < len(line):
                    if line[i] == "`":
                        break
                    i += 1
                value = line[start:i]
                i += 1
                result.write(f"<span class=\"article-inline-code\">{html_escape(value)}</span>")
            case "_":
                i += 1
                start = i
                while i < len(line):
                    if line[i] == "_":
                        break
                    i += 1
                value = line[start:i]
                i += 1
                result.write(f"<span class=\"article-italic\">{html_escape(translate_line(value))}</span>")
            case "*":
                i += 1
                start = i
                while i < len(line):
                    if line[i] == "*":
                        break
                    i += 1
                value = line[start:i]
                i += 1
                result.write(f"<span class=\"article-bold\">{html_escape(translate_line(value))}</span>")
            case "[":
                start = i + 1
                escape_count = 0
                while i < len(line):
                    if line[i] == "]":
                        escape_count -= 1
                        if escape_count < 1:
                            break
                    if line[i] == "[": #]
                        escape_count += 1
                    i += 1
                end = i
                i += 1
                value = line[start:end]
                url = ""
                if line[i] == "(": #)
                    start = i + 1
                    escape_count = 0
                    while i < len(line):
                        if line[i] == ")":
                            escape_count -= 1
                            if escape_count < 1:
                                break
                        if line[i] == "(": #)
                            escape_count += 1
                        i += 1
                    end = i
                    i += 1
                    url = line[start:end]
                    result.write(f"<a href=\"{url}\">{html_escape(value)}</a>")
                else:
                    result.write(f"[{html_escape(translate_line(value))}]")
            case _:
                result.write(line[i])
                i += 1
    return result.getvalue()

def translate_post_to_html(output: StringIO, source: str):
    lines = source.splitlines()
    in_code_block = False
    prev_is_normal_text = False
    for line in lines:
        if line.startswith("#"):
            if prev_is_normal_text:
                output.write("</p>\n")
                prev_is_normal_text = False
            level = 0
            for ch in line:
                if ch != "#":
                    break
                level += 1
                if level >= 6:
                    break
            value = translate_line(line[level:])
            output.write(f"<h{level} class=\"article-h{level}\">{value}</h{level}>\n")
        elif line.startswith("```"):
            if prev_is_normal_text:
                output.write("</p>\n")
                prev_is_normal_text = False
            in_code_block = not in_code_block 
            if in_code_block:
                output.write("<pre class=\"article-code\"><code>\n")
            else:
                output.write("<code></pre>\n")
        elif len(line.lstrip()) == 0:
            if prev_is_normal_text:
                output.write("</p>\n")
                prev_is_normal_text = False
        else:
            if not prev_is_normal_text:
                output.write("<p class=\"article-p\">\n")
            output.write(f"{translate_line(line)}\n")
            prev_is_normal_text = True
            pass
    if prev_is_normal_text:
        output.write("</p>\n")
        prev_is_normal_text = False

def compile_post(filename: str, source: str) -> Tuple[Dict[str, Any], str]:
    # Peek if there's front-matter
    lines = source.splitlines()
    if lines[0].startswith("---"):
        pass
    i = 1
    metadata = {"__input__": filename }
    while i < len(lines):
        if lines[i].startswith("---"):
            i += 1
            break
        key, value = lines[i].split(":", maxsplit=1)
        metadata[key] = value
        i += 1
    body = "\n".join(lines[i:])
    output = StringIO()
    translate_post_to_html(output, body)
    return metadata, output.getvalue()

if __name__ == "__main__":
    posts = []
    for name in os.listdir(os.getcwd()):
        if not name.endswith(".md"):
            continue
        with open(name, "r") as file:
            metadata, html = compile_post(name, file.read())
            html = html_template.substitute(title=metadata["title"], post=html, section_name="articles")
            output_filename = f"{os.path.splitext(name)[0]}.html"
            metadata["__output__"] = output_filename
            with open(output_filename, "w") as outputf:
                outputf.write(html)
            posts.append(metadata)

    index_body =  '<h1 class="section-title"><a href="#articles">Articles</a></h1>\n'
    if len(posts) > 0:
        index_body += f'<div class="projects-list">\n'
        for post in posts:
            url = f"/articles/{post['__output__']}"
            index_body += post_item.substitute(title=post["title"], date=post["date"], url=url)
        index_body += f'</div>\n'
    else:
        index_body += "<p>There's no article currently</p>"
    with open("articles.html", "w") as file:
        html = html_template.substitute(title="List of articles", post=index_body, section_name="posts")
        file.write(html)

